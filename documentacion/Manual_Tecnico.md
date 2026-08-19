# Documentación Técnica -  OxigenScript

# Universidad de San Carlos de Guatemala 
# Facultad de Ingeniería - Ingeniería en Ciencias y Sistemas
# Proyecto 1, ORGANIZACION DE LENGUAJES Y COMPILADORES 2 SECCION B
# Mayelin Lucía Quevedo Camey - carnet: 202307771
# Segundo Semestre 2026

## 1. Introducción
En el presente documento estaremos registrando, de forma detallada, el proceso de configuración del entorno de desarrollo y la construcción del analizador léxico (**lexer.py**) para el proyecto OxigenScript, correspondiente al proyecto 1 del curso de organizacion de lenguaje y compiladores 2.
El objetivo es dejar constancia de las decisiones tomadas, los problemas encontrados durante la implementación y la forma en que fueron resueltos.

El proyecto consiste en el desarrollo de un interprete para OxigenScript, un lenguaje con sintaxis inspirada en Rust.
El intérprete lo construimos con Python utilizando la herramienta PLY (**Python Lex-Yacc**), este mismo para las fases de análisis léxico y sintáctico.
La arquitectura que se va utilizar será cliente/servidor con una API REST (**Flask**) como capa de lógica y un cliente web (**React**) como la capa de presentación. 

## 2.Configuración de todo el entorno de desarrollo
El desarrollo se llevará a cabo en linux mint, utilizando visual studio code como el editor principal.
A continuación estaré detallando el proceso de intalación y configuración de cada herramienta que se utilizó.

### Actualización del sistema:
Desde la terminal del sistema:
- *sudo apt update && sudo apt upgrade -y*

### Instalación de Git
- *sudo apt install git -y*. 
- *git config --global user.name "Mayelin"*
- *git config --global user.email "correo@ejemplo.com"*

### Instalacion de Python, Pip y Venv
Linux Mint incluye Python 3 de forma predeterminada. 
Sin embargo, se requirió instalar el paquete de creación de entornos virtuales específico para la versión de Python instalada (3.12), ya que este no viene incluido.

### Creacion del entorno virtual de Backend
El uso de un entorno virtual (**venv**),
es una buena práctica, lo estuvimos utilizando para poder aislar las dependencias de Python, es decir, solo las que va utilizar el proyecto.
separarlas de las dependencias del sistema operativo, evitando así cualquier tipo de conflicto, ya sea de versiones.
mediante el archivo requirements.txt, el proyecto es reproducible en cualqueir máquina.
- *cd backend*
- *python3 -m venv venv*
- *source venv/bin/activate*

### Instalación de librerías de Python
1. *pip install flask flask-cors ply graphviz*
2. *pip freeze > requirements.txt*

 - **Flask**: Flask es un framework que nos ayudará a exponer la API REST este recibirá el código fuente y devolverá tokens, AST, errores y los resultados de la ejecución.

 - **Flask-CORS**: Permite que el frontend (**Reat**) pueda comunicarse con la API sin ser bloqueado por politicas CORS del navegador.

 - **PLY**: Herramienta Python Lex-Yacc, esta fue utilizada para construir el analizador léxico (lex) y sintáctico (yacc) del lenguaje OxigenScript.

 - **GRAPHVIZ** : Librería cliente de Python para generar, desde código, los archivos en formato DOT que se usarán para el reporte gráfico del AST.

## 3. Estructura del Proyecto
Se decidió separar el proyecto en dos grandes componentes, **backend y frontend**. 

## Contenido del archivo .gitignore
Se documentó cada línea del archivo .gitignore para dejar constancia del motivo de exclusión de cada carpeta/archivo del control de versiones:

- **venv/**: Este archivo contiene todas las librerías instaladas de Python; pesa mucho y se recrea con pip install -r requirements.txt, no es necesario subirlo.

- **__pycache__/ y * .pyc**: Archivos de bytecode que Python genera automáticamente; no aportan valor en el repositorio y se regeneran solos.

- **node_modules/**: Carpeta de dependencias de Node/React; se recrea automáticamente con npm install a partir de package.json.

- **build/**:Carpetas de compilación de producción (por ejemplo, resultado de npm run build); se regeneran a partir del código fuente.

- **.env**Archivo donde se guardarían variables de entorno o credenciales sensibles; nunca debe subirse a un repositorio por motivos de seguridad.


## Estrategia de control de versiones (Git)
Se adoptó un flujo de trabajo basado en tres tipos de rama:

- **main**:Contiene únicamente código estable, íntegro y en condiciones de ser evaluado.

- **develop**:Rama de integración, donde se combina el trabajo de las distintas ramas feature ya terminadas y probadas.

- **feature/***: Una rama por cada bloque funcional grande del proyecto (por ejemplo, feature/lexer_inicial), donde se desarrolla y prueba cada pieza antes de integrarla a develop.

Para práctica personal, llegué a la conclusión que la granularidad correcta para crear una nueva rama feature es a nivel de bloque funcional completo (por ejemplo, todo el analizador léxico).



