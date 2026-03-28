import { useState } from "react";
import "./App.css";

const API = "http://localhost:8000";

const SAMPLE_DATA = {
  cargos: [
    { id: "C1", volume: 1234 },
    { id: "C2", volume: 4352 },
    { id: "C3", volume: 3321 },
    { id: "C4", volume: 2456 },
    { id: "C5", volume: 5123 },
    { id: "C6", volume: 1879 },
    { id: "C7", volume: 4987 },
    { id: "C8", volume: 2050 },
    { id: "C9", volume: 3678 },
    { id: "C10", volume: 5432 },
  ],
  tanks: [
    { id: "T1", capacity: 1234 },
    { id: "T2", capacity: 4352 },
    { id: "T3", capacity: 3321 },
    { id: "T4", capacity: 2456 },
    { id: "T5", capacity: 5123 },
    { id: "T6", capacity: 1879 },
    { id: "T7", capacity: 4987 },
    { id: "T8", capacity: 2050 },
    { id: "T9", capacity: 3678 },
    { id: "T10", capacity: 5432 },
  ],
};

function App() {
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState({ message: "", error: false });

  async function callApi(method, path, body) {
    setStatus({ message: "Loading...", error: false });
    try {
      const opts = {
        method,
        headers: { "Content-Type": "application/json" },
      };
      if (body) opts.body = JSON.stringify(body);

      const res = await fetch(`${API}${path}`, opts);
      const data = await res.json();

      if (!res.ok) {
        setStatus({ message: data.detail || "Request failed", error: true });
        setResult(data);
        return;
      }

      setStatus({ message: `${method} ${path} — Success (${res.status})`, error: false });
      setResult(data);
    } catch (err) {
      setStatus({ message: `Network error: ${err.message}`, error: true });
      setResult(null);
    }
  }

  return (
    <div className="container">
      <h1>ShipIQ Cargo Optimizer</h1>
      <p className="subtitle">Maritime cargo-to-tank allocation service</p>

      <div className="buttons">
        <button onClick={() => callApi("POST", "/input", SAMPLE_DATA)}>
          Load Sample Data
        </button>
        <button onClick={() => callApi("POST", "/optimize")}>
          Run Optimization
        </button>
        <button onClick={() => callApi("GET", "/results")}>
          Get Results
        </button>
      </div>

      {status.message && (
        <div className={`status ${status.error ? "error" : "success"}`}>
          {status.message}
        </div>
      )}

      {result && (
        <pre className="output">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}

export default App;
