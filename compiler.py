VARIABLES = ["a", "b", "c", "d", "e", "f", "g"]


def tokenize(line: str):
    tokens = []
    current = ""
    specials = set("+-*/%=()")

    for ch in line:
        if ch.isspace():
            if current:
                tokens.append(current)
                current = ""
        elif ch in specials:
            if current:
                tokens.append(current)
                current = ""
            tokens.append(ch)
        else:
            current += ch

    if current:
        tokens.append(current)

    return tokens



def to_rpn(expr_tokens):
    output = []
    op_stack = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}

    for t in expr_tokens:
        if t in precedence:
            while op_stack and op_stack[-1] in precedence \
                    and precedence[op_stack[-1]] >= precedence[t]:
                output.append(op_stack.pop())
            op_stack.append(t)
        elif t == "(":
            op_stack.append(t)
        elif t == ")":
            while op_stack and op_stack[-1] != "(":
                output.append(op_stack.pop())
            if not op_stack:
                raise ValueError("Paréntesis desbalanceados")
            op_stack.pop()  # saca el "("
        else:
            output.append(t)

    while op_stack:
        top = op_stack.pop()
        if top in ("(", ")"):
            raise ValueError("Paréntesis desbalanceados al final")
        output.append(top)

    return output


def is_literal(token: str) -> bool: # check para literal numerico
    if not token:
        return False
    if token[0] in "+-":
        return token[1:].isdigit()
    return token.isdigit()


def generate_asm_from_rpn(rpn): #lo generado en rpn lo pasamos a codigo asua
    code = []
    temps = []
    stack = []
    temp_id = 0
    label_id = 0

    def new_temp():
        nonlocal temp_id
        temp_id += 1
        name = f"t{temp_id}"
        temps.append(name)
        return name

    def new_label():
        nonlocal label_id
        label_id += 1
        return f"L{label_id}"

    for token in rpn:
        if token in {"+", "-", "*", "/", "%"}:
            if len(stack) < 2:
                raise ValueError("faltan operandos")
            right = stack.pop()
            left = stack.pop()
            temp = new_temp()

            if token == "+":
                if is_literal(left):
                    code.append(f"    MOV A,{left}")
                else:
                    code.append(f"    MOV A,(v_{left})")

                if is_literal(right):
                    code.append(f"    ADD A,{right}")
                else:
                    code.append(f"    ADD A,(v_{right})")

                code.append(f"    MOV (v_{temp}),A")

            elif token == "-":
                if is_literal(left):
                    code.append(f"    MOV A,{left}")
                else:
                    code.append(f"    MOV A,(v_{left})")

                if is_literal(right):
                    code.append(f"    SUB A,{right}")
                else:
                    code.append(f"    SUB A,(v_{right})")

                code.append(f"    MOV (v_{temp}),A")

            elif token == "/":
                
                temp = new_temp()
                divisor_temp = new_temp()
                dividend_temp = new_temp()
                quotient_temp = new_temp()
                
                if is_literal(right):
                    code.append(f"    MOV A,{right}")
                else:
                    code.append(f"    MOV A,(v_{right})")
                code.append(f"    MOV (v_{divisor_temp}),A")
                
                label_div_ok = new_label()
                label_div_end = new_label()
                code.append(f"    CMP A,0")
                code.append(f"    JEQ {label_div_end}")  # Si divisor == 0, marcar error
                code.append(f"    JMP {label_div_ok}")   # Si no, continuar
                
                # Manejar división por cero
                code.append(f"{label_div_end}:")
                code.append(f"    MOV A,1")
                code.append(f"    MOV (v_error),A")
                code.append(f"    MOV A,0")
                code.append(f"    MOV (v_result),A")
                code.append(f"    JMP end_program")
                
                # Continuar con división normal
                code.append(f"{label_div_ok}:")
                
                if is_literal(left):
                    code.append(f"    MOV A,{left}")
                else:
                    code.append(f"    MOV A,(v_{left})")
                code.append(f"    MOV (v_{dividend_temp}),A")
                
                code.append(f"    MOV A,0")
                code.append(f"    MOV (v_{quotient_temp}),A")
                
                label_div_loop = new_label()
                label_div_continue = new_label()
                label_div_finish = new_label()
                
                code.append(f"{label_div_loop}:")
                code.append(f"    MOV A,(v_{dividend_temp})")
                code.append(f"    CMP A,(v_{divisor_temp})")
                code.append(f"    JGE {label_div_continue}")
                code.append(f"    JMP {label_div_finish}")
                
                code.append(f"{label_div_continue}:")
                code.append(f"    MOV A,(v_{dividend_temp})")
                code.append(f"    SUB A,(v_{divisor_temp})")
                code.append(f"    MOV (v_{dividend_temp}),A")
                
                code.append(f"    MOV A,(v_{quotient_temp})")
                code.append(f"    ADD A,1")
                code.append(f"    MOV (v_{quotient_temp}),A")
                
                code.append(f"    JMP {label_div_loop}")
                
                code.append(f"{label_div_finish}:")
                code.append(f"    MOV A,(v_{quotient_temp})")
                code.append(f"    MOV (v_{temp}),A")

            elif token == "%":
                code.append(f"    ; Módulo {left} % {right}")
                code.append(f"    MOV (v_{temp}),A")

            stack.append(temp)
        else:
            stack.append(token)

    if len(stack) != 1:
        raise ValueError("sobran operandos")

    final = stack.pop()

    if is_literal(final):
        code.append(f"    MOV A,{final}")
    else:
        code.append(f"    MOV A,(v_{final})")
    code.append("    MOV (v_result),A")
    code.append("end_program:")

    return code, temps

