from pydantic import BaseModel


class RiskBreakdown(BaseModel):
    minimal: int = 0
    limited: int = 0
    high: int = 0
    unacceptable: int = 0
    unclassified: int = 0


class AssessmentBreakdown(BaseModel):
    pending: int = 0
    in_progress: int = 0
    passed: int = 0
    failed: int = 0


class PolicyBreakdown(BaseModel):
    draft: int = 0
    in_review: int = 0
    approved: int = 0
    retired: int = 0


class ComplianceDashboardSummary(BaseModel):
    total_ai_systems: int
    total_policies: int
    total_audits: int
    open_findings: int
    average_compliance_score: float
    risk_breakdown: RiskBreakdown
    assessment_breakdown: AssessmentBreakdown
    policy_breakdown: PolicyBreakdown
