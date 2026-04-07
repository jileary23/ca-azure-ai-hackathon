const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003';

export async function postChat(message: string) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function screenEligibility(params: {
  household_size: number;
  monthly_income: number;
  age: number;
  pregnant?: boolean;
  disabled?: boolean;
  county?: string;
}) {
  const res = await fetch(`${API_BASE}/api/eligibility/screen`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Screening failed: ${res.status}`);
  return res.json();
}

export async function analyzeDocument(params: {
  document_type: string;
  file_name: string;
}) {
  const res = await fetch(`${API_BASE}/api/documents/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Document analysis failed: ${res.status}`);
  return res.json();
}

export async function getPrograms() {
  const res = await fetch(`${API_BASE}/api/programs`);
  if (!res.ok) throw new Error(`Programs failed: ${res.status}`);
  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}
