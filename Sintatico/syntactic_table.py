

# Constrói a tabela sintática.
def get_syntactic_table(filename):
    table = {}

    # Lê a partir de uma arquivo e constrói o dicionário.
    with open(filename) as f:
        for line in f:
            production = line
            production_splitted = production.split(",")

            non_terminal = production_splitted[0]
            terminal     = production_splitted[1]
            value        = int(production_splitted[2])

            if not non_terminal in table:
                table.update({non_terminal: {terminal : value}})
            elif not terminal in table[non_terminal]:
                table[non_terminal].update({terminal : value})

    return table
