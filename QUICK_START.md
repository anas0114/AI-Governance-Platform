# 🚀 Quick Start Guide - AI Governance Platform

This guide will help you set up and run the platform locally on Windows.

## Prerequisites

**Before you start, you MUST have:**

1. **Python 3.10+** - [Download here](https://www.python.org/downloads/)
   - During installation, **CHECK "Add Python to PATH"** ✓
   - Verify: Open PowerShell and run `python --version`

2. **Node.js 16+** - [Download here](https://nodejs.org/)
   - Includes npm automatically
   - Verify: Open PowerShell and run `node --version` and `npm --version`

3. **PostgreSQL** (optional if using Docker)
   - Or use Docker for PostgreSQL: See "Using Docker" section below

4. **ChromaDB** (for vector storage)
   - Or use Docker for ChromaDB

---

## Option A: Quick Start with Docker (EASIEST)

If you have Docker Desktop installed, this is the simplest way:

```powershell
# From the AI-Governance-Platform root directory:
docker-compose up --build

# Wait for all services to start (2-3 minutes first run)
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Database: postgres://aigov:aigov@localhost:5432/aigov
```

---

## Option B: Manual Setup (Step by Step)

### Part 1: Backend Setup

```powershell
# 1. Open PowerShell and navigate to the project root
cd C:\Users\YourUsername\Desktop\AI-Governance-Platform

# 2. Go into backend directory
cd backend

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
venv\Scripts\Activate.ps1

# If you get an execution policy error, run this ONCE:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Install all dependencies
pip install -r requirements.txt

# 7. Create .env file from template
Copy-Item .env.example .env

# 8. Edit .env and set OPENAI_API_KEY
# Open backend\.env and add your OpenAI API key
```

**Before running the backend, you need:**
- PostgreSQL running (or using docker-compose)
- ChromaDB running (or using docker-compose)

**To start backend (if PostgreSQL + ChromaDB are already running):**

```powershell
# Make sure venv is activated (you should see (venv) in prompt)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Part 2: Frontend Setup

```powershell
# Open a NEW PowerShell window (keep backend running in other window)

# 1. Navigate to project root
cd C:\Users\YourUsername\Desktop\AI-Governance-Platform

# 2. Go to frontend directory
cd frontend

# 3. Install dependencies
npm install

# 4. Create .env.local file
Copy-Item .env.example .env.local

# 5. Start development server
npm run dev

# Frontend will be available at http://localhost:3000
```

### Part 3: Database & Services Setup

If NOT using Docker, you need to run these separately:

**PostgreSQL** (use Docker):
```powershell
docker run -d `
  --name aigov-postgres `
  -e POSTGRES_USER=aigov `
  -e POSTGRES_PASSWORD=aigov `
  -e POSTGRES_DB=aigov `
  -p 5432:5432 `
  postgres:15
```

**ChromaDB** (use Docker):
```powershell
docker run -d `
  --name aigov-chroma `
  -p 8001:8000 `
  chromadb/chroma:0.5.11
```

---

## Troubleshooting

### "Python was not found"
- Python is not installed OR not in your PATH
- **Fix:** 
  1. Install Python from https://www.python.org/downloads/
  2. During installation, CHECK "Add Python to PATH"
  3. Restart PowerShell after installing

### "venv\Scripts\activate: The term could not be loaded"
- Execution policy issue
- **Fix:** Run this command ONCE in PowerShell:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### "npm: The term is not recognized"
- Node.js/npm not installed OR not in PATH
- **Fix:**
  1. Install Node.js from https://nodejs.org/
  2. Restart PowerShell after installing

### "Cannot connect to database"
- PostgreSQL not running
- **Fix:** Use `docker run...` command above OR ensure PostgreSQL service is running

### "Cannot connect to ChromaDB"
- ChromaDB not running
- **Fix:** Use `docker run...` command above OR ensure ChromaDB is running

### Frontend won't compile
```powershell
cd frontend
rm -r node_modules -Force
rm package-lock.json -Force
npm cache clean --force
npm install
npm run dev
```

### Backend won't start
```powershell
cd backend
# Make sure venv is activated (check for (venv) in prompt)
# If not, run: venv\Scripts\Activate.ps1

# Check Python version
python --version

# Check all dependencies installed
pip list | findstr langchain

# Try starting again
uvicorn app.main:app --reload
```

---

## Default Login (After Seeding Database)

**Email:** `admin@aigovernance.dev`  
**Password:** `ChangeMe123!`

---

## Common Ports

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **PostgreSQL:** localhost:5432
- **ChromaDB:** localhost:8001

---

## Next Steps

1. ✅ Backend running at http://localhost:8000/docs
2. ✅ Frontend running at http://localhost:3000
3. Log in with sample credentials
4. Upload documents, run agents, view collaboration traces!

---

## Need Help?

Check the specific setup guides:
- Backend: See [BACKEND_SETUP.md](./BACKEND_SETUP.md)
- Frontend: See [FRONTEND_SETUP.md](./FRONTEND_SETUP.md)
- Full architecture: See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
