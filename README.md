tokenize(line: str)
Convierte una cadena de texto en una lista de tokens individuales.
Recorre cada carácter y separa palabras, números y operadores especiales (+, -, =, paréntesis) en elementos independientes.

to_rpn(expr_tokens)
Convierte una expresión en notación infija (normal) a notación postfija (RPN - Reverse Polish Notation) usando el algoritmo Shunting Yard.

is_literal(token: str)
Determina si un token es un número literal o una variable.

generate_asm_from_rpn(rpn)
Genera código assembly ASUA a partir de una expresión en RPN.

compile_line(line: str, var_values=None)
Función principal que coordina todo el proceso de compilación.

main()
Es el main :)
