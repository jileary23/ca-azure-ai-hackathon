const API_BASE = import.meta.env.VITE_API_URL || '';

export async function postChat(message: string, language?: string) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language: language || 'en' }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function getAlerts(zip?: string) {
  const params = zip ? `?zip=${encodeURIComponent(zip)}` : '';
  const res = await fetch(`${API_BASE}/api/alerts${params}`);
  if (!res.ok) throw new Error(`Alerts failed: ${res.status}`);
  return res.json();
}

export async function getShelters(zip?: string) {
  const params = zip ? `?zip=${encodeURIComponent(zip)}` : '';
  const res = await fetch(`${API_BASE}/api/shelters${params}`);
  if (!res.ok) throw new Error(`Shelters failed: ${res.status}`);
  return res.json();
}

export async function getAirQuality(zip?: string) {
  const params = zip ? `?zip=${encodeURIComponent(zip)}` : '';
  const res = await fetch(`${API_BASE}/api/air-quality${params}`);
  if (!res.ok) throw new Error(`Air quality failed: ${res.status}`);
  return res.json();
}
