const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8006";

export async function postChat(
  message: string,
  language?: string,
  agencyFilter?: string[]
) {
  const body: Record<string, unknown> = { message };
  if (language) body.language = language;
  if (agencyFilter) body.agency_filter = agencyFilter;

  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function searchDocuments(query: string, agency?: string) {
  const params = new URLSearchParams({ query });
  if (agency) params.set("agency", agency);

  const res = await fetch(`${API_BASE}/api/search?${params}`);
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
}

export async function getAgencies(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/agencies`);
  if (!res.ok) throw new Error(`Agencies failed: ${res.status}`);
  return res.json();
}

export async function getExperts(
  topic: string
): Promise<import("../types").ExpertInfo[]> {
  const res = await fetch(
    `${API_BASE}/api/experts?topic=${encodeURIComponent(topic)}`
  );
  if (!res.ok) throw new Error(`Experts failed: ${res.status}`);
  return res.json();
}
