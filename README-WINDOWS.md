# 🪟 Windows-Specific Setup Guide

This guide is specifically for Windows users setting up the AI Governance Platform.

## TL;DR - Fastest Setup (Uses Docker)

```powershell
# 1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
# 2. Open PowerShell in the project root
# 3. Run:
docker-compose up --build

# Wait 2-3 minutes for all services to start
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

---

## Complete Windows Setup (Without Docker)

### Step 1: Install Required Software

**Python 3.10 or higher:**
1. Go to https://www.python.org/downloads/
2. Click "Download Python 3.12" (or latest)
3. **IMPORTANT:** During installation:
   - ☑️ **CHECK** "Add Python to PATH"
   - ☑️ **CHECK** "Install pip"
4. Click "Install Now"
5. **Restart your computer** or at least restart PowerShell

**Verify Python:**
```powershell
python --version
# Should show: Python 3.10.x or higher
```

**Node.js 16 or higher:**
1. Go to https://nodejs.org/
2. Download the LTS (Long Term Support) version
3. Run the installer and follow defaults
4. **Restart PowerShell after installation**

**Verify Node.js:**
```powershell
node --version
npm --version
# Both should show version numbers
```

---

### Step 2: Check Your System is Ready

```powershell
# Navigate to project root
cd C:\path\to\AI-Governance-Platform

# Run the requirements checker
.\check-requirements.ps1

# If you get an error about execution policy, run this first:
.\FIX_EXECUTION_POLICY.ps1
# Then run check-requirements.ps1 again
```

---

### Step 3: Automated Setup

```powershell
# From project root, run:
.\setup.ps1

# This will automatically:
# ✓ Create Python virtual environment
# ✓ Install Python dependencies
# ✓ Install ChromaDB with the Windows-compatible native wheel workaround
# ✓ Install npm dependencies
# ✓ Create .env files from templates
```

---

### Step 4: Start Database Services

**Option A: Using Docker** (Easiest)
```powershell
docker run -d `
  --name aigov-postgres `
  -e POSTGRES_USER=aigov `
  -e POSTGRES_PASSWORD=aigov `
  -e POSTGRES_DB=aigov `
  -p 5432:5432 `
  postgres:15

docker run -d `
  --name aigov-chroma `
  -p 8001:8000 `
  chromadb/chroma:latest
```

**Option B: Full Docker Compose**
```powershell
# This starts everything in one command
docker-compose up

# Press Ctrl+C to stop, or add -d flag to run in background:
docker-compose up -d
```

---

### Step 5: Start Backend Server

**In PowerShell Window 1:**

```powershell
# Navigate to backend
cd backend

# Activate virtual environment
venv\Scripts\Activate.ps1

# If you see (venv) at the start of your prompt, you're good!
# Start the server
uvicorn app.main:app --reload

# Should show:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Check backend is working:**
- Open http://localhost:8000/docs in your browser
- You should see interactive API documentation

---

### Step 6: Start Frontend Server

**In PowerShell Window 2 (new window):**

```powershell
# Navigate to frontend
cd frontend

# Start development server
npm run dev

# Should show:
# ▲ Next.js version info
# - Local: http://localhost:3000
```

**Check frontend is working:**
- Open http://localhost:3000 in your browser
- You should see the login page

---

## Common Windows Errors and Fixes

### Error: "Python was not found"

**Cause:** Python not installed or not in PATH

**Fix:**
1. Go to https://www.python.org/downloads/
2. Download Python 3.12
3. Run installer
4. **CRITICAL:** CHECK "Add Python to PATH" during installation
5. **Restart PowerShell completely** (close and reopen)
6. Verify: `python --version`

---

### Error: "Cannot be loaded because running scripts is disabled"

**Cause:** PowerShell execution policy blocking scripts

**Fix:**
```powershell
# Run this command:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Type 'Y' and press Enter
# Then retry your script
```

Or just run:
```powershell
.\FIX_EXECUTION_POLICY.ps1
```

---

### Error: "pip: The term is not recognized"

**Cause:** Python's pip not in PATH or Python not properly installed

**Fix:**
```powershell
# Use Python's module runner instead:
python -m pip install --upgrade pip

# Then install requirements:
python -m pip install -r requirements.txt
```

---

### Error: "npm: The term is not recognized"

**Cause:** Node.js not installed or not in PATH

**Fix:**
1. Install Node.js from https://nodejs.org/
2. **Restart PowerShell completely**
3. Verify: `npm --version`

---

### Error: "Cannot connect to database"

**Cause:** PostgreSQL not running

**Fix:**
```powershell
# Check if Docker container is running:
docker ps | findstr postgres

# If not running, start it:
docker run -d `
  --name aigov-postgres `
  -e POSTGRES_USER=aigov `
  -e POSTGRES_PASSWORD=aigov `
  -e POSTGRES_DB=aigov `
  -p 5432:5432 `
  postgres:15
