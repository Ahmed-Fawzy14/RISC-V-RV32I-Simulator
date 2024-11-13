import sys

# Global Variables
registers = [0] * 32
program_counter = 0
memory = {}
labels = {}
executable_instructions = []

# Memory Handling Helper Functions
def store_byte(address, value):
    memory[address] = value & 0xFF

def store_halfword(address, value):
    store_byte(address, value & 0xFF)
    store_byte(address + 1, (value >> 8) & 0xFF)

def store_word(address, value):
    store_byte(address, value & 0xFF)
    store_byte(address + 1, (value >> 8) & 0xFF)
    store_byte(address + 2, (value >> 16) & 0xFF)
    store_byte(address + 3, (value >> 24) & 0xFF)

def load_byte(address):
    if address not in memory:
        print(f"Warning: Loading from uninitialized memory address {address}. Returning 0.")
    return memory.get(address, 0)

def load_halfword(address):
    byte1 = load_byte(address)
    byte2 = load_byte(address + 1)
    value = (byte2 << 8) | byte1
    if value & 0x8000:
        value |= 0xFFFF0000  # Sign-extend to 32 bits
    return value

def load_halfword_unsigned(address):
    byte1 = load_byte(address)
    byte2 = load_byte(address + 1)
    return (byte2 << 8) | byte1

def load_word(address):
    byte1 = load_byte(address)
    byte2 = load_byte(address + 1)
    byte3 = load_byte(address + 2)
    byte4 = load_byte(address + 3)
    return (byte4 << 24) | (byte3 << 16) | (byte2 << 8) | byte1

# Arithmetic and Logical Instructions
def add(rd, rs1, rs2):
    if rd != 0:
        result = (registers[rs1] + registers[rs2]) & 0xFFFFFFFF
        registers[rd] = result
        print(f"ADD: x{rd} = x{rs1} + x{rs2} -> {registers[rd]}")

def sub(rd, rs1, rs2):
    if rd != 0:
        result = (registers[rs1] - registers[rs2]) & 0xFFFFFFFF
        registers[rd] = result
        print(f"SUB: x{rd} = x{rs1} - x{rs2} -> {registers[rd]}")

def addi(rd, rs1, imm):
    if rd != 0:
        result = (registers[rs1] + imm) & 0xFFFFFFFF
        registers[rd] = result
        print(f"ADDI: x{rd} = x{rs1} + {imm} -> {registers[rd]}")

def andi(rd, rs1, imm):
    if rd != 0:
        result = registers[rs1] & imm
        registers[rd] = result
        print(f"ANDI: x{rd} = x{rs1} & {imm} -> {registers[rd]}")

def ori(rd, rs1, imm):
    if rd != 0:
        result = registers[rs1] | imm
        registers[rd] = result
        print(f"ORI: x{rd} = x{rs1} | {imm} -> {registers[rd]}")

def xori(rd, rs1, imm):
    if rd != 0:
        result = registers[rs1] ^ imm
        registers[rd] = result
        print(f"XORI: x{rd} = x{rs1} ^ {imm} -> {registers[rd]}")

def slt(rd, rs1, rs2):
    if rd != 0:
        result = 1 if registers[rs1] < registers[rs2] else 0
        registers[rd] = result
        print(f"SLT: x{rd} = (x{rs1} < x{rs2}) -> {registers[rd]}")

def slti(rd, rs1, imm):
    if rd != 0:
        result = 1 if registers[rs1] < imm else 0
        registers[rd] = result
        print(f"SLTI: x{rd} = (x{rs1} < {imm}) -> {registers[rd]}")

