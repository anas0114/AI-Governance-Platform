"""Smoke tests for the non-AI pages that write user references or aggregate data."""


def test_policy_lifecycle(client, auth_headers):
    created = client.post("/api/v1/policies/", json={"title": "Model Release Policy"}, headers=auth_headers)
    assert created.status_code == 201
    policy_id = created.json()["id"]

    updated = client.patch(f"/api/v1/policies/{policy_id}", json={"status": "approved"}, headers=auth_headers)
    assert updated.json()["status"] == "approved"
    assert client.delete(f"/api/v1/policies/{policy_id}", headers=auth_headers).status_code == 204


def test_ai_system_audit_and_finding(client, auth_headers):
    system = client.post("/api/v1/ai-systems/", json={"name": "Chatbot"}, headers=auth_headers)
    assert system.status_code == 201

    audit = client.post(
        "/api/v1/audits/", json={"ai_system_id": system.json()["id"], "title": "Launch audit"}, headers=auth_headers
    )
    assert audit.status_code == 201

    finding = client.post(
        "/api/v1/audits/findings",
        json={"audit_id": audit.json()["id"], "severity": "medium", "description": "Missing model card"},
        headers=auth_headers,
    )
    assert finding.status_code == 201


def test_dashboard_and_regulation_pages(client, auth_headers):
    dashboard = client.get("/api/v1/compliance/dashboard", headers=auth_headers)
    assert dashboard.status_code == 200
    assert "risk_breakdown" in dashboard.json()

    for path in ("/api/v1/regulations/", "/api/v1/compliance/frameworks", "/api/v1/compliance/assessments", "/api/v1/users/me"):
        assert client.get(path, headers=auth_headers).status_code == 200, path


def test_protected_endpoints_require_login(client):
    assert client.get("/api/v1/policies/").status_code == 401
