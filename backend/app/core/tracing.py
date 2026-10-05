"""Wires up LangSmith tracing via environment variables, if enabled in settings.

LangChain/LangGraph auto-detect these standard env vars and trace every chain,
tool, and LLM call to LangSmith when LANGCHAIN_TRACING_V2 is set.
"""
import os

from app.core.config import settings


def configure_langsmith() -> None:
    if not settings.LANGCHAIN_TRACING_V2:
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
