import { useState, useRef } from "react";
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

  const [errores, setErrores] = useState([]);
  const [tabla, setTabla] = useState([]);
  const [tokens, setTokens] = useState([]);
  const [astImagen, setAstImagen] = useState(null);

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

      const data = respuesta.data;

      setErrores(data.errores || []);
      setTabla(data.tabla_simbolos || []);
      setTokens(data.tokens || []);
      setAstImagen(data.ast_imagen || null);

      if (data.exito) {
        setSalida(data.salida || "(sin salida)");
      } else {
        setSalida(data.salida || "");
        setError(data.error);
      }
    } catch (err) {
      setError("No se pudo conectar con el servidor.");
    } finally {
      setEjecutando(false);
    }
  };

  const Nuevo = () => {
    setCodigo("");
    setSalida("");
    setError(null);
    setErrores([]);
    setTabla([]);
    setTokens([]);
    setAstImagen(null);
  };

  const fileInputRef = useRef(null);
  const Abrir = (evento) => {
    const archivo = evento.target.files[0];
    if (!archivo) return;
    const lector = new FileReader();
    lector.onload = (e) => setCodigo(e.target.result);
    lector.readAsText(archivo);
  };
  const activarSelector = () => fileInputRef.current.click();

  const Guardar = async () => {
    if ("showSaveFilePicker" in window) {
      try {
        const opciones = {
          suggestedName: "archivo.txt",
          types: [{
            description: "archivo de texto o codigo",
            accept: { "text/plain": [".txt", ".oxigen", ".js", ".py"] },
          }],
        };
        const handle = await window.showSaveFilePicker(opciones);
        const writable = await handle.createWritable();
        await writable.write(codigo);
        await writable.close();
        alert("archivo guardado con exito");
      } catch (err) {
        console.log("Guardado cancelado o hubo un error", err);
      }
    } else {
      const blob = new Blob([codigo], { type: "text/plain;charset=utf-8" });
      const enlace = document.createElement("a");
      enlace.href = URL.createObjectURL(blob);
      enlace.download = "archivo.txt";
      enlace.click();
      URL.revokeObjectURL(enlace.href);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h2>OxigenScript</h2>
        <div className="toolbar">
          <button onClick={Nuevo}>Nuevo</button>
          <button onClick={activarSelector}>Abrir</button>
          <input type="file" ref={fileInputRef} onChange={Abrir} style={{ display: "none" }} />
          <button onClick={Guardar}>Guardar</button>
          <button onClick={ejecutarCodigo} disabled={ejecutando}>
            {ejecutando ? "Ejecutando..." : "Ejecutar"}
          </button>
        </div>
      </header>

      <div className="workspace">
        <div className="editor-container">
          <div className="panel-title"><span>Entrada</span></div>
          <Editor
            height="100%"
            defaultLanguage="rust"
            value={codigo}
            onChange={(valor) => setCodigo(valor)}
            theme="vs-dark"
          />
        </div>

        <div className="consola-container">
          <div className="panel-title"><span>Salida</span></div>
          <pre className="consola-salida">
            {salida || "(sin salida)"}
            {error && <span className="consola-error">{"\n[Error] " + error}</span>}
          </pre>
        </div>
      </div>

      <section className="compiler-panel">
        <div className="compiler-tabs">
          <button className={panelActivo === "errores" ? "tab activo" : "tab"}
            onClick={() => { setPanelActivo("errores"); setPanelAbierto(true); }}>
            Errores {errores.length > 0 && `(${errores.length})`}
          </button>
          <button className={panelActivo === "simbolos" ? "tab activo" : "tab"}
            onClick={() => { setPanelActivo("simbolos"); setPanelAbierto(true); }}>
            Tabla de símbolos
          </button>
          <button className={panelActivo === "ast" ? "tab activo" : "tab"}
            onClick={() => { setPanelActivo("ast"); setPanelAbierto(true); }}>
            AST
          </button>
          <button className={panelActivo === "tokens" ? "tab activo" : "tab"}
            onClick={() => { setPanelActivo("tokens"); setPanelAbierto(true); }}>
            Tokens
          </button>
          <button className="collapse-button" onClick={() => setPanelAbierto(!panelAbierto)}>
            {panelAbierto ? "▼" : "▲"}
          </button>
        </div>

        {panelAbierto && (
          <div className="compiler-content">
            {panelActivo === "errores" && (
              <div className="data-section">
                <h3>Errores encontrados</h3>
                <table>
                  <thead>
                    <tr><th>Línea</th><th>Columna</th><th>Tipo</th><th>Mensaje</th></tr>
                  </thead>
                  <tbody>
                    {errores.length === 0 ? (
                      <tr><td colSpan="4">Sin errores</td></tr>
                    ) : (
                      errores.map((e, i) => (
                        <tr key={i}>
                          <td>{e.linea}</td>
                          <td>{e.columna}</td>
                          <td>{e.tipo}</td>
                          <td>{e.descripcion}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {panelActivo === "simbolos" && (
                <div className="data-section">
                  <h3>Tabla de símbolos</h3>
                  <button
                    onClick={async () => {
                      const respuesta = await axios.post(
                        "http://127.0.0.1:8000/reporte_simbolos",
                        { codigo: codigo },
                        { responseType: "blob" }
                      );
                      const enlace = document.createElement("a");
                      enlace.href = URL.createObjectURL(respuesta.data);
                      enlace.download = "tabla_simbolos.html";
                      enlace.click();
                    }}
                    style={{ marginBottom: "10px" }}
                  >
                    Descargar como HTML
                  </button>
                  <table>
                  <thead>
                    <tr><th>Nombre</th><th>Categoría</th><th>Tipo</th><th>Ámbito</th><th>Valor</th></tr>
                  </thead>
                  <tbody>
                    {tabla.map((s, i) => (
                      <tr key={i}>
                        <td>{s.nombre}</td>
                        <td>{s.categoria}</td>
                        <td>{s.tipo}</td>
                        <td>{s.ambito}</td>
                        <td>{s.valor}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {panelActivo === "ast" && (
              <div className="ast-section">
                <h3>Árbol de Sintaxis Abstracta</h3>
                {astImagen ? (
                  <img
                    src={`data:image/png;base64,${astImagen}`}
                    alt="AST"
                    style={{ maxWidth: "100%" }}
                  />
                ) : (
                  <p>Ejecuta un programa para ver su AST</p>
                )}
              </div>
            )}

            {panelActivo === "tokens" && (
              <div className="data-section">
                <h3>Análisis léxico</h3>
                <table>
                  <thead>
                    <tr><th>Lexema</th><th>Token</th><th>Línea</th></tr>
                  </thead>
                  <tbody>
                    {tokens.map((t, i) => (
                      <tr key={i}>
                        <td>{t.lexema}</td>
                        <td>{t.token}</td>
                        <td>{t.linea}</td>
                      </tr>
                    ))}
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