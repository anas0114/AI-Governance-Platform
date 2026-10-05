"""MCP server exposing the Audit System: audits and findings management.

Run with:  python -m app.mcp.audit_system_server
"""
from mcp.server.fastmcp import FastMCP
from sqlalchemy import func, select

from app.db.sync_session import SyncSessionLocal
from app.mcp.common import parse_uuid
from app.models.ai_system import AISystem
from app.models.audit import Audit, AuditFinding

mcp = FastMCP("audit-system")

VALID_AUDIT_STATUSES = {"open", "in_progress", "closed"}
VALID_SEVERITIES = {"low", "medium", "high", "critical"}


@mcp.tool()
def list_audits(ai_system_name: str | None = None, status: str | None = None) -> list[dict]:
    """List audits, optionally filtered by AI system name and/or status (open, in_progress, closed)."""
    with SyncSessionLocal() as db:
        query = select(Audit, AISystem).join(AISystem, Audit.ai_system_id == AISystem.id)
        if ai_system_name:
            query = query.where(AISystem.name.ilike(f"%{ai_system_name}%"))
        if status:
            query = query.where(Audit.status == status)
        rows = db.execute(query.order_by(Audit.created_at.desc())).all()

    return [
        {
            "id": str(audit.id),
            "title": audit.title,
            "ai_system": system.name,
            "status": audit.status,
            "created_at": audit.created_at.isoformat() if audit.created_at else None,
        }
        for audit, system in rows
    ]


@mcp.tool()
def create_audit(ai_system_name: str, title: str) -> dict:
    """Create a new audit run for a registered AI system."""
    with SyncSessionLocal() as db:
        system = db.execute(select(AISystem).where(AISystem.name.ilike(f"%{ai_system_name}%"))).scalars().first()
        if not system:
            return {"error": f"No AI system matching '{ai_system_name}' found."}

        audit = Audit(ai_system_id=system.id, title=title, status="open")
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return {"id": str(audit.id), "title": audit.title, "ai_system": system.name, "status": audit.status}


@mcp.tool()
def update_audit_status(audit_id: str, status: str) -> dict:
    """Update an audit's status (open, in_progress, closed)."""
    if status not in VALID_AUDIT_STATUSES:
        return {"error": f"Invalid status '{status}'. Must be one of {sorted(VALID_AUDIT_STATUSES)}."}

    with SyncSessionLocal() as db:
        audit = db.get(Audit, parse_uuid(audit_id, "audit_id"))
        if not audit:
            return {"error": f"Audit '{audit_id}' not found."}
        audit.status = status
        db.commit()
        db.refresh(audit)
        return {"id": str(audit.id), "status": audit.status}


@mcp.tool()
def list_findings(audit_id: str | None = None, status: str | None = None) -> list[dict]:
    """List audit findings, optionally filtered by audit id and/or status (open, resolved)."""
    with SyncSessionLocal() as db:
        query = select(AuditFinding)
        if audit_id:
            query = query.where(AuditFinding.audit_id == parse_uuid(audit_id, "audit_id"))
        if status:
            query = query.where(AuditFinding.status == status)
        findings = db.execute(query.order_by(AuditFinding.created_at.desc())).scalars().all()

    return [
        {
            "id": str(f.id),
            "audit_id": str(f.audit_id),
            "severity": f.severity,
            "description": f.description,
            "remediation": f.remediation,
            "status": f.status,
        }
        for f in findings
    ]


@mcp.tool()
def create_finding(audit_id: str, severity: str, description: str, remediation: str = "") -> dict:
    """Record a new finding against an audit (severity: low, medium, high, critical)."""
    if severity not in VALID_SEVERITIES:
        return {"error": f"Invalid severity '{severity}'. Must be one of {sorted(VALID_SEVERITIES)}."}

    with SyncSessionLocal() as db:
        audit = db.get(Audit, parse_uuid(audit_id, "audit_id"))
        if not audit:
            return {"error": f"Audit '{audit_id}' not found."}

        finding = AuditFinding(
            audit_id=audit.id, severity=severity, description=description, remediation=remediation, status="open"
        )
        db.add(finding)
        db.commit()
        db.refresh(finding)
        return {"id": str(finding.id), "severity": finding.severity, "status": finding.status}


@mcp.tool()
def resolve_finding(finding_id: str) -> dict:
    """Mark an audit finding as resolved."""
    with SyncSessionLocal() as db:
        finding = db.get(AuditFinding, parse_uuid(finding_id, "finding_id"))
        if not finding:
            return {"error": f"Finding '{finding_id}' not found."}
        finding.status = "resolved"
        db.commit()
        db.refresh(finding)
        return {"id": str(finding.id), "status": finding.status}


@mcp.tool()
def get_audit_summary() -> dict:
    """Aggregate audit stats: audits by status, open findings by severity."""
    with SyncSessionLocal() as db:
        audit_counts = dict(db.execute(select(Audit.status, func.count()).group_by(Audit.status)).all())
        finding_counts = dict(
            db.execute(
                select(AuditFinding.severity, func.count())
                .where(AuditFinding.status == "open")
                .group_by(AuditFinding.severity)
            ).all()
        )

    return {"audits_by_status": audit_counts, "open_findings_by_severity": finding_counts}


if __name__ == "__main__":
    mcp.run()
