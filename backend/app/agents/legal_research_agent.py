"""Legal Research Agent: researches applicable AI regulations and legal obligations."""
from app.agents.agent_factory import build_tool_agent
from app.agents.prompts import LEGAL_RESEARCH_AGENT_PROMPT
from app.agents.tools import search_policies, search_regulations

legal_research_agent = build_tool_agent(
    system_prompt=LEGAL_RESEARCH_AGENT_PROMPT,
    tools=[search_regulations, search_policies],
)
