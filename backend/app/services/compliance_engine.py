"""Rule-based compliance scoring helpers, complementing LLM-based assessments."""


def score_assessment(passed_controls: int, total_controls: int) -> str:
    if total_controls == 0:
        return "0%"
    percentage = round((passed_controls / total_controls) * 100)
    return f"{percentage}%"


def classify_risk(system_description: str) -> str:
    """Very simple keyword-based classifier as a placeholder for the LangGraph risk-classification node."""
    text = system_description.lower()
    if any(k in text for k in ["biometric", "law enforcement", "critical infrastructure"]):
        return "high"
    if any(k in text for k in ["chatbot", "recommendation", "profiling"]):
        return "limited"
    return "minimal"
