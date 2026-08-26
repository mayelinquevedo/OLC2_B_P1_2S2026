#API REST
from flask import Flask, request, jsonify #flask, request (datos de la peticion) y jsonify (respuestas JSON)
from flask_cors import CORS #CORS, para permitir peticiones desde el front
import io   #io, para capturar la salida de los print() en memoria
import sys #sys, para poder redirigir temporalmente sys.stdout


from lexer import lexer #lexer ya construido
from parser import parser #parser ya construido
from interpreter import Interprete #clase Interprete (aun sin instanciar)


app = Flask(__name__)
CORS(app)


# /ejecutar, solo  peticiones POST
@app.route('/ejecutar', methods=['POST'])
def ejecutar():
    datos = request.get_json() # JSON que mando el front
    codigo = datos.get('codigo', '')
    lexer.lineno = 1   
    salida_consola = io.StringIO()
    salida_original = sys.stdout

    try:
        sys.stdout = salida_consola
        ast = parser.parse(codigo, lexer=lexer)   #pasa el codigo por el parser
        if ast is None:    #si el parser no logro construir el arbol, hubo un error de sintaxis
            return jsonify({
                'exito': False,
                'salida': '',
                'error': 'Error de sintaxis en el codigo fuente.'
            })

        #creamos un interprete nuevo (uno por cada peticion) y ejecutamos
        interprete = Interprete()
        interprete.ejecutar_programa(ast)

        #recuperamos todo el texto que se imprimio durante la ejecucion
        resultado = salida_consola.getvalue()
        return jsonify({
            'exito': True,
            'salida': resultado,
            'error': None
        })

    #si algo truena durante la ejecucion
    except Exception as e:
        #recuperamos lo que si alcanzo a imprimirse antes del error
        resultado_parcial = salida_consola.getvalue()
        return jsonify({
            'exito': False,
            'salida': resultado_parcial,
            'error': str(e)
        })

    #esto ejecuta siempre, haya error o no
    finally:
        sys.stdout = salida_original


if __name__ == '__main__':
    app.run(debug=True, port=8000)