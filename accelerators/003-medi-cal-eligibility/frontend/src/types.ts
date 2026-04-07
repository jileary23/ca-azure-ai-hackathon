export interface HealthStatus {
  status: string;
  service: string;
  mock_mode: boolean;
}

export interface EligibilityResult {
  program_type: string;
  likely_eligible: boolean;
  confidence: number;
  income_limit: number;
  fpl_percentage: number;
  factors: string[];
  required_documents: string[];
  next_steps: string[];
}

export interface Citation {
  source: string;
  text: string;
  regulation_ref: string | null;
}

export interface MediCalProgram {
  program_id: string;
  name: string;
  description: string;
  eligibility_criteria: string;
  income_limit: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  eligibility?: EligibilityResult | null;
  citations?: Citation[];
}
