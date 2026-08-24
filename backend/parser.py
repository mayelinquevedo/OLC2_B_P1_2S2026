"""
Analizador sintactico de OxigenScript, se construye con
ply.yacc. Toma los tokens generados por lexer.py y
construye el (AST) usando las clases definidas en ast_nodes.py.
"""

import ply.yacc as yacc
from lexer import tokens  #llamda a tokens, los qe se definieron en el lexer.py
from ast_nodes import *   #  nodos del AST

#Expresiones literales.
def p_expresion_numero_entero(p):
    'expresion : NUMERO_ENTERO'
    p[0] = Literal(p[1], 'i32')

def p_expresion_numero_decimal(p):
    'expresion : NUMERO_DECIMAL'
    p[0] = Literal(p[1], 'f64')

def p_expresion_string(p):
    'expresion : STRING'
    p[0] = Literal(p[1], 'String')

def p_expresion_true(p):
    'expresion : TRUE'
    p[0] = Literal(True, 'bool')

def p_expresion_false(p):
    'expresion : FALSE'
    p[0] = Literal(False, 'bool')


if __name__ == '__main__':
    print("Parser de OxigenScript")