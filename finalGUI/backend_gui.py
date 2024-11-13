import sys

# Global Variables
registers = [0] * 32
program_counter = 0
memory = {}
labels = {}
executable_instructions = []

def to_signed32(val):
    #Convert 32-bit unsigned integer to signed integer
    if val & 0x80000000:
        return val - 0x100000000
    else:
        return val

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
        output_to_gui_global(f"Warning: Loading from uninitialized memory address {address}. Returning 0.")
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
        output_to_gui_global(f"ADD: x{rd} = x{rs1} + x{rs2} -> {registers[rd]}")

def sub(rd, rs1, rs2):
    if rd != 0:
        result = (registers[rs1] - registers[rs2]) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"SUB: x{rd} = x{rs1} - x{rs2} -> {registers[rd]}")

def addi(rd, rs1, imm):
    if rd != 0:
        result = (registers[rs1] + imm) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"ADDI: x{rd} = x{rs1} + {imm} -> {registers[rd]}")

def andi(rd, rs1, imm):
    if rd != 0:
        result = (registers[rs1] & imm) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"ANDI: x{rd} = x{rs1} & {imm} -> {registers[rd]}")

def ori(rd, rs1, imm):
    if rd != 0:
        result = (registers[rs1] | imm) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"ORI: x{rd} = x{rs1} | {imm} -> {registers[rd]}")

def xori(rd, rs1, imm):
    if rd != 0:
        result = (registers[rs1] ^ imm) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"XORI: x{rd} = x{rs1} ^ {imm} -> {registers[rd]}")

def slt(rd, rs1, rs2):
    if rd != 0:
        rs1_val = to_signed32(registers[rs1])
        rs2_val = to_signed32(registers[rs2])
        result = 1 if rs1_val < rs2_val else 0
        registers[rd] = result
        output_to_gui_global(f"SLT: x{rd} = ({rs1_val} < {rs2_val}) -> {result}")

def slti(rd, rs1, imm):
    if rd != 0:
        rs1_val = to_signed32(registers[rs1])
        result = 1 if rs1_val < imm else 0
        registers[rd] = result
        output_to_gui_global(f"SLTI: x{rd} = ({rs1_val} < {imm}) -> {result}")

def sltiu(rd, rs1, imm):
    if rd != 0:
        rs1_val = registers[rs1] & 0xFFFFFFFF
        imm_val = imm & 0xFFFFFFFF
        result = 1 if rs1_val < imm_val else 0
        registers[rd] = result
        output_to_gui_global(f"SLTIU: x{rd} = ({rs1_val} < {imm} unsigned) -> {result}")

def sll(rd, rs1, rs2):
    if rd != 0:
        shift_amount = registers[rs2] & 0x1F
        result = (registers[rs1] << shift_amount) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"SLL: x{rd} = x{rs1} << {shift_amount} -> {registers[rd]}")

def srl(rd, rs1, rs2):
    if rd != 0:
        shift_amount = registers[rs2] & 0x1F
        result = (registers[rs1] & 0xFFFFFFFF) >> shift_amount
        registers[rd] = result
        output_to_gui_global(f"SRL: x{rd} = x{rs1} >> {shift_amount} -> {registers[rd]}")

def sra(rd, rs1, rs2):
    if rd != 0:
        shift_amount = registers[rs2] & 0x1F
        value = to_signed32(registers[rs1])
        result = value >> shift_amount
        registers[rd] = result & 0xFFFFFFFF
        output_to_gui_global(f"SRA: x{rd} = x{rs1} >>> {shift_amount} -> {registers[rd]}")

def slli(rd, rs1, imm):
    if rd != 0:
        shift_amount = imm & 0x1F
        result = (registers[rs1] << shift_amount) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"SLLI: x{rd} = x{rs1} << {shift_amount} -> {registers[rd]}")

def srli(rd, rs1, imm):
    if rd != 0:
        shift_amount = imm & 0x1F
        result = (registers[rs1] & 0xFFFFFFFF) >> shift_amount
        registers[rd] = result
        output_to_gui_global(f"SRLI: x{rd} = x{rs1} >> {shift_amount} -> {registers[rd]}")

