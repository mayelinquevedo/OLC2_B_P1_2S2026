"""
Intrerprete del proyecto, recorre el AST ya construido por parser.py 
y ejecuta el programa
"""
from ast_nodes import *

#Entorno: guarda las variables y sus valores
class Entorno:
    def __init__(self, padre=None):
        self.variables= {}
        self.padre = padre

    def declarar(self, nombre, valor):
        self.variables[nombre] = valor

    def obtener(self, nombre):
        if nombre in self.variables:
            return self.variables[nombre]
        if self.padre is not None:
            return self.padre.obtener(nombre)
        raise Exception(f"Variable '{nombre}' no ha sido declarada.")

    def asignar(self, nombre, valor):
        if nombre in self.variables:
            self.variables[nombre] = valor
        elif self.padre is not None:
            self.padre.asignar(nombre, valor)
        else:
            raise Exception(f"Variable '{nombre}' no ha sido declarada")

#Excepciones especiales, para controlar flujo (return, break, contine)
class SenalReturn(Exception):
    def __init__(self, valor):
        self.valor=valor

class SenalBreak(Exception):
    def __init__(self, etiqueta=None):
        self.etiqueta=etiqueta

class SenalContinue(Exception):
    def __init__(self, etiqueta=None):
        self.etiqueta=etiqueta



