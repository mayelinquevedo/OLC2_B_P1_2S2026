import ply.lex as lex

#palabras reservadas del lenguaje
reservadas = {
    'let': 'LET',
    'mut': 'MUT',
    'fn': 'FN',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'loop': 'LOOP',
    'match': 'MATCH',
    'struct': 'STRUCT',
    'return': 'RETURN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'true': 'TRUE',
    'false': 'FALSE',

#tipos del lenguaje
    'i32': 'TIPO_I32',
    'f64': 'TIPO_F64',
    'bool': 'TIPO_BOOL',
    'char': 'TIPO_CHAR',
    'String': 'TIPO_STRING',
}

#lista de tokens
tokens = [
    'IDENTIFICADOR',
    'NUMERO_ENTERO',
    'NUMERO_DECIMAL',
    'STRING', 'CHAR', 'ETIQUETA',
    'MAS', 'MENOS', 
    'MULT', 'DIV', 'MODULO',
    'IGUAL', 
    'MAYORQUE', 'MENORQUE',
    'IGUAL_IGUAL', 'DIFERENTE',
    'MAYOR_IGUAL', 'MENOR_IGUAL',
    'AND', 'OR', 'NOT', 'AMPER',
    'MAS_IGUAL', 'MENOS_IGUAL',
    'MULT_IGUAL', 'DIV_IGUAL', 'MODULO_IGUAL',
    'RANGO',
    'FLECHA', 'FLECHA_MATCH',
    'LLAVE_IZQ', 'LLAVE_DER', 
    'PAREN_IZQ', 'PAREN_DER',
    'CORCH_IZQ', 'CORCH_DER',
    'DOS_PUNTOS', 'PUNTO_COMA',
    'COMA', 'PUNTO',

] + list(reservadas.values())

#identificadores
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')  
    return t

#tokens simples (simbolos y operadores de un solo caracter o fijo)
t_MAS = r'\+'
t_MENOS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_MODULO = r'%'

#t_IGUAL = r'='
#t_MAYORQUE = r'>'
#t_MENORQUE = r'<'

t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
t_PAREN_IZQ = r'\('
t_PAREN_DER = r'\)'
t_CORCH_IZQ = r'\['
t_CORCH_DER = r'\]'

t_DOS_PUNTOS = r':'
t_PUNTO_COMA = r';'
t_COMA = r','
t_PUNTO = r'\.'

#numeros enters y decimales
def t_NUMERO_DECIMAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_NUMERO_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

#Strings (cadena texto entre comillas dobles " " )
def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    contenido = t.value[1:-1]
    contenido = contenido.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
    t.value = contenido
    return t


#Chars (un solo caracter entre comillas simples ' ')
def t_CHAR(t):
    r"'([^'\\]|\\.)'"
    t.value = t.value[1:-1]
    return t

#Etiquetas de loop ('outer, 'inner, etc)
def t_ETIQUETA(t):
    r"'[a-zA-Z_][a-zA-Z0-9_]*"
    t.value = t.value[1:]  #quitar la comilla simple al inicio
    return t




#Operadores relacionales, logicos y de asigncaion
#PRIMERO COMPUESTOS
def t_IGUAL_IGUAL(t):
    r'=='
    return t


def t_DIFERENTE(t):
    r'!='
    return t

def t_FLECHA(t):
    r'->'
    return t

def t_FLECHA_MATCH(t):
    r'=>'
    return t

def t_MAYOR_IGUAL(t):
    r'>='
    return t

def t_MENOR_IGUAL(t):
    r'<='
    return t

def t_AND(t):
    r'&&'
    return t

def t_OR(t):
    r'\|\|'
    return t

def t_MAS_IGUAL(t):
    r'\+='
    return t

def t_MENOS_IGUAL(t):
    r'-='
    return t

def t_MULT_IGUAL(t):
    r'\*='
    return t

def t_DIV_IGUAL(t):
    r'/='
    return t    

def t_MODULO_IGUAL(t):
    r'%='
    return t

def t_RANGO(t):
    r'\.\.'
    return t

#LUEGO SIMPLES
t_IGUAL = r'='
t_MAYORQUE = r'>'
t_MENORQUE = r'<'
t_NOT = r'!'
t_AMPER = r'&'

#IGNORAR LOS COMETNARIOS
#COMENTARIOS DE UNA LINEA // ...
def t_COMENTARIO_LINEA(t):
    r'//[^\n]*'
    pass #para no retoranr el token y asi ignorar el comentario

#COMENTARIOS DE BLOQUE /* ... */
def t_COMENTARIO_BLOQUE(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')  # Actualizar el número de línea si el comentario abarca muchas
    pass #para no retoranr el token y asi ignorar el comentario

#COMENTARIO DE BLOQUE SIN CERRAR 
def t_COMENTARIO_BLOQUE_SIN_CERRAR(t):
    r'/\*(.|\n)*'
    print(f"[Error Léxico] Línea {t.lineno}: Comentario de bloque sin cerrar (falta '*/')")
    t.lexer.lineno += t.value.count('\n')
    pass


#caracteres ignorados
t_ignore = ' \t'

#seguimiento de linea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


#manejo de errores léxicos
def t_error(t):
    print(f"[Error Léxico] Línea {t.lineno}: Caracter no reconocido '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()


#solo para pruebas
if __name__ == '__main__':
    data = '''
    let x: i32 = 10;
    /* Este comentario
       sí cierra bien */
    let y: i32 = 20; //prueba de comentario 1 linea
    '''
    lexer.input(data)
    for tok in lexer:
        print(tok)