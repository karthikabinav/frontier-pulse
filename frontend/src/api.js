export async function fetchHealth() {
  const response = await fetch("http://localhost:8000/api/v1/health");
  if (!response.ok) {
    throw new Error("Failed to fetch health");
  }
  return response.json();
}