```

---

### Error: "Cannot connect to ChromaDB"

**Cause:** ChromaDB not running

**Fix:**
```powershell
# Check if Docker container is running:
docker ps | findstr chroma

# If not running, start it:
docker run -d `
  --name aigov-chroma `
  -p 8001:8000 `
  chromadb/chroma:latest
```

---

### Error: "venv not recognized" or "activate script not found"

**Cause:** Virtual environment not created or corrupt

**Fix:**
```powershell
cd backend

# Delete old venv
Remove-Item venv -Recurse -Force

# Create new venv
python -m venv venv

# Activate
venv\Scripts\Activate.ps1
```

---

### Error: "ModuleNotFoundError" or "ImportError"

**Cause:** Dependencies not installed in virtual environment

**Fix:**
```powershell
# Make sure venv is activated (you should see (venv) in prompt)
venv\Scripts\Activate.ps1

# Reinstall all dependencies
python -m pip install -r requirements.txt

# Verify langchain is installed:
pip list | findstr langchain
```

---

### Error: Frontend won't start / "next not found"

**Cause:** npm dependencies not installed

**Fix:**
```powershell
cd frontend

# Clean and reinstall
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json -Force
npm cache clean --force
npm install

# Try again
npm run dev
```

---

## Working with Virtual Environment

### Activating Virtual Environment

```powershell
cd backend
venv\Scripts\Activate.ps1

# You should see (venv) at the start of your PowerShell prompt
# Example: (venv) C:\path\to\backend>
```

### Deactivating Virtual Environment

```powershell
deactivate

# The (venv) prefix should disappear from your prompt
```

### Important: Always Activate Before Running Backend Commands

```powershell
# ✗ WRONG - This won't work:
python -m pip install package

# ✓ CORRECT - Activate first:
venv\Scripts\Activate.ps1
python -m pip install package
```

---

## Development Workflow

### After First Setup

**Terminal 1 - Backend:**
```powershell
cd backend
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

**Terminal 3 - Database Services** (if not using persistent Docker containers):
```powershell
docker-compose up -d
```

### Restarting Services

**To restart backend:** Ctrl+C in backend terminal, then run uvicorn command again

**To restart frontend:** Ctrl+C in frontend terminal, then run npm run dev again

**To restart all:** Ctrl+C in all terminals, then restart them

### Checking Service Status

```powershell
# Check if services are running:
docker ps

# Check if ports are in use:
netstat -ano | findstr :3000   # Frontend
netstat -ano | findstr :8000   # Backend
netstat -ano | findstr :5432   # Database
netstat -ano | findstr :8001   # ChromaDB
```

---

## Using Docker for Everything (Recommended)

```powershell
# Start all services
docker-compose up

# Wait for all to be "healthy"
# Ctrl+C to stop everything

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove everything (including data!)
docker-compose down -v
```

---

## File Paths on Windows

When you see `/path/to/file` in Linux/Mac instructions:
- Use `C:\Users\YourUsername\path\to\file` on Windows
- Or use forward slashes: `C:/Users/YourUsername/path/to/file` (Windows PowerShell accepts both)

Example:
```powershell
# Copy
Copy-Item .env.example .env

# Instead of
cp .env.example .env
```

---

## Still Having Issues?

1. **Run the requirements checker:**
   ```powershell
   .\check-requirements.ps1
   ```

2. **Check all services are running:**
   ```powershell
   docker ps
   ```

3. **Check logs for errors:**
   - Backend terminal should show errors directly
   - Frontend terminal should show build errors directly

4. **Check documentation:**
   - Backend: See `BACKEND_SETUP.md`
   - Frontend: See `FRONTEND_SETUP.md`
   - Architecture: See `docs/ARCHITECTURE.md`

5. **Restart everything** (often helps on Windows):
   - Close all PowerShell windows
   - Run `docker-compose down` (if using Docker)
   - Run `.\setup.ps1` again
   - Start services fresh

---

## Quick Reference

| Task | Command |
|------|---------|
| Check Python | `python --version` |
| Check Node.js | `node --version` |
| Check npm | `npm --version` |
| Fix execution policy | `.\FIX_EXECUTION_POLICY.ps1` |
| Check requirements | `.\check-requirements.ps1` |
| Auto setup | `.\setup.ps1` |
| Start all services | `docker-compose up` |
| Stop all services | `docker-compose down` |
| Start backend | `cd backend` then `venv\Scripts\Activate.ps1` then `uvicorn app.main:app --reload` |
| Start frontend | `cd frontend` then `npm run dev` |
| View frontend | http://localhost:3000 |
| View backend docs | http://localhost:8000/docs |

---

Happy coding! 🚀
