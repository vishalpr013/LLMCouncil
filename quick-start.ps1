# LLM Council - Quick Start Script for Windows
# Run this script to check prerequisites and start all services

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   LLM Council - Quick Start" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Color functions
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Error-Custom { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Warning-Custom { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }

# Check prerequisites
Write-Info "Checking prerequisites..."
Write-Host ""

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Success "Python found: $pythonVersion"
} else {
    Write-Error-Custom "Python not found! Please install Python 3.9+"
    exit 1
}

# Check Node.js
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Success "Node.js found: $nodeVersion"
} else {
    Write-Error-Custom "Node.js not found! Please install Node.js 16+"
    exit 1
}

# Check llama.cpp
$llamaCppPath = "$HOME\llama.cpp\build\bin\Release\server.exe"
if (Test-Path $llamaCppPath) {
    Write-Success "llama.cpp server found"
} else {
    Write-Warning-Custom "llama.cpp not found at: $llamaCppPath"
    Write-Info "Please install llama.cpp first. See docs/SETUP.md"
}

# Check models
$modelsDir = ".\local-models\models"
if (Test-Path $modelsDir) {
    $modelCount = (Get-ChildItem $modelsDir -Filter "*.gguf" | Measure-Object).Count
    if ($modelCount -gt 0) {
        Write-Success "Found $modelCount GGUF models"
    } else {
        Write-Warning-Custom "No GGUF models found in $modelsDir"
        Write-Info "Run: .\local-models\model-download.sh"
    }
} else {
    Write-Warning-Custom "Models directory not found"
}

# Check backend .env
if (Test-Path ".\backend\.env") {
    Write-Success "Backend .env file found"
} else {
    Write-Warning-Custom "Backend .env not found"
    Write-Info "Copy backend\.env.example to backend\.env and configure API keys"
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   Starting Services" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Ask user what to start
Write-Host "What would you like to start?" -ForegroundColor Yellow
Write-Host "1. All services (models + backend + frontend)"
Write-Host "2. Backend only"
Write-Host "3. Frontend only"
Write-Host "4. Check health only"
Write-Host "5. Exit"
Write-Host ""

$choice = Read-Host "Enter choice (1-5)"

switch ($choice) {
    "1" {
        Write-Info "Starting all services..."
        Write-Host ""
        
        # Start model servers
        Write-Info "Starting local model servers..."
        Start-Process powershell -ArgumentList "-NoExit", "-File", ".\local-models\start-servers.ps1"
        Start-Sleep -Seconds 5
        
        # Start backend
        Write-Info "Starting backend..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
        Start-Sleep -Seconds 5
        
        # Start frontend
        Write-Info "Starting frontend..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"
        
        Write-Host ""
        Write-Success "All services starting!"
        Write-Info "Frontend: http://localhost:3000"
        Write-Info "Backend: http://localhost:8000"
        Write-Info "API Docs: http://localhost:8000/docs"
    }
    
    "2" {
        Write-Info "Starting backend only..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
        Write-Success "Backend starting at http://localhost:8000"
    }
    
    "3" {
        Write-Info "Starting frontend only..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"
        Write-Success "Frontend starting at http://localhost:3000"
    }
    
    "4" {
        Write-Info "Checking health..."
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
            Write-Host ""
            Write-Host "Backend Status: $($health.status)" -ForegroundColor Green
            Write-Host ""
            Write-Host "Model Status:" -ForegroundColor Yellow
            $health.models.PSObject.Properties | ForEach-Object {
                $status = if ($_.Value -eq "online") { "✅" } else { "❌" }
                Write-Host "  $status $($_.Name): $($_.Value)"
            }
        } catch {
            Write-Error-Custom "Backend not accessible. Is it running?"
        }
    }
    
    "5" {
        Write-Info "Exiting..."
        exit 0
    }
    
    default {
        Write-Error-Custom "Invalid choice"
        exit 1
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Success "Setup complete!"
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Info "Next steps:"
Write-Host "  1. Wait for all services to start (~30 seconds)"
Write-Host "  2. Open http://localhost:3000 in your browser"
Write-Host "  3. Try asking: 'What causes climate change?'"
Write-Host ""
Write-Info "Documentation:"
Write-Host "  Setup Guide: docs\SETUP.md"
Write-Host "  API Docs: docs\API.md"
Write-Host "  Pipeline: docs\PIPELINE.md"
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
