"""
Analizador sintactico de OxigenScript, se construye con
ply.yacc. Toma los tokens generados por lexer.py y
construye el (AST) usando las clases definidas en ast_nodes.py.
"""
import ply.yacc as yacc
from lexer import tokens  #llamda a tokens, los qe se definieron en el lexer.py
from ast_nodes import *   #  nodos del AST
from reports.ast_tree import generar_ast


start = 'programa' #solo para algunas pruebas iniciales   

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

def p_expresion_string_from(p):
    'expresion : TIPO_STRING DOS_PUNTOS DOS_PUNTOS IDENTIFICADOR PAREN_IZQ lista_argumentos PAREN_DER'
    if p[4] == 'from' and len(p[6]) > 0:
        p[0] = p[6][0]
    else:
        p[0] = Literal('', 'String')
    
def p_expresion_true(p):
    'expresion : TRUE'
    p[0] = Literal(True, 'bool')

def p_expresion_false(p):
    'expresion : FALSE'
    p[0] = Literal(False, 'bool')

def p_expresion_char(p):
    'expresion : CHAR'
    p[0] = Literal(p[1], 'char')


def p_expresion_metodo(p):
    'expresion : expresion PUNTO IDENTIFICADOR PAREN_IZQ lista_argumentos PAREN_DER'
    p[0] = LlamadaFuncion(p[3], [p[1]] + p[5])





# Bloque de sentencias { ... }
def p_bloque(p):
    'bloque : LLAVE_IZQ lista_sentencias LLAVE_DER'
    p[0] = p[2]


def p_sentencia_bloque(p):
    'sentencia : bloque'
    p[0] = Bloque(p[1])


def p_lista_sentencias_multiple(p):
    'lista_sentencias : lista_sentencias sentencia'
    p[0] = p[1] + [p[2]]

def p_lista_sentencias_una(p):
    'lista_sentencias : sentencia'
    p[0] = [p[1]]

def p_lista_sentencias_vacia(p):
    'lista_sentencias : '
    p[0] = []

def p_sentencia_metodo(p):
    'sentencia : expresion PUNTO IDENTIFICADOR PAREN_IZQ lista_argumentos PAREN_DER PUNTO_COMA'
    p[0] = LlamadaFuncion(p[3], [p[1]] + p[5] )

# Asignacion (reasignar variable existente)
def p_sentencia_asignacion(p):
    '''sentencia : IDENTIFICADOR IGUAL expresion PUNTO_COMA
                  | IDENTIFICADOR MAS_IGUAL expresion PUNTO_COMA
                  | IDENTIFICADOR MENOS_IGUAL expresion PUNTO_COMA
                  | IDENTIFICADOR MULT_IGUAL expresion PUNTO_COMA
                  | IDENTIFICADOR DIV_IGUAL expresion PUNTO_COMA
                  | IDENTIFICADOR MODULO_IGUAL expresion PUNTO_COMA'''
    p[0] = Asignacion(p[1], p[2], p[3])


# println! y llamadas a funcion
def p_sentencia_llamada(p):
    'sentencia : llamada_funcion PUNTO_COMA'
    p[0] = p[1]

def p_llamada_funcion_normal(p):
    'llamada_funcion : IDENTIFICADOR PAREN_IZQ lista_argumentos PAREN_DER'
    p[0] = LlamadaFuncion(p[1], p[3])

# println! se tokeniza como IDENTIFICADOR('println') seguido de NOT ('!')
def p_llamada_println(p):
    'llamada_funcion : IDENTIFICADOR NOT PAREN_IZQ lista_argumentos PAREN_DER'
    p[0] = LlamadaFuncion(p[1] + '!', p[4])

def p_expresion_llamada(p):
    'expresion : llamada_funcion'
    p[0] = p[1]

def p_lista_argumentos_multiple(p):
    'lista_argumentos : lista_argumentos COMA expresion'
    p[0] = p[1] + [p[3]]

def p_lista_argumentos_uno(p):
    'lista_argumentos : expresion'
    p[0] = [p[1]]

def p_lista_argumentos_vacia(p):
    'lista_argumentos : '
    p[0] = []


# if / if-else
def p_sentencia_if(p):
    'sentencia : IF expresion bloque'
    p[0] = If(p[2], p[3])

def p_sentencia_if_else(p):
    'sentencia : IF expresion bloque ELSE bloque'
    p[0] = If(p[2], p[3], p[5])

def p_sentencia_if_else_if(p):
    'sentencia : IF expresion bloque ELSE sentencia'
    p[0] = If(p[2], p[3], [p[5]])


# while
def p_sentencia_while(p):
    'sentencia : WHILE expresion bloque'
    p[0] = While(p[2], p[3])


# loop (con  etiqueta o sin ella)
def p_sentencia_loop(p):
    'sentencia : LOOP bloque'
    p[0] = Loop(p[2])

def p_sentencia_loop_etiquetado(p):
    'sentencia : ETIQUETA DOS_PUNTOS LOOP bloque'
    p[0] = Loop(p[4], etiqueta=p[1])


# return / break / continue
def p_sentencia_return_valor(p):
    'sentencia : RETURN expresion PUNTO_COMA'
    p[0] = Return(p[2])

def p_sentencia_return_vacio(p):
    'sentencia : RETURN PUNTO_COMA'
    p[0] = Return(None)

def p_sentencia_break(p):
    'sentencia : BREAK PUNTO_COMA'
    p[0] = Break()

