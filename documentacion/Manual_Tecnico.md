# Documentación Técnica — Proyecto OxigenScript

- **Curso:** Organización de Lenguajes y Compiladores 2
- **Universidad:** Universidad de San Carlos de Guatemala
- **Facultad:** Ingeniería — Ingeniería en Ciencias y Sistemas
- **Estudiante:** Mayelin Lucía Quevedo Camey  ,  carnet: 202307771

---

## 1. Introducción


Este documento describe la implementación técnica del intérprete de **OxigenScript**, un lenguaje académico con sintaxis inspirada en Rust, desarrollado como Proyecto 1 del curso Organización de Lenguajes y Compiladores 2. Se detalla la arquitectura del sistema, la gramática formal implementada, los métodos utilizados para procesar y ejecutar el código fuente, y las decisiones de diseño tomadas durante el desarrollo, junto con los desafíos técnicos encontrados y su solución.

El intérprete cubre las tres fases clásicas de procesamiento de lenguajes (análisis léxico, análisis sintáctico y ejecución), a las que se agregó una fase de **análisis semántico** independiente, dado que el enunciado del proyecto la exige como parte del alcance obligatorio aunque no aparezca representada como una caja separada en el diagrama de arquitectura general.

---

## 2. Arquitectura del proyecto

El proyecto sigue una arquitectura monolítica de tipo cliente/servidor, compuesta por tres componentes principales:

- **Backend (Python + Flask + PLY):** aloja el intérprete completo — análisis léxico, sintáctico, semántico y ejecución — expuesto mediante una API REST con un único endpoint principal (`POST /ejecutar`).
- **Frontend (React + Monaco Editor):** interfaz web donde el usuario escribe y ejecuta código, y visualiza los reportes generados (errores, tabla de símbolos, tokens y AST).
- **Definición del lenguaje (PLY):** la gramática formal de OxigenScript, implementada mediante las herramientas `lex` y `yacc` de la librería PLY (Python Lex-Yacc).

### 2.1. Estructura de archivos del backend

```
backend/
├── lexer.py            # Analizador lexico
├── ast_nodes.py         # Clases de nodos del AST
├── parser.py            # Analizador sintactico (gramatica)
├── semantic.py           # Analizador semantico
├── interpreter.py        # Ejecucion del AST
├── errors.py             # Manejo centralizado de errores
├── app.py                 # API REST (Flask)
└── reports/
    ├── ast_tree.py         # Generador de imagen del AST (Graphviz)
    └── symbol_table.py      # Constructor de la tabla de simbolos
```

### 2.2. Flujo de una petición

1. El usuario escribe código en el editor Monaco y presiona "Ejecutar".
2. El frontend envía el código como JSON al endpoint `POST /ejecutar`.
3. El backend tokeniza el código (lexer), construye el AST (parser), lo valida (semántico), y si no hay errores críticos, lo ejecuta (intérprete).
4. La API devuelve un JSON con: la salida de consola, la lista de errores encontrados, la lista de tokens, la tabla de símbolos, y una imagen del AST codificada en base64.
5. El frontend distribuye esta información en la consola de salida y en las pestañas de reportes correspondientes.

---

## 3. Análisis léxico

### 3.1. Herramienta utilizada

Se utilizó el módulo `lex` de la librería **PLY (Python Lex-Yacc)** para construir el analizador léxico. PLY permite definir los patrones de reconocimiento mediante expresiones regulares asociadas a nombres de token, y genera automáticamente el motor de escaneo.

### 3.2. Categorías de tokens reconocidos

| Categoría | Ejemplos |
|---|---|
| Palabras reservadas | `let`, `mut`, `fn`, `if`, `else`, `while`, `loop`, `match`, `struct`, `return`, `break`, `continue`, `true`, `false` |
| Tipos | `i32`, `f64`, `bool`, `char`, `String` |
| Identificadores | Nombres de variables, funciones y structs definidos por el usuario |
| Literales | Números enteros, números decimales, cadenas de texto, caracteres |
| Operadores aritméticos | `+`, `-`, `*`, `/`, `%` |
| Operadores relacionales | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| Operadores lógicos | `&&`, `\|\|`, `!` |
| Operadores de asignación | `=`, `+=`, `-=`, `*=`, `/=`, `%=` |
| Símbolos y delimitadores | `{ } ( ) [ ] : ; , .` |
| Especiales | `->` (retorno de función), `=>` (match), `'etiqueta:` (loops etiquetados) |
| Comentarios | `// línea` y `/* bloque */` (ambos se descartan, no generan token) |

