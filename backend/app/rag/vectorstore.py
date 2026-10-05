"""ChromaDB vector storage: the LangChain `Chroma` wrapper bound to our Chroma client."""
import logging
from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma

from app.core.config import settings
from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)


@lru_cache
def get_chroma_client() -> chromadb.ClientAPI:
    """Use the Chroma server if reachable, otherwise fall back to an embedded on-disk store."""
    try:
        client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        client.heartbeat()
        return client
    except Exception:
        logger.warning(
            "ChromaDB server not reachable at %s:%s; using embedded store at %s",
            settings.CHROMA_HOST,
            settings.CHROMA_PORT,
            settings.CHROMA_PERSIST_DIR,
        )
        # HttpClient mutates the Settings it receives, so the embedded client needs a fresh one.
        return chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )


def get_vectorstore(collection_name: str) -> Chroma:
    return Chroma(
        client=get_chroma_client(),
        collection_name=collection_name,
        embedding_function=get_embeddings(),
    )


def delete_document_vectors(collection_name: str, doc_id: str) -> None:
    """Remove every chunk belonging to a document from its ChromaDB collection."""
    collection = get_chroma_client().get_or_create_collection(name=collection_name)
    collection.delete(where={"doc_id": doc_id})
