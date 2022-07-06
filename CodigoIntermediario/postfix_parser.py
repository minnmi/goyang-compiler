# Transforma uma expressão que utiliza a notação infixa para a expressão corres-
# correspondente na notação posfixa.
# -- Os operadores contidos na expressão podem ser indicados por parâmetro.
#     Ex: {operator_k: precedence_k, ...} -> { '+' : 1, '*': 2}
#
# -- Os operandos da expressão podem ser literais númericos ou texto.
#     Ex: var_1 * var_2, pi * 2, 4/2 e assim por diante.

def top(stack):
    return stack[len(stack) - 1]

def is_empty(data_structure):
    return len(data_structure) == 0

def adapt_minus_sign(expression, operators = [":=", "+", "-", "*", "/", "(", ")"]):
    for i in reversed(range(len(expression))):
        if expression[i] == "-" and expression[i-1] in operators:
            expression_before = expression[:i]
            expression_after = expression[i:]
            temp = expression_before
            temp.append("0")
            temp.extend(expression_after)
            expression = temp

    return expression

def infix_to_postfix(expression, operators = {'+':1, '-':1, '*':2, '/': 2}):
    # A pilha que armazena os operadores e os parênteses.
    stack = []

    # Armaze o resultado.
    out   = []

    for item in expression:
        # Adiciona a abertura de parênteses na pilha.
        if item == '(':
            stack.append('(')

        # Parêntese de fechamente faz descarregar a pilha na saída até encontrar
        # o parêntese de abertura.
        elif item == ')':
            while top(stack) != '(':
                out.append(stack.pop())
            stack.pop() # Remove o '(' da pilha.

        # Para o caso de ser um operador:
        #  1 - Se a pilha está vazia, o topo da pilha é uma abertura de parên-
        #      tese ou a precedência do operador no topo da pilha é menor ou
        #      igual a do operador sendo analisado, adicione-o na pilha.
        #  2 - Caso contrário, adicione-o o topo da pilha na lista de saída e
        #      adicione o novo item na pilha.
        elif item in operators.keys():
            if is_empty(stack)    or \
                top(stack) == '(' or \
                operators[top(stack)] < operators[item]:
                stack.append(item)
            else:
                out.append(stack.pop())
                stack.append(item)

        # Operandos são adicionados na saída.
        else:
            out.append(item)

    # Esvazie a pilha na saída.
    while len(stack) != 0:
        out.append(stack.pop())

    return out


# Realizar testes para verificar a eficácia da função.

expr_1 = ['(', 'a', '+', 'b', ')', '*', 'c']
expr_1_result = ['a', 'b', '+', 'c', '*']
assert infix_to_postfix(expr_1) == expr_1_result

expr_2 = ['(', 'a', '+', 'b', ')', '*', '(', 'c', '+', 'd',')']
expr_2_result = ['a', 'b', '+', 'c', 'd', '+', '*']
assert infix_to_postfix(expr_2) == expr_2_result

expr_3 = ['a', ':=', 'a', '*', 'b']
expr_3_result = ['a', 'a', 'b', '*', ':=']
precedence = {'+':1, '-':1, '*':2, '/':2, ':=':0}
assert infix_to_postfix(expr_3, precedence) == expr_3_result
