
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




#parte de codigo, solo para prueba 

if __name__ == '__main__':
    lit = Literal(10,'i32') #simulacion de un literal: 10 de tipo i32
    print(lit) 

    ident = Identificadores('x')   #simulacion de uso de una variable : x
    print(ident)
    