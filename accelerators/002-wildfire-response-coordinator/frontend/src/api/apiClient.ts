const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8002';

export async function postChat(message: string) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function getIncidents() {
  const res = await fetch(`${API_BASE}/api/incidents`);
  if (!res.ok) throw new Error(`Incidents failed: ${res.status}`);
  return res.json();
}

export async function getWeatherAlerts() {
  const res = await fetch(`${API_BASE}/api/weather/alerts`);
  if (!res.ok) throw new Error(`Weather alerts failed: ${res.status}`);
  return res.json();
}

export async function getEvacuationZones() {
  const res = await fetch(`${API_BASE}/api/evacuation/zones`);
  if (!res.ok) throw new Error(`Evacuation zones failed: ${res.status}`);
  return res.json();
}

export async function getPSPSStatus() {
  const res = await fetch(`${API_BASE}/api/psps/status`);
  if (!res.ok) throw new Error(`PSPS status failed: ${res.status}`);
  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}
