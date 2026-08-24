"""
Analizador sintactico de OxigenScript, se construye con
ply.yacc. Toma los tokens generados por lexer.py y
construye el (AST) usando las clases definidas en ast_nodes.py.
"""
import ply.yacc as yacc
from lexer import tokens  #llamda a tokens, los qe se definieron en el lexer.py
from ast_nodes import *   #  nodos del AST

#Precedencia de operadores (tomando en cuenta de menor a mayor prioridad)
precedence = (
    ('left', 'OR'),   #prioridad más baja
    ('left', 'AND'),
    ('left', 'IGUAL_IGUAL', 'DIFERENTE'),
    ('left', 'MENORQUE', 'MAYORQUE', 'MENOR_IGUAL', 'MAYOR_IGUAL'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULT', 'DIV', 'MODULO'),
    ('right', 'NOT'),     #prioridad más alta
)

# Expresiones: operaciones binarias
def p_expresion_binaria(p):
    '''expresion : expresion MAS expresion
                  | expresion MENOS expresion
                  | expresion MULT expresion
                  | expresion DIV expresion
                  | expresion MODULO expresion
                  | expresion IGUAL_IGUAL expresion
                  | expresion DIFERENTE expresion
                  | expresion MENORQUE expresion
                  | expresion MAYORQUE expresion
                  | expresion MENOR_IGUAL expresion
                  | expresion MAYOR_IGUAL expresion
                  | expresion AND expresion
                  | expresion OR expresion'''
    p[0] = OperacionBinaria(p[1], p[2], p[3])

def p_expresion_agrupacion(p):
    'expresion : PAREN_IZQ expresion PAREN_DER'
    p[0] = p[2]  

def p_expresion_identificador(p):
    'expresion : IDENTIFICADOR'
    p[0] = Identificadores(p[1])




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


#  errores sintacticos
def p_error(p):
    if p:
        print(f"[Error Sintactico] Linea {p.lineno}: token inesperado '{p.value}'")
    else:
        print("[Error Sintactico] Fin de archivo inesperado")


# parser
parser = yacc.yacc()




#ESTA PARTE ES PARA PRUEBA DE PARSER.PY
if __name__ == '__main__':
    from lexer import lexer

    codigo = "10 + 5"

    resultado = parser.parse(codigo, lexer=lexer)
    print(resultado)