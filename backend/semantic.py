"""
recorre el AST antes de ejecutarlo, validando tipos, declaracion de variables,
alcance (scope)
solo verifica que las reglas semanticas se cumplan.
"""
from ast_nodes import *
from errors import agregar_error


class SimboloVariable:
    def __init__(self, tipo, mutable):
        self.tipo = tipo
        self.mutable = mutable


class TablaSimbolosSemantica:
    """Tabla de simbolos con soporte de scopes anidados (pila de diccionarios)"""
    def __init__(self):
        self.pila = [{}]  #cada elemento es un scope 

    def entrar_scope(self):
        self.pila.append({})

    def salir_scope(self):
        self.pila.pop()

    def declarar(self, nombre, tipo, mutable):
        self.pila[-1][nombre] = SimboloVariable(tipo, mutable)

    def existe(self, nombre):
        for scope in reversed(self.pila):
            if nombre in scope:
                return True
        return False

    def obtener(self, nombre):
        for scope in reversed(self.pila):
            if nombre in scope:
                return scope[nombre]
        return None


class AnalizadorSemantico:
    def __init__(self):
        self.tabla = TablaSimbolosSemantica()
        self.funciones = {}  # (para validar llamadas)
        self.tiene_errores = False

    def analizar(self, programa):
        # registramos todas las funciones (para permitir llamadas hacia adelante)
        for decl in programa.declaraciones:
            if isinstance(decl, FuncionDecl):
                self.funciones[decl.nombre] = decl

        for decl in programa.declaraciones:
            if isinstance(decl, FuncionDecl):
                self.revisar_funcion(decl)

        return not self.tiene_errores

    def revisar_funcion(self, funcion):
        self.tabla.entrar_scope()
        for nombre_param, tipo_param in funcion.parametros:
            self.tabla.declarar(nombre_param, tipo_param, mutable=True)
        self.revisar_bloque(funcion.cuerpo)
        self.tabla.salir_scope()

    def revisar_bloque(self, sentencias):
        for s in sentencias:
            self.revisar_sentencia(s)

    def revisar_sentencia(self, nodo):
        tipo = type(nodo).__name__
        metodo = getattr(self, f'rev_{tipo}', None)
        if metodo:
            metodo(nodo)

    def rev_DeclaracionVariable(self, nodo):
        tipo_inferido = None
        if nodo.valor is not None:
            tipo_inferido = self.inferir_tipo(nodo.valor)

        tipo_final = nodo.tipo if nodo.tipo is not None else tipo_inferido
        if nodo.tipo is not None and tipo_inferido is not None:
            if not self._tipos_compatibles(nodo.tipo, tipo_inferido):
                agregar_error(
                    "Semantico",
                    f"No es posible asignar un valor de tipo {tipo_inferido} a una variable de tipo {nodo.tipo}.",
                    nodo.linea
                )
                self.tiene_errores = True

        self.tabla.declarar(nodo.nombre, tipo_final, nodo.mutable)

    def rev_Asignacion(self, nodo):
        if not self.tabla.existe(nodo.nombre):
            agregar_error("Semantico", f"La variable '{nodo.nombre}' no ha sido declarada.", nodo.linea)

            self.tiene_errores = True
        else:
            simbolo = self.tabla.obtener(nodo.nombre)
            if not simbolo.mutable:
                agregar_error(
                    "Semantico",
                    f"No es posible modificar la variable '{nodo.nombre}' porque fue declarada como inmutable.",
                    0
                )
                self.tiene_errores = True
        self.revisar_expresion(nodo.valor)

    def rev_LlamadaFuncion(self, nodo):
        self.revisar_expresion(nodo)

    def rev_If(self, nodo):
        self.revisar_expresion(nodo.condicion)
        self.tabla.entrar_scope()
        self.revisar_bloque(nodo.bloque_si)
        self.tabla.salir_scope()
        if nodo.bloque_sino is not None:
            self.tabla.entrar_scope()
            self.revisar_bloque(nodo.bloque_sino)
            self.tabla.salir_scope()

    def rev_While(self, nodo):
        self.revisar_expresion(nodo.condicion)
        self.tabla.entrar_scope()
        self.revisar_bloque(nodo.bloque)
        self.tabla.salir_scope()

    def rev_Loop(self, nodo):
        self.tabla.entrar_scope()
        self.revisar_bloque(nodo.cuerpo)
        self.tabla.salir_scope()

    def rev_Bloque(self, nodo):
        self.tabla.entrar_scope()
        self.revisar_bloque(nodo.sentencias)
        self.tabla.salir_scope()

    def rev_Return(self, nodo):
        if nodo.valor is not None:
            self.revisar_expresion(nodo.valor)

    def rev_Match(self, nodo):
        self.revisar_expresion(nodo.expresion)

    def revisar_expresion(self, nodo):
        if isinstance(nodo, Identificadores):
            if not self.tabla.existe(nodo.nombre):
                agregar_error("Semantico", f"La variable '{nodo.nombre}' no ha sido declarada.", nodo.linea)
                self.tiene_errores = True
        elif isinstance(nodo, OperacionBinaria):
            self.revisar_expresion(nodo.izquierda)
            self.revisar_expresion(nodo.derecha)
        elif isinstance(nodo, OperacionUnaria):
            self.revisar_expresion(nodo.operando)
        elif isinstance(nodo, LlamadaFuncion):
            for arg in nodo.argumentos:
                self.revisar_expresion(arg)

            es_embebida = nodo.nombre in (
                'println!', 'len', 'contains', 'replace', 'to_uppercase',
                'to_lowercase', 'split', 'reverse', 'typeof', 'random'
            )
            if not es_embebida:
                if nodo.nombre not in self.funciones:
                    agregar_error("Semantico", f"La funcion '{nodo.nombre}' no ha sido declarada.", 0)
                    self.tiene_errores = True
                else:
                    esperados = len(self.funciones[nodo.nombre].parametros)
                    recibidos = len(nodo.argumentos)
                    if esperados != recibidos:
                        agregar_error(
                            "Semantico",
                            f"La funcion '{nodo.nombre}' esperaba {esperados} argumentos, pero recibio {recibidos}.",
                            0
                        )
                        self.tiene_errores = True
        elif isinstance(nodo, Arreglo):
            for e in nodo.elementos:
                self.revisar_expresion(e)
        elif isinstance(nodo, AccesoIndice):
            self.revisar_expresion(nodo.arreglo)

    def inferir_tipo(self, nodo):
        if isinstance(nodo, Literal):
            return nodo.tipo
        if isinstance(nodo, Identificadores):
            simbolo = self.tabla.obtener(nodo.nombre)
            return simbolo.tipo if simbolo else None
        if isinstance(nodo, OperacionBinaria):
            return self.inferir_tipo(nodo.izquierda)  
        if isinstance(nodo, Arreglo):
            return None
        return None

    def _tipos_compatibles(self, tipo_a, tipo_b):
        if tipo_a == tipo_b:
            return True
        numericos = {'i32', 'f64'}
        if tipo_a in numericos and tipo_b in numericos:
            return True
        return False