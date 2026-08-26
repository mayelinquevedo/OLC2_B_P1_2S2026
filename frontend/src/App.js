import  { useState, useRef } from "react";
import Editor from "@monaco-editor/react";
import axios from "axios";
import "./App.css";


const CODIGO_INICIAL = `fn main() {
    let x: i32 = 10;
    println!(x);
}
`;

function App() {
  const [codigo, setCodigo] = useState(CODIGO_INICIAL);
  const [salida, setSalida] = useState("");
  const [error, setError] = useState(null);
  const [ejecutando, setEjecutando] = useState(false);

  const [panelActivo, setPanelActivo] = useState("errores");
  const [panelAbierto, setPanelAbierto] = useState(true);

  const ejecutarCodigo = async () => {
    setEjecutando(true);
    setSalida("");
    setError(null);

    try {
      const respuesta = await axios.post("http://127.0.0.1:8000/ejecutar", {
        codigo: codigo,
      });

      if (respuesta.data.exito) {
        setSalida(respuesta.data.salida || "(sin salida)");
      } else {
        setSalida(respuesta.data.salida || "");
        setError(respuesta.data.error);
      }
    } catch (err) {
      setError("No se pudo conectar con el servidor.");
    } finally {
      setEjecutando(false);
    }
  };
  // Boton NUEVO
  const Nuevo = () => {
    setCodigo("");
    setSalida("");
    setError(null);

  }
  // Boton ABRIR
  const fileInputRef = useRef(null);
  const Abrir = (evento) => {
    const archivo = evento.target.files[0];
    if (!archivo) return;
    const lector = new FileReader();
    lector.onload = (e) => {
      const contenido = e.target.result;
      setCodigo(contenido);
    };
    lector.readAsText(archivo)
  };
  const activarSelector = () =>{
    fileInputRef.current.click();
  }

  //Boton GUARDAR
  const Guardar = async () => {
    if ('showSaveFilePicker' in window){
      try {
        const opciones = {
          suggestedName: 'archivo.txt',
          types: [{
            description: 'archivo de texto o codigo',
            accept: {
              'text/plain': ['.txt', '.oxigen', '.js', '.py'],
            }
          }],
        };
        const handle = await window.showSaveFilePicker(opciones)
        const writable = await handle.createWritable();
        await writable.write(codigo);
        await writable.close();
        alert("archivo guardado con exito");
      } catch (err) {
        console.log("Guardado cancelado por el usuario o hubo algun error", err);
      }
    } else{
      const blob = new Blob([codigo], {type: "text/plain;charset=utf-8" });
      const enlace = document.createElement("a");
      enlace.href = URL.createObjectURL(blob);
      enlace.download = "archivo.txt";
      enlace.click();
      URL.revokeObjectURL(enlace.href)
    }
  };

  return (
  <div className="app-container">

    {/*HEADER*/}
    <header className="app-header">
      <h2>OxigenScript</h2>
      <div className="toolbar">

        <button onClick={Nuevo}>
          Nuevo
        </button>

        <button onClick={activarSelector}>
          Abrir
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={Abrir}
          style={{ display: "none" }}
        />

        <button onClick={Guardar}>
          Guardar
        </button>

        <button
          onClick={ejecutarCodigo}
          disabled={ejecutando}
        >
          {ejecutando ? "Ejecutando..." : "Ejecutar"}
        </button>
      </div>
    </header>


    {/*EDITOR + SALIDA*/}
    <div className="workspace">
      {/* EDITOR */}
      <div className="editor-container">
        <div className="panel-title">
          <span>Entrada</span>
        </div>

        <Editor
          height="100%"
          defaultLanguage="rust"
          value={codigo}
          onChange={(valor) => setCodigo(valor)}
          theme="vs-dark"
        />
      </div>

      {/* SALIDA */}
      <div className="consola-container">
        <div className="panel-title">
          <span>Salida</span>
        </div>

        <pre className="consola-salida">
          {salida || "(sin salida)"}
          {error && (
            <span className="consola-error">
              {"\n[Error] " + error}
            </span>
          )}
        </pre>
      </div>
    </div>


    {/* PANEL*/}
    <section className="compiler-panel">
      {/* BARRA DE PESTAÑAS */}
      <div className="compiler-tabs">
        <button
          className={panelActivo === "errores" ? "tab activo" : "tab"}
          onClick={() => {
            setPanelActivo("errores");
            setPanelAbierto(true);
          }}
        >
           Errores        </button>
        <button
          className={panelActivo === "simbolos" ? "tab activo" : "tab"}
          onClick={() => {
            setPanelActivo("simbolos");
            setPanelAbierto(true);
          }}
        >
          Tabla de símbolos
        </button>

        <button
          className={panelActivo === "ast" ? "tab activo" : "tab"}
          onClick={() => {
            setPanelActivo("ast");
            setPanelAbierto(true);
          }}
        >
          AST
        </button>

        <button
          className={panelActivo === "tokens" ? "tab activo" : "tab"}
          onClick={() => {
            setPanelActivo("tokens");
            setPanelAbierto(true);
          }}
        >
          Tokens
        </button>

        {/* BOTÓN PARA CONTRAER */}
        <button
          className="collapse-button"
          onClick={() => setPanelAbierto(!panelAbierto)}
        >
          {panelAbierto ? "▼" : "▲"}
        </button>
      </div>

      {/* CONTENIDO DEL PANEL */}
      {panelAbierto && (
        <div className="compiler-content">

          {/*ERRORES*/}
          {panelActivo === "errores" && (
            <div className="data-section">
              <h3>Errores encontrados</h3>
              <table>
                <thead>
                  <tr>
                    <th>Línea</th>
                    <th>Columna</th>
                    <th>Tipo</th>
                    <th>Mensaje</th>
                  </tr>
                </thead>
                <tbody>
                </tbody>
              </table>
            </div>
          )}

          {/* TABLA DE SÍMBOLOS */}
          {panelActivo === "simbolos" && (
            <div className="data-section">
              <h3>Tabla de símbolos</h3>
              <table>
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th>Tipo</th>
                    <th>Valor</th>
                    <th>Ámbito</th>
                    <th>Línea</th>
                  </tr>
                </thead>
                <tbody>
                </tbody>
              </table>
            </div>
          )}
          {/*AST*/}
          {panelActivo === "ast" && (
            <div className="ast-section">
              <h3>Árbol de Sintaxis Abstracta</h3>
            </div>
          )}


          {/*TOKENS*/}
          {panelActivo === "tokens" && (
            <div className="data-section">
              <h3>Análisis léxico</h3>
              <table>
                <thead>
                  <tr>
                    <th>Lexema</th>
                    <th>Token</th>
                    <th>Línea</th>
                  </tr>
                </thead>
                <tbody>
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </section>
  </div>
);
}
export default App;