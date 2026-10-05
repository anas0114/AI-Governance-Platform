"""Splits raw document text into overlapping, metadata-tagged chunks."""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.rag.config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(text: str, metadata: dict | None = None) -> list[Document]:
    """Split text into LangChain Document chunks, each tagged with its chunk index."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    base_metadata = metadata or {}

    return [
        Document(page_content=chunk, metadata={**base_metadata, "chunk_index": i})
        for i, chunk in enumerate(chunks)
        if chunk.strip()
    ]