def sltiu(rd, rs1, imm):
    if rd != 0:
        result = 1 if (registers[rs1] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0
        registers[rd] = result
        print(f"SLTIU: x{rd} = (x{rs1} < {imm} unsigned) -> {registers[rd]}")

def sll(rd, rs1, rs2):
    if rd != 0:
        shift_amount = registers[rs2] & 0x1F
        result = (registers[rs1] << shift_amount) & 0xFFFFFFFF
        registers[rd] = result
        print(f"SLL: x{rd} = x{rs1} << ({shift_amount}) -> {registers[rd]}")

def srl(rd, rs1, rs2):
    if rd != 0:
        shift_amount = registers[rs2] & 0x1F
        result = (registers[rs1] & 0xFFFFFFFF) >> shift_amount
        registers[rd] = result
        print(f"SRL: x{rd} = x{rs1} >> ({shift_amount}) -> {registers[rd]}")

def sra(rd, rs1, rs2):
    if rd != 0:
        shift_amount = registers[rs2] & 0x1F
        value = registers[rs1]
        if value & 0x80000000:
            # Arithmetic shift for negative numbers
            result = (value >> shift_amount) | (0xFFFFFFFF << (32 - shift_amount))
        else:
            result = value >> shift_amount
        result &= 0xFFFFFFFF  # Ensure 32-bit
        registers[rd] = result
        print(f"SRA: x{rd} = x{rs1} >>> ({shift_amount}) -> {registers[rd]}")

def slli(rd, rs1, imm):
    if rd != 0:
        shift_amount = imm & 0x1F
        result = (registers[rs1] << shift_amount) & 0xFFFFFFFF
        registers[rd] = result
        print(f"SLLI: x{rd} = x{rs1} << {shift_amount} -> {registers[rd]}")

def srli(rd, rs1, imm):
    if rd != 0:
        shift_amount = imm & 0x1F
        result = (registers[rs1] & 0xFFFFFFFF) >> shift_amount
        registers[rd] = result
        print(f"SRLI: x{rd} = x{rs1} >> {shift_amount} -> {registers[rd]}")

def srai(rd, rs1, imm):
    if rd != 0:
        shift_amount = imm & 0x1F
        value = registers[rs1]
        if value & 0x80000000:
            # Arithmetic shift for negative numbers
            result = (value >> shift_amount) | (0xFFFFFFFF << (32 - shift_amount))
        else:
            result = value >> shift_amount
        result &= 0xFFFFFFFF  # Ensure 32-bit
        registers[rd] = result
        print(f"SRAI: x{rd} = x{rs1} >>> {shift_amount} -> {registers[rd]}")

def sltu(rd, rs1, rs2):
    if rd != 0:
        result = 1 if (registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF) else 0
        registers[rd] = result
        print(f"SLTU: x{rd} = (x{rs1} < x{rs2} unsigned) -> {registers[rd]}")

def xor(rd, rs1, rs2):
    if rd != 0:
        result = registers[rs1] ^ registers[rs2]
        registers[rd] = result
        print(f"XOR: x{rd} = x{rs1} ^ x{rs2} -> {registers[rd]}")

def or_(rd, rs1, rs2):
    if rd != 0:
        result = registers[rs1] | registers[rs2]
        registers[rd] = result
        print(f"OR: x{rd} = x{rs1} | x{rs2} -> {registers[rd]}")

def and_(rd, rs1, rs2):
    if rd != 0:
        result = registers[rs1] & registers[rs2]
        registers[rd] = result
        print(f"AND: x{rd} = x{rs1} & x{rs2} -> {registers[rd]}")

# Branch Instructions 
def beq(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BEQ instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] == registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BEQ: Branch taken to label '{target_label}'")
            return True
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
    else:
        print(f"BEQ: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bne(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BNE instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] != registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BNE: Branch taken to label '{target_label}'")
            return True
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
    else:
        print(f"BNE: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def blt(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BLT instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] < registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BLT: Branch taken to label '{target_label}'")
            return True
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
    else:
        print(f"BLT: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bge(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BGE instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] >= registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BGE: Branch taken to label '{target_label}'")
            return True
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
    else:
        print(f"BGE: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bltu(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BLTU instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if (registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF):
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BLTU: Branch taken to label '{target_label}'")
            return True
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
    else:
        print(f"BLTU: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bgeu(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        print(f"Error: BGEU instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if (registers[rs1] & 0xFFFFFFFF) >= (registers[rs2] & 0xFFFFFFFF):
        if target_label in labels:
            program_counter = labels[target_label]
            print(f"BGEU: Branch taken to label '{target_label}'")
            return True
        else:
            print(f"Error: Label '{target_label}' not found.")
            return False
    else:
        print(f"BGEU: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

# Load and Store Instructions
def lw(rd, offset, rs1):
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
    if rs1 is None or rs2 is None or offset is None:
        print(f"Error: SW instruction missing operands rs2={rs2}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    value_to_store = registers[rs2]
    store_word(address, value_to_store)
    print(f"SW: Stored value {value_to_store} from x{rs2} to memory address {address}")

def sb(rs2, offset, rs1):
    if rs1 is None or rs2 is None or offset is None:
        print(f"Error: SB instruction missing operands rs2={rs2}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    value_to_store = registers[rs2] & 0xFF
    store_byte(address, value_to_store)
    print(f"SB: Stored byte {value_to_store} from x{rs2} to memory address {address}")

def sh(rs2, offset, rs1):
    if rs1 is None or rs2 is None or offset is None:
        print(f"Error: SH instruction missing operands rs2={rs2}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    value_to_store = registers[rs2] & 0xFFFF
    store_halfword(address, value_to_store)
    print(f"SH: Stored halfword {value_to_store} from x{rs2} to memory address {address}")

# Jump and Link Instructions
def jal(rd, target_label):
    global program_counter
    if rd != 0:
        registers[rd] = program_counter + 1  # Store return address
        print(f"JAL: Set x{rd} to {registers[rd]}")
    if target_label in labels:
        program_counter = labels[target_label]  # Jump to label
        print(f"JAL: Jumping to label '{target_label}' at instruction index {labels[target_label]}")
    else:
        raise ValueError(f"Label '{target_label}' not found.")

def jalr(rd, rs1, imm):
    global program_counter
    if rd != 0:
        registers[rd] = program_counter + 1  # Store return address
        print(f"JALR: Set x{rd} to {registers[rd]}")
    target_address = (registers[rs1] + imm) & 0xFFFFFFFF
    if 0 <= target_address < len(executable_instructions):
        program_counter = target_address  # Jump to target address
        print(f"JALR: Jumping to instruction index {target_address}")
    else:
        print(f"Error: Invalid jump address '{target_address}'.")
        sys.exit(1)

# Upper Immediate Instructions
def lui(rd, imm):
    if rd != 0:
        result = (imm << 12) & 0xFFFFFFFF
        registers[rd] = result
        print(f"LUI: Loaded immediate {imm} into x{rd} -> {registers[rd]}")
    else:
        print("Warning: Attempt to write to x0 ignored.")

def auipc(rd, imm):
    if rd != 0:
        # In a real CPU, AUIPC adds the upper immediate to the current PC in bytes.
        # Here, we'll treat PC as an index, so shift appropriately.
        result = (program_counter + (imm << 12)) & 0xFFFFFFFF
        registers[rd] = result
        print(f"AUIPC: Loaded immediate {imm} into x{rd} -> {registers[rd]}")
    else:
        print("Warning: Attempt to write to x0 ignored.")

# System Instructions which halt the program
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

def halt():
    print("HALT - Terminating execution.")
    sys.exit(0)

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
    'ECALL': ecall, 'EBREAK': ebreak, 'HALT': halt
}

# Utility Functions
def read_instructions_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def parse_register(reg):
    reg = reg.strip()
    if reg.lower().startswith('x') and reg[1:].isdigit():
        reg_num = int(reg[1:])
        if 0 <= reg_num < 32:
            return reg_num
    print(f"Error: Invalid register {reg}")
    return None

def parse_immediate(value):
    try:
        return int(value, 0)
    except ValueError:
        print(f"Error: Invalid immediate value '{value}'")
        return None

def instruction_splitting(line):
    line = line.strip()
    if '#' in line:
        line = line.split('#')[0].strip()

    if not line:
        return None, None, None, None, None, None

    parts = line.replace(',', ' ').split()
    opcode = parts[0].upper()

    # Handling Load and Store Instructions with Offset Notation
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


    # Handling JALR Instruction
    elif opcode == 'JALR':
        if len(parts) == 2:
            # Format: jalr rd
            rd = parse_register(parts[1])
            return opcode, rd, None, None, 0, None
        elif len(parts) == 3:
            # Format: jalr rd, rs1
            rd = parse_register(parts[1])
            rs1 = parse_register(parts[2])
            return opcode, rd, rs1, None, 0, None
        elif len(parts) == 4:
            # Format: jalr rd, rs1, imm
            rd = parse_register(parts[1])
            rs1 = parse_register(parts[2])
            imm = parse_immediate(parts[3])
            return opcode, rd, rs1, None, imm, None
        else:
            print(f"Error: JALR instruction missing operands. line='{line}'")
            return None, None, None, None, None, None

    # Immediate Arithmetic and Logical Instructions
    elif opcode in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU',
                    'SLLI', 'SRLI', 'SRAI']:
        if len(parts) != 4:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = parse_register(parts[1])
        rs1 = parse_register(parts[2])
        imm = parse_immediate(parts[3])
        return opcode, rd, rs1, None, imm, None

    # R-type instructions 
    elif opcode in ['ADD', 'SUB', 'SLT', 'SLTU', 'XOR', 'OR', 'AND',
                    'SLL', 'SRL', 'SRA']:
        if len(parts) != 4:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = parse_register(parts[1])
        rs1 = parse_register(parts[2])
        rs2 = parse_register(parts[3])
        return opcode, rd, rs1, rs2, None, None

    # Branch Instructions
    elif opcode in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
        if len(parts) != 4:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rs1 = parse_register(parts[1])
        rs2 = parse_register(parts[2])
        label = parts[3]
        return opcode, None, rs1, rs2, label, None

    # Upper Immediate Instructions
    elif opcode in ['LUI', 'AUIPC']:
        if len(parts) != 3:
            print(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = parse_register(parts[1])
        imm = parse_immediate(parts[2])
        return opcode, rd, None, None, imm, None

    # Jump Instructions
    elif opcode == 'JAL':
        if len(parts) == 2:
            # Format: jal label
            rd = 1  # Default return register x1
            label = parts[1]
            return opcode, rd, None, None, label, None
        elif len(parts) == 3:
            # Format: jal rd, label
            rd = parse_register(parts[1])
            label = parts[2]
            return opcode, rd, None, None, label, None
        else:
            print(f"Error: JAL instruction missing operands. line='{line}'")
            return None, None, None, None, None, None

    # System instructions (ECALL, EBREAK, FENCE, FENCE.TSO, PAUSE, HALT)
    elif opcode in ['ECALL', 'EBREAK', 'FENCE', 'FENCE.TSO', 'PAUSE', 'HALT']:
        return opcode, None, None, None, None, None

    else:
        print(f"Error: Unrecognized instruction format. line='{line}'")
        return None, None, None, None, None, None

def printRegisters(instruction=None):
    global program_counter

    if instruction:
        print(f"\n=== Executing Instruction ===\nInstruction: {instruction}\n")

    display_pc = program_counter

    print(f"{'='*60}")
    print(f"Program Counter (PC): {display_pc}")
    print(f"{'='*60}\n")

    # Print Registers
    print(f"{'='*24} Registers {'='*24}\n")
    headers = ['Register', 'Decimal', 'Hexadecimal', 'Binary']
    print(f"{headers[0]:<10} {headers[1]:>12} {headers[2]:>15} {headers[3]:>35}")
    print('-' * 80)
    for i in range(32):
        reg_name = f"x{i}"
        # Convert to signed decimal
        if registers[i] & 0x80000000:
            decimal_value = registers[i] - 0x100000000
        else:
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
            # Convert to signed decimal for bytes
            if value & 0x80:
                decimal_value = value - 0x100
            else:
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
            print(f"Label '{label}': Instruction Index {addr}")
    else:
        print("\nNo labels found.\n")

def user_input():
    file_path = input("Enter the instruction file path: ").strip()
    while True:
        try:
            program_counter_initial = int(input("Enter the starting address of the program (e.g., 0): ").strip())
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer for the starting address.")

    # Prompt for optional memory file
    memory_file = input("Enter the memory initialization file path (leave empty if none): ").strip()
    if memory_file:
        load_memory_from_file(memory_file)
    return file_path, program_counter_initial

# Function to load memory from a file (initialize memory)
def load_memory_from_file(memory_file):
    global memory
    try:
        with open(memory_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) != 2:
                        print(f"Error: Invalid memory initialization line: '{line}'")
                        continue
                    address_str, value_str = parts
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
    except ValueError as ve:
        print(f"Error processing memory file: {ve}")
        sys.exit(1)

def main():
    global program_counter
    global labels
    global executable_instructions

    # Step 1: Read the instruction file and initialize PC
    file_path, starting_pc = user_input()
    instruction_lines = read_instructions_from_file(file_path)

    # Step 2: First pass to register labels and prepare executable instructions
    labels = {}
    executable_instructions = []
    
    for line_number, line in enumerate(instruction_lines):
        stripped_line = line.strip()
        
        # Remove comments
        if '#' in stripped_line:
            stripped_line = stripped_line.split('#')[0].strip()
        
        # Skip empty lines
        if not stripped_line:
            continue

        # Check for labels
        if stripped_line.endswith(':'):
            label_name = stripped_line[:-1].strip()
            # Map label to the next instruction's index
            labels[label_name] = len(executable_instructions)
        else:
            # Append the executable instruction
            executable_instructions.append(stripped_line)

    # Debug: Print label mappings
    print(f"\nLabel Mappings: {labels}\n")

    # Step 3: Execute instructions
    instruction_count = len(executable_instructions)
    program_counter = starting_pc  # Initialize PC to user-specified starting address
    running = True  # Flag to control the execution loop

    while running and 0 <= program_counter < instruction_count:
        # Fetch the current instruction
        line = executable_instructions[program_counter].strip()
        original_line = line  # Preserve the original line for debugging

        # Print the current instruction and PC before execution
        printRegisters(instruction=original_line)

        # Parse the instruction
        opcode, rd, rs1, rs2, imm_or_label, offset = instruction_splitting(line)
        if not opcode:
            # If parsing failed, skip to the next instruction
            program_counter += 1
            continue

        # Execute the instruction based on its opcode
        if opcode in instructions:
            # Branch Instructions
            if opcode in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
                branch_taken = instructions[opcode](rs1, rs2, imm_or_label)
                if not branch_taken:
                    program_counter += 1
            # Jump Instructions
            elif opcode == 'JAL':
                instructions[opcode](rd, imm_or_label)
            elif opcode == 'JALR':
                instructions[opcode](rd, rs1, imm_or_label)
            # Immediate Arithmetic and Shift Instructions
            elif opcode in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU',
                            'SLLI', 'SRLI', 'SRAI']:
                instructions[opcode](rd, rs1, imm_or_label)
                program_counter += 1
            # Register-Register Arithmetic and Logical Instructions
            elif opcode in ['ADD', 'SUB', 'SLT', 'SLTU', 'XOR', 'OR', 'AND',
                            'SLL', 'SRL', 'SRA']:
                instructions[opcode](rd, rs1, rs2)
                program_counter += 1
            # Load Instructions
            elif opcode in ['LW', 'LH', 'LHU', 'LB', 'LBU']:
                instructions[opcode](rd, imm_or_label, rs1)
                program_counter += 1
            # Store Instructions
            elif opcode in ['SW', 'SH', 'SB']:
                instructions[opcode](rs2, imm_or_label, rs1)
                program_counter += 1
            # Upper Immediate Instructions
            elif opcode in ['LUI', 'AUIPC']:
                instructions[opcode](rd, imm_or_label)
                program_counter += 1
            # System Instructions
            elif opcode in ['ECALL', 'EBREAK', 'FENCE', 'FENCE.TSO', 'PAUSE', 'HALT']:
                instructions[opcode]()
                if opcode == 'HALT':
                    running = False
                program_counter += 1
            else:
                print(f"Error: Unhandled opcode '{opcode}'")
                program_counter += 1
        else:
            print(f"Error: Unknown opcode '{opcode}'")
            program_counter += 1

        # Ensure x0 remains zero
        registers[0] = 0

    print("Program execution completed.")

if __name__ == "__main__":
    main()
