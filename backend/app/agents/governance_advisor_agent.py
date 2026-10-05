"""Governance Advisor Agent: synthesizes policy, risk, and compliance context into recommendations."""
from app.agents.agent_factory import build_tool_agent
from app.agents.governance_tools import get_policy_status, list_open_audit_findings, list_policies_by_status
from app.agents.prompts import GOVERNANCE_ADVISOR_AGENT_PROMPT
from app.agents.risk_tools import get_ai_system_risk_profile, list_high_risk_ai_systems

governance_advisor_agent = build_tool_agent(
    system_prompt=GOVERNANCE_ADVISOR_AGENT_PROMPT,
    tools=[
        get_policy_status,
        list_policies_by_status,
        list_open_audit_findings,
        get_ai_system_risk_profile,
        list_high_risk_ai_systems,
    ],
)
