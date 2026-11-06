"""
Manejo de errores (lexicos, sintacticos,semanticos) para el reporte de errores en el front.
"""

lista_errores = []

def agregar_error(tipo, descripcion, linea, columna=0):
    lista_errores.append({
        "tipo": tipo,
        "descripcion": descripcion,
        "linea": linea,
        "columna": columna,
    })

def limpiar_errores():
    lista_errores.clear()

def obtener_errores():
    return lista_errores

def encontrar_columna(texto, lexpos):
    """Calcula la columna de un token a partir de su posicion absoluta"""
    inicio_linea = texto.rfind('\n', 0, lexpos) + 1 # Busca el último salto de línea anterior
    return (lexpos - inicio_linea) + 1  #mide la distancia hasta el carácter erróneo