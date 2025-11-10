VARIABLES = ["a", "b", "c", "d", "e", "f", "g"]


def tokenize(line: str):
    tokens = []
    current = ""
    specials = set("+-=()")

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
    precedence = {"+": 1, "-": 1}

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

    def new_temp():
        nonlocal temp_id
        temp_id += 1
        name = f"t{temp_id}"
        temps.append(name)
        return name

    for token in rpn:
        if token in {"+", "-"}:
            if len(stack) < 2:
                raise ValueError("faltan operandos")
            right = stack.pop()
            left = stack.pop()
            temp = new_temp()

            # A = left
            if is_literal(left):
                code.append(f"    MOV A,{left}")
            else:
                code.append(f"    MOV A,(v_{left})")

            # A = A ± right
            if token == "+":
                if is_literal(right):
                    code.append(f"    ADD A,{right}")
                else:
                    code.append(f"    ADD A,(v_{right})")
            else:
                if is_literal(right):
                    code.append(f"    SUB A,{right}")
                else:
                    code.append(f"    SUB A,(v_{right})")

            # v_tN = A   (siempre en memoria)
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

    return code, temps
