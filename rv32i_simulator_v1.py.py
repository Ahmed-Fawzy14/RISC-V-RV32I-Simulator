registers = [0] * 32
program_counter = 0
memory = {}
labels = {}

#Funciton Definitions 

#Arithmetic and Logical Instructions 
def add(rd, rs1, rs2):
    global program_counter
    if rd != 0:
        registers[rd] = registers[rs1] + registers[rs2]
    program_counter += 1

def sub(rd, rs1, rs2):
    global program_counter
    if rd != 0:
        registers[rd] = registers[rs1] - registers[rs2]
    program_counter += 1

def addi(rd, rs1, imm):
    global program_counter
    if rd != 0:
        registers[rd] = registers[rs1] + imm
    program_counter += 1

def andi(rd, rs1, imm):
    global program_counter
    if rd != 0:
        registers[rd] = registers[rs1] & imm
    program_counter += 1

def ori(rd, rs1, imm):
    global program_counter
    if rd != 0:
        registers[rd] = registers[rs1] | imm
    program_counter += 1

def xori(rd, rs1, imm):
    global program_counter
    if rd != 0:
        registers[rd] = registers[rs1] ^ imm
    program_counter += 1

#Branch Instructions
def beq(rs1, rs2, target):
    global program_counter
    if registers[rs1] == registers[rs2]:
        program_counter = target
    else:
        program_counter += 1

def bne(rs1, rs2, target):
    global program_counter
    if registers[rs1] != registers[rs2]:
        program_counter = target
    else:
        program_counter += 1

def blt(rs1, rs2, target):
    global program_counter
    if registers[rs1] < registers[rs2]:
        program_counter = target
    else:
        program_counter += 1

#Memory Instructions
def lw(address, rd):
    global program_counter
    registers[rd] = memory.get(address, 0)
    program_counter += 1

def sw(rs1, address):
    global program_counter
    memory[address] = registers[rs1]
    program_counter += 1

#Immediate Instructions
def lui(rd, imm):
    global program_counter
    registers[rd] = imm << 12
    program_counter += 1

def auipc(rd, imm):
    global program_counter
    registers[rd] = program_counter + (imm << 12)
    program_counter += 1

#Synchronization and Halting Instructions
def pause():
    global program_counter
    print("PAUSE")
    program_counter += 1

def fence():
    global program_counter
    print("FENCE")
    program_counter += 1

def fence_tso():
    global program_counter
    print("FENCE.TSO")
    program_counter += 1

def ecall():
    print("ECALL - Halting")
    return True

def ebreak():
    print("EBREAK - Halting")
    return True

def printRegisters():
    # Print registers in decimal format
    print("Register values in decimal:", " ".join(str(register) for register in registers))
    
    # Print registers in binary format
    print("Register values in binary:", " ".join(bin(register) for register in registers))
    
    # Print registers in hexadecimal format
    print("Register values in hexadecimal:", " ".join(hex(register) for register in registers))
    
    print(f"Program Counter: {program_counter}")

# ---------- Utility Functions ----------
def read_instructions_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def instruction_splitting(line):
    # Remove comments
    line = line.split('#')[0].strip()
    parts = line.split(',')
    
    # Handle labels only
    if len(parts) == 1 and parts[0].endswith(':'):
        label = parts[0].strip().replace(':', '')
        return None, None, None, None, None, label

    if not parts[0]:
        return None, None, None, None, None, None

    opcode = parts[0].strip()
    rd = parts[1].strip() if len(parts) > 1 else None
    rs1 = parts[2].strip() if len(parts) > 2 else None
    rs2 = parts[3].strip() if len(parts) > 3 else None
    imm_or_label = parts[4].strip() if len(parts) > 4 else None
    label = parts[5].strip() if len(parts) > 5 else None

    rd = int(rd) if rd and rd.isdigit() else None
    rs1 = int(rs1) if rs1 and rs1.isdigit() else None
    rs2 = int(rs2) if rs2 and rs2.isdigit() else None
    
    # Convert `imm_or_label` to integer if it’s a hexadecimal or decimal number
    if imm_or_label:
        try:
            imm_or_label = int(imm_or_label, 0)  # `0` allows auto-detection of base (hex, dec)
        except ValueError:
            pass  # Leave as a string if it's a label

    return opcode, rd, rs1, rs2, imm_or_label, label

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

# Main function remains the same
def main():
    global program_counter
    file_path = user_input()
    instruction_lines = read_instructions_from_file(file_path)

    # First pass to register labels
    for line_number, line in enumerate(instruction_lines):
        opcode, rd, rs1, rs2, imm_or_label, label = instruction_splitting(line)
        if label:
            labels[label] = line_number

    # Second pass to execute instructions
    while program_counter < len(instruction_lines):
        line = instruction_lines[program_counter]
        opcode, rd, rs1, rs2, imm_or_label, _ = instruction_splitting(line)
        print(opcode, rd, rs1, rs2, imm_or_label, _)
        if not opcode:
            program_counter += 1
            continue

        if opcode in instructions:
            if opcode in ['BEQ', 'BNE', 'BLT']:
                # Branch instructions require rs1, rs2, and a target address
                target = labels[imm_or_label] if isinstance(imm_or_label, str) else imm_or_label
                instructions[opcode](rs1, rs2, target)
            elif opcode in ['LUI', 'AUIPC']:
                # LUI and AUIPC use rd and an immediate value
                instructions[opcode](rd, imm_or_label)
            elif opcode in ['LW', 'SW']:
                # Load and store instructions require address and register
                instructions[opcode](imm_or_label, rd if opcode == 'LW' else rs1)
            else:
                # Arithmetic and other instructions (like ADD, SUB, etc.)
                instructions[opcode](rd, rs1, rs2)
        printRegisters()
        program_counter += 1

    printRegisters()
    print("Labels:", labels)

# Dictionary of instructions remains the same
instructions = {
    'ADD': add,
    'SUB': sub,
    'ADDI': addi,
    'ANDI': andi,
    'ORI': ori,
    'XORI': xori,
    'LW': lw,
    'SW': sw,
    'LUI': lui,
    'AUIPC': auipc,
    'BEQ': beq,
    'BNE': bne,
    'BLT': blt,
    'PAUSE': pause,
    'FENCE': fence,
    'FENCE.TSO': fence_tso,
    'ECALL': ecall,
    'EBREAK': ebreak
}

if __name__ == "__main__":
    main()
