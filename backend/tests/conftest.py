"""Test harness for AI features: isolated DB/vector store plus a fake LLM that makes real tool calls.

The fakes replace only the OpenAI network calls, so every agent graph, tool, RAG pipeline,
endpoint, and persistence path runs exactly as it does in production.
"""
import atexit
import hashlib
import math
import os
import re
import shutil
import tempfile
from typing import Any

_TMP_DIR = tempfile.mkdtemp(prefix="aigov-tests-")
atexit.register(shutil.rmtree, _TMP_DIR, ignore_errors=True)

# Must be set before any app module reads settings.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///" + os.path.join(_TMP_DIR, "test.db").replace("\\", "/")
os.environ["CHROMA_PERSIST_DIR"] = os.path.join(_TMP_DIR, "chroma")
os.environ["CHROMA_PORT"] = "1"
os.environ["OPENAI_API_KEY"] = "sk-test-not-a-real-key"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

import pytest  # noqa: E402
from langchain_core.embeddings import Embeddings  # noqa: E402
from langchain_core.language_models.chat_models import BaseChatModel  # noqa: E402
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage  # noqa: E402
from langchain_core.outputs import ChatGeneration, ChatResult  # noqa: E402
from langchain_core.runnables import RunnableLambda  # noqa: E402

FAILURE: dict[str, Exception | None] = {"exc": None}
ROUTE_TO = "compliance"

_TOOL_ARGS = {
    "query": "risk management high-risk AI systems",
    "framework_name": "EU AI Act",
    "ai_system_name": "Credit",
    "system_name": "Credit",
    "system_description": "biometric identification for law enforcement",
    "policy_title": "Responsible",
    "status": "draft",
}


class KeywordEmbeddings(Embeddings):
    """Deterministic bag-of-words embeddings so related texts are genuinely close in vector space."""

    dim = 256

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            vector[int(hashlib.md5(word.encode()).hexdigest(), 16) % self.dim] += 1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


class FakeToolCallingChat(BaseChatModel):
    """Calls every bound tool once, then answers with a summary of the real tool outputs."""

    tools: list[Any] = []

    @property
    def _llm_type(self) -> str:
        return "fake-tool-calling"

    def bind_tools(self, tools, **kwargs):
        return FakeToolCallingChat(tools=list(tools))

    def with_structured_output(self, schema, **kwargs):
        return RunnableLambda(lambda _: schema(next=ROUTE_TO, reason="test routing"))

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs) -> ChatResult:
        if FAILURE["exc"] is not None:
            raise FAILURE["exc"]

        last = messages[-1]
        if self.tools and not isinstance(last, ToolMessage):
            calls = [
                {"name": t.name, "args": {k: _TOOL_ARGS.get(k, "test") for k in t.args}, "id": f"call_{i}"}
                for i, t in enumerate(self.tools)
            ]
            message = AIMessage(content="", tool_calls=calls)
        else:
            tool_outputs = []
            for m in reversed(messages):
                if not isinstance(m, ToolMessage):
                    break
                tool_outputs.append(str(m.content))
            if tool_outputs:
                content = "Final answer. Tool results: " + " | ".join(o[:150] for o in reversed(tool_outputs))
            else:
                text = last.content if isinstance(last, HumanMessage) else str(last.content)
                content = f"Final answer: {str(text)[:300]}"
            message = AIMessage(content=content)
        return ChatResult(generations=[ChatGeneration(message=message)])


# Patch the OpenAI accessors before agents are built at import time.
import app.rag.embeddings as embeddings_module  # noqa: E402

embeddings_module.get_embeddings = lambda: KeywordEmbeddings()

import app.rag.chain as chain_module  # noqa: E402

chain_module.get_llm = lambda temperature=0.0: FakeToolCallingChat()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def auth_headers(client) -> dict[str, str]:
    credentials = {"email": "tester@example.com", "password": "TestPass123!"}
    assert client.post("/api/v1/auth/register", json=credentials).status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        data={"username": credentials["email"], "password": credentials["password"]},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.fixture
def inject_llm_failure():
    def _inject(exc: Exception) -> None:
        FAILURE["exc"] = exc

    yield _inject
    FAILURE["exc"] = None
