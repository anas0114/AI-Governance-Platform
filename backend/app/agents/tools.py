"""Vector-search tools shared by every specialist agent."""
from langchain.tools import tool

from app.rag.retrieval import retrieve


@tool
def search_policies(query: str) -> str:
    """Search the policies collection in ChromaDB for relevant text chunks."""
    chunks = retrieve(query, "policies")
    return "\n".join(chunk.content for chunk in chunks) if chunks else "No relevant policies found."


@tool
def search_regulations(query: str) -> str:
    """Search the regulations collection in ChromaDB for relevant text chunks."""
    chunks = retrieve(query, "regulations")
    return "\n".join(chunk.content for chunk in chunks) if chunks else "No relevant regulations found."


@tool
def search_evidence(query: str) -> str:
    """Search the uploaded evidence/audit-support documents collection in ChromaDB."""
    chunks = retrieve(query, "evidence")
    return "\n".join(chunk.content for chunk in chunks) if chunks else "No relevant evidence found."


@tool
def search_industry_standards(query: str) -> str:
    """Search industry standards such as NIST AI RMF and ISO/IEC 42001."""
    chunks = retrieve(query, "industry_standards")
    return "\n".join(chunk.content for chunk in chunks) if chunks else "No relevant industry standards found."


@tool
def search_audit_findings(query: str) -> str:
    """Search indexed audit findings and remediation evidence."""
    chunks = retrieve(query, "audit_findings")
    return "\n".join(chunk.content for chunk in chunks) if chunks else "No relevant audit findings found."


@tool
def search_governance_documents(query: str) -> str:
    """Search indexed governance documents and policy content."""
    chunks = retrieve(query, "governance_documents")
    return "\n".join(chunk.content for chunk in chunks) if chunks else "No relevant governance documents found."
