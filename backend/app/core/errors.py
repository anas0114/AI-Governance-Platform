"""Maps AI-provider and agent failures to clear JSON errors instead of opaque 500s."""
import logging

import openai
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from langgraph.errors import GraphRecursionError

from app.core.config import settings

logger = logging.getLogger(__name__)

_PLACEHOLDER_MARKERS = ("your-", "change-me", "xxx")


def is_openai_configured() -> bool:
    key = settings.OPENAI_API_KEY.strip()
    return bool(key) and not any(marker in key.lower() for marker in _PLACEHOLDER_MARKERS)


def _error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(openai.AuthenticationError)
    async def _auth_error(request: Request, exc: openai.AuthenticationError) -> JSONResponse:
        logger.error("OpenAI authentication failed: %s", exc)
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "The OpenAI API key was rejected. Set a valid OPENAI_API_KEY in backend/.env and restart the backend.",
        )

    @app.exception_handler(openai.RateLimitError)
    async def _rate_limit(request: Request, exc: openai.RateLimitError) -> JSONResponse:
        logger.warning("OpenAI rate limit/quota error: %s", exc)
        if getattr(exc, "code", None) == "insufficient_quota":
            return _error(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Your OpenAI account has no remaining quota. Add billing credits at platform.openai.com.",
            )
        return _error(status.HTTP_429_TOO_MANY_REQUESTS, "OpenAI rate limit reached. Wait a moment and try again.")

    @app.exception_handler(openai.APIConnectionError)
    async def _connection_error(request: Request, exc: openai.APIConnectionError) -> JSONResponse:
        logger.error("Could not reach OpenAI: %s", exc)
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Could not reach the OpenAI API. Check your internet connection or proxy settings.",
        )

    @app.exception_handler(openai.APIError)
    async def _api_error(request: Request, exc: openai.APIError) -> JSONResponse:
        logger.error("OpenAI API error: %s", exc)
        return _error(status.HTTP_502_BAD_GATEWAY, f"The OpenAI API returned an error: {exc.message}")

    @app.exception_handler(GraphRecursionError)
    async def _recursion_error(request: Request, exc: GraphRecursionError) -> JSONResponse:
        logger.error("Agent exceeded its step limit: %s", exc)
        return _error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "The agent could not reach an answer within its step limit. Try rephrasing the question.",
        )
