"""Tunable parameters for the RAG pipeline (chunking, retrieval, generation)."""

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Number of chunks retrieved per query and the minimum similarity score (0-1, higher is closer) to keep.
TOP_K = 4
SCORE_THRESHOLD = 0.0

# Collections available in ChromaDB, mirroring app.core.config settings.
COLLECTION_POLICIES = "policies"
COLLECTION_REGULATIONS = "regulations"
COLLECTION_EVIDENCE = "evidence"
COLLECTION_INDUSTRY_STANDARDS = "industry_standards"
COLLECTION_AUDIT_FINDINGS = "audit_findings"
COLLECTION_GOVERNANCE_DOCUMENTS = "governance_documents"

# Legacy collections remain supported; the explicit names make Phase 2 knowledge domains visible.
ALL_COLLECTIONS = [
	COLLECTION_POLICIES,
	COLLECTION_REGULATIONS,
	COLLECTION_EVIDENCE,
	COLLECTION_INDUSTRY_STANDARDS,
	COLLECTION_AUDIT_FINDINGS,
	COLLECTION_GOVERNANCE_DOCUMENTS,
]

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
