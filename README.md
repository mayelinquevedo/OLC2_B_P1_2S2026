# OxigenScript

Intérprete web para **OxigenScript**, un lenguaje académico con sintaxis inspirada en Rust, desarrollado como Proyecto 1 para el curso **Organización de Lenguajes y Compiladores 2** — Universidad de San Carlos de Guatemala, Facultad de Ingeniería.

Permite escribir, ejecutar y depurar programas de OxigenScript desde el navegador, con reportes de análisis léxico, sintáctico, semántico, tabla de símbolos y árbol de sintaxis abstracta (AST)

---

https://meet.google.com/vip-uqbc-zpd

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Lenguaje de implementación | Python 3 |
| Análisis léxico y sintáctico | PLY (Python Lex-Yacc) |
| API REST | Flask + Flask-CORS |
| Interfaz web | React |
| Editor de código | Monaco Editor |
| Reporte visual del AST | Graphviz |

---

## Arquitectura

```
Cliente (React + Monaco)  --HTTP-->  API REST (Flask)  -->  Interprete
                                                              ├── lexer.py     (analisis lexico)
                                                              ├── parser.py    (analisis sintactico + AST)
                                                              ├── semantic.py  (analisis semantico)
                                                              └── interpreter.py (ejecucion)
```

---

## Estructura del repositorio

```
OLC2_B_P1_2S2026/
├── backend/
│   ├── lexer.py             # Analizador lexico
│   ├── ast_nodes.py          # Clases de nodos del AST
│   ├── parser.py             # Analizador sintactico
│   ├── semantic.py            # Analizador semantico
│   ├── interpreter.py         # Interprete (ejecucion)
│   ├── errors.py               # Manejo centralizado de errores
│   ├── app.py                   # API REST (Flask)
│   ├── requirements.txt
│   └── reports/
│       ├── ast_tree.py           # Generador de imagen del AST
│       └── symbol_table.py        # Constructor de tabla de simbolos
├── frontend/                  # Aplicacion React
├── documentacion/
│   ├── Manual_Tecnico.md        # Documentacion tecnica
│   └── Manual_Usuario.md         # Manual de usuario (con capturas)
└── README.md
```

---

## Instalación y ejecución rápida

Requisitos: Python 3.10+, Node.js 18+, Graphviz (paquete de sistema).

```bash
# Clonar el repositorio
git clone https://github.com/mayelinquevedo/OLC2_B_P1_2S2026.git
cd OLC2_B_P1_2S2026

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py          # corre en http://127.0.0.1:8000

# Frontend (en otra terminal)
cd frontend
npm install
npm start                # abre http://localhost:3000
```

Instrucciones detalladas, con capturas de pantalla, en [`documentacion/Manual_Usuario.md`](documentacion/Manual_Usuario.md).

---

## Características del lenguaje soportadas

- Variables (`let` / `let mut`), tipado estático con inferencia, valores por defecto
- Operadores aritméticos, relacionales, lógicos y de asignación (con promoción de tipos básica)
- Control de flujo: `if` / `else if` / `else`, `while`, `loop` (con etiquetas), `match`
- Sentencias de transferencia: `return`, `break`, `continue` (con etiquetas)
- Arreglos de tamaño fijo y acceso por índice
- Strings con métodos embebidos (`len`, `contains`, `replace`, `to_uppercase`, `to_lowercase`, `split`)
- Structs, incluyendo anidados
- Funciones con parámetros y tipo de retorno
- Funciones embebidas: `println!`, `typeof`, `random`, `reverse`
- Reporte de errores léxicos, sintácticos y semánticos, con **recuperación de errores** (el análisis continúa tras encontrar un error)
- Reportes de tabla de símbolos, tokens y AST visual (Graphviz)

Limitaciones conocidas: slices de arreglos (`&arr[1..4]`) y raw strings (`r"..."`) no están implementados — ver detalle en la documentación técnica.

---

## Documentación

-  [Documentación técnica](documentacion/Manual_Tecnico.md) — gramática formal, arquitectura, decisiones de diseño y desafíos técnicos
-  [Manual de usuario](documentacion/Manual_Usuario.md) — guía de instalación y uso de la interfaz, con capturas de pantalla

---

## Autora

Mayelin Quevedo — 202307771
