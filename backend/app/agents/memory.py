"""Conversation memory for LangGraph agents.

Uses LangGraph's MemorySaver checkpointer keyed by `thread_id`, so each session
(e.g. a chat/session_id from the frontend) keeps its own message history across
calls. This is in-process memory suitable for local dev/demo; swap for a
persistent checkpointer (e.g. Postgres-backed) for production.
"""
from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver


@lru_cache
def get_memory_saver() -> MemorySaver:
    return MemorySaver()


def thread_config(thread_id: str) -> dict:
    """Build the LangGraph invoke config that scopes a call to a given conversation thread."""
    return {"configurable": {"thread_id": thread_id}}
