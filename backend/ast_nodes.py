#clase base de la que van a heredar todos los nodos del AST
#para identificar cualquier pieza del arbol
class Nodo:
    pass
    linea = 0

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


#operacion con dos operandos(SUMA, RESTA, MULTI, DIV, ETC)
class OperacionBinaria(Nodo):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

    def __repr__(self):
        return f"({self.izquierda} {self.operador} {self.derecha})"




class Bloque(Nodo):
    def __init__(self, sentencias):
        self.sentencias =  sentencias

    def __repr__(self):
        return f"Bloque({self.sentencias})"

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


#Funciones y transferencias de control
class FuncionDecl(Nodo):
    def __init__(self, nombre, parametros, tipo_retorno, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.tipo_retorno = tipo_retorno
        self.cuerpo = cuerpo

    def __repr__(self):
        return f"FuncionDecl({self.nombre}({self.parametros}) -> {self.tipo_retorno}, {self.cuerpo})"

class Return(Nodo):
    def __init__(self, valor=None):
        self.valor = valor 

    def __repr__(self):
        return f"Return({self.valor})"

class Break(Nodo):
    def __init__(self, etiqueta=None):
        self.etiqueta = etiqueta 
        
    def __repr__(self):
        return f"Break({self.etiqueta})"

class Continue(Nodo):
    def __init__(self, etiqueta=None):
        self.etiqueta = etiqueta 
        
    def __repr__(self):
        return f"Continue({self.etiqueta})"


#Loop, asignación y operación unaria
class Loop(Nodo):
    def __init__(self, cuerpo, etiqueta=None):
        self.cuerpo = cuerpo
        self.etiqueta = etiqueta

    def __repr__(self):
        return f"Loop(etiqueta={self.etiqueta}, {self.cuerpo})"


class Asignacion(Nodo):
    def __init__(self, nombre, operador, valor):
            self.nombre = nombre
            self.operador = operador
            self.valor = valor

    def __repr__(self):
        return f"Asignacion({self.nombre} {self.operador} {self.valor})"


class OperacionUnaria(Nodo):
    def __init__(self, operador, operando):
            self.operador = operador
            self.operando = operando
    
    def __repr__(self):
        return f"OperacionUnaria({self.operador} {self.operando})"


#Arreglos, match y structs
class Arreglo(Nodo):
    def __init__(self, elementos):
        self.elementos = elementos

    def __repr__(self):
        return f"Arreglo({self.elementos})"

class AccesoIndice(Nodo):
    def __init__(self, arreglo, indice):
        self.arreglo = arreglo
        self.indice = indice

    def __repr__(self):
        return f"AccesoIndice({self.arreglo}[{self.indice}])"


class CasoMatch(Nodo):
    def __init__(self, patron, cuerpo):
        self.patron = patron
        self.cuerpo = cuerpo

    def __repr__(self):
        patron_str = self.patron if self.patron is not None else "_"
        return f"CasoMatch({patron_str} => {self.cuerpo})"

class Match(Nodo):
    def __init__(self, expresion, casos):
        self.expresion = expresion
        self.casos = casos

    def __repr__(self):
        return f"Match({self.expresion}, {self.casos})"


class StructDecl(Nodo):
    def __init__(self, nombre, campos):
        self.nombre = nombre
        self.campos = campos

    def __repr__(self):
        return f"StructDecl({self.nombre}, {self.campos})"


class StructInit(Nodo):
    def __init__(self, nombre, valor):
        self.nombre = nombre
        self.valor = valor

    def __repr__(self):
        return f"StructInit({self.nombre}, {self.valor})"

##FUNCION AGREGADA LUEGO DEL ULTIMO commit
class AsignacionIndice(Nodo):
    def __init__(self, nombre_arreglo, indice, valor):
        self.nombre_arreglo = nombre_arreglo
        self.indice = indice
        self.valor = valor

    def __repr__(self):
        return f"AsignacionIndice({self.nombre_arreglo}[{self.indice}] = {self.valor})"



class Programa(Nodo):
    def __init__(self, declaraciones):
        self.declaraciones = declaraciones

    def __repr__(self):
        return f"Programa({self.declaraciones})"
    

#ESTE ES SOLO PARA PRUEBAS
if __name__ == '__main__':
    from lexer import lexer
    from parser import parser

    codigo = '''
    fn main() {
        let numeros = [10, 20, 30];
        let mut i = 0;
        while i < numeros.len() {
            println!("{}", numeros[i]);
            i = i + 1;
        }
    }
    '''

    ast = parser.parse(codigo, lexer=lexer)
    print(ast)