### 3.3. Decisiones de diseño

**Distinción entre identificadores y palabras reservadas.** En lugar de escribir una regla de token independiente para cada una de las diecinueve palabras reservadas del lenguaje, se optó por reconocer cualquier secuencia de letras/dígitos/guion bajo como un identificador genérico, y luego comparar el texto capturado contra un diccionario de palabras reservadas (`reservadas.get(valor, 'IDENTIFICADOR')`). Si la palabra coincide con una clave del diccionario, se reclasifica al tipo de token correspondiente; en caso contrario, se conserva como `IDENTIFICADOR`. Esta estrategia, además de reducir la cantidad de código, resuelve de forma natural el requisito de que el lenguaje sea *case sensitive* (sección 3.2.1 del enunciado): como la comparación de cadenas en Python distingue mayúsculas de minúsculas, una palabra como `Let` (con mayúscula) no coincide con la clave `let` del diccionario y se trata como un identificador común.

**Orden de las reglas y operadores compuestos.** PLY evalúa las reglas de tipo función en el orden textual en que aparecen en el archivo. Esto resultó crítico para distinguir operadores compuestos de sus contrapartes simples: si `t_IGUAL` (`=`) se hubiera evaluado antes que la regla de `==`, el lexer habría reconocido dos tokens `IGUAL` consecutivos en lugar de un único `IGUAL_IGUAL`. La solución fue declarar todos los operadores compuestos (`==`, `!=`, `>=`, `<=`, `&&`, `\|\|`, `+=`, `-=`, `*=`, `/=`, `%=`, `->`, `=>`, `..`) como reglas de tipo función, ubicadas *antes* que las reglas simples equivalentes.

**Conflicto entre literales de carácter y etiquetas de loop.** El lenguaje utiliza comilla simple tanto para literales de carácter (`'a'`) como para etiquetas de ciclos (`'outer:`). Ambos patrones comienzan igual, por lo que el orden de las reglas determina cuál se reconoce primero. Se resolvió colocando la regla de `CHAR` (que exige comilla de cierre inmediata) antes que la regla de `ETIQUETA` (que no la exige): así, `'x'` se reconoce como `CHAR` porque cumple el patrón más estricto, mientras que `'outer` (sin cierre cercano) falla esa primera prueba y cae en la regla de `ETIQUETA`.

**Comentarios de bloque sin cerrar.** Se implementaron dos reglas relacionadas: `t_COMENTARIO_BLOQUE`, que reconoce un comentario que sí cierra correctamente (usando un cuantificador no codicioso `*?` para detenerse en el *primer* `*/` encontrado, evitando que dos comentarios consecutivos se fusionen en uno solo), y `t_COMENTARIO_BLOQUE_SIN_CERRAR`, que se activa únicamente cuando la primera regla no logra encontrar un cierre, consumiendo el resto del archivo y reportando el error léxico específico exigido por la sección 3.2.2 del enunciado.

**Resiliencia ante errores léxicos.** Conforme a la sección 3.4.1 del enunciado, la función `t_error` no detiene el análisis: reporta el carácter no reconocido junto con su línea y columna mediante `agregar_error(...)`, y utiliza `t.lexer.skip(1)` para saltar únicamente el carácter problemático, permitiendo que el resto del archivo se siga tokenizando con normalidad.

---

## 4. Análisis sintáctico

### 4.1. Herramienta utilizada

Se utilizó el módulo `yacc` de PLY para construir el analizador sintáctico, definiendo la gramática mediante funciones `p_regla(p)`, donde el docstring de cada función especifica la producción gramatical y el cuerpo construye el nodo correspondiente del AST.

### 4.2. Gramática formal (resumen de producciones principales)