def compile_line(line: str, var_values=None): #compila una linea
    if var_values is None:
        var_values = {}

    tokens = tokenize(line)
    if "=" not in tokens:
        raise ValueError("La expresión debe contener '='")

    eq_index = tokens.index("=")
    lhs = tokens[:eq_index]
    rhs = tokens[eq_index + 1:]

    if len(lhs) != 1 or lhs[0] != "result":
        raise ValueError("Solo se soporta 'result' en el lado izquierdo")

    rpn = to_rpn(rhs)

    code, temps = generate_asm_from_rpn(rpn)

    data_lines = []
    data_lines.append("DATA:")
    for v in VARIABLES:
        value = var_values.get(v, 0)
        name = f"v_{v}"
        data_lines.append(f"{name:8} {value}")
    for t in temps:
        name = f"v_{t}"
        data_lines.append(f"{name:8} 0")
    data_lines.append(f"{'v_result':8} 0")
    data_lines.append(f"{'v_error':8} 0")
    data_lines.append("")

    code_lines = ["CODE:"]
    code_lines.extend(code)

    all_lines = data_lines + code_lines
    total_lines = sum(1 for l in all_lines if l.strip())

    mem_accesses = 0
    for instr in code:
        s = instr.strip()
        if not s:
            continue
        op = s.split()[0]
        if op in ("MOV", "ADD", "SUB") and "(" in s and ")" in s:
            mem_accesses += 1

    return all_lines, total_lines, mem_accesses

def main():
    expr = input("ingresa expresión \n> ")

    print("\n valores iniciales variables:")
    var_values = {}
    for v in VARIABLES:
        s = input(f"{v} = ")
        s = s.strip()
        if s == "":
            var_values[v] = 0
        else:
            var_values[v] = int(s)

    asm_lines, total_lines, mem_accesses = compile_line(expr, var_values)

    print("\n;assebly: ")
    for line in asm_lines:
        print(line)
    print(f"\n; lineas totales: {total_lines}")
    print(f";memoria : {mem_accesses}")

    with open("program.asm", "w") as f:
        for line in asm_lines:
            f.write(line + "\n")
        f.write(f"\n; Líneas totales: {total_lines}\n")
        f.write(f"; Accesos a memoria (aprox): {mem_accesses}\n")

    print("\nguardado en program.asm")


if __name__ == "__main__":
    main()