#Interprete principal(ESTRUCTURA BASE)
class Interprete:
    def __init__(self):
        self.entorno_global = Entorno()
        self.funciones = {}

    def ejecutar_programa(self, programa):
        for decl in programa.declaraciones:
            if isinstance(decl, FuncionDecl):
                self.funciones[decl.nombre] = decl

        if 'main' not in self.funciones:
            raise Exception("No se encontro la funcion 'main'.")

        self.llamar_funcion('main', [])

    def llamar_funcion(self, nombre, argumentos):
        funcion = self.funciones[nombre]
        entorno_funcion = Entorno(padre=self.entorno_global)

        for (nombre_param, tipo_param), valor in zip(funcion.parametros, argumentos):
            entorno_funcion.declarar(nombre_param, valor)

        try:
            self.ejecutar_bloque(funcion.cuerpo, entorno_funcion)
        except SenalReturn as señal:
            return señal.valor
        return None

    def ejecutar_bloque(self, sentencias, entorno):
        for sentencia in sentencias:
            self.ejecutar_sentencia(sentencia, entorno)

    def ejecutar_sentencia(self, nodo, entorno):
        tipo = type(nodo).__name__
        metodo = getattr(self, f'ejec_{tipo}', None)
        if metodo is None:
            raise Exception(f"No se sabe como ejecutar el nodo: {tipo}")
        return metodo(nodo, entorno)

    def evaluar(self, nodo, entorno):
        tipo = type(nodo).__name__
        metodo = getattr(self, f'eval_{tipo}', None)
        if metodo is None:
            raise Exception(f"No se sabe como evaluar el nodo: {tipo}")
        return metodo(nodo, entorno)

    def ejec_DeclaracionVariable(self, nodo, entorno):
        if nodo.valor is not None:
            valor = self.evaluar(nodo.valor, entorno) 
        else:
            valor = self.valor_por_defecto(nodo.tipo)
        entorno.declarar(nodo.nombre, valor)    

    # VALOR_POR_DEFECTO 
    def valor_por_defecto(self, tipo):
        if tipo == 'i32':
            return 0
        if tipo == 'f64':
            return 0.0
        if tipo == 'bool':
            return False
        if tipo == 'String':
            return ""
        return None

    def ejec_Asignacion(self, nodo, entorno):
        valor_nuevo = self.evaluar(nodo.valor, entorno)
        if nodo.operador == '=':
            entorno.asignar(nodo.nombre, valor_nuevo)
        else:
            valor_actual = entorno.obtener(nodo.nombre)
            op = nodo.operador[0]  # '+=' -> '+'
            resultado = self.aplicar_operador(op, valor_actual, valor_nuevo)
            entorno.asignar(nodo.nombre, resultado)

    def ejec_LlamadaFuncion(self, nodo, entorno):
        self.evaluar(nodo, entorno)

    def ejec_If(self, nodo, entorno):
        condicion = self.evaluar(nodo.condicion, entorno)
        if condicion:
            self.ejecutar_bloque(nodo.bloque_si, Entorno(padre=entorno))
        elif nodo.bloque_sino is not None:
            self.ejecutar_bloque(nodo.bloque_sino, Entorno(padre=entorno))

    def ejec_While(self, nodo, entorno):
        while self.evaluar(nodo.condicion, entorno):
            try:
                self.ejecutar_bloque(nodo.bloque, Entorno(padre=entorno))
            except SenalBreak:
                break
            except SenalContinue:
                continue

    def ejec_Loop(self, nodo, entorno):
        while True:
            try:
                self.ejecutar_bloque(nodo.cuerpo, Entorno(padre=entorno))
            except SenalBreak as señal:
                if señal.etiqueta is None or señal.etiqueta == nodo.etiqueta:
                    break
                raise
            except SenalContinue as señal:
                if señal.etiqueta is None or señal.etiqueta == nodo.etiqueta:
                    continue
                raise

    def ejec_Return(self, nodo, entorno):
        valor = self.evaluar(nodo.valor, entorno) if nodo.valor is not None else None
        raise SenalReturn(valor)

    def ejec_Break(self, nodo, entorno):
        raise SenalBreak(nodo.etiqueta)

    def ejec_Continue(self, nodo, entorno):
        raise SenalContinue(nodo.etiqueta)

    def ejec_Match(self, nodo, entorno):
        valor = self.evaluar(nodo.expresion, entorno)
        for caso in nodo.casos:
            if caso.patron is None: 
                self.ejecutar_sentencia_o_expr(caso.cuerpo, entorno)
                return
            patron_valor = self.evaluar(caso.patron, entorno)
            if patron_valor == valor:
                self.ejecutar_sentencia_o_expr(caso.cuerpo, entorno)
                return

    def ejecutar_sentencia_o_expr(self, nodo, entorno):
        if isinstance(nodo, LlamadaFuncion):
            self.evaluar(nodo, entorno)
        else:
            self.ejecutar_sentencia(nodo, entorno)

    def eval_Literal(self, nodo, entorno):
        return nodo.valor

    def eval_Identificadores(self, nodo, entorno):
        return entorno.obtener(nodo.nombre)

    def eval_OperacionBinaria(self, nodo, entorno):
        izq = self.evaluar(nodo.izquierda, entorno)
        der = self.evaluar(nodo.derecha, entorno)
        return self.aplicar_operador(nodo.operador, izq, der)

    def eval_OperacionUnaria(self, nodo, entorno):
        valor = self.evaluar(nodo.operando, entorno)
        if nodo.operador == '!':
            return not valor
        if nodo.operador == '-':
            return -valor

    def eval_Arreglo(self, nodo, entorno):
        return [self.evaluar(e, entorno) for e in nodo.elementos]

    def eval_AccesoIndice(self, nodo, entorno):
        arreglo = self.evaluar(nodo.arreglo, entorno)
        indice = self.evaluar(nodo.indice, entorno)
        return arreglo[indice]

    def eval_LlamadaFuncion(self, nodo, entorno):
        argumentos = [self.evaluar(a, entorno) for a in nodo.argumentos]

        if nodo.nombre == 'println!':
            if len(argumentos) == 1:
                print(self.formatear_valor(argumentos[0]))
            else:
                plantilla = argumentos[0]
                resto = argumentos[1:]
                for val in resto:
                    plantilla = plantilla.replace('{}', self.formatear_valor(val), 1)
                print(plantilla)
            return None

        return self.llamar_funcion(nodo.nombre, argumentos)

    def formatear_valor(self, valor):
        if isinstance(valor, bool):
            return 'true' if valor else 'false'
        return str(valor)

    def aplicar_operador(self, operador, izq, der):
        if operador == '+': return izq + der
        if operador == '-': return izq - der
        if operador == '*': return izq * der
        if operador == '/': return izq / der
        if operador == '%': return izq % der
        if operador == '==': return izq == der
        if operador == '!=': return izq != der
        if operador == '<': return izq < der
        if operador == '>': return izq > der
        if operador == '<=': return izq <= der
        if operador == '>=': return izq >= der
        if operador == '&&': return izq and der
        if operador == '||': return izq or der
        raise Exception(f"Operador no soportado: {operador}")



# para PRUEBASS
if __name__ == '__main__':
    from lexer import lexer
    from parser import parser

    codigo = '''
    fn main() {
        let mut x: i32 = 10;
        if x > 5 {
            println!("es mayor a 5");
        }
        while x > 0 {
            println!(x);
            x -= 1;
        }
    }
    '''

    ast = parser.parse(codigo, lexer=lexer)
    interprete = Interprete()
    interprete.ejecutar_programa(ast)