
import sys
sys.path.append("./Lexico")
sys.path.append("./Sintatico")
sys.path.append("./Semantico")
sys.path.append("./CodigoIntermediario")

import os
from Lexico import lexer
from Sintatico.syntactic_analyser import SyntaticAnalyser as SyntaticAnalyser
from Semantico.semantic import SemanticAnalyser as SemanticAnalyser

from CodigoIntermediario.intermediate_code \
    import IntermediateCode as IntermediateCode

from CodigoFinal.final_code import FinalCode as FinalCode

def main(args):
    input = args[0]
    output = args[1]

    # Lê o  fluxo do código fonte atual em fatorial.txt e armazena na variável.
    content = ""

    with open(input, 'r') as file:
        content = file.read()

    print("+" + ("[[ Goyangi Compiler ]]".center(78, "-")) + "+")

    lex = lexer.Lexer(content)
    if lex.tokenize():
        print("|\t✔ ─── Lexer".ljust(73, " ") + "|")
    else:
        print("|\t✗ ─── Lexer".ljust(73, " ") + "|")
        exit(1)

    syntatic = SyntaticAnalyser(lex.get_table())
    if syntatic.analyse():
        print("|\t✔ ─── Syntactic".ljust(73, " ") + "|")
    else:
        print("|\t✗ ─── Syntactic".ljust(73, " ") + "|")
        exit(1)

    semantic = SemanticAnalyser(lex.get_table())
    if semantic.semantic_parser():
        print("|\t✔ ─── Semantic".ljust(73, " ") + "|")
    else:
        print("|\t✗ ─── Semantic".ljust(73, " ") + "|")
        exit(1)

    intermediateCode = IntermediateCode(lex.get_table())
    code = intermediateCode.generate()
    print("|\t✔ ─── Intermediary Code".ljust(73, " ") + "|")

    finalCode = FinalCode(code["variables"], code["strings"], code["code"])

    outputFile = open(output, mode="w")
    outputFile.write(finalCode.compile())
    print("|\t✔ ─── Final Code".ljust(73, " ") + "|")


    print("+" + ("".center(78, "-")) + "+")


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)