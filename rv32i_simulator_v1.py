import re


registers = [0] * 32
program_counter = 0
memory = {}
labels = {}
csr_registers = {}


# Memory Handling Functions 
def store_byte(address, value):
    """ Store a single byte (8 bits) in memory """
    memory[address] = value & 0xFF

def store_halfword(address, value):
    """ Store a halfword (2 bytes) in memory """
    store_byte(address, value & 0xFF)
    store_byte(address + 1, (value >> 8) & 0xFF)

def store_word(address, value):
    """ Store a word (4 bytes) in memory """
    store_byte(address, value & 0xFF)
    store_byte(address + 1, (value >> 8) & 0xFF)
    store_byte(address + 2, (value >> 16) & 0xFF)
    store_byte(address + 3, (value >> 24) & 0xFF)

def load_byte(address):
    """ Load a single byte (8 bits) from memory """
    return memory.get(address, 0)

def load_halfword(address):
    """ Load a halfword (2 bytes) from memory and sign-extend """
    byte1 = load_byte(address)
    byte2 = load_byte(address + 1)
    value = (byte2 << 8) | byte1
    return value if byte2 < 0x80 else value | 0xFFFF0000

def load_halfword_unsigned(address):
    """ Load a halfword (2 bytes) from memory and zero-extend """
    byte1 = load_byte(address)
    byte2 = load_byte(address + 1)
    return (byte2 << 8) | byte1

def load_word(address):
    """ Load a word (4 bytes) from memory """
    byte1 = load_byte(address)
    byte2 = load_byte(address + 1)
    byte3 = load_byte(address + 2)
    byte4 = load_byte(address + 3)
    return (byte4 << 24) | (byte3 << 16) | (byte2 << 8) | byte1


