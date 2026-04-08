import sys

def assemble_riscv(instruction, output_format='binary'):
    opcode_map = {
        'add':  ('R', '0000000', '000', '0110011'),
        'sub':  ('R', '0100000', '000', '0110011'),
        'or':   ('R', '0000000', '110', '0110011'),
        'and':  ('R', '0000000', '111', '0110011'),
        'xor':  ('R', '0000000', '100', '0110011'),
        'sll':  ('R', '0000000', '001', '0110011'),
        'srl':  ('R', '0000000', '101', '0110011'),
        'sra':  ('R', '0100000', '101', '0110011'),
        'addi': ('I', '000', '0010011'),
        'slti': ('I', '010', '0010011'),
        'ori':  ('I', '110', '0010011'),
        'xori': ('I', '100', '0010011'),
        'andi': ('I', '111', '0010011'),
        'slli': ('I', '001', '0010011'),
        'srli': ('I', '101', '0010011'),
        'srai': ('I', '101', '0010011'),
        'lw':   ('I', '010', '0000011'),
        'lh':   ('I', '001', '0000011'),
        'lb':   ('I', '000', '0000011'),
        'lbu':  ('I', '100', '0000011'),
        'lhu':  ('I', '101', '0000011'),
        'sw':   ('S', '010', '0100011'),
        'sh':   ('S', '001', '0100011'),
        'sb':   ('S', '000', '0100011'),
        'beq':  ('B', '000', '1100011'),
        'bne':  ('B', '001', '1100011'),
        'blt':  ('B', '100', '1100011'),
        'bge':  ('B', '101', '1100011'),
        'bltu': ('B', '110', '1100011'),
        'bgeu': ('B', '111', '1100011'),
        'lui':  ('U', '0000000', '0110111'),
        'auipc':('U', '0000000', '0010111'),
    }
    
    parts = instruction.replace(',', '').split()
    
    if not parts:
        return ""
    
    mnemonic = parts[0]
    
    if mnemonic not in opcode_map:
        return "Instrução não suportada"
    
    fmt, *params = opcode_map[mnemonic]
    
    if fmt == 'R':
        funct7, funct3, opcode = params
        rd, rs1, rs2 = [reg_to_bin(r) for r in parts[1:]]
        binary_code = f"{funct7}{rs2}{rs1}{funct3}{rd}{opcode}"
    
    elif fmt == 'I':
        funct3, opcode = params
        if mnemonic in ['lw', 'lh', 'lb', 'lbu', 'lhu']:
            rd, mem = parts[1], parts[2]
            offset, rs1 = mem.split('(')
            rs1 = rs1[:-1]
        else:
            rd, rs1, imm = parts[1:]
        
        rd, rs1 = reg_to_bin(rd), reg_to_bin(rs1)
        if mnemonic in ['lw', 'lh', 'lb', 'lbu', 'lhu']:
            imm = offset
        imm = imm_to_bin(imm, 12)
        binary_code = f"{imm}{rs1}{funct3}{rd}{opcode}"
    
    elif fmt == 'S':
        funct3, opcode = params
        rs2, mem = parts[1], parts[2]
        offset, rs1 = mem.split('(')
        rs1 = rs1[:-1]
        rs2, rs1 = reg_to_bin(rs2), reg_to_bin(rs1)
        imm_bin = imm_to_bin(offset, 12)
        imm_11_5, imm_4_0 = imm_bin[:7], imm_bin[7:]
        binary_code = f"{imm_11_5}{rs2}{rs1}{funct3}{imm_4_0}{opcode}"

    elif fmt == 'B':
        funct3, opcode = params
        rs1, rs2, imm = parts[1], parts[2], parts[3]
        rs1, rs2 = reg_to_bin(rs1), reg_to_bin(rs2)
        
        imm = imm if imm.isdigit() else "0"  
        
        imm_bin = imm_to_bin(imm, 12)
        imm_12, imm_10_5, imm_4_1, imm_11 = imm_bin[0], imm_bin[1:7], imm_bin[7:11], imm_bin[11]
        binary_code = f"{imm_12}{imm_10_5}{rs2}{rs1}{funct3}{imm_4_1}{imm_11}{opcode}"
    
    elif fmt == 'U':
        opcode = params[1]
        rd, imm = parts[1], parts[2]
        rd = reg_to_bin(rd)
        
        imm = imm if imm.isdigit() else "0"
        imm_bin = imm_to_bin(imm, 20)  
        binary_code = f"{imm_bin}{rd}{opcode}"

    
    else:
        return "Formato não suportado"
    
    if output_format == 'hex':
        return format(int(binary_code, 2), '08x')
    return binary_code

def reg_to_bin(reg):
    """Converte registrador xN para binário de 5 bits."""
    return format(int(reg[1:]), '05b')

def imm_to_bin(imm, bits):
    imm = int(imm)
    if imm < 0:
        imm = (1 << bits) + imm  
    return format(imm & ((1 << bits) - 1), f'0{bits}b')

def main():
    if len(sys.argv) < 2:
        print("Uso: python assembler.py <arquivo_entrada.asm> [arquivo_saida] [hex]")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != 'hex' else None
    output_format = 'hex' if 'hex' in sys.argv else 'binary'
    
    try:
        with open(input_file, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        return
    
    if output_file:
        with open(output_file, 'w') as output:
            for line in lines:
                line = line.strip()
                if line:
                    output.write(assemble_riscv(line, output_format) + '\n')
        print(f"Arquivo de saída '{output_file}' gerado com sucesso")
    else:
        for line in lines:
            line = line.strip()
            if line:
                print(assemble_riscv(line, output_format))

if __name__ == "__main__":
    main()
