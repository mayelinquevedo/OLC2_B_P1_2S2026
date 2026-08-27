"""
Construye la tabla de simbolos recorriendo el AST que ya construimos.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from ast_nodes import *


def construir_tabla_simbolos(programa):
    tabla = []
    for decl in programa.declaraciones:
        if isinstance(decl, FuncionDecl):
            tabla.append({
                "nombre": decl.nombre, "categoria": "Funcion",
                "tipo": decl.tipo_retorno or "void", "ambito": "Global", "valor": "-"
            })
            _recorrer(decl.cuerpo, decl.nombre, tabla)
        elif isinstance(decl, StructDecl):
            tabla.append({
                "nombre": decl.nombre, "categoria": "Struct",
                "tipo": "-", "ambito": "Global", "valor": "-"
            })
    return tabla


def _recorrer(sentencias, ambito, tabla):
    for s in sentencias:
        if isinstance(s, DeclaracionVariable):
            tabla.append({
                "nombre": s.nombre, "categoria": "Variable",
                "tipo": s.tipo or "inferido", "ambito": ambito,
                "valor": repr(s.valor) if s.valor is not None else "-"
            })
        elif isinstance(s, If):
            _recorrer(s.bloque_si, ambito, tabla)
            if s.bloque_sino:
                _recorrer(s.bloque_sino, ambito, tabla)
        elif isinstance(s, While):
            _recorrer(s.bloque, ambito, tabla)
        elif isinstance(s, Loop):
            _recorrer(s.cuerpo, ambito, tabla)
        elif isinstance(s, Bloque):
            _recorrer(s.sentencias, ambito, tabla)