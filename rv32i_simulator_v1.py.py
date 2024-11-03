# by Ahmed Elkhodary
# last updated nov 11


registers = [0] * 32
program_counter = 0
memory = {}

# **************************FUNCTIONS DEFINITIONS*************************

# ----------Arithmetical & logical instructions-------------
def add(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = registers[rs1] + registers[rs2]
def sub(rd, rs1, rs2):
    if rd != 0:
        registers[rd] = registers[rs1] - registers[rs2]
def addi(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] + imm
def andi(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] & imm
def ori(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] | imm
def xori(rd, rs1, imm):
    if rd != 0:
        registers[rd] = registers[rs1] ^ imm
#------------shifting operations---------------
def slli(rd, rs1, shamt):
    if rd != 0:
        registers[rd] = registers[rs1] << shamt
def srli(rd, rs1, shamt):
    if rd != 0:
        registers[rd] = registers[rs1] >> shamt
def srai(rd, rs1, shamt):
    if rd != 0:
        registers[rd] = (registers[rs1] >> shamt) | (-(registers[rs1] < 0) << (32 - shamt))
# ----------------Loading and storing operations------------
def lw(address, rd):
    registers[rd] = memory.get(address, 0)
def sw(rs1, address):
    memory[address] = registers[rs1]
# -----------------Immediate instructions--------------
def lui(rd, imm):
    registers[rd] = imm << 12
def auipc(rd, imm):
    registers[rd] = (program_counter + (imm << 12))
# -----------Branch instructions-----------
def beq(rs1, rs2, imm):
    global program_counter
    if registers[rs1] == registers[rs2]:
        program_counter += imm - 1
def bne(rs1, rs2, imm):
    global program_counter
    if registers[rs1] != registers[rs2]:
        program_counter += imm - 1

def blt(rs1, rs2, imm):
    global program_counter
    if registers[rs1] < registers[rs2]:
        program_counter += imm - 1

#------------------Halting instructions-------------
def ecall():
    print("CANNOT EXECUTE ECALL SINCE IT IS A HALTING INSTRUCTION")
    return True
def ebreak():
    print("CANNOT EXECUTE EBREAK SINCE IT IS A HALTING INSTRUCTION")
    return True

def pause():
    print("CANNOT EXECUTE PAUSE SINCE IT IS A HALTING INSTRUCTION")
    return True

def fence():
    print("CANNOT EXECUTE FENCE SINCE IT IS A HALTING INSTRUCTION")
    return True

def fence_tso():
    print("CANNOT EXECUTE FENCE.TSO SINCE IT IS A HALTING INSTRUCTION")
    return True

# Instruction mapping (dictionary output to actual function)
instructions = {
    'ADD': add,
    'SUB': sub,
    'ADDI': addi,
    'ANDI': andi,
    'ORI': ori,
    'XORI': xori,
    'SLLI': slli,
    'SRLI': srli,
    'SRAI': srai,
    'LW': lw,
    'SW': sw,
    'LUI': lui,
    'AUIPC': auipc,
    'BEQ': beq,
    'BNE': bne,
    'BLT': blt,
    'ECALL': ecall,
    'EBREAK': ebreak,
    'PAUSE': pause,
    'FENCE': fence,
    'FENCE.TSO': fence_tso
}

# checking the user input and splits a single line of instruction (parts) into opcode, rd, rs...
def read_instructions_from_file(file_path):
    with open(file_path, 'r') as file:
        instructions = file.readlines()
    return instructions


def instruction_splitting(line):
    parts = line.strip().split(',') # cuz the instruction is separated by commas ','
    opcode = parts[0].strip()  # First part is the opcode
    rd = parts[1].strip() if len(parts) > 1 and parts[1].strip() != "" else None # it then moves to rd field which is 1st field
    rs1 = parts[2].strip() if len(parts) > 2 and parts[2].strip() != "" else None #2nd feild
    rs2 = parts[3].strip() if len(parts) > 3 and parts[3].strip() != "" else None #3rd field
    imm = parts[4].strip() if len(parts) > 4 and parts[4].strip() != "" else None #4th field
    return opcode, rd, rs1, rs2, imm


def main():
    file_path = r"D:\Downloads\rv32i_instructions.txt"  # text file path on my pc
    instruction_lines = read_instructions_from_file(file_path)

    for line in instruction_lines:
        instruction = instruction_splitting(line)
        print(instruction)


if __name__ == "__main__":
    main()
