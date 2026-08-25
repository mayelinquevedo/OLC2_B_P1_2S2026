import React, { useState } from "react";
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
      setError("No se pudo conectar con el servidor. ¿Esta corriendo app.py?");
    } finally {
      setEjecutando(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>OxigenScript</h1>
        <button onClick={ejecutarCodigo} disabled={ejecutando}>
          {ejecutando ? "Ejecutando..." : "▶ Ejecutar"}
        </button>
      </header>

      <div className="editor-container">
        <Editor
          height="60vh"
          defaultLanguage="rust"
          value={codigo}
          onChange={(valor) => setCodigo(valor)}
          theme="vs-dark"
        />
      </div>

      <div className="consola-container">
        <h3>Consola de salida</h3>
        <pre className="consola-salida">
          {salida}
          {error && <span className="consola-error">{"\n[Error] " + error}</span>}
        </pre>
      </div>
    </div>
  );
}

export default App;