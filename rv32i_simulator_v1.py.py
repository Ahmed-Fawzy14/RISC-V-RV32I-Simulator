

registers = [0]*32
program_counter=0
memort = {}

def add(rd, rs1, rs2):
    registers[rd]= registers[rs1]+registers[rs2]
    
def sub(rd, rs1, rs2):
    registers[rd] = registers[rs1] - registers[rs2]
    
def lw(address, rd):
    registers[rd]=memory.get(address, 0)
    
def sw(rs1, address):
    memory[address] = registers[rs1]
    
def ecall():
    print("CANNOT EXECUTE ECALL SINCE IT IS A HAULTING INSTRUCTION")
    return True

def ebreak():
    print("CANNOT EXECUTE EBREAK SINCE IT IS A HAULTING INSTRUCTION")
    return True
    
def pause():
    print("CANNOT EXECUTE PAUSE SINCE IT IS A HAULTING INSTRUCTION")
    return True
    
def fence():
    print("CANNOT EXECUTE FENCE SINCE IT IS A HAULTING INSTRUCTION")
    return True
    
def fence_tso():
    print("CANNOT EXECUTE FENCE.TSO SINCE IT IS A HAULTING INSTRUCTION")
    return True


instructions = {
    'ADD': add,
    'SUB': sub,
    'LW': lw,
    'SW':sw,
    'ECALL':ecall,
    'EBREAK':ebreak,
    'PAUSE':pause,
    'FENCE':fence,
    'FENCE.TSO':fence_tso
}

def load_program_file(filename):
    program = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().strip(',')
            opcode = parts[0].strip()

