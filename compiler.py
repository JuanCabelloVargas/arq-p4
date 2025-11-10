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
