import type {
  AnalysisResult,
  EvidenceQueryRequest,
  EvidenceQueryResponse,
  VideoSubmitRequest,
  VideoSubmitResponse,
} from "../types";

const BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

export const api = {
  submitVideo(body: VideoSubmitRequest) {
    return request<VideoSubmitResponse>("/api/analyze", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  getAnalysis(jobId: string) {
    return request<AnalysisResult>(`/api/analysis/${jobId}`);
  },

  queryEvidence(body: EvidenceQueryRequest) {
    return request<EvidenceQueryResponse>("/api/query", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};