```
programa        : lista_declaraciones
declaracion_top : funcion
                | STRUCT IDENTIFICADOR '{' lista_campos '}'

funcion         : FN IDENTIFICADOR '(' lista_parametros ')' bloque
                | FN IDENTIFICADOR '(' lista_parametros ')' '->' tipo bloque

bloque          : '{' lista_sentencias '}'

sentencia       : LET IDENTIFICADOR ':' tipo '=' expresion ';'
                | LET MUT IDENTIFICADOR ':' tipo '=' expresion ';'
                | LET IDENTIFICADOR '=' expresion ';'
                | LET IDENTIFICADOR ':' tipo ';'
                | IDENTIFICADOR '=' expresion ';'
                | IDENTIFICADOR ('+=' | '-=' | '*=' | '/=' | '%=') expresion ';'
                | IF expresion bloque
                | IF expresion bloque ELSE bloque
                | IF expresion bloque ELSE sentencia
                | WHILE expresion bloque
                | LOOP bloque
                | ETIQUETA ':' LOOP bloque
                | RETURN expresion ';' | RETURN ';'
                | BREAK ';' | BREAK ETIQUETA ';'
                | CONTINUE ';' | CONTINUE ETIQUETA ';'
                | MATCH expresion '{' lista_casos '}'
                | llamada_funcion ';'
                | bloque
                | error ';'                      -- recuperacion de errores

expresion       : expresion ('+'|'-'|'*'|'/'|'%') expresion
                | expresion ('=='|'!='|'<'|'>'|'<='|'>=') expresion
                | expresion ('&&'|'||') expresion
                | '!' expresion | '-' expresion
                | '(' expresion ')'
                | IDENTIFICADOR
                | NUMERO_ENTERO | NUMERO_DECIMAL | STRING | CHAR | TRUE | FALSE
                | '[' lista_argumentos ']'
                | expresion '[' expresion ']'
                | expresion '.' IDENTIFICADOR '(' lista_argumentos ')'
                | expresion '.' IDENTIFICADOR
                | llamada_funcion

tipo            : TIPO_I32 | TIPO_F64 | TIPO_BOOL | TIPO_CHAR | TIPO_STRING
                | IDENTIFICADOR                    -- tipo definido por struct
                | '[' tipo ';' NUMERO_ENTERO ']'
```

### 4.3. Decisiones de diseño

**Precedencia de operadores.** Se declaró una tabla `precedence` que resuelve ambigüedades aritméticas y lógicas, ordenada de menor a mayor prioridad: `||`, `&&`, igualdad/desigualdad, relacionales, suma/resta, multiplicación/división/módulo, y negación unaria. Adicionalmente, se agregó una precedencia alta para el operador `.` (acceso a método o campo), ya que sin ella una expresión como `i < numeros.len()` se agrupaba incorrectamente como `len(i < numeros)` en lugar de `i < len(numeros)`.

**`println!` y el operador `!`.** Como el lexer tokeniza `println!` como dos tokens independientes (`IDENTIFICADOR('println')` seguido de `NOT`), se definió una regla específica `llamada_funcion : IDENTIFICADOR NOT '(' lista_argumentos ')'` que reconstruye el nombre completo (`p[1] + '!'`) al construir el nodo `LlamadaFuncion`.

**`String::from(...)`.** Se tradujo directamente a un `Literal` de tipo `String`, extrayendo el argumento recibido, sin crear un nodo especial adicional, ya que semánticamente equivale a un literal de texto una vez evaluado.

**Structs anidados y tipos personalizados.** Inicialmente, la regla `campo : IDENTIFICADOR ':' tipo` solo aceptaba los cinco tipos primitivos como tipo de un campo. Al probar `struct Rectangle { position: Point }`, se detectó que un campo puede tener como tipo el nombre de otro struct definido por el usuario; la solución fue agregar `IDENTIFICADOR` como alternativa válida de la producción `tipo`. De forma similar, la instanciación de un struct (`valor_campo`) se amplió para aceptar como valor de un campo tanto una expresión simple como otra instanciación de struct completa (`IDENTIFICADOR '{' lista_valores '}'`), permitiendo construir jerarquías de structs anidados.

**Comas finales (trailing commas).** Siguiendo la convención de Rust, se permite una coma sobrante después del último elemento de una lista de campos o valores de struct. Esto se resolvió agregando una producción adicional `lista_campos : lista_campos ','` (sin un campo después de la coma), evitando que el parser fallara al encontrar el `}` de cierre inmediatamente después de una coma.

**Recuperación de errores sintácticos.** Se utilizó el token especial `error` de PLY para definir la producción `sentencia : error ';'`. Cuando el parser encuentra una secuencia de tokens que no calza con ninguna sentencia válida, pero eventualmente encuentra un `;`, esta regla permite descartar los tokens problemáticos, reportar el error mediante `agregar_error(...)`, y continuar el análisis del resto del programa desde el punto seguro siguiente, en lugar de abortar por completo. Las listas de sentencias filtran los resultados `None` producidos por esta regla de recuperación antes de construir el AST final.

---

## 5. Árbol de Sintaxis Abstracta (AST)

