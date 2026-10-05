"""Synchronous SQLAlchemy session for use inside LangChain/LangGraph tool functions.

LangChain tools are simplest as plain sync callables, so agent tools use this
sync engine rather than the async engine powering the FastAPI request path.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

_sync_database_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2").replace("+aiosqlite", "")

_connect_args = {"check_same_thread": False} if _sync_database_url.startswith("sqlite") else {}

sync_engine = create_engine(_sync_database_url, future=True, connect_args=_connect_args)

SyncSessionLocal = sessionmaker(bind=sync_engine, autoflush=False, expire_on_commit=False)
