
from copy import deepcopy
from postfix_parser import infix_to_postfix
#Lista com os operadores
operators = ["+", "-", "*", "/"]
#Mapeamento dos registradores
operators_map = {
    "+": "ADD",
    "-": "SUB",
    "/": "IDIV",
    "*": "IMUL"
}

def top(stack):
    return stack[-1]

def is_operator(lex):
    return lex in operators

def is_number(element):
    try:
        int(element)
        return True
    except:
        return False


class IntermediateCode:
    def __init__(self, lex_table):
        # Armazena as variáveis que devem ser criadas.
        self.variables = []

        # Armazenas as string utilizadas.
        self.strings = {"string_mask": "\"%s\"", "int_mask": "\"%d\""}

        # Armazena as pseudo instruções.
        self.execution_code = []

        # A tabela que contém os lexemas.
        self.lexemes = deepcopy([row[2:] for row in lex_table])

        self.current_label_id = 0

    # Atribui labels únicos para cada escopo.
    def define_unique_labels(self):
        label_match = []
        for i in range(len(self.lexemes)):
            cur_token = self.lexemes[i][0]

            # Cria um identificador único que relaciona os labels. Que estão
            # associados.
            if cur_token == "begin" or \
                cur_token == "if"   or \
                cur_token == "while":

                # Adiciona o identificador. Adiciona na pilha "label_match" para
                # para que os pares se associem corretamente.
                self.lexemes[i].append(self.current_label_id)
                label_match.append(self.current_label_id)
                self.current_label_id += 1

            elif cur_token == "else":
                self.lexemes[i].append(top(label_match))

            elif cur_token == "end":
                self.lexemes[i].append(label_match.pop())

    # Remove string contidas na tabela de lexemas e adiciona na lista de
    # strings. As strings são substituidas por códigos na tabela de lexamas.
    # Esses códigos são usados como chaves nas tabelas de strings. O formato desse có-
    # digo é "str_" + um identificador único.
    def extract_string(self, where):
        symbol = "str_" + str(len(self.strings))

        self.strings.update({symbol: self.lexemes[where][1]})
        self.lexemes[where][1] = symbol

        return 1

    # Declara todas as variáveis inteiras e as remove da tabela de lexemas.
    # Retorna 3 para indicar que todos os lexemas foram avançados.
    def extract_variable(self, where):
        self.variables.append(self.lexemes[where + 1][1])
        return 3

    # Normaliza o if-stmt, isto é, if-else-end. Com isso uma abordagem única po-
    # de ser utilizada. Padronização do if/elses. Indica se para o if existe um else.
    def normalize_if_stmt(self):
        i = 0
        while i < len(self.lexemes):
            cur_item = self.lexemes[i]

            if cur_item[0] == "if":
                has_else = False # Indica se há else-stmt.
                k = 1
                # Enquanto o "end" correspondente ao "if" não for encontrado,
                # avançe o "k". O "end" corresponde a um "if" quando o id é o
                # mesmo.
                while not (self.lexemes[i + k][0] == "end" and \
                    self.lexemes[i + k][2] == cur_item[2]):
                    if self.lexemes[i + k][0] == "else" and \
                        self.lexemes[i + k][2] == cur_item[2]:
                        has_else = True

                    k += 1

                # Caso não tenha o else, adicione-o imediatamente antes do
                # "end".
                if not has_else:
                    self.lexemes.insert(i+k, ["else", "else", cur_item[2]])
                    self.lexemes.insert(i+k+1, ["tk_colon", ":"])

            i += 1

    # Indica o deslocamento do parêntese de fechamento em relação a "start".
    def detect_close_parenthesis_offset(self, start):
        k = 1
        while self.lexemes[start + k][0] != "tk_closeparenthesis":
            k += 1
        return k

    # Indica o deslocamento de um "end" com identificador igual a "code" em relação
    # a "start".
    def detect_end(self, start, code):
        k = 1
        while self.lexemes[start + k][0] != "end" or \
            self.lexemes[start + k][2] != code:
            k += 1
        return k

    # Processa expressões condicionais. Retorna a instrução de comparação que
    # deve ser utilizada.
    def conditional_expr(self, where):
        # As expressões são da forma "opL @ opR".
        operands = [self.lexemes[where + 1], self.lexemes[where + 3]]
        operator = self.lexemes[where + 2]

        # Usa o endereçamento indireto para referência a memória.
        for i in range(len(operands)):
            if operands[i][0] == "id":
                operands[i] = "[" + operands[i][1] + "]"
            else:
                operands[i] = operands[i][1]

        # Aplica o operador.
        if operator[1] == ">":
            operator = "JL"
        elif operator[1] == "<":
            operator = "JNL"

        # Realiza a comparação baseado nos operandos.
        self.execution_code.append(["MOV", "EAX", operands[0]])
        self.execution_code.append(["MOV", "EBX", operands[1]])
        self.execution_code.append(["CMP", "EAX", "EBX"])

        return operator

    # Gera o código para o if/if-else. Retorna 6 porque seis lexemas são avan-
    # çados.
    def if_stmt(self, where):
        jump_type = self.conditional_expr(where + 1)
        self.execution_code.append(\
            [jump_type, "else_" + str(self.lexemes[where][2])])

        return 6 # if, (, op, @, op, ).

    # Gera o código para o loop while. Retorna 6 porque seis lexemas são avan-
    # çados.
    def while_stmt(self, where):
        while_code = self.lexemes[where][2]

        # Adiciona o campo de começo do loop.
        begin_label = "begin_" + str(while_code)
        self.execution_code.append(\
            ["label", begin_label])

        jump_type = self.conditional_expr(where + 1)

        # Adiciona o campo de saída do loop.
        end_label = "end_" + str(while_code)
        self.execution_code.append(\
            [jump_type, end_label])

        # Quando o while-stmt é verificado o "end" correspondente não sabe que
        # deve retornar a "begin". Por isso é introduzido um pseudo-lexema
        # "goto" que prepara para chamar (ex, JMP) esse begin.
        for i in range(len(self.lexemes)):
            if self.lexemes[i][0] == "end" and \
               self.lexemes[i][2] == while_code:
                self.lexemes.insert(i,\
                     ["goto", begin_label])
                break

        return 6 # while, (, op, @, );

    # Gera o código para a impressão de uma string.
    def print_string_stmt(self, where):
        self.extract_string(where + 2)
        string = self.lexemes[where + 2][1]

        self.execution_code.append(["PUSH", string])
        self.execution_code.append(["PUSH", "string_mask"])
        self.execution_code.append(["CALL", "print"])
        return 5 # "print" + "(" + "string" + ")" + ";" -> 5 elementos.

    # Gera o código para a impressão de um inteiro.
    def print_int_stmt(self, where):
        # Obtém o operando. Pode ser uma referência ou um imediato.
        src = self.lexemes[where + 2][1]

        # Caso seja uma referência a memória, use a indireção.
        if self.lexemes[where + 2][0] == "id":
            src = "[" + src + "]"

        self.execution_code.append(["PUSH", src])
        self.execution_code.append(["PUSH", "int_mask"])
        self.execution_code.append(["CALL", "print"])
        return 5 # "print" + "(" + "number/id" + ")" + ";" -> 5 elementos.

    # Gera o código para a leitura de um inteiro.
    def read_int(self, where):
        var_name = self.lexemes[where + 2][1]
        self.execution_code.append(["PUSH", var_name])
        self.execution_code.append(["PUSH", "int_mask"])
        self.execution_code.append(["CALL", "scan"])
        return 5 # "scan" + "(" + "id" + ")" + ";" -> 5 elementos.
    
    #Atribuição das expressões.
    def assignment(self, where):
        target = self.lexemes[where - 1]

        idx = self.lexemes.index(["tk_semicolon", ";"], where)
        expr = self.lexemes[where + 1: idx]
        expr = list(map(lambda lexeme: lexeme[1], expr))
        expr = infix_to_postfix(adapt_minus_sign(expr))

        bigExpr = len(expr) >= 3
        while len(expr) >= 3:
            for i in list(reversed(range(len(expr)))):
                if len(expr) < 3:
                    break
                operator = expr[i]
                operands = [expr[i - 1], expr[i - 2]]

                if not is_operator(operator)    or \
                       is_operator(operands[0]) or \
                       is_operator(operands[1])    :
                    continue

                for op, reg in zip(operands, ["EBX", "EAX"]):
                    if op.startswith("STK"):
                        self.execution_code.append(["POP", reg])
                    else:
                        if not is_number(op):
                            op = "[%s]"%op

                        self.execution_code.append(["MOV", reg, op])

                self.execution_code.append(\
                    [operators_map[operator], "EAX", "EBX"])

                self.execution_code.append(["PUSH", "EAX"])

                temp = expr[:i - 2]
                temp.append("STK")
                temp.extend(expr[i + 1:])
                expr = temp

        if bigExpr:
            self.execution_code.append(["POP", "EBX"])
        else:
            operand = expr[0]
            if not is_number(operand):
                operand = "[%s]"%str(operand)
            self.execution_code.append(["MOV", "EBX", operand])

        self.execution_code.append(["MOV", "EAX", target[1]])
        self.execution_code.append(["MOV", "[EAX]", "EBX"])

        return idx - where

    # Gera o código intermediário.
    def generate(self):
        self.define_unique_labels()
        self.normalize_if_stmt()

        ptr = 0
        while ptr < len(self.lexemes):
            # print(self.lexemes[ptr])
            cur_token = self.lexemes[ptr][0]
            cur_lexeme = self.lexemes[ptr][1]

            if cur_token == "int":
                ptr += self.extract_variable(ptr)

            elif cur_token == "begin":
                self.execution_code.append([
                    "label",
                    "begin_" + str(self.lexemes[ptr][2])
                ])
                ptr += 1

            elif cur_token == "end":
                self.execution_code.append([
                    "label",
                    "end_" + str(self.lexemes[ptr][2])
                ])
                ptr += 1

            elif cur_token == "else":
                label_code = str(self.lexemes[ptr][2])

                self.execution_code.append([
                    "JMP", "end_" + label_code
                ])
                self.execution_code.append([
                    "label", "else_" + label_code
                ])
                ptr += 1

            elif cur_token == "write":
                if self.lexemes[ptr + 2][0] == "string":
                    ptr += self.print_string_stmt(ptr)
                else:
                    ptr += self.print_int_stmt(ptr)

            elif cur_token == "read":
                ptr += self.read_int(ptr)

            elif cur_token == "if":
                ptr += self.if_stmt(ptr)

            elif cur_token == "while":
                ptr += self.while_stmt(ptr)

            elif cur_token == "goto":
                self.execution_code.append([
                    "JMP", cur_lexeme
                ])
                ptr += 1

            elif cur_token == "tk_assign":
                # print("before: %d"%ptr)
                ptr += self.assignment(ptr)
                # print("before: %d"%ptr)
            else:
                ptr += 1

        return {
            "variables": self.variables,
            "strings"  : self.strings,
            "code"     : self.execution_code
        }