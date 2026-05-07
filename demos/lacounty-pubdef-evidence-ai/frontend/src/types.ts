// Shared TypeScript types mirroring backend Pydantic schemas

export type AnalysisStatus = "pending" | "processing" | "completed" | "failed";
export type SpeakerRole = "officer" | "suspect" | "witness" | "unknown";
export type Significance = "high" | "medium" | "low";

export interface Speaker {
  id: string;
  role: SpeakerRole;
  label: string;
  total_speech_seconds: number;
}

export interface TranscriptLine {
  speaker: string;
  speaker_role: SpeakerRole;
  start_seconds: number;
  end_seconds: number;
  text: string;
  confidence: number;
  timestamp?: string;
}

export interface KeyMoment {
  timestamp_seconds: number;
  timestamp_label: string;
  description: string;
  significance: Significance;
  category: string;
}

export interface EvidenceSummary {
  narrative: string;
  timeline: string[];
  miranda_rights_read: boolean | null;
  miranda_timestamp: string | null;
  use_of_force_detected: boolean;
  consent_given: boolean | null;
  discrepancies: string[];
  defense_considerations: string[];
}

export interface AnalysisResult {
  job_id: string;
  case_number: string;
  status: AnalysisStatus;
  video_duration_seconds: number | null;
  created_at: string;
  completed_at: string | null;
  speakers: Speaker[];
  transcript: TranscriptLine[];
  key_moments: KeyMoment[];
  summary: EvidenceSummary | null;
  video_indexer_video_id: string | null;
  error: string | null;
}

export interface VideoSubmitRequest {
  video_url?: string;
  case_number: string;
  incident_date?: string;
  description?: string;
  use_mock?: boolean;
}

export interface VideoSubmitResponse {
  job_id: string;
  status: AnalysisStatus;
  case_number: string;
  message: string;
}

export interface EvidenceQueryRequest {
  job_id: string;
  question: string;
}

export interface EvidenceQueryResponse {
  question: string;
  answer: string;
  supporting_timestamps: string[];
  confidence: "high" | "medium" | "low";
}
