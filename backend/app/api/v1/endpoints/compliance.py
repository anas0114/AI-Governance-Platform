from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.ai_system import AISystem
from app.models.audit import Audit, AuditFinding
from app.models.compliance import ComplianceAssessment, ComplianceFramework
from app.models.policy import Policy
from app.schemas.compliance import ComplianceAssessmentCreate, ComplianceAssessmentRead, ComplianceFrameworkRead
from app.schemas.dashboard import (
    AssessmentBreakdown,
    ComplianceDashboardSummary,
    PolicyBreakdown,
    RiskBreakdown,
)

router = APIRouter()


@router.get("/frameworks", response_model=list[ComplianceFrameworkRead])
async def list_frameworks(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> list[ComplianceFramework]:
    result = await db.execute(select(ComplianceFramework))
    return list(result.scalars().all())


@router.get("/dashboard", response_model=ComplianceDashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> ComplianceDashboardSummary:
    """Aggregate stats powering the Compliance Dashboard module."""
    total_ai_systems = (await db.execute(select(func.count()).select_from(AISystem))).scalar_one()
    total_policies = (await db.execute(select(func.count()).select_from(Policy))).scalar_one()
    total_audits = (await db.execute(select(func.count()).select_from(Audit))).scalar_one()
    open_findings = (
        await db.execute(select(func.count()).select_from(AuditFinding).where(AuditFinding.status == "open"))
    ).scalar_one()

    risk_counts = dict(
        (await db.execute(select(AISystem.risk_level, func.count()).group_by(AISystem.risk_level))).all()
    )
    assessment_counts = dict(
        (
            await db.execute(
                select(ComplianceAssessment.status, func.count()).group_by(ComplianceAssessment.status)
            )
        ).all()
    )
    policy_counts = dict(
        (await db.execute(select(Policy.status, func.count()).group_by(Policy.status))).all()
    )

    scores = (
        (await db.execute(select(ComplianceAssessment.score).where(ComplianceAssessment.score.is_not(None))))
        .scalars()
        .all()
    )
    numeric_scores = [float(s.rstrip("%")) for s in scores if s]
    average_score = round(sum(numeric_scores) / len(numeric_scores), 1) if numeric_scores else 0.0

    return ComplianceDashboardSummary(
        total_ai_systems=total_ai_systems,
        total_policies=total_policies,
        total_audits=total_audits,
        open_findings=open_findings,
        average_compliance_score=average_score,
        risk_breakdown=RiskBreakdown(**risk_counts),
        assessment_breakdown=AssessmentBreakdown(**assessment_counts),
        policy_breakdown=PolicyBreakdown(**policy_counts),
    )


@router.get("/assessments", response_model=list[ComplianceAssessmentRead])
async def list_assessments(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> list[ComplianceAssessment]:
    result = await db.execute(select(ComplianceAssessment))
    return list(result.scalars().all())


@router.post("/assessments", response_model=ComplianceAssessmentRead, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_in: ComplianceAssessmentCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> ComplianceAssessment:
    assessment = ComplianceAssessment(**assessment_in.model_dump(), status="pending")
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return assessment
