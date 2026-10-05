import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import is_openai_configured, register_exception_handlers
from app.core.tracing import configure_langsmith
from app.db.base import Base
from app.db.session import engine

# Import models
from app.models.user import User

logger = logging.getLogger(__name__)

configure_langsmith()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if not is_openai_configured():
        logger.warning("OPENAI_API_KEY is missing or a placeholder; AI features will return 503 until it is set.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan
)

register_exception_handlers(app)


# Registered before CORSMiddleware so CORS wraps it and error responses still carry CORS headers.
@app.middleware("http")
async def catch_unhandled_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Check the backend logs for details."},
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str | bool]:
    return {"status": "ok", "ai_configured": is_openai_configured()}


@app.get("/health")
async def health_check():
    return {"status": "ok"}