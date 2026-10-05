# AI Governance Platform - Automated Setup Script
# Run this script from the project root to set everything up

param(
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [switch]$UseDocker
)

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  AI Governance Platform - Setup Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we should use Docker
if ($UseDocker) {
    Write-Host "Starting with Docker Compose..." -ForegroundColor Green
    docker-compose up --build
    exit 0
}

# Setup Backend
if (-not $SkipBackend) {
    Write-Host "Setting up Backend..." -ForegroundColor Yellow
    Write-Host ""
    
    if (-not (Test-Path "backend")) {
        Write-Host "Error: backend directory not found" -ForegroundColor Red
        exit 1
    }
    
    Push-Location backend
    
    # Create venv
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Cyan
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to create virtual environment" -ForegroundColor Red
            Write-Host "Make sure Python 3.10+ is installed and in your PATH" -ForegroundColor Yellow
            exit 1
        }
    }
    
    # Activate venv
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    Write-Host "Upgrading pip..." -ForegroundColor Cyan
    python -m pip install --upgrade pip | Out-Null
    
    # Install dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    if ($env:OS -eq "Windows_NT" -and (Test-Path "requirements-windows.txt")) {
        pip install -r requirements-windows.txt
        if ($LASTEXITCODE -eq 0) {
            pip install chroma-hnswlib==0.7.5
            pip install chromadb==0.5.11 langchain-chroma==0.1.4 --no-deps
        }
    } else {
        pip install -r requirements.txt
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    
    # Create .env if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Host "Creating .env file..." -ForegroundColor Cyan
        Copy-Item .env.example .env
        Write-Host "⚠ Edit backend\.env and add your OPENAI_API_KEY" -ForegroundColor DarkYellow
    }
    
    Pop-Location
    Write-Host "✓ Backend setup complete" -ForegroundColor Green
    Write-Host ""
}

# Setup Frontend
if (-not $SkipFrontend) {
    Write-Host "Setting up Frontend..." -ForegroundColor Yellow
    Write-Host ""
    
    if (-not (Test-Path "frontend")) {
        Write-Host "Error: frontend directory not found" -ForegroundColor Red
        exit 1
    }
    
    Push-Location frontend
    
    # Install dependencies
    Write-Host "Installing npm dependencies..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    
    # Create .env.local if it doesn't exist
    if (-not (Test-Path ".env.local")) {
        Write-Host "Creating .env.local file..." -ForegroundColor Cyan
        Copy-Item .env.example .env.local
    }
    
    Pop-Location
    Write-Host "✓ Frontend setup complete" -ForegroundColor Green
    Write-Host ""
}

# Summary
Write-Host "================================================" -ForegroundColor Green
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
if (-not $SkipBackend) {
    Write-Host "1. Backend (in new PowerShell window):" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "   uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host ""
}
if (-not $SkipFrontend) {
    Write-Host "2. Frontend (in another new PowerShell window):" -ForegroundColor Yellow
    Write-Host "   cd frontend" -ForegroundColor White
    Write-Host "   npm run dev" -ForegroundColor White
    Write-Host ""
}
Write-Host "3. Open browser to http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: Make sure PostgreSQL and ChromaDB are running!" -ForegroundColor DarkYellow
Write-Host "      Use 'docker-compose up' in another terminal if needed" -ForegroundColor DarkYellow
