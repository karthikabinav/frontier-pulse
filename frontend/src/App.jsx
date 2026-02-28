import { useEffect, useMemo, useState } from "react";
import { api } from "./api";

function App() {
  const [health, setHealth] = useState(null);
  const [diagnostics, setDiagnostics] = useState(null);
  const [policies, setPolicies] = useState(null);
  const [papers, setPapers] = useState([]);
  const [hypotheses, setHypotheses] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [memoryEntries, setMemoryEntries] = useState([]);
  const [memoryTypeFilter, setMemoryTypeFilter] = useState("");
  const [qa, setQa] = useState([]);
  const [brief, setBrief] = useState(null);
  const [editorValue, setEditorValue] = useState("");
  const [exports, setExports] = useState([]);
  const [status, setStatus] = useState("Idle");

  const weekKey = useMemo(() => {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 1);
    const day = Math.floor((now - start) / 86400000) + 1;
    const week = Math.ceil(day / 7);
    return `${now.getFullYear()}-W${String(week).padStart(2, "0")}`;
  }, []);

  async function loadMemory(filter = memoryTypeFilter) {
    const entries = await api.memory({ memory_type: filter || undefined, limit: 100 });
    setMemoryEntries(entries);
  }

  async function loadAll() {
    setStatus("Loading data...");
    try {
      const [
        healthRes,
        diagnosticsRes,
        ingestion,
        inference,
        project,
        paperList,
        hypList,
        clusterList,
        latestBrief,
        qaList,
      ] = await Promise.all([
        api.health(),
        api.diagnostics(),
        api.ingestionPolicy(),
        api.inferencePolicy(),
        api.projectPolicy(),
        api.papers(),
        api.hypotheses(),
        api.clusters(),
        api.latestBrief(),
        api.qaChecklist(),
      ]);

      setHealth(healthRes);
      setDiagnostics(diagnosticsRes);
      setPolicies({ ingestion, inference, project });
      setPapers(paperList);
      setHypotheses(hypList);
      setClusters(clusterList);
      setBrief(latestBrief);
      setEditorValue(latestBrief?.markdown_content ?? "");
      setQa(qaList.checklist || []);
      await loadMemory(memoryTypeFilter);
      setStatus("Ready");
    } catch (err) {
      setStatus(`Load failed: ${err.message}`);
    }
  }

  async function runWeekly() {
    setStatus("Running weekly workflow...");
    try {
      const result = await api.runWeekly();
      setStatus(`Run completed: ${result.notes}`);
      await loadAll();
    } catch (err) {
      setStatus(`Run failed: ${err.message}`);
    }
  }

  async function saveBrief() {
    setStatus("Saving brief version...");
    try {
      const next = await api.updateBrief({
        week_key: brief?.week_key || weekKey,
        editor: "user",
        markdown_content: editorValue,
      });
      setBrief(next);
      setStatus(`Saved version ${next.version_number}`);
    } catch (err) {
      setStatus(`Save failed: ${err.message}`);
    }
  }

  async function generateExports() {
    if (!brief?.id) {
      setStatus("No brief available to export.");
      return;
    }
    setStatus("Generating exports...");
    try {
      const response = await api.generateExports(brief.id);
      setExports(response.items);
      setStatus("Exports ready. Use Copy buttons.");
    } catch (err) {
      setStatus(`Export failed: ${err.message}`);
    }
  }

  async function applyMemoryFilter(nextFilter) {
    setMemoryTypeFilter(nextFilter);
    try {
      setStatus("Loading memory...");
      await loadMemory(nextFilter);
      setStatus("Ready");
    } catch (err) {
      setStatus(`Memory load failed: ${err.message}`);
    }
  }

  function copyText(text) {
    navigator.clipboard.writeText(text);
    setStatus("Copied to clipboard.");
  }

  useEffect(() => {
    loadAll();
  }, []);

  useEffect(() => {
    function onKeydown(event) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "r") {
        event.preventDefault();
        runWeekly();
      }
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        saveBrief();
      }
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "e") {
        event.preventDefault();
        generateExports();
      }
    }
    window.addEventListener("keydown", onKeydown);
    return () => window.removeEventListener("keydown", onKeydown);
  });

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <h1>aifrontierpulse V1</h1>
          <p className="sub">Literature-survey foundation for an automated AI researcher</p>
        </div>
        <div className="actions">
          <button onClick={runWeekly}>Run Weekly (Ctrl/Cmd+R)</button>
          <button onClick={saveBrief}>Save Brief (Ctrl/Cmd+S)</button>
          <button onClick={generateExports}>Generate Exports (Ctrl/Cmd+E)</button>
          <button onClick={loadAll}>Refresh</button>
        </div>
      </header>

      <p className="status">{status}</p>

      <section className="grid two">
        <article className="panel">
          <h2>System & Diagnostics</h2>
          <p>API: {health ? "healthy" : "unknown"}</p>
          <p>DB: {diagnostics?.db_ok ? "connected" : "unknown"}</p>
          <p>Scheduler mode: {diagnostics?.scheduler_mode || "-"}</p>
          <p>Latest week: {diagnostics?.latest_week_key || "-"}</p>
          <p>Last run: {diagnostics?.last_run_completed_at || "-"}</p>
          <p>Last run notes: {diagnostics?.last_run_notes || "-"}</p>
        </article>

        <article className="panel">
          <h2>Accumulation Snapshot</h2>
          <p>Papers: {diagnostics?.paper_count ?? papers.length}</p>
          <p>Alpha cards: {diagnostics?.alpha_card_count ?? 0}</p>
          <p>Hypotheses: {diagnostics?.hypothesis_count ?? hypotheses.length}</p>
          <p>Clusters: {diagnostics?.cluster_count ?? clusters.length}</p>
          <p>Memory total: {diagnostics?.memory_total_count ?? 0}</p>
          <p>Memory hypotheses: {diagnostics?.memory_hypothesis_count ?? 0}</p>
          <p>Memory alpha nuggets: {diagnostics?.memory_alpha_nugget_count ?? 0}</p>
          <p>Memory weekly synthesis: {diagnostics?.memory_weekly_synthesis_count ?? 0}</p>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <h2>Policy Snapshot</h2>
          <p>Sources: {policies?.ingestion?.sources?.join(", ") || "-"}</p>
          <p>LLM: {policies?.inference?.llm_model || "-"}</p>
          <p>Embeddings: {policies?.project?.embedding_model || "-"}</p>
          <p>Topic bias: {policies?.ingestion?.topic_bias_enabled ? "enabled" : "disabled"}</p>
          <p>Topic keywords: {(policies?.ingestion?.topic_bias_keywords || []).slice(0, 6).join(", ")}...</p>
        </article>

        <article className="panel">
          <h2>Memory Browser</h2>
          <div className="actions">
            <button onClick={() => applyMemoryFilter("")}>All</button>
            <button onClick={() => applyMemoryFilter("hypothesis")}>Hypotheses</button>
            <button onClick={() => applyMemoryFilter("alpha_nugget")}>Alpha nuggets</button>
            <button onClick={() => applyMemoryFilter("weekly_synthesis")}>Weekly synthesis</button>
          </div>
          <ul className="rows">
            {memoryEntries.slice(0, 12).map((m) => (
              <li key={m.memory_key}>
                <strong>{m.memory_type} • {m.source_week}</strong>
                <span>{m.title}</span>
                <span>{m.summary.slice(0, 180)}...</span>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <h2>Hypothesis Table</h2>
          <ul className="rows">
            {hypotheses.slice(0, 12).map((h) => (
              <li key={h.id}>
                <strong>{h.text}</strong>
                <span>
                  support {h.support_count} | contradiction {h.contradiction_count} | strength {h.strength_score.toFixed(2)}
                </span>
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Cluster Panel</h2>
          <ul className="rows">
            {clusters.slice(0, 12).map((c) => (
              <li key={c.id}>
                <strong>{c.name}</strong>
                <span>
                  {c.dominant_bottleneck} | papers {c.paper_count}
                </span>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="panel">
        <h2>Weekly Brief Editor</h2>
        <textarea value={editorValue} onChange={(e) => setEditorValue(e.target.value)} rows={16} />
      </section>

      <section className="grid two">
        <article className="panel">
          <h2>QA Checklist</h2>
          <ul className="rows">
            {qa.map((item) => (
              <li key={item.id}>
                <strong>{item.passed ? "PASS" : "PENDING"}</strong>
                <span>{item.title}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Export Outputs (Clipboard)</h2>
          <ul className="rows">
            {exports.map((item) => (
              <li key={item.platform}>
                <strong>{item.platform}</strong>
                <span>{item.content.slice(0, 120)}...</span>
                <button onClick={() => copyText(item.content)}>Copy</button>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}

export default App;
