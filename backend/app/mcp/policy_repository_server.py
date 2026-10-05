"""MCP server exposing the Policy Repository: CRUD + semantic search over policies.

Run with:  python -m app.mcp.policy_repository_server
"""
import uuid

from mcp.server.fastmcp import FastMCP
from sqlalchemy import select

from app.db.sync_session import SyncSessionLocal
from app.mcp.common import parse_uuid
from app.models.policy import Policy
from app.rag.ingestion import ingest_text
from app.rag.retrieval import retrieve

mcp = FastMCP("policy-repository")

VALID_STATUSES = {"draft", "in_review", "approved", "retired"}


def _serialize(policy: Policy) -> dict:
    return {
        "id": str(policy.id),
        "title": policy.title,
        "description": policy.description,
        "version": policy.version,
        "status": policy.status,
        "created_at": policy.created_at.isoformat() if policy.created_at else None,
        "updated_at": policy.updated_at.isoformat() if policy.updated_at else None,
    }


@mcp.tool()
def list_policies(status: str | None = None) -> list[dict]:
    """List governance policies, optionally filtered by status (draft, in_review, approved, retired)."""
    with SyncSessionLocal() as db:
        query = select(Policy)
        if status:
            query = query.where(Policy.status == status)
        policies = db.execute(query.order_by(Policy.updated_at.desc())).scalars().all()
    return [_serialize(p) for p in policies]


@mcp.tool()
def get_policy(policy_id: str) -> dict:
    """Get the full detail (including content) of a policy by its id."""
    with SyncSessionLocal() as db:
        policy = db.get(Policy, parse_uuid(policy_id, "policy_id"))
        if not policy:
            return {"error": f"Policy '{policy_id}' not found."}
        result = _serialize(policy)
        result["content"] = policy.content
        return result


@mcp.tool()
def create_policy(title: str, description: str = "", content: str = "") -> dict:
    """Create a new draft policy and embed its content into ChromaDB for the AI Copilot to cite."""
    with SyncSessionLocal() as db:
        policy = Policy(title=title, description=description, content=content, version=1, status="draft")
        db.add(policy)
        db.commit()
        db.refresh(policy)

        if content:
            ingest_text("policies", str(policy.id), f"{title}\n{content}", metadata={"filename": title})

        return _serialize(policy)


@mcp.tool()
def update_policy_status(policy_id: str, status: str) -> dict:
    """Transition a policy's approval status (draft -> in_review -> approved, or retired)."""
    if status not in VALID_STATUSES:
        return {"error": f"Invalid status '{status}'. Must be one of {sorted(VALID_STATUSES)}."}

    with SyncSessionLocal() as db:
        policy = db.get(Policy, parse_uuid(policy_id, "policy_id"))
        if not policy:
            return {"error": f"Policy '{policy_id}' not found."}
        policy.status = status
        db.commit()
        db.refresh(policy)
        return _serialize(policy)


@mcp.tool()
def search_policies(query: str) -> list[dict]:
    """Semantic search over embedded policy text for a natural-language query."""
    chunks = retrieve(query, "policies")
    return [{"content": c.content, "metadata": c.metadata, "score": c.score} for c in chunks]


if __name__ == "__main__":
    mcp.run()
