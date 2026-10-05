export interface ComplianceFramework {
  id: string;
  name: string;
  description?: string;
}

export interface ComplianceAssessment {
  id: string;
  ai_system_id: string;
  framework_id: string;
  status: "pending" | "in_progress" | "passed" | "failed";
  score?: string;
  created_at: string;
}
