"""Compliance-related tools: framework/control lookups and assessment status."""
from langchain_core.tools import tool
from sqlalchemy import select

from app.db.sync_session import SyncSessionLocal
from app.models.ai_system import AISystem
from app.models.compliance import ComplianceAssessment, ComplianceControl, ComplianceFramework


@tool
def list_compliance_frameworks() -> str:
    """List all compliance frameworks tracked in the platform (e.g. EU AI Act, NIST AI RMF, ISO 42001)."""
    with SyncSessionLocal() as db:
        frameworks = db.execute(select(ComplianceFramework)).scalars().all()

    if not frameworks:
        return "No compliance frameworks found."
    return "\n".join(f"- {f.name}: {f.description or 'no description'}" for f in frameworks)


@tool
def get_framework_controls(framework_name: str) -> str:
    """Get the controls/requirements defined under a named compliance framework."""
    with SyncSessionLocal() as db:
        framework = (
            db.execute(select(ComplianceFramework).where(ComplianceFramework.name.ilike(f"%{framework_name}%")))
            .scalars()
            .first()
        )
        if not framework:
            return f"No framework matching '{framework_name}' found."

        controls = (
            db.execute(select(ComplianceControl).where(ComplianceControl.framework_id == framework.id))
            .scalars()
            .all()
        )

    if not controls:
        return f"No controls recorded yet for {framework.name}."
    return "\n".join(f"- {c.code} {c.title}: {c.description or ''}" for c in controls)


@tool
def get_compliance_assessments(ai_system_name: str = "") -> str:
    """Get compliance assessment status and scores, optionally filtered by AI system name."""
    with SyncSessionLocal() as db:
        query = (
            select(ComplianceAssessment, AISystem, ComplianceFramework)
            .join(AISystem, ComplianceAssessment.ai_system_id == AISystem.id)
            .join(ComplianceFramework, ComplianceAssessment.framework_id == ComplianceFramework.id)
        )
        if ai_system_name:
            query = query.where(AISystem.name.ilike(f"%{ai_system_name}%"))
        rows = db.execute(query).all()

    if not rows:
        return "No matching compliance assessments found."
    return "\n".join(
        f"- {system.name} vs {framework.name}: {assessment.status} (score: {assessment.score or 'n/a'})"
        for assessment, system, framework in rows
    )
