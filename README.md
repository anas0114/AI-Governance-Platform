# AI Governance & Compliance Platform

A full-stack platform for governing AI systems: policy management, compliance
assessments against frameworks (EU AI Act, NIST AI RMF, ISO 42001), audit
tracking, and an AI-powered copilot built with LangChain + LangGraph over a
ChromaDB vector store.

## Tech Stack
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy 2.0 (async), Alembic
- **Database**: PostgreSQL
- **AI Orchestration**: LangChain, LangGraph
- **Vector Store**: ChromaDB

## Project Structure

```
AI-Governance-Platform/
├── backend/          FastAPI service (API, DB models, LangChain/LangGraph agents)
├── frontend/          Next.js application
├── docs/              Architecture documentation
└── docker-compose.yml Local dev orchestration (postgres, chroma, backend, frontend)
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full architecture details.

## Phase 1 Modules
- **Regulation Repository** — track regulations and clauses/articles, auto-embedded into ChromaDB (`/regulations`)
- **Compliance Dashboard** — aggregate risk, assessment, policy, and audit finding stats (`/dashboard`)
- **Policy Management** — CRUD + approval workflow (draft → in_review → approved/retired) (`/policies`)
- **Research Workspace** — grounded copilot Q&A over regulations/policies plus saved notes (`/research`)

## Phase 2: RAG System
Document ingestion (txt/pdf/docx) → chunking → OpenAI embeddings → ChromaDB storage → similarity
retrieval → citation-grounded answers. The repository exposes four explicit knowledge domains:
Regulations, Industry Standards, Audit Findings, and Governance Documents, while preserving the
legacy Policies and Evidence collections. See `backend/app/rag/` and the `/documents`, `/chat`,
`/research/queries` endpoints.

## Phase 3: Governance Agents (LangGraph multi-agent)
Four specialist agents, each with their own tools/prompt/memory, coordinated by a supervisor
orchestrator (`backend/app/agents/orchestrator.py`):
- **Legal Research Agent** — `/api/v1/agents/legal-research`
- **Compliance Agent** — `/api/v1/agents/compliance`
- **Risk Evaluation Agent** — `/api/v1/agents/risk-evaluation`
- **Governance Advisor Agent** — `/api/v1/agents/governance-advisor`
- **Auto-routed orchestration** — `/api/v1/agents/orchestrate` (frontend: `/agents`)

Conversation memory is scoped per `session_id` via a LangGraph `MemorySaver` checkpointer.

## Phase 4: MCP Integration
Four standalone MCP (Model Context Protocol) servers under `backend/app/mcp/`, so any MCP-compatible
client (VS Code, Claude Desktop, etc.) can call the platform's tools directly:
- **Policy Repository** — `python -m app.mcp.policy_repository_server`
- **Compliance Tool** — `python -m app.mcp.compliance_tool_server`
- **Audit System** — `python -m app.mcp.audit_system_server`
- **Document Management** — `python -m app.mcp.document_management_server`

Each runs over stdio and reuses the same DB models and RAG pipeline as the REST API. A ready-to-use
editor config is provided at [.vscode/mcp.json](.vscode/mcp.json) (update the Python interpreter path
if your virtual environment isn't at `backend/.venv`).

## Phase 5: Multi-Agent Collaboration
A fixed-order pipeline runs all four specialists in sequence, each building on prior findings:

`Research Agent → Compliance Agent → Risk Agent → Governance Agent`

- **Run** — `POST /api/v1/collaboration/` (frontend: `/collaboration`)
- **Audit trail** — `GET /api/v1/collaboration/` lists every past run; `GET /api/v1/collaboration/{run_id}`
  returns the full per-agent trace (recommendation traceability).
- **Observability** — `backend/app/agents/observability.py` records every chain/tool/LLM call (name,
  duration, truncated input/output) per agent step, persisted alongside the run.
- **LangSmith tracing** — set `LANGCHAIN_TRACING_V2=true` plus `LANGCHAIN_API_KEY` in `backend/.env` to
  also trace every call in LangSmith (`backend/app/core/tracing.py`).

## Getting Started

### ⚡ Quick Start (All Platforms)

**Using Docker (Easiest - Recommended):**
```bash
docker-compose up --build
```
Then open http://localhost:3000 (frontend) and http://localhost:8000 (backend API)

### 🪟 Windows Users
**See [README-WINDOWS.md](./README-WINDOWS.md) for detailed Windows-specific instructions and common fixes.**

Quick commands:
```powershell
# Check if system is ready
.\check-requirements.ps1

# Automated setup (backend + frontend)
.\setup.ps1

# Start database services
docker-compose up -d

# In new PowerShell: Start backend
cd backend
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# In another new PowerShell: Start frontend
cd frontend
npm run dev
```

### Mac/Linux Users

**Prerequisites:**
- Python 3.10+
- Node.js 16+
- PostgreSQL (or Docker)
- ChromaDB (or Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

**Database services** (in separate terminals):
```bash
# PostgreSQL
docker run -d -e POSTGRES_USER=aigov -e POSTGRES_PASSWORD=aigov \
  -e POSTGRES_DB=aigov -p 5432:5432 postgres:15

# ChromaDB
docker run -d -p 8001:8000 chromadb/chroma:latest
```
```