### 5.1. Diseño de las clases de nodos

Siguiendo lo solicitado en la sección 3.4.3 del enunciado, se diseñaron manualmente las clases de nodos del AST (`ast_nodes.py`), ya que PLY no genera esta estructura de forma automática. Se utilizaron clases estándar de Python (con `__init__` y `__repr__`), en lugar de `dataclasses`, para tener control explícito paso a paso sobre la construcción de cada nodo durante el desarrollo.

Todas las clases heredan de una clase base común `Nodo`, la cual además centraliza el atributo `linea` (número de línea de origen en el código fuente), utilizado posteriormente por el analizador semántico para reportar errores con ubicación precisa.

Los nodos se dividen en dos categorías:

- **Nodos hoja**, que no contienen otros nodos: `Literal`, `Identificadores`.
- **Nodos compuestos**, que contienen uno o más nodos hijos (u otras estructuras, como listas de nodos): `DeclaracionVariable`, `OperacionBinaria`, `OperacionUnaria`, `If`, `While`, `Loop`, `Match`, `CasoMatch`, `FuncionDecl`, `LlamadaFuncion`, `Asignacion`, `Return`, `Break`, `Continue`, `Arreglo`, `AccesoIndice`, `StructDecl`, `StructInit`, `Bloque`, `Programa`.

### 5.2. Generación del reporte visual (Graphviz)

Para el reporte de AST exigido en la sección 3.4.3, se implementó una función genérica (`generar_ast` en `reports/ast_tree.py`) capaz de dibujar **cualquier** nodo del AST sin necesidad de código específico por cada clase. La función utiliza la introspección de Python (`vars(nodo)`) para inspeccionar automáticamente los atributos de cualquier objeto: si un atributo es a su vez una instancia de `Nodo`, se dibuja como un rectángulo conectado mediante una flecha etiquetada con el nombre del atributo; si es una lista que contiene nodos, se recorre generando una flecha por cada elemento; y si es un valor simple (número, cadena, booleano), se agrega como texto dentro del mismo rectángulo del nodo padre. Este enfoque evitó tener que escribir una función de dibujo distinta por cada uno de los más de veinte tipos de nodo del lenguaje, y permite que cualquier nodo nuevo que se agregue a `ast_nodes.py` sea automáticamente compatible con el visualizador, sin modificaciones adicionales.

---

## 6. Análisis semántico

### 6.1. Justificación de su implementación como módulo independiente

Si bien el diagrama de arquitectura de la sección 3.1.1 del enunciado únicamente menciona tres fases (léxica, sintáctica y de ejecución), la sección 3.5 (alcance obligatorio) exige explícitamente "análisis semántico: validación de tipos, declaración y alcance (scope) de identificadores, manejo de entornos", y la sección 3.4.1 ejemplifica varios tipos de error con la etiqueta `[Error Semántico]`. Por ello se decidió implementar esta validación en un módulo separado (`semantic.py`), que recorre el AST **antes** de la ejecución real, sin producir ningún efecto observable (no imprime, no evalúa ciclos), limitándose a verificar reglas y acumular errores.

### 6.2. Validaciones implementadas

- **Declaración de variables antes de su uso**, con soporte de scopes anidados mediante una pila de diccionarios (`TablaSimbolosSemantica`), que permite que un bloque interno acceda a variables declaradas en un bloque externo, respetando el principio de scope léxico.
- **Modificación de variables inmutables**: se registra si cada variable fue declarada con `mut`, y se reporta un error si se intenta reasignar una variable que no lo permite.
- **Tipos incompatibles en declaración de variables**: se infiere el tipo del valor asignado y se compara contra el tipo declarado explícitamente, permitiendo la promoción numérica básica entre `i32` y `f64`.
- **Funciones no declaradas** y **número incorrecto de argumentos** en una llamada, exceptuando las funciones embebidas del lenguaje (`println!`, `len`, `contains`, `replace`, `to_uppercase`, `to_lowercase`, `split`, `reverse`, `typeof`, `random`), que se excluyen de esta validación por no estar registradas como declaraciones de usuario.

### 6.3. Limitación conocida