def srai(rd, rs1, imm):
    if rd != 0:
        shift_amount = imm & 0x1F
        value = to_signed32(registers[rs1])
        result = value >> shift_amount
        registers[rd] = result & 0xFFFFFFFF
        output_to_gui_global(f"SRAI: x{rd} = x{rs1} >>> {shift_amount} -> {registers[rd]}")

def sltu(rd, rs1, rs2):
    if rd != 0:
        rs1_val = registers[rs1] & 0xFFFFFFFF
        rs2_val = registers[rs2] & 0xFFFFFFFF
        result = 1 if rs1_val < rs2_val else 0
        registers[rd] = result
        output_to_gui_global(f"SLTU: x{rd} = ({rs1_val} < {rs2_val} unsigned) -> {result}")

def xor(rd, rs1, rs2):
    if rd != 0:
        result = (registers[rs1] ^ registers[rs2]) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"XOR: x{rd} = x{rs1} ^ x{rs2} -> {registers[rd]}")

def or_(rd, rs1, rs2):
    if rd != 0:
        result = (registers[rs1] | registers[rs2]) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"OR: x{rd} = x{rs1} | x{rs2} -> {registers[rd]}")

def and_(rd, rs1, rs2):
    if rd != 0:
        result = (registers[rs1] & registers[rs2]) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"AND: x{rd} = x{rs1} & x{rs2} -> {registers[rd]}")

