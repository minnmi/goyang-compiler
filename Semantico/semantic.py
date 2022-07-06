

class SemanticAnalyser:
    def __init__(self, token_list):
        self.token_list = token_list

    def semantic_parser(self, silence_mode=True):
        token_list = self.token_list

        # Lista de variáveis declaradas.
        var_list = []

        for i in range(len(token_list)):
            current_token = token_list[i][2]

            # if para verificar se i é variável.
            if current_token == "id":
                var_id = token_list[i][3]
                #print(f"\t─── Variable: {var_id}")

                if token_list[i - 1][2] == "int":
                    # if para verificar se a variável foi declarada
                    if not (var_id in var_list):
                        var_list.append(var_id)
                        # print(f"\t─── Declared Variable: {var_id}")

                        # Adiciona a variável com o valor de inicialização.
                        """ if token_list[i + 1][2] == "tk_assign":
                            var_dicts.update({
                                var_id: token_list[i + 1][3]
                            }) """
                        # Caso a variável não tenha sido inicializada.
                        """ else:
                            print("Initialized variable.")
                            exit(1) """

                    # Tentativa de redeclaração de variável.
                    else:
                        #if not silence_mode:
                            #print("Variable redeclaration.")
                        print("\t─── Variable redeclaration")
                        #return False

                # Averigua se a variável foi adicionada ao dicionário
                elif not (var_id in var_list):
                    if not silence_mode:
                        print("\t─── Reference to unknown variable.")
                    print(token_list[i])
                    return False

                elif token_list[i + 1][2] == "tk_assign":
                    k = i + 2
                    while token_list[k][2] != "tk_semicolon":
                        k += 1
                    expr = token_list[i + 2:k]
                    expr = [row[3] for row in expr]
                    #print(expr)
                    for i in range(len(expr)):
                        if expr[i] == "/" and expr[i + 1] == "0":
                            # print(f"\t─── Error! Division by zero: {expr}")
                            return False

        return True
