const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8004";

export async function postChat(message: string) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function classifyProject(params: {
  project_description: string;
  project_type?: string;
  address?: string;
}) {
  const res = await fetch(`${API_BASE}/api/intake/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Classification failed: ${res.status}`);
  return res.json();
}

export async function getApplications() {
  const res = await fetch(`${API_BASE}/api/applications`);
  if (!res.ok) throw new Error(`Applications failed: ${res.status}`);
  return res.json();
}

export async function estimateFees(params: {
  project_type: string;
  square_footage?: number;
  valuation?: number;
}) {
  const res = await fetch(`${API_BASE}/api/fees/estimate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Fee estimation failed: ${res.status}`);
  return res.json();
}
