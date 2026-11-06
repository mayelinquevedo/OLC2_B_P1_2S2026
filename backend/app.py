#API REST
from flask import Flask, request, jsonify #flask, request (datos de la peticion) y jsonify (respuestas JSON)
from flask_cors import CORS #CORS, para permitir peticiones desde el front
import io  #io, para capturar la salida de los print() en memoria
import sys #sys, para poder redirigir temporalmente sys.stdout
import base64
from semantic import AnalizadorSemantico
from lexer import lexer     #lexer ya construido.
from parser import parser #parser ya construido
from interpreter import Interprete #clase Interprete (aun sin instanciar)
from errors import limpiar_errores, obtener_errores
from reports.symbol_table import construir_tabla_simbolos
from reports.ast_tree import generar_ast
import os

app = Flask(__name__)
CORS(app)

def obtener_tokens(codigo):
    lex_temporal = lexer.clone()
    lex_temporal.lineno = 1
    from errors import lista_errores
    respaldo = list(lista_errores)

    lex_temporal.input(codigo)
    tokens_lista = []
    while True:
        tok = lex_temporal.token()
        if not tok:
            break
        tokens_lista.append({"lexema": str(tok.value), "token": tok.type, "linea": tok.lineno})

    lista_errores.clear()
    lista_errores.extend(respaldo)

    return tokens_lista

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/reporte_simbolos', methods=['POST'])
def reporte_simbolos_html():
    datos = request.get_json()
    codigo = datos.get('codigo', '')

    lexer.lineno = 1
    limpiar_errores()
    ast = parser.parse(codigo, lexer=lexer)

    if ast is None:
        return "No se pudo generar el reporte: hay errores de sintaxis en el codigo.", 400

    tabla = construir_tabla_simbolos(ast)

    filas_html = "".join(
        f"<tr><td>{s['nombre']}</td><td>{s['categoria']}</td><td>{s['tipo']}</td>"
        f"<td>{s['ambito']}</td><td>{s['valor']}</td></tr>"
        for s in tabla
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Tabla de Simbolos - OxigenScript</title>
<style>
    body {{ font-family: sans-serif; padding: 20px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f3f4f6; }}
</style>
</head>
<body>
<h2>Tabla de Simbolos - OxigenScript</h2>
<table>
<tr><th>Nombre</th><th>Categoria</th><th>Tipo</th><th>Ambito</th><th>Valor</th></tr>
{filas_html}
</table>
</body>
</html>"""

    return html, 200, {'Content-Type': 'text/html'}


@app.route('/ejecutar', methods=['POST'])
def ejecutar():
    datos = request.get_json()
    codigo = datos.get('codigo', '')

    limpiar_errores()
    lexer.lineno = 1

    salida_consola = io.StringIO()
    salida_original = sys.stdout

    tokens_reporte = obtener_tokens(codigo)
    tabla_simbolos = []
    ast_base64 = None

    try:
        sys.stdout = salida_consola
        ast = parser.parse(codigo, lexer=lexer)

        if ast is None:
            sys.stdout = salida_original
            return jsonify({
                'exito': False,
                'salida': '',
                'error': 'Error de sintaxis en el codigo fuente.',
                'errores': obtener_errores(),
                'tokens': tokens_reporte,
                'tabla_simbolos': [],
                'ast_imagen': None,
            })

 # Generamos el AST fuera de la captura de stdout, con ruta absoluta
        try:
            ruta_ast = os.path.join(BASE_DIR, "reports", "ast_actual")
            generar_ast(ast, ruta_ast)
            with open(ruta_ast + ".png", "rb") as f:
                ast_base64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"No se pudo generar AST: {e}")
            ast_base64 = None

        

        tabla_simbolos = construir_tabla_simbolos(ast)
        analizador = AnalizadorSemantico()
        analizador.analizar(ast)
        interprete = Interprete()
        interprete.ejecutar_programa(ast)

        resultado = salida_consola.getvalue()
        sys.stdout = salida_original   # restauramos ANTES de generar el AST

       

        return jsonify({
            'exito': True,
            'salida': resultado,
            'error': None,
            'errores': obtener_errores(),
            'tokens': tokens_reporte,
            'tabla_simbolos': tabla_simbolos,
            'ast_imagen': ast_base64,
        })

    except Exception as e:
        resultado_parcial = salida_consola.getvalue()
        return jsonify({
            'exito': False,
            'salida': resultado_parcial,
            'error': str(e),
            'errores': obtener_errores(),
            'tokens': tokens_reporte,
            'tabla_simbolos': tabla_simbolos,
            'ast_imagen': ast_base64,
        })

    finally:
        sys.stdout = salida_original

if __name__ == '__main__':
    app.run(debug=True, port=8000)