def p_sentencia_break_etiqueta(p):
    'sentencia : BREAK ETIQUETA PUNTO_COMA'
    p[0] = Break(p[2])

def p_sentencia_continue(p):
    'sentencia : CONTINUE PUNTO_COMA'
    p[0] = Continue()

def p_sentencia_continue_etiqueta(p):
    'sentencia : CONTINUE ETIQUETA PUNTO_COMA'
    p[0] = Continue(p[2])


# Funciones
def p_funcion_decl(p):
    'funcion : FN IDENTIFICADOR PAREN_IZQ lista_parametros PAREN_DER bloque'
    p[0] = FuncionDecl(p[2], p[4], None, p[6])

def p_funcion_decl_con_retorno(p):
    'funcion : FN IDENTIFICADOR PAREN_IZQ lista_parametros PAREN_DER FLECHA tipo bloque'
    p[0] = FuncionDecl(p[2], p[4], p[7], p[8])

def p_lista_parametros_multiple(p):
    'lista_parametros : lista_parametros COMA parametro'
    p[0] = p[1] + [p[3]]

def p_lista_parametros_uno(p):
    'lista_parametros : parametro'
    p[0] = [p[1]]

def p_lista_parametros_vacia(p):
    'lista_parametros : '
    p[0] = []

def p_parametro(p):
    'parametro : IDENTIFICADOR DOS_PUNTOS tipo'
    p[0] = (p[1], p[3])

# Programa completo: una o mas funciones
def p_programa(p):
    'programa : lista_funciones'
    p[0] = Programa(p[1])

def p_lista_funciones_multiple(p):
    'lista_funciones : lista_funciones funcion'
    p[0] = p[1] + [p[2]]

def p_lista_funciones_una(p):
    'lista_funciones : funcion'
    p[0] = [p[1]]


# Arreglos y acceso por indice
def p_expresion_arreglo(p):
    'expresion : CORCH_IZQ lista_argumentos CORCH_DER'
    p[0] = Arreglo(p[2])

def p_expresion_acceso_indice(p):
    'expresion : expresion CORCH_IZQ expresion CORCH_DER'
    p[0] = AccesoIndice(p[1], p[3])

def p_tipo_arreglo(p):
    'tipo : CORCH_IZQ tipo PUNTO_COMA NUMERO_ENTERO CORCH_DER'
    p[0] = f"[{p[2]}; {p[4]}]"


# Operacion unaria (negacion, negativo)
def p_expresion_unaria(p):
    '''expresion : NOT expresion
                  | MENOS expresion %prec NOT'''
    p[0] = OperacionUnaria(p[1], p[2])


# Match
def p_sentencia_match(p):
    'sentencia : MATCH expresion LLAVE_IZQ lista_casos LLAVE_DER'
    p[0] = Match(p[2], p[4])

def p_lista_casos_multiple(p):
    'lista_casos : lista_casos caso_match'
    p[0] = p[1] + [p[2]]

def p_lista_casos_uno(p):
    'lista_casos : caso_match'
    p[0] = [p[1]]

def p_caso_match_valor(p):
    'caso_match : expresion FLECHA_MATCH llamada_funcion COMA'
    p[0] = CasoMatch(p[1], p[3])

def p_caso_match_comodin(p):
    'caso_match : IDENTIFICADOR FLECHA_MATCH llamada_funcion COMA'
    if p[1] == '_':
        p[0] = CasoMatch(None, p[3])
    else:
        p[0] = CasoMatch(Identificadores(p[1]), p[3])


# Structs
def p_struct_decl(p):
    'sentencia : STRUCT IDENTIFICADOR LLAVE_IZQ lista_campos LLAVE_DER'
    p[0] = StructDecl(p[2], p[4])

def p_lista_campos_multiple(p):
    'lista_campos : lista_campos COMA campo'
    p[0] = p[1] + [p[3]]

def p_lista_campos_uno(p):
    'lista_campos : campo'
    p[0] = [p[1]]

def p_lista_campos_vacia(p):
    'lista_campos : '
    p[0] = []

def p_campo(p):
    'campo : IDENTIFICADOR DOS_PUNTOS tipo'
    p[0] = (p[1], p[3])

# Instanciacion de struct
def p_declaracion_struct_init(p):
    'sentencia : LET IDENTIFICADOR IGUAL IDENTIFICADOR LLAVE_IZQ lista_valores LLAVE_DER PUNTO_COMA'
    p[0] = DeclaracionVariable(p[2], p[4], StructInit(p[4], p[6]), mutable=False)

def p_lista_valores_multiple(p):
    'lista_valores : lista_valores COMA valor_campo'
    p[0] = p[1] + [p[3]]

def p_lista_valores_uno(p):
    'lista_valores : valor_campo'
    p[0] = [p[1]]

def p_valor_campo(p):
    'valor_campo : IDENTIFICADOR DOS_PUNTOS expresion'
    p[0] = (p[1], p[3])


# Acceso a campo de struct 
def p_expresion_acceso_campo(p):
    'expresion : expresion PUNTO IDENTIFICADOR'
    p[0] = AccesoIndice(p[1], p[3])  


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

    codigo = '''
    fn main() {
        let caracter: char = 'A';
        let texto = String::from("Hola");
        let numeros = [10, 20, 30];
        println!("{}", numeros.len());
    }
    '''

    resultado = parser.parse(codigo, lexer=lexer)
    print(resultado)