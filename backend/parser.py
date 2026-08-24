"""
Analizador sintactico de OxigenScript, se construye con
ply.yacc. Toma los tokens generados por lexer.py y
construye el (AST) usando las clases definidas en ast_nodes.py.
"""
import ply.yacc as yacc
from lexer import tokens  #llamda a tokens, los qe se definieron en el lexer.py
from ast_nodes import *   #  nodos del AST



start = 'sentencia' #temporal, solo para algunas pruebas iniciales   

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




# Declaracion de variables (let / let mut)

#   con tipo explicito y valor
def p_declaracion_variable_completa(p):
    'sentencia : LET IDENTIFICADOR DOS_PUNTOS tipo IGUAL expresion PUNTO_COMA'
    p[0] = DeclaracionVariable(p[2], p[4], p[6], mutable=False)

def p_declaracion_variable_mut_completa(p):
    'sentencia : LET MUT IDENTIFICADOR DOS_PUNTOS tipo IGUAL expresion PUNTO_COMA'
    p[0] = DeclaracionVariable(p[3], p[5], p[7], mutable=True)



# tipo inferido, solo valor
def p_declaracion_variable_inferida(p):
    'sentencia : LET IDENTIFICADOR IGUAL expresion PUNTO_COMA'
    p[0] = DeclaracionVariable(p[2], None, p[4], mutable=False)

def p_declaracion_variable_mut_inferida(p):
    'sentencia : LET MUT IDENTIFICADOR IGUAL expresion PUNTO_COMA'
    p[0] = DeclaracionVariable(p[3], None, p[5], mutable=True)



# solo tipo, sin valor inicial
def p_declaracion_variable_sin_valor(p):
    'sentencia : LET IDENTIFICADOR DOS_PUNTOS tipo PUNTO_COMA'
    p[0] = DeclaracionVariable(p[2], p[4], None, mutable=False)

def p_declaracion_variable_mut_sin_valor(p):
    'sentencia : LET MUT IDENTIFICADOR DOS_PUNTOS tipo PUNTO_COMA'
    p[0] = DeclaracionVariable(p[3], p[5], None, mutable=True)


# Tipos del lenguaje
def p_tipo(p):
    '''tipo : TIPO_I32
            | TIPO_F64
            | TIPO_BOOL
            | TIPO_CHAR
            | TIPO_STRING'''
    p[0] = p[1]

# parser
parser = yacc.yacc()




#ESTA PARTE ES PARA PRUEBA DE PARSER.PY
if __name__ == '__main__':
    from lexer import lexer

    codigo = "let mut x: i32 = 10 + 5;"

    resultado = parser.parse(codigo, lexer=lexer)
    print(resultado)