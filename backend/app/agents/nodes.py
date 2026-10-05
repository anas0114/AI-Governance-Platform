from app.agents.state import GovernanceAgentState
from app.rag.chain import RAG_SYSTEM_PROMPT, get_llm
from app.rag.citation import build_context_and_sources
from app.rag.retrieval import retrieve
from app.services.compliance_engine import classify_risk


def retrieve_node(state: GovernanceAgentState) -> dict:
    """Retrieve relevant chunks from ChromaDB and build numbered citation context."""
    chunks = retrieve(state["query"], state["collection"])
    context, sources = build_context_and_sources(chunks)
    return {
        "retrieved_docs": [chunk.content for chunk in chunks],
        "context": context,
        "sources": sources,
    }


def classify_risk_node(state: GovernanceAgentState) -> dict:
    """Classify AI-system risk based on the retrieved context (used in assessment workflows)."""
    context = "\n".join(state["retrieved_docs"])
    return {"risk_level": classify_risk(context)}


def generate_answer_node(state: GovernanceAgentState) -> dict:
    """Generate an answer grounded in the retrieved context, citing sources as [1], [2], ..."""
    if not state["retrieved_docs"]:
        answer = "I couldn't find any relevant information in the knowledge base to answer that."
        return {"answer": answer, "messages": [answer]}

    llm = get_llm()
    prompt = f"{RAG_SYSTEM_PROMPT.format(context=state['context'])}\n\nQuestion: {state['query']}"
    response = llm.invoke(prompt)
    return {"answer": response.content, "messages": [response.content]}
