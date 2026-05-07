const API_BASE = import.meta.env.VITE_API_URL || '';

export async function postChat(message: string, language?: string, county?: string) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language, county }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function prescreenEligibility(params: {
  household_size: number;
  monthly_income: number;
  county: string;
  has_children?: boolean;
  age?: number;
}) {
  const res = await fetch(`${API_BASE}/api/eligibility/prescreen`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Prescreen failed: ${res.status}`);
  return res.json();
}

export async function getPrograms() {
  const res = await fetch(`${API_BASE}/api/programs`);
  if (!res.ok) throw new Error(`Programs failed: ${res.status}`);
  return res.json();
}

export async function getOffices(county: string) {
  const res = await fetch(`${API_BASE}/api/offices?county=${encodeURIComponent(county)}`);
  if (!res.ok) throw new Error(`Offices failed: ${res.status}`);
  return res.json();
}

export async function getLanguages() {
  const res = await fetch(`${API_BASE}/api/languages`);
  if (!res.ok) throw new Error(`Languages failed: ${res.status}`);
  return res.json();
}
