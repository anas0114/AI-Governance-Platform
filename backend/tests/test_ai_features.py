"""End-to-end tests for every AI feature: research, copilot, documents, agents, orchestration, collaboration."""
import httpx
import openai
import pytest

from app.core.config import settings
from app.db.sync_session import SyncSessionLocal
from app.models.ai_system import AISystem
from app.models.audit import Audit, AuditFinding
from app.models.compliance import ComplianceAssessment, ComplianceControl, ComplianceFramework
from app.models.policy import Policy

ORIGIN = {"Origin": "http://localhost:3000"}


def _openai_error(cls, status_code: int, body: dict | None = None):
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    return cls("provider error", response=httpx.Response(status_code, request=request), body=body)


@pytest.fixture(scope="module", autouse=True)
def seed_governance_data(client):
    with SyncSessionLocal() as db:
        framework = ComplianceFramework(name="EU AI Act", description="EU AI regulation")
        system = AISystem(name="Credit Scoring Model", description="Loan approvals", risk_level="high")
        db.add_all([framework, system])
        db.flush()
        audit = Audit(ai_system_id=system.id, title="Q3 Audit", status="open")
        db.add_all(
            [
                ComplianceControl(framework_id=framework.id, code="Art.9", title="Risk management system"),
                ComplianceAssessment(ai_system_id=system.id, framework_id=framework.id, status="failed", score="48%"),
                Policy(title="Responsible AI Usage Policy", status="draft", version=1),
                audit,
            ]
        )
        db.flush()
        db.add(AuditFinding(audit_id=audit.id, severity="high", description="Missing bias testing", status="open"))
        db.commit()


