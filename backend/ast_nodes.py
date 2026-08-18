
#clase base dela que van a heredar todos los nodos del AST
#para identificar cualquier pieza del arbol
class Nodo:
    pass

#nodos: Valores literales e identificadores (hojas)
class Literal(Nodo):
    def __init__(self, valor, tipo):
        self.valor = valor  #valor real
        self. tipo = tipo   #el tipo como string (i32, f64, bool, string, char, bool)

    def __repr__(self):
        return f"Literal({self.valor!r}, {self.tipo})"


#uso del nombre de una varibale dentro de una expresion
class Identificadores(Nodo):
    def __init__(self, nombre):
        self.nombre = nombre

    def __repr__(self):
        return f"Identificador({self.nombre})"

#declaracion de una variable
class DeclaracionVariable(Nodo):
    def __init__(self, nombre, tipo, valor, mutable=False):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor
        self.mutable = mutable

    def __repr__(self):
        mut = "mut " if self.mutable else ""
        return f"DeclaracionVariable({mut}{self.nombre}: {self.tipo} = {self.valor})"


#operacion con dos operandos
class OperacionBinaria(Nodo):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

    def __repr__(self):
        return f"({self.izquierda} {self.operador} {self.derecha})"



#SENTENCIA if/if else
class If(Nodo):
    def __init__(self, condicion, bloque_si, bloque_sino=None):
        self.condicion = condicion
        self.bloque_si = bloque_si
        self.bloque_sino = bloque_sino

    def __repr__(self):
        return f"If({self.condicion}, si={self.bloque_si}, sino={self.bloque_sino})"

#SENTENCIA while

class While(Nodo):
    def __init__(self, condicion, bloque):
        self.condicion = condicion  
        self.bloque = bloque        # lista de nodos (sentencias dentro del while)

    def __repr__(self):
        return f"While({self.condicion}, {self.bloque})"

#LLAMADA A FUNCION println
class LlamadaFuncion(Nodo):
    def __init__(self, nombre, argumentos):
        self.nombre = nombre          # nombre de la función,
        self.argumentos = argumentos  # lista de nodos (los argumentos pasados)

    def __repr__(self):
        return f"LlamadaFuncion({self.nombre}, {self.argumentos})"



#este bloque de prueba lo estaré cambiando conforme le agrego caracteristicas a mi AST
#parte de codigo, solo para prueba 
if __name__ == '__main__':
    lit = Literal(10, 'i32')
    print(lit)

    ident = Identificadores('x')
    print(ident)

    suma = OperacionBinaria(Literal(10, 'i32'), '+', Literal(5, 'i32'))
    decl = DeclaracionVariable('x', 'i32', suma, mutable=False)
    print(decl)

    # Simulamos: if x > 5 { println!("mayor"); }
    condicion = OperacionBinaria(Identificadores('x'), '>', Literal(5, 'i32'))
    llamada = LlamadaFuncion('println!', [Literal('mayor', 'String')])
    sentencia_if = If(condicion, [llamada])
    print(sentencia_if)