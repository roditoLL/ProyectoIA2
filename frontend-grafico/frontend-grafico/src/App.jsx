import { useEffect, useState } from "react";
import "./App.css";
import SimilaridadGraph from "./SimilaridadGraph";

export default function App() {
  const [carreras, setCarreras] = useState([]);
  const [areas, setAreas] = useState([]);
  const [asignaturas, setAsignaturas] = useState([]);
  const [resultados, setResultados] = useState([]);

  const [filters, setFilters] = useState({
    nombre: "",
    carrera: "",
    area: "",
  });

  const [data, setData] = useState(null); // resultados del backend

  useEffect(() => {
    fetch("http://127.0.0.1:8000/carreras/")
      .then((r) => r.json())
      .then(setCarreras)
      .catch(console.error);

    fetch("http://127.0.0.1:8000/areas/")
      .then((r) => r.json())
      .then(setAreas)
      .catch(console.error);

      // fetch de asignaturas
      fetch("http://127.0.0.1:8000/asignaturas/")
        .then(r => r.json())
        .then(setAsignaturas)
        .catch(console.error);
        
        fetch(`http://127.0.0.1:8000/similares?nombre=${encodeURIComponent(filters.nombre)}`)
        .then(r => r.json())
        .then(setResultados)
        .catch(console.error);


  }, []);

  function handleChange(e) {
    const { name, value } = e.target;
    setFilters((f) => ({ ...f, [name]: value }));
  }

  function handleBuscar() {
  const nombre = filters.nombre.trim();
  if (!nombre) {
    alert("Debes escribir un nombre de asignatura");
    return;
  }

  fetch(`http://127.0.0.1:8000/similares?nombre=${encodeURIComponent(nombre)}`)
    .then((res) => res.json())
    .then((data) => {
      console.log("Datos recibidos:", data);
      setData(data); // este es el estado que renderiza el grafo
    })
    .catch((err) => {
      console.error("Error al buscar similares:", err);
    });
}


  return (
    <div style={{ height: "100vh", fontFamily: "sans-serif", display: "flex", flexDirection: "column" }}>
      <header style={{ padding: "20px", borderBottom: "1px solid #ddd" }}>
        <h1 style={{ margin: 0 }}>Análisis de similitud entre asignaturas</h1>
      </header>

      <div style={{ display: "flex", flex: 1 }}>
        <aside style={{
          width: 300,
          padding: 20,
          borderRight: "1px solid #ddd",
          boxSizing: "border-box"
        }}>
          <h2>Buscar asignaturas</h2>

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: "block", marginBottom: 4 }}>Nombre</label>
            <select
            name="nombre"
            value={filters.nombre}
            onChange={handleChange}
            style={{ width: "100%", padding: 6 }}
          >
            <option value="">Seleccione una asignatura</option>
            {asignaturas.map(a => (
              <option key={a.id} value={a.nombre}>{a.nombre}</option>
            ))}
          </select>

          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: "block", marginBottom: 4 }}>Carrera</label>
            <select
              name="carrera"
              value={filters.carrera}
              onChange={handleChange}
              style={{ width: "100%", padding: 6 }}
            >
              <option value="">Todas</option>
              {carreras.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", marginBottom: 4 }}>Área</label>
            <select
              name="area"
              value={filters.area}
              onChange={handleChange}
              style={{ width: "100%", padding: 6 }}
            >
              <option value="">Todas</option>
              {areas.map(a => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>

          <button
            onClick={handleBuscar}
            style={{
              width: "100%",
              padding: 10,
              background: "#0066ff",
              color: "#fff",
              border: "none",
              cursor: "pointer"
            }}
          >
            Buscar
          </button>
        </aside>

        <main style={{ flex: 1, padding: 20, overflow: "auto" }}>
          <h2>Resultados</h2>
          {/* Solo renderiza el grafo si hay datos */}
          {data ? (
            <SimilaridadGraph data={data} />
          ) : (
            <p>No hay resultados aún. Pulsa “Buscar”.</p>
          )}
        </main>
      </div>
    </div>
  );
}
