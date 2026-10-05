"""MCP server exposing the Compliance Tool: frameworks, controls, assessments, dashboard stats.

Run with:  python -m app.mcp.compliance_tool_server
"""
from mcp.server.fastmcp import FastMCP
from sqlalchemy import func, select

from app.db.sync_session import SyncSessionLocal
from app.mcp.common import parse_uuid
from app.models.ai_system import AISystem
from app.models.compliance import ComplianceAssessment, ComplianceControl, ComplianceFramework

mcp = FastMCP("compliance-tool")

VALID_ASSESSMENT_STATUSES = {"pending", "in_progress", "passed", "failed"}


@mcp.tool()
def list_frameworks() -> list[dict]:
    """List all compliance frameworks tracked in the platform (e.g. EU AI Act, NIST AI RMF, ISO 42001)."""
    with SyncSessionLocal() as db:
        frameworks = db.execute(select(ComplianceFramework)).scalars().all()
    return [{"id": str(f.id), "name": f.name, "description": f.description} for f in frameworks]


@mcp.tool()
def get_framework_controls(framework_name: str) -> list[dict]:
    """Get the controls/requirements defined under a named compliance framework."""
    with SyncSessionLocal() as db:
        framework = (
            db.execute(select(ComplianceFramework).where(ComplianceFramework.name.ilike(f"%{framework_name}%")))
            .scalars()
            .first()
        )
        if not framework:
            return [{"error": f"No framework matching '{framework_name}' found."}]

        controls = (
            db.execute(select(ComplianceControl).where(ComplianceControl.framework_id == framework.id))
            .scalars()
            .all()
        )
    return [{"id": str(c.id), "code": c.code, "title": c.title, "description": c.description} for c in controls]


@mcp.tool()
def list_assessments(ai_system_name: str | None = None) -> list[dict]:
    """List compliance assessments (status/score), optionally filtered by AI system name."""
    with SyncSessionLocal() as db:
        query = (
            select(ComplianceAssessment, AISystem, ComplianceFramework)
            .join(AISystem, ComplianceAssessment.ai_system_id == AISystem.id)
            .join(ComplianceFramework, ComplianceAssessment.framework_id == ComplianceFramework.id)
        )
        if ai_system_name:
            query = query.where(AISystem.name.ilike(f"%{ai_system_name}%"))
        rows = db.execute(query).all()

    return [
        {
            "id": str(assessment.id),
            "ai_system": system.name,
            "framework": framework.name,
            "status": assessment.status,
            "score": assessment.score,
        }
        for assessment, system, framework in rows
    ]


@mcp.tool()
def create_assessment(ai_system_name: str, framework_name: str) -> dict:
    """Create a new pending compliance assessment for an AI system against a framework."""
    with SyncSessionLocal() as db:
        system = db.execute(select(AISystem).where(AISystem.name.ilike(f"%{ai_system_name}%"))).scalars().first()
        if not system:
            return {"error": f"No AI system matching '{ai_system_name}' found."}

        framework = (
            db.execute(select(ComplianceFramework).where(ComplianceFramework.name.ilike(f"%{framework_name}%")))
            .scalars()
            .first()
        )
        if not framework:
            return {"error": f"No framework matching '{framework_name}' found."}

        assessment = ComplianceAssessment(ai_system_id=system.id, framework_id=framework.id, status="pending")
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        return {
            "id": str(assessment.id),
            "ai_system": system.name,
            "framework": framework.name,
            "status": assessment.status,
        }


@mcp.tool()
def update_assessment_status(assessment_id: str, status: str, score: str | None = None) -> dict:
    """Update a compliance assessment's status (pending, in_progress, passed, failed) and optional score."""
    if status not in VALID_ASSESSMENT_STATUSES:
        return {"error": f"Invalid status '{status}'. Must be one of {sorted(VALID_ASSESSMENT_STATUSES)}."}

    with SyncSessionLocal() as db:
        assessment = db.get(ComplianceAssessment, parse_uuid(assessment_id, "assessment_id"))
        if not assessment:
            return {"error": f"Assessment '{assessment_id}' not found."}
        assessment.status = status
        if score is not None:
            assessment.score = score
        db.commit()
        db.refresh(assessment)
        return {"id": str(assessment.id), "status": assessment.status, "score": assessment.score}


@mcp.tool()
def get_compliance_dashboard() -> dict:
    """Aggregate compliance stats: risk breakdown, assessment status counts, average score."""
    with SyncSessionLocal() as db:
        risk_counts = dict(db.execute(select(AISystem.risk_level, func.count()).group_by(AISystem.risk_level)).all())
        assessment_counts = dict(
            db.execute(select(ComplianceAssessment.status, func.count()).group_by(ComplianceAssessment.status)).all()
        )
        scores = (
            db.execute(select(ComplianceAssessment.score).where(ComplianceAssessment.score.is_not(None)))
            .scalars()
            .all()
        )

    numeric_scores = [float(s.rstrip("%")) for s in scores if s]
    average_score = round(sum(numeric_scores) / len(numeric_scores), 1) if numeric_scores else 0.0

    return {
        "risk_breakdown": risk_counts,
        "assessment_breakdown": assessment_counts,
        "average_compliance_score": average_score,
    }


if __name__ == "__main__":
    mcp.run()
