import { useEffect, useState } from "react";
import { fetchHealth } from "./api";

function App() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch((err) => setError(err.message));
  }, []);

  return (
    <main className="shell">
      <header>
        <h1>Frontier Pulse</h1>
        <p>Local-first research intelligence cockpit.</p>
      </header>

      <section className="panel">
        <h2>Backend Status</h2>
        {health && <p>API healthy at {health.timestamp}</p>}
        {error && <p className="error">{error}</p>}
        {!health && !error && <p>Checking API...</p>}
      </section>

      <section className="panel">
        <h2>V1 Pipeline</h2>
        <ol>
          <li>Ingest arXiv papers</li>
          <li>Extract alpha cards</li>
          <li>Build hypothesis graph</li>
          <li>Generate weekly brief + export formats</li>
        </ol>
      </section>
    </main>
  );
}

export default App;