@pytest.fixture(scope="module")
def indexed_clause(client, auth_headers):
    regulation = client.post(
        "/api/v1/regulations/", json={"title": "EU Artificial Intelligence Act"}, headers=auth_headers
    ).json()
    response = client.post(
        f"/api/v1/regulations/{regulation['id']}/clauses",
        json={
            "clause_number": "Article 9",
            "title": "Risk management system",
            "text": "A risk management system shall be established for high-risk AI systems.",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


# --- Error handling: the original bug surfaced as a fake "CORS" error in the browser. ---


def test_missing_api_key_returns_clear_503_with_cors(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "your-openai-api-key")
    response = client.post(
        "/api/v1/agents/orchestrate", json={"query": "hi"}, headers={**auth_headers, **ORIGIN}
    )
    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]
    assert response.headers["access-control-allow-origin"] == ORIGIN["Origin"]


@pytest.mark.parametrize(
    ("exc", "status_code", "expected_text"),
    [
        (_openai_error(openai.AuthenticationError, 401), 503, "API key was rejected"),
        (_openai_error(openai.RateLimitError, 429, {"code": "insufficient_quota"}), 429, "no remaining quota"),
        (_openai_error(openai.RateLimitError, 429), 429, "rate limit"),
        (RuntimeError("unexpected boom"), 500, "Internal server error"),
    ],
)
def test_ai_failures_return_json_errors_with_cors(
    client, auth_headers, inject_llm_failure, exc, status_code, expected_text
):
    inject_llm_failure(exc)
    for path, body in [
        ("/api/v1/agents/compliance", {"query": "status?"}),
        ("/api/v1/collaboration/", {"query": "status?"}),
    ]:
        response = client.post(path, json=body, headers={**auth_headers, **ORIGIN})
        assert response.status_code == status_code, path
        assert expected_text in response.json()["detail"], path
        assert response.headers["access-control-allow-origin"] == ORIGIN["Origin"], path


# --- Research workspace and copilot (RAG with citations). ---


def test_research_query_answers_with_citations_and_is_saved(client, auth_headers, indexed_clause):
    response = client.post(
        "/api/v1/research/queries",
        json={"query": "risk management high-risk AI systems", "collection": "regulations"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["answer"].startswith("Final answer")
    assert any(s.get("clause_number") == "Article 9" for s in body["sources"])
    assert all(s["citation"] == i for i, s in enumerate(body["sources"], start=1))

    history = client.get("/api/v1/research/queries", headers=auth_headers).json()
    assert any(q["id"] == body["id"] for q in history)


def test_research_query_on_empty_collection_does_not_fail(client, auth_headers):
    response = client.post(
        "/api/v1/research/queries", json={"query": "anything", "collection": "evidence"}, headers=auth_headers
    )
    assert response.status_code == 201
    assert "couldn't find" in response.json()["answer"]


def test_copilot_chat_answers_with_sources(client, auth_headers, indexed_clause):
    response = client.post(
        "/api/v1/chat/",
        json={"query": "risk management high-risk AI systems", "collection": "regulations"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["sources"]


def test_research_notes_crud(client, auth_headers):
    created = client.post(
        "/api/v1/research/notes", json={"title": "Note", "content": "Findings"}, headers=auth_headers
    )
    assert created.status_code == 201
    note_id = created.json()["id"]
    assert client.delete(f"/api/v1/research/notes/{note_id}", headers=auth_headers).status_code == 204


# --- Document ingestion. ---


def test_document_upload_is_indexed_searchable_and_path_safe(client, auth_headers):
    upload = client.post(
        "/api/v1/documents/upload",
        files={"file": ("../../evil.txt", b"Evidence of quarterly bias testing for the credit model.", "text/plain")},
        data={"collection": "evidence"},
        headers=auth_headers,
    )
    assert upload.status_code == 201
    document = upload.json()
    assert document["filename"] == "evil.txt"
    assert document["chunk_count"] > 0

    hits = client.get(
        f"/api/v1/documents/{document['id']}/search", params={"q": "bias testing"}, headers=auth_headers
    ).json()
    assert any("bias testing" in h["content"] for h in hits)

    assert client.delete(f"/api/v1/documents/{document['id']}", headers=auth_headers).status_code == 204


def test_document_upload_rejects_unknown_collection(client, auth_headers):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("a.txt", b"text", "text/plain")},
        data={"collection": "../secrets"},
        headers=auth_headers,
    )
    assert response.status_code == 400


# --- Governance agents: each specialist must run its real tools against the database. ---


@pytest.mark.parametrize(
    ("endpoint", "agent_name", "expected_tool_output"),
    [
        ("legal-research", "legal_research", "risk management system"),
        ("compliance", "compliance", "Art.9 Risk management system"),
        ("risk-evaluation", "risk_evaluation", "Credit Scoring Model: risk_level=high"),
        ("governance-advisor", "governance_advisor", "Missing bias testing"),
    ],
)
def test_specialist_agent_uses_its_tools(client, auth_headers, indexed_clause, endpoint, agent_name, expected_tool_output):
    response = client.post(f"/api/v1/agents/{endpoint}", json={"query": "assess"}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["agent"] == agent_name
    assert "Tool results" in body["answer"]
    assert expected_tool_output in body["answer"]


def test_specialist_agent_keeps_session_memory(client, auth_headers):
    first = client.post("/api/v1/agents/compliance", json={"query": "first"}, headers=auth_headers).json()
    second = client.post(
        "/api/v1/agents/compliance",
        json={"query": "follow-up", "session_id": first["session_id"]},
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert second.json()["session_id"] == first["session_id"]


def test_orchestrator_routes_to_exactly_one_agent_per_question(client, auth_headers):
    first = client.post("/api/v1/agents/orchestrate", json={"query": "Are we compliant?"}, headers=auth_headers)
    assert first.status_code == 200
    assert first.json()["agent_trace"] == ["compliance"]
    assert "Art.9" in first.json()["answer"]

    second = client.post(
        "/api/v1/agents/orchestrate",
        json={"query": "And now?", "session_id": first.json()["session_id"]},
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert second.json()["agent_trace"] == ["compliance"]


# --- Multi-agent collaboration and audit trail. ---


def test_collaboration_runs_all_agents_in_order_and_is_auditable(client, auth_headers, indexed_clause):
    response = client.post(
        "/api/v1/collaboration/", json={"query": "Should we deploy the credit model?"}, headers=auth_headers
    )
    assert response.status_code == 201
    run = response.json()

    assert [s["agent_name"] for s in run["steps"]] == ["research", "compliance", "risk_evaluation", "governance_advisor"]
    assert run["final_recommendation"].startswith("Final answer")
    for step in run["steps"]:
        assert step["duration_ms"] is not None
        assert any(e["type"] == "tool" for e in step["events"]), step["agent_name"]

    runs = client.get("/api/v1/collaboration/", headers=auth_headers).json()
    assert any(r["id"] == run["run_id"] for r in runs)

    detail = client.get(f"/api/v1/collaboration/{run['run_id']}", headers=auth_headers).json()
    assert [s["agent_name"] for s in detail["steps"]] == [s["agent_name"] for s in run["steps"]]
    assert detail["final_recommendation"] == run["final_recommendation"]
