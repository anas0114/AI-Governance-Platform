export type AgentName = "legal_research" | "compliance" | "risk_evaluation" | "governance_advisor";

export interface AgentQueryResponse {
  agent: AgentName;
  answer: string;
  session_id: string;
}

export interface OrchestrationResponse {
  answer: string;
  session_id: string;
  agent_trace: AgentName[];
}
