"""Deprecated: superseded by app.rag.vectorstore. Kept as a thin re-export for compatibility."""
from app.rag.vectorstore import get_chroma_client, get_vectorstore  # noqa: F401


def get_or_create_collection(name: str):
    return get_chroma_client().get_or_create_collection(name=name)


def query_collection(collection_name: str, query_text: str, n_results: int = 4) -> dict:
    collection = get_or_create_collection(collection_name)
    return collection.query(query_texts=[query_text], n_results=n_results)
