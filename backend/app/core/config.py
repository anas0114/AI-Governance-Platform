import json
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Governance Platform API"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    DATABASE_URL: str = "postgresql+asyncpg://aigov:aigov@localhost:5432/aigov"

    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_POLICIES: str = "policies"
    CHROMA_COLLECTION_REGULATIONS: str = "regulations"
    CHROMA_COLLECTION_EVIDENCE: str = "evidence"
    CHROMA_COLLECTION_INDUSTRY_STANDARDS: str = "industry_standards"
    CHROMA_COLLECTION_AUDIT_FINDINGS: str = "audit_findings"
    CHROMA_COLLECTION_GOVERNANCE_DOCUMENTS: str = "governance_documents"
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # LangSmith tracing/observability (optional; leave disabled for local dev without an account).
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "ai-governance-platform"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
