"""Governance-related tools: policy status and audit finding lookups."""
from langchain_core.tools import tool
from sqlalchemy import select

from app.db.sync_session import SyncSessionLocal
from app.models.audit import AuditFinding
from app.models.policy import Policy


@tool
def get_policy_status(policy_title: str) -> str:
    """Look up a governance policy's current status and version by title."""
    with SyncSessionLocal() as db:
        policy = db.execute(select(Policy).where(Policy.title.ilike(f"%{policy_title}%"))).scalars().first()

    if not policy:
        return f"No policy matching '{policy_title}' found."
    return f"{policy.title}: status={policy.status}, version={policy.version}"


@tool
def list_policies_by_status(status: str) -> str:
    """List governance policies filtered by status: draft, in_review, approved, or retired."""
    with SyncSessionLocal() as db:
        policies = db.execute(select(Policy).where(Policy.status == status)).scalars().all()

    if not policies:
        return f"No policies with status '{status}'."
    return "\n".join(f"- {p.title} (v{p.version})" for p in policies)


@tool
def list_open_audit_findings() -> str:
    """List all open audit findings across every audit, with severity."""
    with SyncSessionLocal() as db:
        findings = db.execute(select(AuditFinding).where(AuditFinding.status == "open")).scalars().all()

    if not findings:
        return "No open audit findings."
    return "\n".join(f"- [{f.severity}] {f.description}" for f in findings)
