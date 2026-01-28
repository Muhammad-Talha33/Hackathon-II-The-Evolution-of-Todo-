# Kubernetes Deployment Guide (Track B)
## Phase IV - Local Kubernetes with Minikube/Helm

**Last Updated**: 2026-01-14

This guide covers deploying the Todo AI Chatbot to a local Kubernetes cluster using **Minikube** (primary platform) and **Helm** charts.

---

## ⚠️ SLAT Limitation Notice

**Primary Platform**: Minikube (requires SLAT-capable CPU)
**Current Hardware Limitation**: SLAT (Second Level Address Translation) not available on current system
**Fallback Alternative**: kind (Kubernetes in Docker) - documented below as workaround

**What is SLAT?**
SLAT (also known as EPT on Intel, RVI on AMD) is a CPU virtualization feature required by Minikube's hypervisor-based approach. Minikube uses hypervisors (Hyper-V, VirtualBox, VMware) that require SLAT for efficient nested virtualization.

**Check SLAT Support**:
```powershell
# Windows: Check Hyper-V Requirements
systeminfo | findstr /C:"Hyper-V Requirements"
# Look for "Second Level Address Translation: Yes"
```

If SLAT is NOT available, use **kind** (Kubernetes in Docker) as documented in the Alternative Setup section below.

---

## Prerequisites

**For Minikube (Primary)**:
- ✅ Docker Desktop installed and running
- ✅ kubectl installed (v1.25+)
- ✅ Helm installed (v3.x)
- ✅ Minikube installed (v1.30+)
- ✅ SLAT-capable CPU with virtualization enabled in BIOS
- ✅ Docker images built (`todo-backend:latest`, `todo-frontend:latest`)

**For kind (SLAT Workaround)**:
- ✅ Docker Desktop installed and running
- ✅ kubectl installed (v1.25+)
- ✅ Helm installed (v3.x)
- ✅ kind installed (v0.20+)
- ✅ Docker images built (`todo-backend:latest`, `todo-frontend:latest`)

See [prerequisites.md](./prerequisites.md) for installation instructions.

---

## Quick Start (Minikube - Primary Platform)

### 1. Start Minikube Cluster

```bash
# Start Minikube with Docker driver (most compatible)
minikube start --driver=docker

# Or with specific resources
minikube start --driver=docker --cpus=4 --memory=8192

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Expected Output**:
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.27.3
```

### 2. Configure Docker Environment

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images directly in Minikube (no need to load)
docker build -f docker/backend/Dockerfile -t todo-backend:latest ./backend
docker build -f docker/frontend/Dockerfile -t todo-frontend:latest ./frontend
```

**Note**: Images built this way are available directly to Minikube without loading.

### 3. Create Kubernetes Secrets (Minikube)

```bash
# Method 1: Using kubectl
kubectl create secret generic todo-backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-your-openai-api-key' \
  --from-literal=DATABASE_URL='postgresql://user:pass@host:5432/db' \
  --from-literal=SECRET_KEY='your-jwt-secret-key' \
  --from-literal=REFRESH_TOKEN_EXPIRE_DAYS='7' \
  --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES='60'

# Verify secret created
kubectl get secrets
```

### 4. Deploy Backend with Helm (Minikube)

```bash
# Install backend chart
helm install todo-backend ./helm/backend -f helm/backend/values-local.yaml

# Check deployment
kubectl get deployments
kubectl get pods -l app=todo-backend
kubectl get svc todo-backend
```

### 5. Access Backend (Minikube)

```bash
# Option 1: Port forward
kubectl port-forward svc/todo-backend 8000:8000

# Option 2: Minikube service (opens in browser)
minikube service todo-backend --url

# Test health endpoint
curl http://localhost:8000/health
```

### 6. Deploy Frontend with Helm (Minikube)

```bash
# Install frontend chart
helm install todo-frontend ./helm/frontend -f helm/frontend/values-local.yaml

# Access frontend via Minikube
minikube service todo-frontend --url
# Or use NodePort: http://localhost:30080
```

---

## Alternative Setup (kind - SLAT Workaround)

**⚠️ Use this only if Minikube cannot run due to SLAT limitation.**

### 1. Create kind Cluster

```bash
# Create a single-node cluster
kind create cluster --name todo-local

# Verify cluster is running
kubectl cluster-info --context kind-todo-local
kubectl get nodes
```

**Expected Output**:
```
NAME                       STATUS   ROLES           AGE   VERSION
todo-local-control-plane   Ready    control-plane   1m    v1.27.3
```

### 2. Load Docker Images into kind

Since kind runs in Docker containers, you must load images from your local Docker registry:

```bash
# Load backend image
kind load docker-image todo-backend:latest --name todo-local

# Load frontend image
kind load docker-image todo-frontend:latest --name todo-local