# Arithmetic and Logical Instructions
def add(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = registers[rs1] + registers[rs2]

def sub(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = registers[rs1] - registers[rs2]

def addi(rd, rs1, imm):
    """ Add immediate value to rs1 and store in rd """
    if rd is not None and imm is not None:
        registers[rd] = registers[rs1] + imm
    else:
        print(f"Error: ADDI instruction missing operands. rd={rd}, rs1={rs1}, imm={imm}")


def andi(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] & imm

def ori(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] | imm

def xori(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] ^ imm

def slt(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = 1 if registers[rs1] < registers[rs2] else 0

#should be stliu
def slti(rd, rs1, imm):
    if rd != 0:
        registers[rd] = 1 if registers[rs1] < imm else 0

def sltiu(rd, rs1, imm):
    if rd != 0:
        registers[rd] = 1 if (registers[rs1] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0

def sll(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = registers[rs1] << (registers[rs2] & 0x1F)

def srl(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = (registers[rs1] & 0xFFFFFFFF) >> (registers[rs2] & 0x1F)

def sra(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = registers[rs1] >> (registers[rs2] & 0x1F)

def sltu(rd, rs1, rs2):
    """ Set Less Than Unsigned """
    registers[rd] = 1 if (registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF) else 0

def xor(rd, rs1, rs2):
    """ Bitwise XOR """
    registers[rd] = registers[rs1] ^ registers[rs2]

def or_(rd, rs1, rs2):
    """ Bitwise OR """
    registers[rd] = registers[rs1] | registers[rs2]

def and_(rd, rs1, rs2):
    """ Bitwise AND """
    registers[rd] = registers[rs1] & registers[rs2]


# Branch Instructions with Labels
def beq(rs1, rs2, target_label):
    """
    Branch if equal: If registers[rs1] == registers[rs2], jump to the label.
    """
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BEQ instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    # Check if the values in the registers are equal
    if registers[rs1] == registers[rs2]:
        print(f"BEQ: Branch taken to label '{target_label}'")
        
        # Ensure the label exists in the dictionary
        if target_label in labels:
            # Update the program counter to the label's address
            new_pc = labels[target_label]
            print(f"BEQ: Updated PC to {new_pc} for label '{target_label}'")
            program_counter = new_pc
        else:
            print(f"Error: Label '{target_label}' not found in labels dictionary.")
            return False
        return True
    else:
        print(f"BEQ: Branch not taken, registers[{rs1}]={registers[rs1]}, registers[{rs2}]={registers[rs2]}")
    return False




def bne(rs1, rs2, target_label):
    global program_counter
    if registers[rs1] != registers[rs2]:
        print(f"BNE: Branch taken to label '{target_label}'")
        if isinstance(target_label, str):
            program_counter = labels.get(target_label, program_counter)
        elif isinstance(target_label, int):
            program_counter = target_label
        return True
    return False

def bge(rs1, rs2, target_label):
    global program_counter
    if registers[rs1] >= registers[rs2]:
        print(f"BGE: Branch taken to label '{target_label}'")
        if isinstance(target_label, str):
            program_counter = labels.get(target_label, program_counter)
        elif isinstance(target_label, int):
            program_counter = target_label
        return True
    return False

def blt(rs1, rs2, target_label):
    global program_counter
    if registers[rs1] < registers[rs2]:
        print(f"BLT: Branch taken to label '{target_label}'")
        if isinstance(target_label, str):
            program_counter = labels.get(target_label, program_counter)
        elif isinstance(target_label, int):
            program_counter = target_label
        return True
    return False

def bltu(rs1, rs2, target_label):
    global program_counter
    if (registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF):
        print(f"BLTU: Branch taken to label '{target_label}'")
        if isinstance(target_label, str):
            program_counter = labels.get(target_label, program_counter)
        elif isinstance(target_label, int):
            program_counter = target_label
        return True
    return False

def bgeu(rs1, rs2, target_label):
    global program_counter
    if (registers[rs1] & 0xFFFFFFFF) >= (registers[rs2] & 0xFFFFFFFF):
        print(f"BGEU: Branch taken to label '{target_label}'")
        if isinstance(target_label, str):
            program_counter = labels.get(target_label, program_counter)
        elif isinstance(target_label, int):
            program_counter = target_label
        return True
    return False


# Memory Instructions
# Load and Store Instructions
def lw(rd, offset, rs1):
    """
    Load a word from memory into register rd from address computed as offset + value in rs1.
    """
    if rd is None or rd < 0 or rd >= len(registers):
        print(f"Error: Invalid register index rd={rd}")
        return
    if rs1 is None or rs1 < 0 or rs1 >= len(registers):
        print(f"Error: Invalid register index rs1={rs1}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_word(address)
    print(f"LW: Loaded word {registers[rd]} from address {address} into register x{rd}")



def lb(rd, offset, rs1):
    """
    Load a byte from memory into register rd from address computed as offset + value in rs1.
    """
    if rd is None or rd < 0 or rd >= len(registers):
        print(f"Error: Invalid register index rd={rd}")
        return
    if rs1 is None or rs1 < 0 or rs1 >= len(registers):
        print(f"Error: Invalid register index rs1={rs1}")
        return

    address = registers[rs1] + offset
    byte = load_byte(address)
    registers[rd] = byte if byte < 0x80 else byte | 0xFFFFFF00
    print(f"LB: Loaded byte {registers[rd]} from address {address} into register x{rd}")

def lbu(rd, offset, rs1):
    """
    Load an unsigned byte from memory into register rd from address computed as offset + value in rs1.
    """
    if rd is None or rd < 0 or rd >= len(registers):
        print(f"Error: Invalid register index rd={rd}")
        return
    if rs1 is None or rs1 < 0 or rs1 >= len(registers):
        print(f"Error: Invalid register index rs1={rs1}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_byte(address)
    print(f"LBU: Loaded unsigned byte {registers[rd]} from address {address} into register x{rd}")


def lh(rd, offset, rs1):
    """
    Load a halfword (2 bytes) from memory into register rd from address computed as offset + value in rs1.
    """
    if rd is None or rd < 0 or rd >= len(registers):
        print(f"Error: Invalid register index rd={rd}")
        return
    if rs1 is None or rs1 < 0 or rs1 >= len(registers):
        print(f"Error: Invalid register index rs1={rs1}")
        return

    address = registers[rs1] + offset
    halfword = load_halfword(address)
    registers[rd] = halfword if halfword < 0x8000 else halfword | 0xFFFF0000
    print(f"LH: Loaded halfword {registers[rd]} from address {address} into register x{rd}")


def lhu(rd, offset, rs1):
    """
    Load an unsigned halfword (2 bytes) from memory into register rd from address computed as offset + value in rs1.
    """
    if rd is None or rd < 0 or rd >= len(registers):
        print(f"Error: Invalid register index rd={rd}")
        return
    if rs1 is None or rs1 < 0 or rs1 >= len(registers):
        print(f"Error: Invalid register index rs1={rs1}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_halfword(address)
    print(f"LHU: Loaded unsigned halfword {registers[rd]} from address {address} into register x{rd}")


def sw(rs1, offset, rs2):
    """
    Store the value from register rs1 to memory at address computed as offset + value in rs2.
    """
    if rs1 is None or rs1 < 0 or rs1 >= len(registers):
        print(f"Error: Invalid register index rs1={rs1}")
        return
    if rs2 is None or rs2 < 0 or rs2 >= len(registers):
        print(f"Error: Invalid register index rs2={rs2}")
        return

    # Calculate the memory address
    address = registers[rs2] + offset
    value_to_store = registers[rs1]
    
    # Store the word (4 bytes) in memory
    store_word(address, value_to_store)
    print(f"SW: Stored value {value_to_store} from register x{rs1} to memory address {address}")




def sb(rs1, offset, rs2):
    """
    Store the lowest byte of the value in rs1 to memory at address computed as offset + value in rs2.
    """
    if rs1 is None or rs1 < 0 or rs1 >= len(registers):
        print(f"Error: Invalid register index rs1={rs1}")
        return
    if rs2 is None or rs2 < 0 or rs2 >= len(registers):
        print(f"Error: Invalid register index rs2={rs2}")
        return

    address = registers[rs2] + offset
    value_to_store = registers[rs1] & 0xFF
    
    store_byte(address, value_to_store)
    print(f"SB: Stored byte {value_to_store} from register x{rs1} to memory address {address}")


def sh(rs1, offset, rs2):
    """
    Store the lowest 2 bytes of the value in rs1 to memory at address computed as offset + value in rs2.
    """
    if rs1 is None or rs1 < 0 or rs1 >= len(registers):
        print(f"Error: Invalid register index rs1={rs1}")
        return
    if rs2 is None or rs2 < 0 or rs2 >= len(registers):
        print(f"Error: Invalid register index rs2={rs2}")
        return

    address = registers[rs2] + offset
    value_to_store = registers[rs1] & 0xFFFF
    
    store_halfword(address, value_to_store)
    print(f"SH: Stored halfword {value_to_store} from register x{rs1} to memory address {address}")




# Jump and Link Instructions
def jal(rd, target_label):
    """
    Jump and Link: Store the return address in rd and jump to the label.
    If rd is x0, the return address is not stored.
    """
    global program_counter
    if rd is None or target_label is None:
        print(f"Error: JAL instruction missing operands rd={rd}, label={target_label}")
        return

    # Store the return address (address of next instruction) in rd unless rd is x0
    if rd != 0:
        registers[rd] = program_counter + 1

    # Jump to the target label
    if isinstance(target_label, str):
        if target_label in labels:
            program_counter = labels[target_label]
        else:
            print(f"Error: Label '{target_label}' not found.")
            return
    elif isinstance(target_label, int):
        program_counter = target_label

    print(f"JAL: Jumped to label '{target_label}', return address stored in x{rd}")





def jalr(rd, rs1, offset):
    global program_counter
    if rd != 0:
        registers[rd] = program_counter + 1
    program_counter = (registers[rs1] + offset) & ~1


# Immediate Instructions
def lui(rd, imm):
    registers[rd] = imm << 12

def auipc(rd, imm):
    registers[rd] = program_counter + (imm << 12)

def slti(rd, rs1, imm):
    """ Set Less Than Immediate """
    registers[rd] = 1 if registers[rs1] < imm else 0

def sltiu(rd, rs1, imm):
    """ Set Less Than Immediate Unsigned """
    registers[rd] = 1 if (registers[rs1] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0

def slli(rd, rs1, imm):
    """ Shift Left Logical Immediate """
    registers[rd] = registers[rs1] << (imm & 0x1F)

def srli(rd, rs1, imm):
    """ Shift Right Logical Immediate (zero-fill) """
    registers[rd] = (registers[rs1] & 0xFFFFFFFF) >> (imm & 0x1F)

def srai(rd, rs1, imm):
    """ Shift Right Arithmetic Immediate (sign-extend) """
    registers[rd] = registers[rs1] >> (imm & 0x1F)

# System Instructions
def ecall():
    print("ECALL - Halting")
    return True

def ebreak():
    print("EBREAK - Halting")
    return True

def fence():
    print("fence - Halting")
    return True

def fence_tso():
    print("fence.tso - Halting")
    return True

def pause():
    print("PAUSE - Halting")
    return True

def register_labels(instruction_lines):
    """
    Registers labels by associating them with the actual address in the instruction list.
    """
    global labels
    labels = {}
    address = 0
    for line in instruction_lines:
        line = line.strip()
        if '#' in line:
            line = line.split('#')[0].strip()
        if not line:
            continue

        # Check if the line is a label
        if line.endswith(':'):
            label_name = line[:-1].strip()
            labels[label_name] = address  # Store the program counter address, not the line number
        else:
            address += 1




def printRegisters(instruction=None):
    """
    Prints the state of the program, including the program counter, registers,
    memory contents, and labels (if available).
    """
    # # Print the current instruction being executed, if provided
    # if instruction:
    #     print("\n=== Executing Instruction ===")
    #     print(f"Instruction: {instruction}\n")
    
    # Print the program counter
    print("\n=== Program Counter ===")
    print(f"PC: {program_counter}\n")

    print("\n=== Register Values ===")
    
    # Print registers in decimal format
    print("\nDecimal:")
    for i in range(0, 32, 4):
        print(f"x{i:02}: {registers[i]:>8} | x{i+1:02}: {registers[i+1]:>8} | x{i+2:02}: {registers[i+2]:>8} | x{i+3:02}: {registers[i+3]:>8}")
    
    # Print registers in binary format
    print("\nBinary:")
    for i in range(0, 32, 4):
        print(f"x{i:02}: {bin(registers[i]):>32} | x{i+1:02}: {bin(registers[i+1]):>32} | x{i+2:02}: {bin(registers[i+2]):>32} | x{i+3:02}: {bin(registers[i+3]):>32}")

    # Print registers in hexadecimal format
    print("\nHexadecimal:")
    for i in range(0, 32, 4):
        print(f"x{i:02}: {hex(registers[i]):>10} | x{i+1:02}: {hex(registers[i+1]):>10} | x{i+2:02}: {hex(registers[i+2]):>10} | x{i+3:02}: {hex(registers[i+3]):>10}")
    
    # Print memory contents if not empty
    print("\n=== Memory Contents ===")
    if memory:
        print(f"{'Address':<12}{'Byte Value (Hex)':<20}{'Byte Value (Dec)':<20}")
        for address in sorted(memory.keys()):
            print(f"0x{address:08X}     0x{memory[address]:02X}                {memory[address]}")
    else:
        print("Memory is empty.")
    
    # Print labels dictionary if available
    if 'labels' in globals() and labels:
        print("\n=== Labels Dictionary ===")
        for label, address in labels.items():
            print(f"Label '{label}': Address {address}")
    else:
        print("\nNo labels found.")



#First pass to register labels
def scan_labels(instruction_lines):
    labels = {}
    address = 0
    for line in instruction_lines:
        line = line.strip()
        # Ignore comments
        if '#' in line:
            line = line.split('#')[0].strip()
        if not line:
            continue

        # Check if the line is a label
        if line.endswith(':'):
            label_name = line[:-1].strip()
            labels[label_name] = address
        else:
            # Increment address only for actual instructions
            address += 1
    return labels



#Utility Functions

def read_instructions_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()



def instruction_splitting(line):
    """
    Split an instruction line into its components.
    Handles R-type, I-type, S-type, B-type, U-type, and J-type instructions.
    """
    line = line.strip()
    # Remove comments
    if '#' in line:
        line = line.split('#')[0].strip()

    if not line:
        return None, None, None, None, None, None

    parts = line.replace(',', '').split()
    opcode = parts[0].upper()

    # Handling S-type instructions with offset notation (e.g., SW, SB, SH, LW)
    if opcode in ['SW', 'SB', 'SH', 'LW', 'LH', 'LHU', 'LB', 'LBU']:
        if len(parts) != 3:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        
        # Parse the offset notation like 100(x2)
        try:
            offset, base_register = parts[2].split('(')
            offset = int(offset)
            rs1 = int(base_register[:-1][1:])  # Remove closing parenthesis and extract register number
        except ValueError:
            print(f"Error: Invalid offset notation. line='{line}'")
            return None, None, None, None, None, None

        if opcode == 'SW' or opcode in ['SB', 'SH']:
            rs2 = int(parts[1][1:])  # Register to store
            return opcode, None, rs1, rs2, offset, None
        else:  # For LW, LH, LHU, LB, LBU
            rd = int(parts[1][1:])  # Register to load into
            return opcode, rd, rs1, None, offset, None

    # I-type instructions (e.g., ADDI, ANDI, ORI, XORI, SLTI, SLTIU, JALR)
    if opcode in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU', 'JALR']:
        if len(parts) != 4:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = int(parts[1][1:])
        rs1 = int(parts[2][1:])
        imm = int(parts[3]) if parts[3].isdigit() else parts[3]
        return opcode, rd, rs1, None, imm, None

    # R-type instructions (e.g., ADD, SUB, SLT, SLTU, XOR, OR, AND, SLL, SRL, SRA)
    elif opcode in ['ADD', 'SUB', 'SLT', 'SLTU', 'XOR', 'OR', 'AND', 'SLL', 'SRL', 'SRA']:
        if len(parts) != 4:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = int(parts[1][1:])
        rs1 = int(parts[2][1:])
        rs2 = int(parts[3][1:])
        return opcode, rd, rs1, rs2, None, None

    # B-type instructions (e.g., BEQ, BNE, BLT, BGE, BLTU, BGEU)
    elif opcode in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
        if len(parts) != 4:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rs1 = int(parts[1][1:])
        rs2 = int(parts[2][1:])
        label = parts[3]
        return opcode, None, rs1, rs2, label, None

    # U-type instructions (e.g., LUI, AUIPC)
    elif opcode in ['LUI', 'AUIPC']:
        if len(parts) != 3:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = int(parts[1][1:])
        imm = int(parts[2])
        return opcode, rd, None, None, imm, None

    # J-type instructions (e.g., JAL)
    elif opcode == 'JAL':
        if len(parts) != 3:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = int(parts[1][1:])
        label = parts[2]
        return opcode, rd, None, None, label, None

    print(f"Error: Unrecognized instruction format. line='{line}'")
    return None, None, None, None, None, None



       

def parse_register(reg):
    """ Helper function to parse register names like x1, x2, etc. """
    if reg[0].lower() == 'x' and reg[1:].isdigit():
        return int(reg[1:])
    print(f"Error: Invalid register {reg}")
    return None

def parse_immediate(value):
    """ Helper function to parse immediate values. """
    try:
        return int(value)
    except ValueError:
        return value  # Return as label if it's not an integer







# Additional function to load memory from a file with type detection
def load_memory_from_file(memory_file):
    global memory
    with open(memory_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                address, value = line.split(',')
                address = int(address.strip(), 0)  # Convert address to integer
                value = value.strip()

                # Detect and store value type
                if value.startswith('"') and value.endswith('"'):
                    memory[address] = value[1:-1]  # Remove double quotes for string
                elif value.startswith("'") and value.endswith("'"):
                    memory[address] = value[1]  # Remove single quotes for char
                else:
                    memory[address] = int(value, 0)  # Convert to integer if no quotes

# Modified user_input function
def user_input():
    global program_counter
    print("Enter the instruction file path:")
    file_path = input().strip()
    print("Enter the starting address of the program:")
    program_counter = int(input().strip())
    
    # Prompt for optional memory file
    print("Enter the memory initialization file path (leave empty if none):")
    memory_file = input().strip()
    if memory_file:
        load_memory_from_file(memory_file)
    print(memory)
    return file_path


def main():
    global program_counter
    program_counter = 0
    
    # Step 1: Read the instruction file
    file_path = user_input()
    instruction_lines = read_instructions_from_file(file_path)
    
    # Step 2: First pass to register labels
    labels = {}
    for line_number, line in enumerate(instruction_lines):
        line = line.strip()
        if '#' in line:
            line = line.split('#')[0].strip()
        if not line:
            continue

        if line.endswith(':'):
            label_name = line[:-1].strip()
            labels[label_name] = line_number

    # Debug: Print registered labels
    print("\n=== Registered Labels ===")
    for label, address in labels.items():
        print(f"Label '{label}': Address {address}")

    # Step 3: Execute instructions
    while program_counter < len(instruction_lines):
        line = instruction_lines[program_counter].strip()

        print("\n=== Executing Instruction ===")
        print(f"Instruction: {line}")
        print(f"Current PC: {program_counter}")
        print(f"Labels Dictionary: {labels}")

        # Ignore comments and empty lines
        if '#' in line:
            line = line.split('#')[0].strip()
        if not line:
            program_counter += 1
            continue

        # Check if the line is a label and skip it during execution
        if line.endswith(':'):
            program_counter += 1
            continue

        # Parse the instruction
        opcode, rd, rs1, rs2, imm_or_label, offset = instruction_splitting(line)
        if not opcode:
            program_counter += 1
            continue

        # Debug: Print parsed instruction components
        print(f"Parsed: opcode={opcode}, rd={rd}, rs1={rs1}, rs2={rs2}, imm_or_label={imm_or_label}, offset={offset}")

        # Execute the instruction based on its type
        if opcode in instructions:
            if opcode in ['BEQ', 'BNE', 'BGE', 'BLT', 'BLTU', 'BGEU']:
                branch_taken = instructions[opcode](rs1, rs2, imm_or_label)
                print(f"BEQ/BNE: Branch taken={branch_taken}, New PC={program_counter}")
                
                if branch_taken:
        # Update the program counter to the label address
                    if imm_or_label in labels:
                        program_counter = labels[imm_or_label]
                        print(f"Branch taken to label '{imm_or_label}', new PC={program_counter}")
                            # Ensure we move past the instruction after the label
                        program_counter += 1
                    continue  # Skip incrementing program counter in the main loop
            elif opcode in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU']:
                instructions[opcode](rd, rs1, imm_or_label)
            elif opcode in ['LW', 'LB', 'LBU', 'LH', 'LHU']:
                instructions[opcode](rd, imm_or_label, rs1)
            elif opcode in ['SW', 'SB', 'SH']:
                instructions[opcode](rs1, imm_or_label, rs2)
            elif opcode == 'JAL':
                if imm_or_label in labels:
                    print(f"JAL: Jumping to label '{imm_or_label}' at address {labels[imm_or_label]}")
                    instructions[opcode](rd, labels[imm_or_label])
                    continue  # Skip incrementing program counter since we jumped
                else:
                    print(f"Error: Label '{imm_or_label}' not found.")
                    break
            elif opcode == 'JALR':
                instructions[opcode](rd, rs1, imm_or_label)
                continue  # Jumped, so skip incrementing program counter
            else:
                instructions[opcode](rd, rs1, rs2)

        # Print the current state of registers after execution
        printRegisters(instruction=line)

        # Increment the program counter
        program_counter += 1
        print(f"Next PC: {program_counter}")


  



# Dictionary of instructions remains the same
instructions = {
    'ADD': add, 'SUB': sub, 'ADDI': addi, 'ANDI': andi,
    'ORI': ori, 'XORI': xori, 'SLT': slt, 'SLTI': slti, 'SLTIU': sltiu,
    'SLL': sll, 'SRL': srl, 'SRA': sra, 'SLLI': slli, 'SRLI': srli, 'SRAI': srai,
    'SLTU': sltu, 'XOR': xor, 'OR': or_, 'AND': and_,
    'BEQ': beq, 'BNE': bne, 'BLT': blt, 'BGE': bge, 'BLTU': bltu, 'BGEU': bgeu,
    'LW': lw, 'SW': sw, 'LH': lh, 'LHU': lhu, 'LB': lb, 'LBU': lbu, 'SB': sb, 'SH': sh,
    'JAL': jal, 'JALR': jalr, 'LUI': lui, 'AUIPC': auipc,
    'FENCE': fence, 'FENCE.TSO': fence_tso, 'PAUSE': pause,
    'ECALL': ecall, 'EBREAK': ebreak
}

if __name__ == "__main__":
    main()
