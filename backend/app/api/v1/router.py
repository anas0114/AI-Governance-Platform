from fastapi import APIRouter

from app.api.v1.endpoints import (
    agents,
    ai_systems,
    audits,
    auth,
    chat,
    collaboration,
    compliance,
    documents,
    policies,
    regulations,
    research,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(ai_systems.router, prefix="/ai-systems", tags=["ai-systems"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(audits.router, prefix="/audits", tags=["audits"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(regulations.router, prefix="/regulations", tags=["regulations"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["collaboration"])
