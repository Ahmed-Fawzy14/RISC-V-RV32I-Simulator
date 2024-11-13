import sys

# Global Variables
registers = [0] * 32
program_counter = 0
memory = {}
labels = {}
csr_registers = {}

# Memory is handled in little-endian format

# Memory Handling Functions
def store_byte(address, value):
    """Store a single byte (8 bits) in memory."""
    memory[address] = value & 0xFF

def store_halfword(address, value):
    """Store a halfword (2 bytes) in memory."""
    store_byte(address, value & 0xFF)
    store_byte(address + 1, (value >> 8) & 0xFF)

def store_word(address, value):
    """Store a word (4 bytes) in memory."""
    store_byte(address, value & 0xFF)
    store_byte(address + 1, (value >> 8) & 0xFF)
    store_byte(address + 2, (value >> 16) & 0xFF)
    store_byte(address + 3, (value >> 24) & 0xFF)

def load_byte(address):
    """Load a single byte (8 bits) from memory."""
    if address not in memory:
        print(f"Warning: Loading from uninitialized memory address {address}. Returning 0.")
    return memory.get(address, 0)

def load_halfword(address):
    """Load a halfword (2 bytes) from memory and sign-extend."""
    byte1 = load_byte(address)
    byte2 = load_byte(address + 1)
    value = (byte2 << 8) | byte1
    if value & 0x8000:
        value |= 0xFFFF0000  # Sign-extend to 32 bits
    return value

def load_halfword_unsigned(address):
    """Load a halfword (2 bytes) from memory and zero-extend."""
    byte1 = load_byte(address)
    byte2 = load_byte(address + 1)
    return (byte2 << 8) | byte1

def load_word(address):
    """Load a word (4 bytes) from memory."""
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
    """Add immediate value to rs1 and store in rd."""
    if rd != 0:
        if rd is not None and imm is not None:
            registers[rd] = registers[rs1] + imm
        else:
            print(f"Error: ADDI instruction missing operands. rd={rd}, rs1={rs1}, imm={imm}")
    else:
        print("Warning: Attempt to write to x0 ignored.")

def andi(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] & imm
    else:
        print("Warning: Attempt to write to x0 ignored.")

def ori(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] | imm
    else:
        print("Warning: Attempt to write to x0 ignored.")

def xori(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] ^ imm
    else:
        print("Warning: Attempt to write to x0 ignored.")

def slt(rd, rs1, rs2):
    """Set Less Than."""
    if rd != 0:
        registers[rd] = 1 if registers[rs1] < registers[rs2] else 0
    else:
        print("Warning: Attempt to write to x0 ignored.")

def slti(rd, rs1, imm):
    """Set Less Than Immediate."""
    if rd != 0:
        registers[rd] = 1 if registers[rs1] < imm else 0
    else:
        print("Warning: Attempt to write to x0 ignored.")

