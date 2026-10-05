"""Lightweight observability: captures every chain/tool/LLM call during an agent run.

Independent of LangSmith — this always records structured events (name, phase,
duration, truncated input/output) so a run's audit trail is available even
without an external tracing account configured.
"""
import time
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler

MAX_TEXT_LENGTH = 500


def _truncate(value: Any) -> str:
    text = str(value)
    return text if len(text) <= MAX_TEXT_LENGTH else f"{text[:MAX_TEXT_LENGTH]}…"


class CollaborationTracer(BaseCallbackHandler):
    """Collects a flat, chronological list of observability events for one agent invocation."""

    def __init__(self) -> None:
        self.events: list[dict] = []
        self._starts: dict[str, float] = {}

    def _record_start(self, run_id: UUID, kind: str, name: str, payload: Any) -> None:
        self._starts[str(run_id)] = time.perf_counter()
        self.events.append({"type": kind, "name": name, "phase": "start", "detail": _truncate(payload)})

    def _record_end(self, run_id: UUID, kind: str, name: str, payload: Any) -> None:
        started = self._starts.pop(str(run_id), None)
        duration_ms = round((time.perf_counter() - started) * 1000, 1) if started else None
        self.events.append(
            {"type": kind, "name": name, "phase": "end", "detail": _truncate(payload), "duration_ms": duration_ms}
        )

    def on_chain_start(self, serialized, inputs, *, run_id, **kwargs) -> None:
        name = (serialized or {}).get("name", "chain")
        self._record_start(run_id, "chain", name, inputs)

    def on_chain_end(self, outputs, *, run_id, **kwargs) -> None:
        self._record_end(run_id, "chain", "chain", outputs)

    def on_tool_start(self, serialized, input_str, *, run_id, **kwargs) -> None:
        name = (serialized or {}).get("name", "tool")
        self._record_start(run_id, "tool", name, input_str)

    def on_tool_end(self, output, *, run_id, **kwargs) -> None:
        self._record_end(run_id, "tool", "tool", output)

    def on_llm_start(self, serialized, prompts, *, run_id, **kwargs) -> None:
        self._record_start(run_id, "llm", "llm", None)

    def on_llm_end(self, response, *, run_id, **kwargs) -> None:
        self._record_end(run_id, "llm", "llm", None)

    def on_tool_error(self, error, *, run_id, **kwargs) -> None:
        self.events.append({"type": "tool", "name": "tool", "phase": "error", "detail": _truncate(error)})
