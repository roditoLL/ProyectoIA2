import { useEffect, useState } from "react";
import "./App.css";
import SimilaridadGraph from "./SimilaridadGraph";
import ClipLoader from "react-spinners/ClipLoader";

export default function App() {
  const [carreras, setCarreras] = useState([]);
  const [areas, setAreas] = useState([]);
  const [asignaturas, setAsignaturas] = useState([]);
  const [resultados, setResultados] = useState([]);
  const [loading, setLoading] = useState(false);

  const [filters, setFilters] = useState({
    nombre: "",
    carrera: "",
    area: "",
  });

  useEffect(() => {
    fetch("http://127.0.0.1:8000/carreras/")
      .then((r) => r.json())
      .then(setCarreras)
      .catch(console.error);

    fetch("http://127.0.0.1:8000/areas/")
      .then((r) => r.json())
      .then(setAreas)
      .catch(console.error);

    fetch("http://127.0.0.1:8000/asignaturas/")
      .then((r) => r.json())
      .then(setAsignaturas)
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!filters.nombre) return;
    console.log(filters)
    

    let url = `http://127.0.0.1:8000/similares?nombre=${encodeURIComponent(filters.nombre)}`;

    if (!filters.carrera || filters.carrera.trim() === "") {
      url += `&carrera=Todas`;
    } else {
      url += `&carrera=${encodeURIComponent(filters.carrera)}`;
    }

    if (filters.area) {
      url += `&area=${encodeURIComponent(filters.area)}`;
    }

    fetch(url)
      .then((r) => r.json())
      .then(setResultados)
    setLoading(true)
    if (resultados) {
      setLoading(false)
    }
  }, [filters]);

  function handleChange(e) {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function handleSubmit(e) {
    e.preventDefault(); // evita que se recargue la página
    if (!filters.nombre.trim()) {
      alert("Debes seleccionar un nombre de asignatura");
      return;
    }

    // Este setFilters ya activa el useEffect automáticamente
    setFilters((prev) => ({ ...prev }));
  }

  return (
    <div style={{ height: "100vh", fontFamily: "sans-serif", display: "flex", flexDirection: "column" }}>
      <header style={{ padding: "20px", borderBottom: "1px solid #ddd" }}>
        <h1 style={{ margin: 0 }}>Análisis de similitud entre asignaturas</h1>
      </header>

      <div style={{ display: "flex", flex: 1 }}>
        <aside
          style={{
            width: 300,
            padding: 20,
            borderRight: "1px solid #ddd",
            boxSizing: "border-box",
          }}
        >
          <h2>Buscar asignaturas</h2>

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: "block", marginBottom: 4 }}>Nombre</label>
              <select
                name="nombre"
                value={filters.nombre}
                onChange={handleChange}
                style={{ width: "100%", padding: 6 }}
              >
                <option value="">Seleccione una asignatura</option>
                {asignaturas.map((a) => (
                  <option key={a.id} value={a.nombre}>
                    {a.nombre}
                  </option>
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
                {carreras.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
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
                {areas.map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              style={{
                width: "100%",
                padding: 10,
                background: "#0066ff",
                color: "#fff",
                border: "none",
                cursor: "pointer",
              }}
            >
              Buscar
            </button>
          </form>
        </aside>
        <main style={{ flex: 1, padding: 20, overflow: "auto" }}>
          <h2>Resultados</h2>
          {loading ? (
            <div style={{ display: "flex", justifyContent: "center", padding: 40 }}>
              <ClipLoader color="#36d7b7" size={50} />
            </div>
          ) : resultados ? (
            <SimilaridadGraph data={resultados} />
          ) : (
            <p>No hay resultados aún. Pulsa “Buscar”.</p>
          )}
        </main>
      </div>
    </div>
  );
}
