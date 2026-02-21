const API_BASE = "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed for ${path}`);
  }
  return response.json();
}

export const api = {
  health: () => request("/health"),
  runWeekly: () => request("/workflows/weekly-run", { method: "POST", body: JSON.stringify({}) }),
  ingestionPolicy: () => request("/workflows/ingestion-policy"),
  inferencePolicy: () => request("/workflows/inference-policy"),
  projectPolicy: () => request("/workflows/project-policy"),
  papers: () => request("/papers?limit=50"),
  hypotheses: () => request("/hypotheses"),
  clusters: () => request("/clusters"),
  latestBrief: () => request("/briefs/latest"),
  updateBrief: (payload) => request("/briefs/update", { method: "POST", body: JSON.stringify(payload) }),
  qaChecklist: () => request("/qa/checklist"),
  generateExports: (briefVersionId) =>
    request("/exports/generate", {
      method: "POST",
      body: JSON.stringify({ brief_version_id: briefVersionId }),
    }),
};
