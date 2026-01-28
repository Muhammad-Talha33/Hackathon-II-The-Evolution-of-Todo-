# =============================================================================
# Deploy via Docker Compose - Todo AI Chatbot (PowerShell)
# =============================================================================
# Usage: .\scripts\deploy-compose.ps1 [Up|Down|Restart|Logs|Status]
# =============================================================================

param(
    [ValidateSet("Up", "Down", "Restart", "Logs", "Status")]
    [string]$Command = "Up"
)

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
$COMPOSE_FILE = Join-Path $PROJECT_ROOT "docker-compose.yml"

function Write-Info { param([string]$Message); Write-Host "[INFO] $Message" -ForegroundColor Green }
function Write-Warn { param([string]$Message); Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message); Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Test-Prerequisites {
    # Check Docker
    try {
        docker info | Out-Null
    }
    catch {
        Write-Error "Docker is not running"
        exit 1
    }

    # Check .env file
    $envFile = Join-Path $PROJECT_ROOT ".env"
    if (-not (Test-Path $envFile)) {
        Write-Error ".env file not found. Copy .env.example to .env and fill in secrets."
        exit 1
    }

    # Check Docker Compose file
    if (-not (Test-Path $COMPOSE_FILE)) {
        Write-Error "docker-compose.yml not found"
        exit 1
    }

    Write-Info "Prerequisites check passed"
}

function Deploy-Up {
    Write-Info "Starting Docker Compose services..."
    Set-Location $PROJECT_ROOT

    docker-compose up -d

    Write-Info "Waiting for services to be healthy..."
    Start-Sleep -Seconds 10

    Show-Status
}

function Deploy-Down {
    Write-Info "Stopping Docker Compose services..."
    Set-Location $PROJECT_ROOT

    docker-compose down

    Write-Info "Services stopped"
}

function Deploy-Restart {
    Write-Info "Restarting Docker Compose services..."
    Deploy-Down
    Deploy-Up
}

function Show-Logs {
    Write-Info "Showing logs (Ctrl+C to exit)..."
    Set-Location $PROJECT_ROOT

    docker-compose logs -f
}

function Show-Status {
    Write-Info "Service Status:"
    Set-Location $PROJECT_ROOT

    docker-compose ps

    Write-Host ""
    Write-Info "Health Checks:"

    # Check backend
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        Write-Host "  Backend:  HEALTHY (http://localhost:8000)" -ForegroundColor Green
    }
    catch {
        Write-Host "  Backend:  NOT READY" -ForegroundColor Red
    }

    # Check frontend
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        Write-Host "  Frontend: HEALTHY (http://localhost:3000)" -ForegroundColor Green
    }
    catch {
        Write-Host "  Frontend: NOT READY" -ForegroundColor Red
    }
}

# Main
switch ($Command) {
    "Up" {
        Test-Prerequisites
        Deploy-Up
    }
    "Down" {
        Deploy-Down
    }
    "Restart" {
        Test-Prerequisites
        Deploy-Restart
    }
    "Logs" {
        Show-Logs
    }
    "Status" {
        Show-Status
    }
}