# Verify images are loaded
docker exec -it todo-local-control-plane crictl images | grep todo
```

### 3. Create Kubernetes Secrets

Create secrets for backend environment variables:

```bash
# Method 1: Using kubectl (recommended)
kubectl create secret generic todo-backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-your-openai-api-key' \
  --from-literal=DATABASE_URL='postgresql://user:pass@host:5432/db' \
  --from-literal=SECRET_KEY='your-jwt-secret-key' \
  --from-literal=REFRESH_TOKEN_EXPIRE_DAYS='7' \
  --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES='60'

# Verify secret created
kubectl get secrets
kubectl describe secret todo-backend-secrets
```

**Method 2: Using Helm values file** (see Step 4 below)

### 4. Deploy Backend with Helm

```bash
# Install backend chart
helm install todo-backend ./helm/backend

# Or with custom values file (recommended for secrets)
# First create helm/backend/values-local.yaml (gitignored):
cat > helm/backend/values-local.yaml <<EOF
replicaCount: 1
image:
  repository: todo-backend
  tag: latest
  pullPolicy: IfNotPresent
secrets:
  openaiApiKey: "sk-your-openai-api-key"
  databaseUrl: "postgresql://user:pass@host:5432/db"
  secretKey: "your-jwt-secret-key"
  refreshTokenExpireDays: "7"
  accessTokenExpireMinutes: "60"
config:
  corsOrigins: "http://localhost:30080,http://todo-frontend:3000"
  environment: "development"
EOF

# Install with custom values
helm install todo-backend ./helm/backend -f helm/backend/values-local.yaml

# Check deployment status
kubectl get deployments
kubectl get pods -l app=todo-backend
kubectl get svc todo-backend
```

**Expected Output**:
```
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
todo-backend   1/1     1            1           30s

NAME                            READY   STATUS    RESTARTS   AGE
todo-backend-6d8f9c7b5d-x7k2m   1/1     Running   0          30s

NAME           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
todo-backend   ClusterIP   10.96.100.123   <none>        8000/TCP   30s
```

### 5. Test Backend Deployment

```bash
# Port-forward to access backend locally
kubectl port-forward svc/todo-backend 8000:8000

# In another terminal, test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy","environment":"development"}

# Test API docs
curl http://localhost:8000/docs
# Expected: HTML content

# View backend logs
kubectl logs -l app=todo-backend --tail=50
```

### 6. Deploy Frontend with Helm

```bash
# Install frontend chart
helm install todo-frontend ./helm/frontend

# Or with custom values
cat > helm/frontend/values-local.yaml <<EOF
replicaCount: 1
image:
  repository: todo-frontend
  tag: latest
  pullPolicy: IfNotPresent
service:
  type: NodePort
  port: 3000
  nodePort: 30080
config:
  apiUrl: "http://todo-backend:8000"
  nodeEnv: "production"
EOF

helm install todo-frontend ./helm/frontend -f helm/frontend/values-local.yaml

# Check deployment
kubectl get deployments
kubectl get pods -l app=todo-frontend
kubectl get svc todo-frontend
```

### 7. Access Frontend

**Option 1: Port Forward**
```bash
kubectl port-forward svc/todo-frontend 3000:3000
# Open browser: http://localhost:3000
```

**Option 2: NodePort (requires kind port mapping)**

For NodePort to work, you need to create kind cluster with port mapping:

```bash
# Create kind-config.yaml
cat > kind-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 30080
        protocol: TCP
EOF

# Delete existing cluster
kind delete cluster --name todo-local

# Create cluster with port mapping
kind create cluster --name todo-local --config kind-config.yaml

# After deploying, access via:
# http://localhost:30080
```

---

## Helm Chart Management

### Upgrade Helm Release

```bash
# Update backend chart
helm upgrade todo-backend ./helm/backend -f helm/backend/values-local.yaml

# Update frontend chart
helm upgrade todo-frontend ./helm/frontend -f helm/frontend/values-local.yaml

# Check upgrade history
helm history todo-backend
helm history todo-frontend
```

### Rollback Helm Release

```bash
# Rollback to previous version
helm rollback todo-backend
helm rollback todo-frontend

# Rollback to specific revision
helm rollback todo-backend 1
```

### Scale Deployment

```bash
# Scale backend replicas
helm upgrade todo-backend ./helm/backend --set replicaCount=2

# Or edit values file and upgrade
# Verify scaling
kubectl get pods -l app=todo-backend
```

### Uninstall Helm Release

```bash
# Uninstall charts
helm uninstall todo-backend
helm uninstall todo-frontend

# Verify resources removed
kubectl get all
kubectl get secrets
```

---

## Alternative: kubectl apply (Without Helm)

If you prefer not to use Helm, you can deploy using raw Kubernetes manifests:

### 1. Create Secrets

```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-...' \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=SECRET_KEY='...' \
  --from-literal=REFRESH_TOKEN_EXPIRE_DAYS='7' \
  --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES='60'
