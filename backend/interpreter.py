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
        self.variable[nombre] = valor

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