El análisis semántico solo se ejecuta si el AST se construyó exitosamente; si existe un error sintáctico no recuperable en el punto de fallo, las sentencias posteriores a ese punto no llegan a validarse semánticamente en esa misma pasada. Asimismo, el analizador no interrumpe la ejecución del programa cuando detecta un error semántico: el error se reporta en la lista de errores, pero el intérprete continúa intentando ejecutar el programa, pudiendo producir una excepción adicional en tiempo de ejecución (por ejemplo, al intentar leer una variable que ya fue señalada como no declarada). Esta decisión se tomó por razones de tiempo de desarrollo; una versión futura debería impedir la ejecución cuando existan errores semánticos críticos.

---

## 7. Ejecución (Intérprete)

### 7.1. Estrategia general

El intérprete (`interpreter.py`) recorre el AST ya construido y validado, usando un **patrón de despacho por tipo de nodo**: los métodos `ejecutar_sentencia` y `evaluar` obtienen dinámicamente el nombre de la clase del nodo actual (`type(nodo).__name__`) y localizan, mediante `getattr`, el método correspondiente (`ejec_NombreDeClase` o `eval_NombreDeClase`). Esta técnica evita mantener una larga cadena de `if/elif` por cada tipo de nodo y facilita agregar soporte para nuevos nodos sin modificar el código de despacho.

### 7.2. Manejo de entornos y alcance

Se implementó una clase `Entorno`, que representa el conjunto de variables visibles en un punto del programa y mantiene una referencia a su entorno "padre" (el bloque que lo contiene). La búsqueda de una variable (`obtener`) y su actualización (`asignar`) recorren la cadena de entornos hacia arriba si no se encuentra en el entorno actual, mientras que la declaración (`declarar`) siempre crea la variable en el entorno más interno. Cada bloque de sentencias (cuerpo de una función, de un `if`, de un `while`, etc.) crea su propio `Entorno` hijo antes de ejecutarse, replicando el comportamiento de alcance léxico exigido por la sección 3.3.1 del enunciado.

### 7.3. Sentencias de transferencia de control

Las sentencias `return`, `break` y `continue` se implementaron lanzando excepciones de Python personalizadas (`SenalReturn`, `SenalBreak`, `SenalContinue`), capturadas en los puntos correspondientes (`llamar_funcion` para `return`; los bucles `while`/`loop` para `break`/`continue`). Este mecanismo permite que estas sentencias interrumpan la ejecución normal incluso cuando están anidadas varios niveles de profundidad dentro de bloques `if` o bucles internos, sin necesidad de propagar manualmente un valor de "señal" a través de cada nivel de recursión. Para el soporte de etiquetas (`'outer: loop { ... break 'outer; }`), cada señal de `Break`/`Continue` porta opcionalmente el nombre de la etiqueta de destino; si la etiqueta no coincide con el bucle que la captura, la excepción se vuelve a lanzar (`raise`) para que la capture el bucle correspondiente en un nivel más externo.

### 7.4. Funciones embebidas

Las funciones embebidas del lenguaje (`println!`, `len`, `contains`, `replace`, `to_uppercase`, `to_lowercase`, `split`, `reverse`, `typeof`, `random`) se resolvieron directamente dentro de `eval_LlamadaFuncion`, comparando el nombre de la función contra una lista de nombres reservados antes de intentar buscarla entre las funciones definidas por el usuario. La mayoría se apoyan directamente en métodos equivalentes de Python (`str.replace`, `str.upper`, `list.reverse`, `len()`), dado que el modelo de datos interno del intérprete representa los `String` de OxigenScript como cadenas nativas de Python, y los arreglos como listas nativas.

### 7.5. Formato de salida

Se implementó una función `formatear_valor` para traducir los valores booleanos de Python (`True`/`False`) a la convención de Rust/OxigenScript (`true`/`false`) en minúscula, y una función `formatear_debug` para el marcador de formato `{:?}` (usado para depuración de arreglos), que reconstruye la representación de una lista de forma similar a como lo haría Rust.

### 7.6. Representación de structs

Se optó por representar una instancia de struct como un diccionario nativo de Python (`{nombre_campo: valor}`), en lugar de crear una clase dinámica por cada tipo de struct declarado. Esta decisión simplificó considerablemente el acceso a campos (reutilizando el nodo `AccesoIndice`, ya usado para arreglos, distinguiendo en tiempo de evaluación si el índice es una cadena de texto —campo de struct— o una expresión —índice de arreglo—) y el soporte de structs anidados, a cambio de perder cierta validación de tipos estática sobre la forma exacta de un struct, la cual queda parcialmente delegada al análisis semántico.

---

## 8. API REST (Flask)

### 8.1. Captura de la salida de consola

