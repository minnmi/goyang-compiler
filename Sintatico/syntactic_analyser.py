import productions
import syntactic_table

from copy import deepcopy

def push(list, value):
    list.push(value)

def pop(list):
    list.remove(top(list))

def top(list):
    return list[0]

class SyntaticAnalyser:
    def __init__(self, token_table):
        self.token_table = token_table
        self.productions = productions.productions
        self.syntactic_table = \
            syntactic_table.get_syntactic_table("Sintatico/ST.txt")

    def analyse(self):
        max_iterations = 10E3
        cur_iteration = 0

        stack = ["<PROGRAM>"]
        tokens = [tk[2] for tk in self.token_table] # Obtém apenas o token.


        while len(stack) > 0 and cur_iteration < max_iterations:
            # Controle de loop infinito.
            cur_iteration = cur_iteration = 1

            # Obtém o não-terminal e o terminal, respectivamente.
            n_ter = top(stack)
            ter = top(tokens)

            # Quatro critérios de análise:
            #   Critério 0:
            #       Se o topo da pilha é um caractere nulo (î), apenas remova-o.
            #   Critério 1:
            #       Se o topo da pilha for o mesmo terminal que o topo da lista
            #       de tokens
            #   Critério 2:
            #       Se houve um par (não-terminal, terminal) que não está na ta-
            #       bela sintática LL(1), então um erro ocorreu.
            #   Critério 3:
            #       O topo da pilha é diferente do topo da pilha de tokens, por-
            #       tanto, procure a produção correspondente e expanda-a na pi-
            #       lha, porém inverta-a antes.

            if top(stack) == "î": # Critério 0.
                pop(stack)

            elif top(stack) == top(tokens): # Critério 1.
                pop(stack)
                pop(tokens)
            elif not n_ter in self.syntactic_table or \
                not ter in self.syntactic_table[n_ter]: # Critério 2 (Erro).
                print("Syntactic error.")
                exit(1)

            else: # Critério 3.
                pop(stack)

                idx = self.syntactic_table[n_ter][ter]

                # Adiciona a nova produção invertida na pilha.
                new_production = deepcopy(self.productions[idx])
                new_production.extend(stack)
                stack = new_production

        # Retorna True se tiver passado no analisador sintático, False caso con-
        # trário.
        return len(stack) == 0 and len(tokens) == 0
