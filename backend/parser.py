"""
Analizador sintactico de OxigenScript, se construye con
ply.yacc. Toma los tokens generados por lexer.py y
construye el (AST) usando las clases definidas en ast_nodes.py.
"""

import ply.yacc as yacc
from lexer import tokens  #llamda a tokens, los qe se definieron en el lexer.py
from ast_nodes import *   #  nodos del AST




if __name__ == '__main__':
    print("Parser de OxigenScript")