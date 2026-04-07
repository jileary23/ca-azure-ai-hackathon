const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8007";

export async function postChat(message: string, language?: string) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function lookupClaimStatus(params: {
  claim_id?: string;
  ssn_last4?: string;
  last_name?: string;
}) {
  const res = await fetch(`${API_BASE}/api/claim-status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Claim status failed: ${res.status}`);
  return res.json();
}

export async function calculateBenefits(params: {
  claim_type: string;
  quarterly_wages: number[];
}) {
  const res = await fetch(`${API_BASE}/api/benefits/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Calculation failed: ${res.status}`);
  return res.json();
}

export async function getTimeline(claimType: string) {
  const res = await fetch(
    `${API_BASE}/api/claims/${encodeURIComponent(claimType)}/timeline`
  );
  if (!res.ok) throw new Error(`Timeline failed: ${res.status}`);
  return res.json();
}