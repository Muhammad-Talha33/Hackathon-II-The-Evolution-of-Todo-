# Deployment Prerequisites
## Phase IV - Local Kubernetes Deployment

**Last Updated**: 2026-01-14

This document lists all required tools and their installation instructions for deploying the Todo AI Chatbot.

---

## Required Tools

### 1. Docker Desktop

**Purpose**: Build container images and run containers locally

**Required Version**: Latest stable (24.x+)

**Installation**:
- **Windows**: Download from [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- **macOS**: Download from [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow [Docker Engine installation guide](https://docs.docker.com/engine/install/)

**Verification**:
```bash
docker --version
# Expected: Docker version 24.x.x or higher

docker-compose --version
# Expected: Docker Compose version v2.x.x or higher
```

**Configuration**:
- Allocate at least **4GB RAM** and **2 CPU cores** in Docker Desktop settings
- Enable **File Sharing** for your project directory
- Ensure Docker Engine is running before deployment

---

### 2. kubectl (Kubernetes CLI)

**Purpose**: Interact with Kubernetes clusters

**Required Version**: 1.25+ (compatible with Kubernetes 1.25-1.29)

**Installation**:

**Windows (via Chocolatey)**:
```powershell
choco install kubernetes-cli
```

**Windows (manual)**:
```powershell
curl.exe -LO "https://dl.k8s.io/release/v1.29.0/bin/windows/amd64/kubectl.exe"
# Move to C:\Windows\System32\ or add to PATH
```

**macOS (via Homebrew)**:
```bash
brew install kubectl
```

**Linux**:
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

**Verification**:
```bash
kubectl version --client
# Expected: Client Version v1.25+ displayed
```

---

### 3. Helm (Kubernetes Package Manager)

**Purpose**: Deploy and manage Kubernetes applications via Helm charts

**Required Version**: 3.x (latest stable)

**Installation**:

**Windows (via Chocolatey)**:
```powershell
choco install kubernetes-helm
```

**Windows (via Scoop)**:
```powershell
scoop install helm
```

**macOS (via Homebrew)**:
```bash
brew install helm
```

**Linux**:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Verification**:
```bash
helm version
# Expected: version.BuildInfo{Version:"v3.x.x" ...}
```

---

### 4. kind (Kubernetes in Docker) - OPTIONAL

**Purpose**: Run Kubernetes cluster locally without Minikube (SLAT workaround)

**Required Version**: Latest stable (0.20+)

**When to Install**:
- Required for **Track B** (Kubernetes deployment)
- NOT required for **Track A** (Docker Compose only)
- Recommended if Minikube is unavailable due to SLAT limitation

**Installation**:

**Windows (via Chocolatey)**:
```powershell
choco install kind
```

**Windows (manual)**:
```powershell
curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/latest/kind-windows-amd64
move kind-windows-amd64.exe C:\Windows\System32\kind.exe
```

**macOS (via Homebrew)**:
```bash
brew install kind
```

**Linux**:
```bash
# For AMD64 / x86_64
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# For ARM64
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-arm64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

**Verification**:
```bash
kind --version
# Expected: kind v0.20.x or higher
```

**kind vs Minikube**:
- **kind**: Runs Kubernetes in Docker containers (no VM, no SLAT requirement)
- **Minikube**: Runs Kubernetes in VM (requires hypervisor + SLAT support)
- For this project: **kind is recommended** due to SLAT limitation

---

### 5. Git (Version Control)

**Purpose**: Clone repository and manage deployment artifacts

**Required Version**: 2.x+

**Installation**:
- **Windows**: Download from [Git for Windows](https://git-scm.com/download/win)
- **macOS**: Pre-installed or via `brew install git`
- **Linux**: `sudo apt install git` (Debian/Ubuntu) or `sudo yum install git` (RHEL/CentOS)

**Verification**:
```bash
git --version
# Expected: git version 2.x.x
```

---

## Optional Tools

### kubectl-ai (AI-Assisted Kubernetes Operations)

**Purpose**: Get AI-powered kubectl command suggestions

**Installation**:
```bash
pip install kubectl-ai

# Configure OpenAI API key
export OPENAI_API_KEY=sk-your-api-key
```

**Example Usage**:
```bash
kubectl-ai "deploy the todo backend with 2 replicas"
kubectl-ai "check why the pods are failing"
```

**Note**: Requires valid OpenAI API key

---

### kagent (Cluster Analysis Tool)

**Purpose**: Analyze cluster health and optimize resources

**Installation**: Follow [kagent installation guide](https://github.com/kubeshop/kagent)

**Example Usage**:
```bash
kagent "analyze the cluster health"
kagent "optimize resource allocation"
```

---

## System Requirements

### Hardware
- **CPU**: 2+ cores (4+ recommended for Kubernetes)
- **RAM**: 4GB minimum (8GB+ recommended for Kubernetes)
- **Disk**: 10GB free space for Docker images and cluster data

### Operating System
- **Windows**: Windows 10/11 (64-bit), WSL2 enabled for Docker Desktop
- **macOS**: macOS 10.15+ (Catalina or newer)
- **Linux**: Ubuntu 20.04+, Debian 10+, RHEL 8+, or equivalent

### Network
- Internet connection for downloading images and accessing Neon PostgreSQL
- Ports **8000** (backend) and **3000** (frontend) available on localhost
- For Kubernetes: Port **30080** (NodePort) available

---

## Verification Script

Run this script to verify all required tools are installed:

```bash
#!/bin/bash

echo "=== Deployment Prerequisites Verification ==="
echo ""

# Docker
echo "1. Docker:"
if command -v docker &> /dev/null; then
    docker --version
    echo "   ✅ Docker installed"
else
    echo "   ❌ Docker NOT installed"
fi
echo ""

# Docker Compose
echo "2. Docker Compose:"
if command -v docker-compose &> /dev/null; then
    docker-compose --version
    echo "   ✅ Docker Compose installed"
else
    echo "   ❌ Docker Compose NOT installed"
fi
echo ""

# kubectl
echo "3. kubectl:"
if command -v kubectl &> /dev/null; then
    kubectl version --client --short 2>&1 | head -1
    echo "   ✅ kubectl installed"
else
    echo "   ❌ kubectl NOT installed"
fi
echo ""

# Helm
echo "4. Helm:"
if command -v helm &> /dev/null; then
    helm version --short
    echo "   ✅ Helm installed"
else
    echo "   ❌ Helm NOT installed"
fi
echo ""

# kind (optional)
echo "5. kind (optional):"
if command -v kind &> /dev/null; then
    kind --version
    echo "   ✅ kind installed"
else
    echo "   ⚠️  kind NOT installed (optional for Track B)"
fi
echo ""

# Git
echo "6. Git:"
if command -v git &> /dev/null; then
    git --version
    echo "   ✅ Git installed"
else
    echo "   ❌ Git NOT installed"
fi
echo ""

echo "=== Verification Complete ==="
```

**Save as**: `scripts/verify-prerequisites.sh`

**Run**: `bash scripts/verify-prerequisites.sh`

---

## Next Steps

After installing all required tools:

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   git checkout 004-phase4-local-k8s
   ```

2. **Create Secrets File**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual secrets
   ```

3. **Choose Deployment Track**:
   - **Track A (Docker Compose)**: Follow `docs/deployment/docker-compose.md`
   - **Track B (Kubernetes)**: Follow `docs/deployment/kubernetes.md`

4. **Refer to Quick Start**:
   - See `specs/004-phase4-local-k8s/quickstart.md` for step-by-step deployment guide

---

**Questions or Issues?** Check `docs/deployment/troubleshooting.md` for common problems and solutions.
