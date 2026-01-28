# =============================================================================
# Build Docker Images - Todo AI Chatbot (PowerShell)
# =============================================================================
# Usage: .\scripts\build-images.ps1
# Options:
#   -BackendOnly   Build only backend image
#   -FrontendOnly  Build only frontend image
#   -NoCache       Build without Docker cache
# =============================================================================

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoCache
)

$ErrorActionPreference = "Stop"

# Configuration
$BACKEND_IMAGE = "todo-backend:latest"
$FRONTEND_IMAGE = "todo-frontend:latest"
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-Docker {
    try {
        docker info | Out-Null
        Write-Info "Docker is running"
        return $true
    }
    catch {
        Write-Error "Docker is not running. Please start Docker Desktop."
        exit 1
    }
}

function Build-Backend {
    Write-Info "Building backend image: $BACKEND_IMAGE"
    Set-Location $PROJECT_ROOT

    $startTime = Get-Date
    $cacheArg = if ($NoCache) { "--no-cache" } else { "" }

    try {
        if ($NoCache) {
            docker build --no-cache -f docker/backend/Dockerfile -t $BACKEND_IMAGE ./backend
        } else {
            docker build -f docker/backend/Dockerfile -t $BACKEND_IMAGE ./backend
        }
        $duration = (Get-Date) - $startTime
        Write-Info "Backend image built successfully in $([math]::Round($duration.TotalSeconds))s"
    }
    catch {
        Write-Error "Backend image build failed: $_"
        exit 1
    }
}

function Build-Frontend {
    Write-Info "Building frontend image: $FRONTEND_IMAGE"
    Set-Location $PROJECT_ROOT

    $startTime = Get-Date

    try {
        if ($NoCache) {
            docker build --no-cache -f docker/frontend/Dockerfile -t $FRONTEND_IMAGE ./frontend
        } else {
            docker build -f docker/frontend/Dockerfile -t $FRONTEND_IMAGE ./frontend
        }
        $duration = (Get-Date) - $startTime
        Write-Info "Frontend image built successfully in $([math]::Round($duration.TotalSeconds))s"
    }
    catch {
        Write-Error "Frontend image build failed: $_"
        exit 1
    }
}

function Show-Images {
    Write-Info "Built images:"
    docker images | Select-String -Pattern "todo-(backend|frontend)"
}

# Main execution
Write-Host "=============================================="
Write-Host "  Todo AI Chatbot - Docker Image Builder"
Write-Host "=============================================="
Write-Host ""

Test-Docker

$buildBackend = -not $FrontendOnly
$buildFrontend = -not $BackendOnly

if ($buildBackend) {
    Build-Backend
}

if ($buildFrontend) {
    Build-Frontend
}

Write-Host ""
Show-Images

Write-Host ""
Write-Info "Build complete!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  - Docker Compose: docker-compose up -d"
Write-Host "  - Kubernetes:     kind load docker-image $BACKEND_IMAGE --name todo-local"
Write-Host "                    kind load docker-image $FRONTEND_IMAGE --name todo-local"
