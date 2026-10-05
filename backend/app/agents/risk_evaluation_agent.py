"""Risk Evaluation Agent: classifies and reports on AI system risk levels."""
from app.agents.agent_factory import build_tool_agent
from app.agents.prompts import RISK_EVALUATION_AGENT_PROMPT
from app.agents.risk_tools import classify_ai_system_risk, get_ai_system_risk_profile, list_high_risk_ai_systems

risk_evaluation_agent = build_tool_agent(
    system_prompt=RISK_EVALUATION_AGENT_PROMPT,
    tools=[classify_ai_system_risk, get_ai_system_risk_profile, list_high_risk_ai_systems],
)
