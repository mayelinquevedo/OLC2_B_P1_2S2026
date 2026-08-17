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
    'MAS', 'MENOS', 
    'MULT', 'DIV', 'MODULO',
    'IGUAL', 
    'MAYORQUE', 'MENORQUE',
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

t_IGUAL = r'='
t_MAYORQUE = r'>'
t_MENORQUE = r'<'

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
    let mut edad: i32 = 20; 
    fn saludar(){
        if edad {
            return true; 
        }
    }
    '''

    lexer.input(data)
    for tok in lexer:
        print(tok)