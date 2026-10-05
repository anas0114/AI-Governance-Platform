export interface CollaborationEvent {
  type: string;
  name: string;
  phase: "start" | "end" | "error";
  detail?: string;
  duration_ms?: number | null;
}

export interface CollaborationStep {
  agent_name: string;
  output: string;
  duration_ms: number | null;
  events: CollaborationEvent[];
}

export interface CollaborationResponse {
  run_id: string;
  session_id: string;
  query: string;
  final_recommendation: string;
  steps: CollaborationStep[];
}

export interface CollaborationRunSummary {
  id: string;
  query: string;
  session_id: string;
  final_recommendation: string | null;
  created_at: string;
}
