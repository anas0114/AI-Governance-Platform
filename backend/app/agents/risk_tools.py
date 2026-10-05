"""Risk-related tools: rule-based classification and AI system risk lookups."""
from langchain_core.tools import tool
from sqlalchemy import select

from app.db.sync_session import SyncSessionLocal
from app.models.ai_system import AISystem
from app.models.audit import Audit, AuditFinding
from app.services.compliance_engine import classify_risk


@tool
def classify_ai_system_risk(system_description: str) -> str:
    """Classify the risk level (minimal/limited/high) of an AI system from a free-text description."""
    return classify_risk(system_description)


@tool
def get_ai_system_risk_profile(system_name: str) -> str:
    """Look up an AI system's registered risk level, lifecycle stage, and open audit findings by name."""
    with SyncSessionLocal() as db:
        system = db.execute(select(AISystem).where(AISystem.name.ilike(f"%{system_name}%"))).scalars().first()
        if not system:
            return f"No AI system matching '{system_name}' found in the registry."

        findings = (
            db.execute(
                select(AuditFinding)
                .join(Audit, AuditFinding.audit_id == Audit.id)
                .where(Audit.ai_system_id == system.id, AuditFinding.status == "open")
            )
            .scalars()
            .all()
        )

    findings_text = "; ".join(f"[{f.severity}] {f.description}" for f in findings) or "none"
    return (
        f"{system.name}: risk_level={system.risk_level}, lifecycle_stage={system.lifecycle_stage}, "
        f"open_findings={findings_text}"
    )


@tool
def list_high_risk_ai_systems() -> str:
    """List all AI systems currently classified as high or unacceptable risk."""
    with SyncSessionLocal() as db:
        systems = (
            db.execute(select(AISystem).where(AISystem.risk_level.in_(["high", "unacceptable"])))
            .scalars()
            .all()
        )

    if not systems:
        return "No high-risk AI systems registered."
    return "\n".join(f"- {s.name} ({s.risk_level}, {s.lifecycle_stage})" for s in systems)
