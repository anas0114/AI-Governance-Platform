"""Compliance Agent: evaluates AI systems against tracked compliance frameworks."""
from app.agents.agent_factory import build_tool_agent
from app.agents.compliance_tools import get_compliance_assessments, get_framework_controls, list_compliance_frameworks
from app.agents.prompts import COMPLIANCE_AGENT_PROMPT
from app.agents.tools import search_policies, search_regulations

compliance_agent = build_tool_agent(
    system_prompt=COMPLIANCE_AGENT_PROMPT,
    tools=[list_compliance_frameworks, get_framework_controls, get_compliance_assessments, search_regulations, search_policies],
)
