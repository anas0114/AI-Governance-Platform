export type RiskLevel = "minimal" | "limited" | "high" | "unacceptable" | "unclassified";

export interface AISystem {
  id: string;
  name: string;
  description?: string;
  owner?: string;
  risk_level: RiskLevel;
  lifecycle_stage: string;
  created_at: string;
  updated_at: string;
}