def sltiu(rd, rs1, imm):
    """Set Less Than Immediate Unsigned."""
    if rd != 0:
        registers[rd] = 1 if (registers[rs1] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0
    else:
        print("Warning: Attempt to write to x0 ignored.")

def sll(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = registers[rs1] << (registers[rs2] & 0x1F)
    else:
        print("Warning: Attempt to write to x0 ignored.")

def srl(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = (registers[rs1] & 0xFFFFFFFF) >> (registers[rs2] & 0x1F)
    else:
        print("Warning: Attempt to write to x0 ignored.")

def sra(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = registers[rs1] >> (registers[rs2] & 0x1F)
    else:
        print("Warning: Attempt to write to x0 ignored.")

def slli(rd, rs1, imm):
    """Shift Left Logical Immediate."""
    if rd != 0:
        registers[rd] = registers[rs1] << (imm & 0x1F)
    else:
        print("Warning: Attempt to write to x0 ignored.")

def srli(rd, rs1, imm):
    """Shift Right Logical Immediate (zero-fill)."""
    if rd != 0:
        registers[rd] = (registers[rs1] & 0xFFFFFFFF) >> (imm & 0x1F)
    else:
        print("Warning: Attempt to write to x0 ignored.")

def srai(rd, rs1, imm):
    """Shift Right Arithmetic Immediate (sign-extend)."""
    if rd != 0:
        registers[rd] = registers[rs1] >> (imm & 0x1F)
    else:
        print("Warning: Attempt to write to x0 ignored.")

def sltu(rd, rs1, rs2):
    """Set Less Than Unsigned."""
    if rd != 0:
        registers[rd] = 1 if (registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF) else 0
    else:
        print("Warning: Attempt to write to x0 ignored.")

def xor(rd, rs1, rs2):
    """Bitwise XOR."""
    if rd != 0:
        registers[rd] = registers[rs1] ^ registers[rs2]
    else:
        print("Warning: Attempt to write to x0 ignored.")

def or_(rd, rs1, rs2):
    """Bitwise OR."""
    if rd != 0:
        registers[rd] = registers[rs1] | registers[rs2]
    else:
        print("Warning: Attempt to write to x0 ignored.")

def and_(rd, rs1, rs2):
    """Bitwise AND."""
    if rd != 0:
        registers[rd] = registers[rs1] & registers[rs2]
    else:
        print("Warning: Attempt to write to x0 ignored.")

# Branch Instructions with Labels
def beq(rs1, rs2, target_label):
    """Branch if Equal."""
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BEQ instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] == registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BEQ: Branch taken to label '{target_label}'")
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
        return True
    else:
        print(f"BEQ: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bne(rs1, rs2, target_label):
    """Branch if Not Equal."""
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BNE instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] != registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BNE: Branch taken to label '{target_label}'")
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
        return True
    else:
        print(f"BNE: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def blt(rs1, rs2, target_label):
    """Branch if Less Than."""
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BLT instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] < registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BLT: Branch taken to label '{target_label}'")
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
        return True
    else:
        print(f"BLT: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bge(rs1, rs2, target_label):
    """Branch if Greater Than or Equal."""
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BGE instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] >= registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BGE: Branch taken to label '{target_label}'")
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
        return True
    else:
        print(f"BGE: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bltu(rs1, rs2, target_label):
    """Branch if Less Than Unsigned."""
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BLTU instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if (registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF):
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BLTU: Branch taken to label '{target_label}'")
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
        return True
    else:
        print(f"BLTU: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bgeu(rs1, rs2, target_label):
    """Branch if Greater Than or Equal Unsigned."""
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BGEU instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if (registers[rs1] & 0xFFFFFFFF) >= (registers[rs2] & 0xFFFFFFFF):
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BGEU: Branch taken to label '{target_label}'")
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
        return True
    else:
        print(f"BGEU: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

# Memory Instructions
def lw(rd, offset, rs1):
    """Load Word."""
    if rd == 0:
        print("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        print(f"Error: LW instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_word(address)
    print(f"LW: Loaded word {registers[rd]} from address {address} into x{rd}")

def lb(rd, offset, rs1):
    """Load Byte."""
    if rd == 0:
        print("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        print(f"Error: LB instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    byte = load_byte(address)
    if byte & 0x80:
        byte |= 0xFFFFFF00  # Sign-extend to 32 bits
    registers[rd] = byte
    print(f"LB: Loaded byte {registers[rd]} from address {address} into x{rd}")

def lbu(rd, offset, rs1):
    """Load Byte Unsigned."""
    if rd == 0:
        print("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        print(f"Error: LBU instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_byte(address)
    print(f"LBU: Loaded unsigned byte {registers[rd]} from address {address} into x{rd}")

def lh(rd, offset, rs1):
    """Load Halfword."""
    if rd == 0:
        print("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        print(f"Error: LH instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_halfword(address)
    print(f"LH: Loaded halfword {registers[rd]} from address {address} into x{rd}")

def lhu(rd, offset, rs1):
    """Load Halfword Unsigned."""
    if rd == 0:
        print("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        print(f"Error: LHU instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_halfword_unsigned(address)
    print(f"LHU: Loaded unsigned halfword {registers[rd]} from address {address} into x{rd}")

def sw(rs2, offset, rs1):
    """Store Word."""
    if rs1 is None or rs2 is None or offset is None:
        print(f"Error: SW instruction missing operands rs2={rs2}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    value_to_store = registers[rs2]
    store_word(address, value_to_store)
    print(f"SW: Stored value {value_to_store} from x{rs2} to memory address {address}")

def sb(rs2, offset, rs1):
    """Store Byte."""
    if rs1 is None or rs2 is None or offset is None:
        print(f"Error: SB instruction missing operands rs2={rs2}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    value_to_store = registers[rs2] & 0xFF
    store_byte(address, value_to_store)
    print(f"SB: Stored byte {value_to_store} from x{rs2} to memory address {address}")

def sh(rs2, offset, rs1):
    """Store Halfword."""
    if rs1 is None or rs2 is None or offset is None:
        print(f"Error: SH instruction missing operands rs2={rs2}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    value_to_store = registers[rs2] & 0xFFFF
    store_halfword(address, value_to_store)
    print(f"SH: Stored halfword {value_to_store} from x{rs2} to memory address {address}")

# Jump and Link Instructions
def jal(rd, target_label):
    """Jump and Link."""
    global program_counter
    if rd is None or target_label is None:
        print(f"Error: JAL instruction missing operands rd={rd}, label={target_label}")
        return

    if rd != 0:
        registers[rd] = program_counter + 1

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
    """Jump and Link Register."""
    global program_counter
    if rd != 0:
        registers[rd] = program_counter + 1
    target_address = (registers[rs1] + offset) & 0xFFFFFFFE  # Ensure least significant bit is zero
    program_counter = target_address
    print(f"JALR: Jumped to address {target_address}, return address stored in x{rd}")

# Immediate Instructions
def lui(rd, imm):
    if rd != 0:
        registers[rd] = imm << 12
    else:
        print("Warning: Attempt to write to x0 ignored.")

def auipc(rd, imm):
    if rd != 0:
        registers[rd] = program_counter + (imm << 12)
    else:
        print("Warning: Attempt to write to x0 ignored.")

# System Instructions
def ecall():
    print("ECALL - Halting")
    sys.exit(0)

def ebreak():
    print("EBREAK - Halting")
    sys.exit(0)

def fence():
    print("FENCE - Operation not implemented.")

def fence_tso():
    print("FENCE.TSO - Operation not implemented.")

def pause():
    print("PAUSE - Operation not implemented.")

# Utility Functions
def read_instructions_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def parse_register(reg):
    """Helper function to parse register names like x0, x1, etc."""
    reg = reg.strip()
    if reg.lower().startswith('x') and reg[1:].isdigit():
        reg_num = int(reg[1:])
        if 0 <= reg_num < 32:
            return reg_num
    print(f"Error: Invalid register {reg}")
    return None

def parse_immediate(value):
    """Helper function to parse immediate values."""
    try:
        return int(value, 0)
    except ValueError:
        print(f"Error: Invalid immediate value '{value}'")
        return None

def instruction_splitting(line):
    """Split an instruction line into its components."""
    line = line.strip()
    if '#' in line:
        line = line.split('#')[0].strip()

    if not line:
        return None, None, None, None, None, None

    parts = line.replace(',', ' ').split()
    opcode = parts[0].upper()

    # Handling S-type and I-type instructions with offset notation
    if opcode in ['SW', 'SB', 'SH', 'LW', 'LH', 'LHU', 'LB', 'LBU']:
        if len(parts) != 3:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        reg1 = parse_register(parts[1])
        try:
            offset_str, base_register = parts[2].split('(')
            offset = parse_immediate(offset_str)
            reg2 = parse_register(base_register[:-1])
        except ValueError:
            print(f"Error: Invalid offset notation. line='{line}'")
            return None, None, None, None, None, None
        if opcode in ['SW', 'SB', 'SH']:
            return opcode, None, reg2, reg1, offset, None  # rs2, offset, rs1
        else:
            return opcode, reg1, reg2, None, offset, None  # rd, rs1, offset

    # I-type instructions
    elif opcode in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU', 'JALR']:
        if len(parts) != 4:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = parse_register(parts[1])
        rs1 = parse_register(parts[2])
        imm = parse_immediate(parts[3])
        return opcode, rd, rs1, None, imm, None

    # R-type instructions
    elif opcode in ['ADD', 'SUB', 'SLT', 'SLTU', 'XOR', 'OR', 'AND', 'SLL', 'SRL', 'SRA']:
        if len(parts) != 4:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = parse_register(parts[1])
        rs1 = parse_register(parts[2])
        rs2 = parse_register(parts[3])
        return opcode, rd, rs1, rs2, None, None

    # B-type instructions
    elif opcode in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
        if len(parts) != 4:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rs1 = parse_register(parts[1])
        rs2 = parse_register(parts[2])
        label = parts[3]
        return opcode, None, rs1, rs2, label, None

    # U-type instructions
    elif opcode in ['LUI', 'AUIPC']:
        if len(parts) != 3:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = parse_register(parts[1])
        imm = parse_immediate(parts[2])
        return opcode, rd, None, None, imm, None

    # J-type instructions
    elif opcode == 'JAL':
        if len(parts) != 3:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = parse_register(parts[1])
        label = parts[2]
        return opcode, rd, None, None, label, None

    # System instructions
    elif opcode in ['ECALL', 'EBREAK', 'FENCE', 'FENCE.TSO', 'PAUSE']:
        return opcode, None, None, None, None, None

    print(f"Error: Unrecognized instruction format. line='{line}'")
    return None, None, None, None, None, None

def printRegisters(instruction=None):
    """Prints the state of the program."""
    global program_counter

    if instruction:
        print(f"\n=== Executing Instruction ===\nInstruction: {instruction}\n")

    # Adjust the program counter for display purposes
    current_pc = program_counter
    if instruction:
        current_pc -= 1

    print(f"{'='*60}")
    print(f"Program Counter (PC): {current_pc}")
    print(f"{'='*60}\n")

    # Print Registers
    print(f"{'='*24} Registers {'='*24}\n")
    headers = ['Register', 'Decimal', 'Hexadecimal', 'Binary']
    print(f"{headers[0]:<10} {headers[1]:>12} {headers[2]:>15} {headers[3]:>35}")
    print('-' * 80)
    for i in range(32):
        reg_name = f"x{i}"
        decimal_value = registers[i]
        hex_value = f"0x{registers[i]:08X}"
        bin_value = f"0b{registers[i]:032b}"
        print(f"{reg_name:<10} {decimal_value:>12} {hex_value:>15} {bin_value:>35}")
    print('\n')

    # Print Memory Contents
    print(f"{'='*22} Memory Contents {'='*22}\n")
    if memory:
        headers = ['Address (Hex)', 'Address (Dec)', 'Decimal', 'Hexadecimal', 'Binary']
        print(f"{headers[0]:<15} {headers[1]:>15} {headers[2]:>12} {headers[3]:>15} {headers[4]:>35}")
        print('-' * 100)
        for address in sorted(memory.keys()):
            value = memory[address]
            decimal_value = value
            hex_value = f"0x{value:02X}"
            bin_value = f"0b{value:08b}"
            print(f"0x{address:08X} {address:>15} {decimal_value:>12} {hex_value:>15} {bin_value:>35}")
    else:
        print("Memory is empty.\n")

    # Print Labels Dictionary if available
    if labels:
        print(f"{'='*25} Labels {'='*25}\n")
        for label, addr in labels.items():
            print(f"Label '{label}': Address {addr}")
    else:
        print("\nNo labels found.\n")

# User Input Function
def user_input():
    global program_counter
    file_path = input("Enter the instruction file path: ").strip()
    while True:
        try:
            program_counter = int(input("Enter the starting address of the program: ").strip())
            break
        except ValueError:
            print("Invalid input. Please enter an integer for the starting address.")

    # Prompt for optional memory file
    memory_file = input("Enter the memory initialization file path (leave empty if none): ").strip()
    if memory_file:
        load_memory_from_file(memory_file)
    return file_path

# Function to load memory from a file
def load_memory_from_file(memory_file):
    global memory
    try:
        with open(memory_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    address_str, value_str = line.split(',')
                    address = int(address_str.strip(), 0)
                    value = value_str.strip()
                    if value.startswith('"') and value.endswith('"'):
                        # Handle string values
                        string_value = value[1:-1]
                        for i, char in enumerate(string_value):
                            store_byte(address + i, ord(char))
                    elif value.startswith("'") and value.endswith("'"):
                        # Handle character values
                        store_byte(address, ord(value[1]))
                    else:
                        # Handle numeric values
                        store_word(address, int(value, 0))
    except FileNotFoundError:
        print(f"Error: Memory file '{memory_file}' not found.")
        sys.exit(1)

# Main Function
def main():
    global program_counter
    global labels

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

    # Step 3: Execute instructions
    instruction_count = len(instruction_lines)
    while program_counter < instruction_count:
        line = instruction_lines[program_counter].strip()
        original_line = line  # Keep the original line for printing

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

        # Execute the instruction based on its type
        if opcode in instructions:
            if opcode in ['BEQ', 'BNE', 'BGE', 'BLT', 'BLTU', 'BGEU']:
                branch_taken = instructions[opcode](rs1, rs2, imm_or_label)
                if branch_taken:
                    continue  # Branch taken; program_counter updated within the branch function
                else:
                    program_counter += 1  # Branch not taken; proceed to next instruction
            elif opcode in ['JAL']:
                instructions[opcode](rd, imm_or_label)
                # Do not increment program_counter; it's updated within the instruction
            elif opcode in ['JALR']:
                instructions[opcode](rd, rs1, imm_or_label)
                # Do not increment program_counter; it's updated within the instruction
            elif opcode in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU']:
                instructions[opcode](rd, rs1, imm_or_label)
                program_counter += 1
            elif opcode in ['LW', 'LB', 'LBU', 'LH', 'LHU']:
                instructions[opcode](rd, imm_or_label, rs1)
                program_counter += 1
            elif opcode in ['SW', 'SB', 'SH']:
                instructions[opcode](rs2, imm_or_label, rs1)
                program_counter += 1
            elif opcode in ['LUI', 'AUIPC']:
                instructions[opcode](rd, imm_or_label)
                program_counter += 1
            elif opcode in ['ECALL', 'EBREAK', 'FENCE', 'FENCE.TSO', 'PAUSE']:
                instructions[opcode]()
                program_counter += 1
            else:
                instructions[opcode](rd, rs1, rs2)
                program_counter += 1
        else:
            print(f"Error: Unknown opcode '{opcode}'")
            program_counter += 1
            continue

        # Ensure x0 remains zero
        registers[0] = 0

        # Print the current state of registers after execution
        printRegisters(instruction=original_line)

# Dictionary of instructions
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
