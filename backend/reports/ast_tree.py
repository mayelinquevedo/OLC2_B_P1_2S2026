"""
aquí voy a Generar una imagen con ayuda de graphviz de cualquier
arbol construido con las clases de ast_nodes.py
"""
from graphviz import Digraph
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from ast_nodes import Nodo


def _es_nodo(obj):
    return isinstance(obj, Nodo)


def _es_lista_de_nodos(obj):
    return isinstance(obj, list) and (len(obj) == 0 or any(_es_nodo(e) for e in obj))


def generar_ast(raiz, nombre_archivo="ast_output"):
    grafo = Digraph(comment="AST OxigenScript")
    grafo.attr("node", shape="box", style="filled", fillcolor="#EAF2FB",
               fontname="Helvetica", fontsize="10")
    grafo.attr("edge", fontname="Helvetica", fontsize="9")

    contador = {"n": 0}

    def nuevo_id():
        contador["n"] += 1
        return f"nodo{contador['n']}"

    def visitar(nodo):
        mi_id = nuevo_id()
        etiqueta = type(nodo).__name__

        atributos_simples = []
        hijos = []

        for clave, valor in vars(nodo).items():
            if _es_nodo(valor):
                id_hijo = visitar(valor)
                hijos.append((clave, id_hijo))
            elif _es_lista_de_nodos(valor):
                for i, elem in enumerate(valor):
                    if _es_nodo(elem):
                        id_hijo = visitar(elem)
                        hijos.append((f"{clave}[{i}]", id_hijo))
                    else:
                        atributos_simples.append(f"{clave}[{i}]={elem!r}")
            elif valor is None:
                continue
            else:
                atributos_simples.append(f"{clave}={valor!r}")

        texto = etiqueta
        if atributos_simples:
            texto += "\\n" + "\\n".join(atributos_simples)

        grafo.node(mi_id, texto)

        for etiqueta_borde, id_hijo in hijos:
            grafo.edge(mi_id, id_hijo, label=etiqueta_borde)

        return mi_id

    visitar(raiz)
    grafo.render(nombre_archivo, format="png", cleanup=True)
    print(f"AST generado en: {nombre_archivo}.png")


if __name__ == "__main__":
    from ast_nodes import (Literal, Identificadores, DeclaracionVariable, LlamadaFuncion, FuncionDecl, Programa)

    decl_x = DeclaracionVariable(nombre="x", tipo="i32", valor=Literal(10, "i32"), mutable=False)
    llamada_print = LlamadaFuncion(nombre="println!", argumentos=[Identificadores("x")])
    funcion_main = FuncionDecl(nombre="main", parametros=[], tipo_retorno=None, cuerpo=[decl_x, llamada_print])
    programa = Programa(declaraciones=[funcion_main])

    generar_ast(programa, "backend/reports/prueba1del_enunciado")