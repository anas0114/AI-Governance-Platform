export interface RiskBreakdown {
  minimal: number;
  limited: number;
  high: number;
  unacceptable: number;
  unclassified: number;
}

export interface AssessmentBreakdown {
  pending: number;
  in_progress: number;
  passed: number;
  failed: number;
}

export interface PolicyBreakdown {
  draft: number;
  in_review: number;
  approved: number;
  retired: number;
}

export interface ComplianceDashboardSummary {
  total_ai_systems: number;
  total_policies: number;
  total_audits: number;
  open_findings: number;
  average_compliance_score: number;
  risk_breakdown: RiskBreakdown;
  assessment_breakdown: AssessmentBreakdown;
  policy_breakdown: PolicyBreakdown;
}
