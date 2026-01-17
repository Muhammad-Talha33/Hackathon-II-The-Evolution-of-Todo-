# Quickstart Guide: Phase IV Deployment
## Todo AI Chatbot - Local Kubernetes Deployment

**Last Updated**: 2026-01-13
**Branch**: `004-phase4-local-k8s`

## Prerequisites

Before starting, ensure you have:

| Tool | Version | Installation | Verification |
|------|---------|--------------|--------------|
| **Docker Desktop** | Latest | [Install Docker Desktop](https://www.docker.com/products/docker-desktop) | `docker --version` |
| **kubectl** | 1.25+ | [Install kubectl](https://kubernetes.io/docs/tasks/tools/) | `kubectl version --client` |
| **Helm** | 3.x | [Install Helm](https://helm.sh/docs/intro/install/) | `helm version` |
| **kind** (optional) | Latest | `choco install kind` (Windows) | `kind --version` |
| **Git** | Any | [Install Git](https://git-scm.com/downloads) | `git --version` |

**Important Note**: Due to SLAT limitation on current hardware, Minikube is not available. This guide provides **two deployment tracks**:
- **Track A**: Docker Compose (immediate, works now)
- **Track B**: kind (Kubernetes in Docker, alternative to Minikube)

---

## Track A: Docker Compose Deployment (Immediate)

**Use this track** if you want to deploy immediately without Kubernetes.

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd <repository-name>
git checkout 004-phase4-local-k8s
```

### Step 2: Create Secrets File

```bash
# Copy the template
cp .env.example .env

# Edit with your actual secrets
# Windows: notepad .env
# macOS/Linux: nano .env
```

**Required values in `.env`**:
```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-jwt-secret-key  # Generate: openssl rand -hex 32
```

### Step 3: Build Docker Images

```bash
# Build both images
docker-compose build

# Or build individually
docker build -f docker/backend/Dockerfile -t todo-backend:latest ./backend
docker build -f docker/frontend/Dockerfile -t todo-frontend:latest ./frontend
```

**Expected output**:
```
✅ Building backend... Done (2-3 minutes)
✅ Building frontend... Done (2-3 minutes)
```

### Step 4: Start Application

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

**Expected output**:
```
NAME              STATE    PORTS
todo-backend      Up       0.0.0.0:8000->8000/tcp
todo-frontend     Up       0.0.0.0:3000->3000/tcp
```

### Step 5: Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 6: Verify Health

```bash
# Backend health check
curl http://localhost:8000/health

# Expected: {"status": "healthy"}

# Frontend health check
curl http://localhost:3000

# Expected: HTML response
```

### Step 7: Stop Application

```bash
# Stop services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

**Track A Complete!** ✅

---

## Track B: Kubernetes Deployment (kind)

**Use this track** to deploy on Kubernetes using kind (works without SLAT).

### Step 1: Install and Create kind Cluster

```bash
# Install kind (if not already installed)
# Windows:
choco install kind

# macOS:
brew install kind

# Linux:
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create cluster
kind create cluster --name todo-local

# Verify cluster
kubectl cluster-info --context kind-todo-local
kubectl get nodes
```

**Expected output**:
```
Creating cluster "todo-local" ...
 ✓ Ensuring node image (kindest/node:v1.27.0)
 ✓ Preparing nodes
 ✓ Writing configuration
 ✓ Starting control-plane
 ✓ Installing CNI
 ✓ Installing StorageClass
Set kubectl context to "kind-todo-local"
```

### Step 2: Build Docker Images

```bash
# Build images
docker build -f docker/backend/Dockerfile -t todo-backend:latest ./backend
docker build -f docker/frontend/Dockerfile -t todo-frontend:latest ./frontend

# Load images into kind cluster (REQUIRED for kind)
kind load docker-image todo-backend:latest --name todo-local
kind load docker-image todo-frontend:latest --name todo-local

# Verify images loaded
docker exec -it todo-local-control-plane crictl images | grep todo
```

### Step 3: Create Secrets

**Option 1: Using kubectl**:
```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-your-openai-api-key' \
  --from-literal=DATABASE_URL='postgresql://user:password@host:5432/db' \
  --from-literal=SECRET_KEY='your-jwt-secret' \
  --from-literal=REFRESH_TOKEN_EXPIRE_DAYS='7' \
  --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES='60'

# Verify
kubectl get secret todo-backend-secrets
```

**Option 2: Using Helm values**:
Create `helm/backend/values-local.yaml`:
```yaml
secrets:
  openaiApiKey: "sk-your-openai-api-key"
  databaseUrl: "postgresql://user:password@host:5432/db"
  secretKey: "your-jwt-secret"
  refreshTokenExpireDays: "7"
  accessTokenExpireMinutes: "60"
```

### Step 4: Deploy with Helm

```bash
# Install backend
helm install todo-backend ./helm/backend -f helm/backend/values-local.yaml

# Install frontend
helm install todo-frontend ./helm/frontend

# Check deployment status
helm list
kubectl get deployments
kubectl get pods
kubectl get services
```

**Expected output**:
```
NAME            STATUS    AGE
todo-backend    deployed  10s
todo-frontend   deployed  5s

NAME                READY   STATUS    RESTARTS   AGE
todo-backend-xxx    1/1     Running   0          30s
todo-frontend-xxx   1/1     Running   0          25s
```

### Step 5: Access Application

**Option 1: Port Forwarding**:
```bash
# Forward frontend service
kubectl port-forward svc/todo-frontend 3000:3000

# Forward backend service (in another terminal)
kubectl port-forward svc/todo-backend 8000:8000
```

**Option 2: NodePort (if configured)**:
```bash
# Get NodePort
kubectl get svc todo-frontend

# Access at http://localhost:<NodePort>
```

**Option 3: kind-specific ingress** (advanced):
See [kind ingress documentation](https://kind.sigs.k8s.io/docs/user/ingress/)

### Step 6: Verify Deployment

```bash
# Check pod logs
kubectl logs -l app=todo-backend
kubectl logs -l app=todo-frontend

# Check pod status
kubectl get pods -o wide

# Describe deployment
kubectl describe deployment todo-backend

# Test backend health
kubectl port-forward svc/todo-backend 8000:8000 &
curl http://localhost:8000/health
```

### Step 7: Update Deployment

```bash
# Modify values-local.yaml, then upgrade
helm upgrade todo-backend ./helm/backend -f helm/backend/values-local.yaml

# Check rollout status
kubectl rollout status deployment/todo-backend
```

### Step 8: Cleanup

```bash
# Uninstall Helm releases
helm uninstall todo-backend
helm uninstall todo-frontend

# Delete secrets
kubectl delete secret todo-backend-secrets

# Delete kind cluster
kind delete cluster --name todo-local
```

**Track B Complete!** ✅

---

## Troubleshooting

### Docker Compose Issues

#### Problem: "ERROR: Couldn't connect to Docker daemon"
**Solution**:
```bash
# Ensure Docker Desktop is running
# Windows: Check system tray for Docker icon
# Restart Docker Desktop if needed
```

#### Problem: "port 8000 is already in use"
**Solution**:
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000

# Kill process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 on host instead
```

#### Problem: Backend fails to connect to database
**Solution**:
```bash
# Check DATABASE_URL in .env
# Ensure Neon PostgreSQL is accessible
# Test connection:
docker-compose run backend python -c "import psycopg2; psycopg2.connect('your-database-url')"
```

---

### Kubernetes (kind) Issues

#### Problem: "error: unable to connect to cluster"
**Solution**:
```bash
# Check cluster status
kind get clusters

# Recreate cluster if needed
kind delete cluster --name todo-local
kind create cluster --name todo-local
```

#### Problem: Pods stuck in "ImagePullBackOff"
**Solution**:
```bash
# Images must be loaded into kind cluster
kind load docker-image todo-backend:latest --name todo-local
kind load docker-image todo-frontend:latest --name todo-local

# Restart pods
kubectl rollout restart deployment/todo-backend
```

#### Problem: Pods stuck in "CrashLoopBackOff"
**Solution**:
```bash
# Check pod logs for errors
kubectl logs <pod-name>

# Common causes:
# 1. Missing secrets
kubectl get secrets

# 2. Wrong environment variables
kubectl describe pod <pod-name>

# 3. Health check failures
kubectl describe pod <pod-name> | grep -A 10 "Events"
```

#### Problem: Cannot access frontend at http://localhost:30080
**Solution**:
```bash
# kind requires port mapping in cluster config
# Create kind-config.yaml:
cat <<EOF > kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30080
    hostPort: 30080
    protocol: TCP
EOF

# Recreate cluster with config
kind delete cluster --name todo-local
kind create cluster --name todo-local --config kind-config.yaml
```

---

## Validation Checklist

After deployment, verify:

### Track A (Docker Compose)
- [ ] `docker-compose ps` shows both services as "Up"
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API docs at http://localhost:8000/docs
- [ ] Backend health check returns `{"status": "healthy"}`
- [ ] Can create, view, and interact with todos in UI
- [ ] No errors in `docker-compose logs`

### Track B (Kubernetes)
- [ ] `kubectl get pods` shows all pods as "Running"
- [ ] `helm list` shows releases as "deployed"
- [ ] `kubectl get secrets` shows `todo-backend-secrets`
- [ ] Pod logs show successful startup (no errors)
- [ ] Frontend accessible via port-forward or NodePort
- [ ] Backend health endpoint responds correctly
- [ ] Can create, view, and interact with todos in UI

---

## Next Steps

After successful deployment:

1. **Explore AI Tools** (optional):
   - Install `kubectl-ai` for AI-assisted cluster management
   - Install `kagent` for cluster analysis
   - See `docs/deployment/ai-tools.md` for usage examples

2. **Learn Kubernetes**:
   - Experiment with scaling: `kubectl scale deployment todo-backend --replicas=2`
   - Try rolling updates: Modify Helm values and upgrade
   - Explore pod logs: `kubectl logs -f <pod-name>`

3. **Production Preparation** (future):
   - Replace NodePort with Ingress + TLS
   - Add monitoring (Prometheus, Grafana)
   - Implement auto-scaling (HPA)
   - Set up CI/CD pipeline

---

## Quick Reference

### Docker Compose Commands
```bash
docker-compose up -d          # Start services
docker-compose down           # Stop and remove containers
docker-compose logs -f        # Follow logs
docker-compose restart        # Restart services
docker-compose build          # Rebuild images
docker-compose ps             # List services
```

### Kubernetes Commands
```bash
kubectl get pods              # List pods
kubectl get svc               # List services
kubectl logs <pod-name>       # View pod logs
kubectl describe pod <pod>    # Pod details
kubectl port-forward svc/<name> <port>:<port>  # Forward port
kubectl exec -it <pod> -- bash  # Shell into pod
```

### Helm Commands
```bash
helm list                     # List releases
helm install <name> <chart>   # Install chart
helm upgrade <name> <chart>   # Upgrade release
helm uninstall <name>         # Uninstall release
helm status <name>            # Release status
helm get values <name>        # View values
```

---

**Need help?** Check the full documentation at `docs/deployment/` or open an issue on GitHub.
