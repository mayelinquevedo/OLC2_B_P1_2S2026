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
] + list(reservadas.values())

#identificadores

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')  # Check for reserved words
    return t


#caracteres ignorados
t_ignore = ' \t'

#seguimiento de linea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


#manejo de errores léxicos
def t_error(t):
    print(f"[Error Léxico] Línea {t.lineno}: Cáracter no reconocido '{t.value[0]}'")
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