```

### 2. Deploy Backend

```bash
# Apply backend manifests
kubectl apply -f k8s/backend/deployment.yaml
kubectl apply -f k8s/backend/service.yaml

# If using ConfigMap:
kubectl apply -f k8s/backend/configmap.yaml
```

### 3. Deploy Frontend

```bash
# Apply frontend manifests
kubectl apply -f k8s/frontend/deployment.yaml
kubectl apply -f k8s/frontend/service.yaml
kubectl apply -f k8s/frontend/configmap.yaml
```

### 4. Delete Resources

```bash
kubectl delete -f k8s/backend/
kubectl delete -f k8s/frontend/
kubectl delete secret todo-backend-secrets
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# - ImagePullBackOff: Image not loaded into kind
# - CrashLoopBackOff: Check logs for application errors
# - Pending: Resource constraints or scheduling issues
```

### Image Pull Errors

**For Minikube**:
```bash
# Verify images are available to Minikube
eval $(minikube docker-env)
docker images | grep todo

# If missing, rebuild in Minikube's Docker
docker build -f docker/backend/Dockerfile -t todo-backend:latest ./backend
docker build -f docker/frontend/Dockerfile -t todo-frontend:latest ./frontend
```

**For kind (SLAT workaround)**:
```bash
# Verify images are loaded in kind
docker exec -it todo-local-control-plane crictl images

# If missing, reload images
kind load docker-image todo-backend:latest --name todo-local
kind load docker-image todo-frontend:latest --name todo-local
```

### Secret Issues

```bash
# Verify secrets exist
kubectl get secrets

# Check secret contents (base64 encoded)
kubectl get secret todo-backend-secrets -o yaml

# Verify pod has access to secrets
kubectl describe pod <pod-name> | grep -A 10 Environment
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints todo-backend
kubectl get endpoints todo-frontend

# Test service connectivity from within cluster
kubectl run test-pod --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl http://todo-backend:8000/health

# Port-forward for local access
kubectl port-forward svc/todo-backend 8000:8000
kubectl port-forward svc/todo-frontend 3000:3000
```

### Helm Issues

```bash
# List all releases
helm list

# Check release status
helm status todo-backend

# View rendered templates (dry-run)
helm install todo-backend ./helm/backend --dry-run --debug

# View values used in release
helm get values todo-backend
```

---

## Best Practices

### Secrets Management

1. **Never commit secrets to version control**:
   - Use `values-local.yaml` (gitignored)
   - Use `--set` flags for CI/CD
   - Use external secret managers for production

2. **Rotate secrets regularly**:
   ```bash
   # Update secret
   kubectl create secret generic todo-backend-secrets \
     --from-literal=SECRET_KEY='new-key' \
     --dry-run=client -o yaml | kubectl apply -f -

   # Restart pods to pick up new secret
   kubectl rollout restart deployment/todo-backend
   ```

### Resource Limits

Always define resource requests and limits:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Health Checks

Ensure liveness and readiness probes are configured:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 20

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Helm Chart Versioning

- Use semantic versioning (1.0.0, 1.0.1, etc.)
- Increment chart version on every change
- Tag app version separately from chart version

---

## Cleanup

### Delete Minikube Cluster

```bash
# Stop Minikube
minikube stop

# Delete entire cluster (removes all resources)
minikube delete

# This removes all deployments, services, secrets, and resources
```

### Delete kind Cluster (if using SLAT workaround)

```bash
# Delete entire cluster
kind delete cluster --name todo-local

# This removes all deployments, services, secrets, and resources
```

### Remove Docker Images

```bash
# Remove local images
docker rmi todo-backend:latest
docker rmi todo-frontend:latest

# Prune unused images
docker image prune
```

---

## Next Steps

- **Production Deployment**: Migrate to cloud Kubernetes (EKS, GKE, AKS)
- **Ingress Controller**: Add NGINX Ingress for external access
- **Monitoring**: Install Prometheus and Grafana for observability
- **CI/CD**: Automate deployments with GitHub Actions or GitLab CI

---

## AI-Assisted DevOps Tools (Optional)

For enhanced Kubernetes operations, you can use AI-powered tools that accept natural language commands:

### kubectl-ai

```bash
# Install
pip install kubectl-ai

# Examples
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "scale the backend to handle more load"
kubectl-ai "check why the pods are failing"
```

### kagent

```bash
# Cluster health analysis
kagent analyze "check cluster health"

# Resource optimization
kagent optimize "analyze resource allocation"
```

See [ai-tools.md](./ai-tools.md) for detailed documentation and examples.

**Manual Fallbacks**: All AI tool commands have equivalent kubectl commands documented in the respective sections above.

---

## Additional Resources

- [kind Documentation](https://kind.sigs.k8s.io/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [AI Tools Guide](./ai-tools.md)

---

**Questions or Issues?** See [troubleshooting.md](./troubleshooting.md) for common problems and solutions.