Dado que el intérprete utiliza `print()` de Python para implementar `println!`, y la API necesita devolver esa salida como parte de una respuesta JSON (no imprimirla directamente en la terminal del servidor), se implementó una redirección temporal de `sys.stdout` hacia un objeto `io.StringIO()` durante la duración de cada petición, restaurando el `stdout` original en un bloque `finally` para no afectar peticiones posteriores ni los logs internos del servidor.

### 8.2. Reinicio de estado entre peticiones

Al tratarse de un lexer y un parser construidos como objetos globales (reutilizados entre peticiones para evitar el costo de reconstruir las tablas LALR en cada llamada), se detectó que el contador interno de líneas del lexer (`lexer.lineno`) no se reiniciaba automáticamente entre ejecuciones sucesivas, provocando que los números de línea reportados en los errores se acumularan de una petición a la siguiente. La solución fue reiniciar explícitamente `lexer.lineno = 1` y limpiar la lista global de errores (`limpiar_errores()`) al inicio de cada petición al endpoint `/ejecutar`.

### 8.3. Estructura de la respuesta

Cada petición exitosa o fallida devuelve un objeto JSON con los siguientes campos: `exito` (booleano), `salida` (texto acumulado de los `println!` ejecutados), `error` (mensaje de la excepción de más alto nivel, si la hubo), `errores` (lista completa de errores léxicos, sintácticos y semánticos detectados), `tokens` (lista de todos los tokens reconocidos, para el reporte de análisis léxico), `tabla_simbolos` (lista de identificadores declarados con su categoría, tipo, ámbito y valor), y `ast_imagen` (la imagen PNG del árbol de sintaxis abstracta, codificada en base64, para su renderizado directo en el navegador sin necesidad de servir un archivo estático adicional).

---

## 9. Desafíos técnicos adicionales

**Rutas relativas dependientes del directorio de ejecución.** Durante las pruebas iniciales del reporte de AST, se generaban archivos en ubicaciones inconsistentes según si un script se ejecutaba desde la raíz del proyecto o desde la carpeta `backend/`. La solución definitiva fue construir siempre rutas absolutas dentro de la API (`os.path.dirname(os.path.abspath(__file__))`), independientes del directorio desde el cual se invoque el proceso de Flask.

**Duplicación de errores léxicos en el reporte de tokens.** Al generar el listado de tokens para el reporte de análisis léxico, se tokeniza el código fuente por separado (mediante `lexer.clone()`) del proceso real que efectúa el parser. Como ambas tokenizaciones disparan la función `t_error` de forma independiente, cada error léxico se reportaba dos veces en la lista de errores. Se resolvió respaldando y restaurando la lista de errores alrededor de la tokenización auxiliar destinada únicamente al reporte, dejando que el único registro real de errores léxicos provenga de la tokenización que efectúa el parser durante la construcción del AST.

**Secuencias de escape en cadenas de texto.** El lexer inicialmente capturaba el contenido de un string de forma literal, sin interpretar secuencias como `\n` o `\"`. Se agregó un procesamiento adicional dentro de la regla `t_STRING`, reemplazando las secuencias de escape más comunes (`\n`, `\"`, `\\`) por su carácter real correspondiente, antes de asignar el valor final del token.

---

## 10. Funcionalidades no implementadas

Por razones de priorización de tiempo, las siguientes características de la especificación del lenguaje quedaron pendientes de implementación:

- **Slices de arreglos** (`&arreglo[inicio..fin]`), sección 3.3.10.
- **Raw strings** (`r"..."`), sección 3.3.11.

Ambas se documentan aquí como limitaciones conocidas del intérprete, y podrían incorporarse en una iteración futura extendiendo la gramática del parser con las reglas correspondientes para los tokens `AMPER` y `RANGO` (ya reconocidos por el analizador léxico, pero sin una producción sintáctica asociada).

---

## 11. Conclusiones

El desarrollo de OxigenScript permitió aplicar de forma práctica los conceptos fundamentales de construcción de intérpretes: desde el reconocimiento de patrones léxicos mediante expresiones regulares, pasando por la resolución de ambigüedades gramaticales y conflictos de precedencia en un analizador LALR, hasta el diseño de una representación intermedia (AST) y su posterior recorrido para la validación semántica y la ejecución real del programa. La separación del proyecto en módulos con responsabilidades claras (`lexer.py`, `parser.py`, `semantic.py`, `interpreter.py`) facilitó tanto el desarrollo incremental como la identificación y corrección de errores de forma aislada durante las pruebas.
