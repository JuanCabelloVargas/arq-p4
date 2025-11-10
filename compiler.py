VARIABLES = ["a", "b", "c", "d", "e", "f", "g"]


def tokenize(line: str):
    """
    Convierte una línea en tokens
    """
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



def to_rpn(expr_tokens): #Shuting yard 
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


def is_literal(token: str) -> bool: #check si es literal numerico o no, esto para data mas tarde
    if not token:
        return False
    if token[0] in "+-":
        return token[1:].isdigit()
    return token.isdigit()