# Branch Instructions 
def beq(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        output_to_gui_global(f"Error: BEQ instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] == registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            output_to_gui_global(f"BEQ: Branch taken to label '{target_label}'")
            return True
        else:
            output_to_gui_global(f"Error: Label '{target_label}' not found.")
            return False
    else:
        output_to_gui_global(f"BEQ: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bne(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        output_to_gui_global(f"Error: BNE instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] != registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            output_to_gui_global(f"BNE: Branch taken to label '{target_label}'")
            return True
        else:
            output_to_gui_global(f"Error: Label '{target_label}' not found.")
            return False
    else:
        output_to_gui_global(f"BNE: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def blt(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        output_to_gui_global(f"Error: BLT instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] < registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            output_to_gui_global(f"BLT: Branch taken to label '{target_label}'")
            return True
        else:
            output_to_gui_global(f"Error: Label '{target_label}' not found.")
            return False
    else:
        output_to_gui_global(f"BLT: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bge(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        output_to_gui_global(f"Error: BGE instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if registers[rs1] >= registers[rs2]:
        if target_label in labels:
            program_counter = labels[target_label]
            output_to_gui_global(f"BGE: Branch taken to label '{target_label}'")
            return True
        else:
            output_to_gui_global(f"Error: Label '{target_label}' not found.")
            return False
    else:
        output_to_gui_global(f"BGE: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bltu(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        output_to_gui_global(f"Error: BLTU instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if (registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF):
        if target_label in labels:
            program_counter = labels[target_label]
            output_to_gui_global(f"BLTU: Branch taken to label '{target_label}'")
            return True
        else:
            output_to_gui_global(f"Error: Label '{target_label}' not found.")
            return False
    else:
        output_to_gui_global(f"BLTU: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

def bgeu(rs1, rs2, target_label):
    global program_counter
    if rs1 is None or rs2 is None:
        output_to_gui_global(f"Error: BGEU instruction missing operands rs1={rs1}, rs2={rs2}")
        return False

    if (registers[rs1] & 0xFFFFFFFF) >= (registers[rs2] & 0xFFFFFFFF):
        if target_label in labels:
            program_counter = labels[target_label]
            output_to_gui_global(f"BGEU: Branch taken to label '{target_label}'")
            return True
        else:
            output_to_gui_global(f"Error: Label '{target_label}' not found.")
            return False
    else:
        output_to_gui_global(f"BGEU: Branch not taken, x{rs1}={registers[rs1]}, x{rs2}={registers[rs2]}")
    return False

# Load and Store Instructions
def lw(rd, offset, rs1):
    if rd == 0:
        output_to_gui_global("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        output_to_gui_global(f"Error: LW instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_word(address)
    output_to_gui_global(f"LW: Loaded word {registers[rd]} from address {address} into x{rd}")

def lb(rd, offset, rs1):
    if rd == 0:
        output_to_gui_global("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        output_to_gui_global(f"Error: LB instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    byte = load_byte(address)
    if byte & 0x80:
        byte |= 0xFFFFFF00  # Sign-extend to 32 bits
    registers[rd] = byte
    output_to_gui_global(f"LB: Loaded byte {registers[rd]} from address {address} into x{rd}")

def lbu(rd, offset, rs1):
    if rd == 0:
        output_to_gui_global("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        output_to_gui_global(f"Error: LBU instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_byte(address)
    output_to_gui_global(f"LBU: Loaded unsigned byte {registers[rd]} from address {address} into x{rd}")

def lh(rd, offset, rs1):
    if rd == 0:
        output_to_gui_global("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        output_to_gui_global(f"Error: LH instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_halfword(address)
    output_to_gui_global(f"LH: Loaded halfword {registers[rd]} from address {address} into x{rd}")

def lhu(rd, offset, rs1):
    if rd == 0:
        output_to_gui_global("Warning: Attempt to write to x0 ignored.")
        return
    if rd is None or rs1 is None or offset is None:
        output_to_gui_global(f"Error: LHU instruction missing operands rd={rd}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    registers[rd] = load_halfword_unsigned(address)
    output_to_gui_global(f"LHU: Loaded unsigned halfword {registers[rd]} from address {address} into x{rd}")

def sw(rs2, offset, rs1):
    if rs1 is None or rs2 is None or offset is None:
        output_to_gui_global(f"Error: SW instruction missing operands rs2={rs2}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    value_to_store = registers[rs2]
    store_word(address, value_to_store)
    output_to_gui_global(f"SW: Stored value {value_to_store} from x{rs2} to memory address {address}")

def sb(rs2, offset, rs1):
    if rs1 is None or rs2 is None or offset is None:
        output_to_gui_global(f"Error: SB instruction missing operands rs2={rs2}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    value_to_store = registers[rs2] & 0xFF
    store_byte(address, value_to_store)
    output_to_gui_global(f"SB: Stored byte {value_to_store} from x{rs2} to memory address {address}")

def sh(rs2, offset, rs1):
    if rs1 is None or rs2 is None or offset is None:
        output_to_gui_global(f"Error: SH instruction missing operands rs2={rs2}, rs1={rs1}, offset={offset}")
        return

    address = registers[rs1] + offset
    value_to_store = registers[rs2] & 0xFFFF
    store_halfword(address, value_to_store)
    output_to_gui_global(f"SH: Stored halfword {value_to_store} from x{rs2} to memory address {address}")

# Jump and Link Instructions
def jal(rd, target_label):
    global program_counter
    if rd != 0:
        registers[rd] = program_counter + 1  # Store return address
        output_to_gui_global(f"JAL: Set x{rd} to {registers[rd]}")
    if target_label in labels:
        program_counter = labels[target_label]  # Jump to label
        output_to_gui_global(f"JAL: Jumping to label '{target_label}' at instruction index {labels[target_label]}")
    else:
        raise ValueError(f"Label '{target_label}' not found.")

def jalr(rd, rs1, imm):
    global program_counter
    if rd != 0:
        registers[rd] = program_counter + 1  # Store return address
        output_to_gui_global(f"JALR: Set x{rd} to {registers[rd]}")
    target_address = (registers[rs1] + imm) & 0xFFFFFFFF
    if 0 <= target_address < len(executable_instructions):
        program_counter = target_address  # Jump to target address
        output_to_gui_global(f"JALR: Jumping to instruction index {target_address}")
    else:
        output_to_gui_global(f"Error: Invalid jump address '{target_address}'.")
        sys.exit(1)

# Upper Immediate Instructions
def lui(rd, imm):
    if rd != 0:
        result = (imm << 12) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"LUI: Loaded immediate {imm} into x{rd} -> {registers[rd]}")
    else:
        output_to_gui_global("Warning: Attempt to write to x0 ignored.")

def auipc(rd, imm):
    if rd != 0:
        # In a real CPU, AUIPC adds the upper immediate to the current PC in bytes.
        # Here, we'll treat PC as an index, so shift appropriately.
        result = (program_counter + (imm << 12)) & 0xFFFFFFFF
        registers[rd] = result
        output_to_gui_global(f"AUIPC: Loaded immediate {imm} into x{rd} -> {registers[rd]}")
    else:
        output_to_gui_global("Warning: Attempt to write to x0 ignored.")

# System Instructions which halt the program
def ecall():
    output_to_gui_global("ECALL - Halting")
    global stop_simulation
    stop_simulation = True

def ebreak():
    output_to_gui_global("EBREAK - Halting")
    global stop_simulation
    stop_simulation = True

def fence():
    output_to_gui_global("FENCE - Halting.")

def fence_tso():
    output_to_gui_global("FENCE.TSO - Halting.")

def pause():
    output_to_gui_global("PAUSE - Halting.")

# Utility Functions for reading and parsing instructions
def read_instructions_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        output_to_gui_global(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def parse_register(reg):
    reg = reg.strip()
    if reg.lower().startswith('x') and reg[1:].isdigit():
        reg_num = int(reg[1:])
        if 0 <= reg_num < 32:
            return reg_num
    output_to_gui_global(f"Error: Invalid register {reg}")
    return None

def parse_immediate(value):
    try:
        return int(value, 0)
    except ValueError:
        output_to_gui_global(f"Error: Invalid immediate value '{value}'")
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
            output_to_gui_global(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        reg1 = parse_register(parts[1])
        try:
            offset_str, base_register = parts[2].split('(')
            offset = parse_immediate(offset_str)
            reg2 = parse_register(base_register[:-1])
        except ValueError:
            output_to_gui_global(f"Error: Invalid offset notation. line='{line}'")
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
            output_to_gui_global(f"Error: JALR instruction missing operands. line='{line}'")
            return None, None, None, None, None, None

    # Immediate Arithmetic and Logical Instructions
    elif opcode in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU',
                    'SLLI', 'SRLI', 'SRAI']:
        if len(parts) != 4:
            output_to_gui_global(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = parse_register(parts[1])
        rs1 = parse_register(parts[2])
        imm = parse_immediate(parts[3])
        return opcode, rd, rs1, None, imm, None

    # R-type instructions 
    elif opcode in ['ADD', 'SUB', 'SLT', 'SLTU', 'XOR', 'OR', 'AND',
                    'SLL', 'SRL', 'SRA']:
        if len(parts) != 4:
            output_to_gui_global(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rd = parse_register(parts[1])
        rs1 = parse_register(parts[2])
        rs2 = parse_register(parts[3])
        return opcode, rd, rs1, rs2, None, None

    # Branch Instructions
    elif opcode in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
        if len(parts) != 4:
            output_to_gui_global(f"Error: {opcode} instruction missing operands. line='{line}'")
            return None, None, None, None, None, None
        rs1 = parse_register(parts[1])
        rs2 = parse_register(parts[2])
        label = parts[3]
        return opcode, None, rs1, rs2, label, None

    # Upper Immediate Instructions
    elif opcode in ['LUI', 'AUIPC']:
        if len(parts) != 3:
            output_to_gui_global(f"Error: {opcode} instruction missing operands. line='{line}'")
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
            output_to_gui_global(f"Error: JAL instruction missing operands. line='{line}'")
            return None, None, None, None, None, None

    # System instructions (ECALL, EBREAK, FENCE, FENCE.TSO, PAUSE)
    elif opcode in ['ECALL', 'EBREAK', 'FENCE', 'FENCE.TSO', 'PAUSE']:
        return opcode, None, None, None, None, None

    else:
        output_to_gui_global(f"Error: Unrecognized instruction format. line='{line}'")
        return None, None, None, None, None, None

def output_to_gui_globalRegisters(instruction=None):
    """output_to_gui_globals the state of the program."""
    global program_counter

    if instruction:
        output_to_gui_global(f"\n=== Executing Instruction ===\nInstruction: {instruction}\n")

    # Adjust the program counter for display purposes
    current_pc = program_counter
    if instruction:
        current_pc -= 1

    output_to_gui_global(f"{'='*60}")
    output_to_gui_global(f"Program Counter (PC): {current_pc}")
    output_to_gui_global(f"{'='*60}\n")

    # output_to_gui_global Registers
    output_to_gui_global(f"{'='*24} Registers {'='*24}\n")
    headers = ['Register', 'Decimal', 'Hexadecimal', 'Binary']
    output_to_gui_global(f"{headers[0]:<10} {headers[1]:>12} {headers[2]:>15} {headers[3]:>35}")
    output_to_gui_global('-' * 80)
    for i in range(32):
        reg_name = f"x{i}"
        # Convert to signed decimal
        if registers[i] & 0x80000000:
            decimal_value = registers[i] - 0x100000000
        else:
            decimal_value = registers[i]
        hex_value = f"0x{registers[i]:08X}"
        bin_value = f"0b{registers[i]:032b}"
        output_to_gui_global(f"{reg_name:<10} {decimal_value:>12} {hex_value:>15} {bin_value:>35}")
    output_to_gui_global('\n')

    # output_to_gui_global Memory Contents
    output_to_gui_global(f"{'='*22} Memory Contents {'='*22}\n")
    if memory:
        headers = ['Address (Hex)', 'Address (Dec)', 'Decimal', 'Hexadecimal', 'Binary']
        output_to_gui_global(f"{headers[0]:<15} {headers[1]:>15} {headers[2]:>12} {headers[3]:>15} {headers[4]:>35}")
        output_to_gui_global('-' * 100)
        for address in sorted(memory.keys()):
            value = memory[address]
            decimal_value = value
            hex_value = f"0x{value:02X}"
            bin_value = f"0b{value:08b}"
            output_to_gui_global(f"0x{address:08X} {address:>15} {decimal_value:>12} {hex_value:>15} {bin_value:>35}")
    else:
        output_to_gui_global("Memory is empty.\n")

    # output_to_gui_global Labels Dictionary if available
    if labels:
        output_to_gui_global(f"{'='*25} Labels {'='*25}\n")
        for label, addr in labels.items():
            output_to_gui_global(f"Label '{label}': Address {addr}")
    else:
        output_to_gui_global("\nNo labels found.\n")

# Function to load memory from a text input
def load_memory_from_text(memory_text):
    global memory
    if memory_text:
        lines = memory_text.splitlines()
        for line in lines:
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

# Function to parse and read instructions from text input
def read_instructions_from_text(instructions_text):
    return instructions_text.splitlines()

# Main Function with text input modification
def main(instructions_text, memory_text, output_to_gui, starting_pc):
    global program_counter
    global labels
    global output_to_gui_global
    global executable_instructions
    output_to_gui_global = output_to_gui
    global registers, memory, labels, csr_registers, stop_simulation
    registers = [0] * 32
    memory = {}
    labels = {}
    csr_registers = {}
    stop_simulation = False
    # Step 1: Get the instruction and memory data as text
    load_memory_from_text(memory_text)
    
    # Step 2: Read instructions
    instruction_lines = read_instructions_from_text(instructions_text)
    base_address = starting_pc
    # Step 3: First pass to register labels
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
            # Map label to the instruction address
            labels[label_name] = base_address + len(executable_instructions)
        else:
            # Append the executable instruction
            executable_instructions.append(stripped_line)

    # Step 4: Execute instructions
    instruction_count = len(executable_instructions)
    program_counter = starting_pc # Initialize PC to user-specified starting address
    running = True  # Flag to control the execution loop

    # Validate starting_pc
    if program_counter < base_address or program_counter >= base_address + instruction_count:
        output_to_gui_global(f"Error: Starting PC {program_counter} is out of valid instruction address range.")
        return

    while not stop_simulation and running and 0 <= (program_counter - base_address) < instruction_count:
        # Calculate the index in the executable_instructions list
        index = program_counter - base_address

        # Fetch the current instruction
        try:
            line = executable_instructions[index].strip()
        except IndexError:
            output_to_gui_global(f"Error: Program counter {program_counter} out of bounds.")
            break

        original_line = line  # Preserve the original line for debugging

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
                output_to_gui_global(f"Error: Unhandled opcode '{opcode}'")
                program_counter += 1
        else:
            output_to_gui_global(f"Error: Unknown opcode '{opcode}'")
            program_counter += 1

        # output_to_gui_global the register states after execution
        output_to_gui_globalRegisters(instruction=original_line)

        # Ensure x0 remains zero
        registers[0] = 0




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