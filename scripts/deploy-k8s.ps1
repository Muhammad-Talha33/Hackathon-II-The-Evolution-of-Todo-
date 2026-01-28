# =============================================================================
# Deploy to Kubernetes via Helm - Todo AI Chatbot (PowerShell)
# =============================================================================
# Usage: .\scripts\deploy-k8s.ps1 [Up|Down|Status]
# Options:
#   -ClusterName NAME   Kind cluster name (default: todo-local)
#   -CreateCluster      Create kind cluster if not exists
# =============================================================================

param(
    [ValidateSet("Up", "Down", "Status")]
    [string]$Command = "Up",
    [string]$ClusterName = "todo-local",
    [switch]$CreateCluster
)

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot

function Write-Info { param([string]$Message); Write-Host "[INFO] $Message" -ForegroundColor Green }
function Write-Warn { param([string]$Message); Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message); Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Test-Prerequisites {
    # Check Docker
    try { docker info | Out-Null }
    catch { Write-Error "Docker is not running"; exit 1 }

    # Check kubectl
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-Error "kubectl not found. Install it first."
        exit 1
    }

    # Check helm
    if (-not (Get-Command helm -ErrorAction SilentlyContinue)) {
        Write-Error "Helm not found. Install it first."
        exit 1
    }

    # Check kind
    if (-not (Get-Command kind -ErrorAction SilentlyContinue)) {
        Write-Error "kind not found. Install it first."
        exit 1
    }

    Write-Info "Prerequisites check passed"
}

function New-Cluster {
    $clusters = kind get clusters 2>$null
    if ($clusters -contains $ClusterName) {
        Write-Info "Cluster '$ClusterName' already exists"
        return
    }

    Write-Info "Creating kind cluster: $ClusterName"

    $kindConfig = @"
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 30080
        protocol: TCP
      - containerPort: 30000
        hostPort: 30000
        protocol: TCP
"@

    $configPath = Join-Path $env:TEMP "kind-config.yaml"
    $kindConfig | Out-File -FilePath $configPath -Encoding UTF8

    kind create cluster --name $ClusterName --config $configPath
    Remove-Item $configPath

    Write-Info "Cluster created successfully"
}

function Import-Images {
    Write-Info "Loading Docker images into kind cluster..."

    $backendExists = docker images --format "{{.Repository}}" | Select-String -Pattern "todo-backend"
    $frontendExists = docker images --format "{{.Repository}}" | Select-String -Pattern "todo-frontend"

    if (-not $backendExists) {
        Write-Error "todo-backend:latest not found. Run build-images.ps1 first."
        exit 1
    }

    if (-not $frontendExists) {
        Write-Error "todo-frontend:latest not found. Run build-images.ps1 first."
        exit 1
    }

    kind load docker-image todo-backend:latest --name $ClusterName
    kind load docker-image todo-frontend:latest --name $ClusterName

    Write-Info "Images loaded successfully"
}

function Deploy-Backend {
    Write-Info "Deploying backend..."
    Set-Location $PROJECT_ROOT

    $valuesFile = Join-Path $PROJECT_ROOT "helm/backend/values-local.yaml"
    if (Test-Path $valuesFile) {
        helm upgrade --install todo-backend ./helm/backend -f $valuesFile
    } else {
        Write-Warn "values-local.yaml not found. Using default values."
        helm upgrade --install todo-backend ./helm/backend
    }
}

function Deploy-Frontend {
    Write-Info "Deploying frontend..."
    Set-Location $PROJECT_ROOT

    $valuesFile = Join-Path $PROJECT_ROOT "helm/frontend/values-local.yaml"
    if (Test-Path $valuesFile) {
        helm upgrade --install todo-frontend ./helm/frontend -f $valuesFile
    } else {
        helm upgrade --install todo-frontend ./helm/frontend
    }
}

function Deploy-Up {
    if ($CreateCluster) {
        New-Cluster
    }

    # Set kubectl context
    kubectl config use-context "kind-$ClusterName" 2>$null

    Import-Images
    Deploy-Backend
    Deploy-Frontend

    Write-Info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=120s deployment/todo-backend 2>$null
    kubectl wait --for=condition=available --timeout=120s deployment/todo-frontend 2>$null

    Show-Status
}

function Deploy-Down {
    Write-Info "Uninstalling Helm releases..."

    try { helm uninstall todo-frontend 2>$null } catch { Write-Warn "todo-frontend not found" }
    try { helm uninstall todo-backend 2>$null } catch { Write-Warn "todo-backend not found" }

    Write-Info "Releases uninstalled"
}

function Show-Status {
    Write-Info "Deployment Status:"
    Write-Host ""

    Write-Host "Helm Releases:"
    helm list

    Write-Host ""
    Write-Host "Deployments:"
    kubectl get deployments

    Write-Host ""
    Write-Host "Pods:"
    kubectl get pods

    Write-Host ""
    Write-Host "Services:"
    kubectl get services

    Write-Host ""
    Write-Info "Access:"
    Write-Host "  Backend:  kubectl port-forward svc/todo-backend 8000:8000"
    Write-Host "  Frontend: http://localhost:30080 (if NodePort configured)"
    Write-Host "            kubectl port-forward svc/todo-frontend 3000:3000"
}

# Main
Test-Prerequisites

switch ($Command) {
    "Up" { Deploy-Up }
    "Down" { Deploy-Down }
    "Status" { Show-Status }
}
