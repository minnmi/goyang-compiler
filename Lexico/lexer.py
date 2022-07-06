# Um RegEx, ou Expressão Regular, é uma sequência de caracteres que forma um padrão de pesquisa.
# O RegEx pode ser usado para verificar se uma sequência contém o padrão de pesquisa especificado.
import os
import re


## [col, lin, token, expr]

class Lexer(object):
    def __init__(self, source_code):

        self.source_code = source_code

        # Os operadores da linguagem.
        # self.operators  = [':=', ':', ';', '(', ')', '/', '*', '+', '-', '=', '<', '>'];
        self.operators = {
            ';': 'tk_semicolon',
            '(': 'tk_openparenthesis',
            ')': 'tk_closeparenthesis',
            ':': 'tk_colon',
            ':=': 'tk_assign',
            '+': "+",
            '-': "-",
            '*': "*",
            '/': "/",
            '<': "<",
            '>': ">",
            '=': "="
            }

        # As palavras-chave da linguagem.
        self.keyword = ["begin", "end", "write", "read", "if", "else", "while", "int"];

        # A tabela de tokens resultante.
        self.table = []

        # Tabela que retorna o código associado por uma palavra(string)
        self.string_replace = {}

    # Método que acha aspas
    def find_quotation_marks(self, line):
        positions = []
        last_match = 0
        while line.find('"', last_match) != -1:
            last_match = line.find('"', last_match) + 1
            positions.append(last_match)

        return positions

    # Método que permite associar um código a um valor e, posteriormente, ter acesso ao valor a partir do código associado.
    def replace_string_by_code(self, line):
        quotations = self.find_quotation_marks(line)

        if (len(quotations) % 2 != 0):
            raise Exception("Bad formed string.")

        while len(quotations) > 0:
            end = quotations.pop()
            begin = quotations.pop()

            cipher = "$" + str(len(self.string_replace) + 1)

            self.string_replace.update({cipher: line[begin - 1: end]})

            line = line[:begin - 1] + cipher + line[end:]

        return line

    # Método que calcula a quantidade de caracteres que deram match. Ex: reaf e read => 3
    def numero_de_match(self, txt1, txt2):
        qnt = 0  # A quantidade de caracteres que deram match.
        idx = 0  # Posição do caractere que está sendo avaliado.

        while idx < min(len(txt1), len(txt2)):
            if txt1[idx] == txt2[idx]:
                qnt += 1
                idx += 1
            else:
                break

        return qnt

    # Método que calcula se deu match com os operadores.
    def match_operator(self, txt):
        for opt in self.operators:
            if opt == txt:
                return len(txt)

        return 0

    # Verifica se os caracteres ESTÃO dando match. Por exemplo: "rea" e "read" vai retornar 3.
    def match_keyword(self, txt):
        qnt = 0

        for opt in self.keyword:
            if self.numero_de_match(opt, txt) == len(txt):
                qnt += 1

        return qnt

    # Verifica se deu match em um inteiro.
    def match_integer(self, txt):
        # Caso haja match, retorna o tamanho da string.
        if re.match('^[0-9]+$', txt):
            return len(txt)

        # Não houve match.
        return 0

    # Verifica se deu match em uma string.
    def match_string(self, txt):
        # Caso haja match, retorna o tamanho da string.
        if re.match('^\$[0-9]*$', txt):
            return len(txt)

        # Não houve match.
        return 0

    # Verifica se deu match em um id.
    def match_id(self, txt):
        # Caso haja match, retorna o tamanho da string.
        if re.match('^(_|[a-zA-Z])(_|[a-zA-Z]|[0-9])*$', txt):
            return len(txt)

        # Não houve match.
        return 0

    # Calcula a quantidade de tipos de matchs que ocorreram.
    def has_match(self, txt):
        qnt = 0

        if self.match_operator(txt) > 0:
            qnt += 1

        if self.match_keyword(txt) > 0:
            qnt += 1

        if self.match_integer(txt) > 0:
            qnt += 1

        if self.match_string(txt) > 0:
            qnt += 1

        if self.match_id(txt) > 0:
            qnt += 1

        return qnt

    # Restaura as strings.
    def restore_string(self):
        for i in range(len(self.table)):
            row = self.table[i]
            cur_token = row[2]
            if cur_token == "string":
                cipher = row[3]
                row[3] = self.string_replace[cipher]



    # Gera os tokens
    def tokenize(self):
        # Indica se há erros na análise léxica.
        result = True

        source_code = self.source_code.split('\n')

        # Indica o inicio e o fim da expressão.
        [col_begin, col_end] = [0, 0]

        # Indica o número da linha que está sendo avaliada.
        line = 0

        # my_path = os.path.abspath(os.path.dirname(__file__))
        # file = open(os.path.join(my_path, '../Sintatico/tokenslist.txt'), 'w')
        # file.write('token,lexeme,lines,columns\n')

        # Enquanto der match vai aumentando a posição do caractere que representa o final da expressão.
        while line < len(source_code):

            cur_line = source_code[line] + " "
            cur_line = self.replace_string_by_code(cur_line)

            while col_end < len(cur_line) + 1:
                if cur_line[col_begin: col_end] in ['', ' ', '\t', '\n']:
                    col_begin = col_end
                    col_end += 1
                    continue

                if self.has_match(cur_line[col_begin: col_end + 1]) > 0:
                    col_end += 1

                # Cria uma condição para o caso de col_end alcançar o fim da linha e houver um match.

                else:
                    expr = cur_line[col_begin: col_end]

                    num_matchs = self.has_match(expr)

                    if num_matchs >= 1:
                        if self.match_operator(expr):
                            self.table.append([line + 1, col_begin, self.operators[expr], expr])
                            # file.write(str(self.operators[expr]) + ',' + str(expr)+ ',' + str(line + 1)+ ',' + str(col_begin) + '\n')

                        elif self.match_keyword(expr):
                            self.table.append([line + 1, col_begin, expr, expr])
                            # file.write(str(expr) + ',' + str(expr)+ ',' + str(line + 1)+ ',' + str(col_begin) + '\n')

                        elif self.match_integer(expr):
                            self.table.append([line + 1, col_begin, "integer", expr])
                            # file.write("integer" + ',' + str(expr)+ ',' + str(line + 1)+ ',' + str(col_begin) + '\n')

                        elif self.match_string(expr):
                            self.table.append([line + 1, col_begin, "string", expr])
                            # file.write("string" + ',' + str(expr)+ ',' + str(line + 1)+ ',' + str(col_begin) + '\n')

                        elif self.match_id(expr):
                            self.table.append([line + 1, col_begin, "id", expr])
                            # file.write("id" + ',' + str(expr)+ ',' + str(line + 1)+ ',' + str(col_begin) + '\n')

                    else:
                        self.table.append([line + 1, col_begin, "ERROR", expr])
                        result = False

                    col_begin = col_end
                    col_end += 1

            col_begin = 0
            col_end = 0

            line += 1

        self.restore_string()
        return result

    def get_table(self):
        return self.table
