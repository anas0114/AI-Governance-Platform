# AI Governance Platform - System Requirements Checker
# Run this script to verify your system is ready

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  AI Governance Platform - Prerequisites Check" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    $pythonMinor = [int]$pythonVersion.Split('.')[1]
    if ($pythonMinor -ge 10) {
        Write-Host "✓ Python $pythonVersion installed" -ForegroundColor Green
    } else {
        Write-Host "✗ Python 3.10+ required (you have $pythonVersion)" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "✗ Python not found or not in PATH" -ForegroundColor Red
    Write-Host "  Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  IMPORTANT: Check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    $allGood = $false
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = & node --version 2>&1
    Write-Host "✓ Node.js $nodeVersion installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found or not in PATH" -ForegroundColor Red
    Write-Host "  Download: https://nodejs.org/" -ForegroundColor Yellow
    $allGood = $false
}

# Check npm
Write-Host "Checking npm..." -ForegroundColor Yellow
try {
    $npmVersion = & npm --version 2>&1
    Write-Host "✓ npm $npmVersion installed" -ForegroundColor Green
} catch {
    Write-Host "✗ npm not found" -ForegroundColor Red
    Write-Host "  npm should be installed with Node.js" -ForegroundColor Yellow
    $allGood = $false
}

# Check Docker (optional)
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = & docker --version 2>&1
    Write-Host "✓ Docker installed: $dockerVersion" -ForegroundColor Green
    Write-Host "  (You can use 'docker-compose up' for easy setup)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Docker not found (optional - for easier setup)" -ForegroundColor DarkYellow
    Write-Host "  Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "✓ System is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Check QUICK_START.md for setup instructions" -ForegroundColor Yellow
    Write-Host "  2. Or run: docker-compose up --build" -ForegroundColor Yellow
} else {
    Write-Host "✗ Some requirements are missing" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install the missing tools:" -ForegroundColor Cyan
    Write-Host "  1. Python 3.10+: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  2. Node.js 16+: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host "  3. (Optional) Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "IMPORTANT: After installing Python, restart PowerShell!" -ForegroundColor Red
}
Write-Host "================================================" -ForegroundColor Cyan
