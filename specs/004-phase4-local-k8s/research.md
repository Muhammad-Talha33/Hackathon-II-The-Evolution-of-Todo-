# Phase 0: Research & Technology Decisions
## Phase IV - Local Kubernetes Deployment

**Date**: 2026-01-13
**Status**: Completed
**Branch**: `004-phase4-local-k8s`

## Critical Constraint Analysis

### SLAT Limitation Impact

**Problem**: Current laptop CPU lacks SLAT (Second Level Address Translation) support, preventing Minikube from running.

**SLAT Requirement**: Minikube uses hypervisors (Hyper-V on Windows, VirtualBox, VMware) that require hardware virtualization with SLAT/EPT (Extended Page Tables) for efficient nested virtualization.

**Verification Command**:
```powershell
# Windows: Check for SLAT support
systeminfo | findstr /C:"Hyper-V Requirements"
# Look for "Second Level Address Translation: Yes"
```

## Alternative Kubernetes Runtimes (Research Findings)

### Option 1: kind (Kubernetes in Docker) ✅ RECOMMENDED

**Decision**: Use kind as primary K8s alternative for local testing

**Rationale**:
- Runs Kubernetes inside Docker containers (not VMs), bypassing SLAT requirement
- Officially supported by Kubernetes SIG (Special Interest Group)
- Fast cluster creation (<1 minute)
- Multi-node cluster support for testing
- Works with existing Docker Desktop installation

**Installation**:
```bash
# Windows (via Chocolatey)
choco install kind

# Or download binary
curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/latest/kind-windows-amd64
move kind-windows-amd64.exe C:\Windows\System32\kind.exe
```

**Usage**:
```bash
# Create single-node cluster
kind create cluster --name todo-local

# Create multi-node cluster
kind create cluster --config kind-config.yaml

# Load local images (important!)
kind load docker-image todo-backend:latest --name todo-local
kind load docker-image todo-frontend:latest --name todo-local

# Delete cluster
kind delete cluster --name todo-local
```

**Pros**:
- No SLAT/hypervisor dependency
- Real Kubernetes API (100% compatibility)
- Fast iteration cycles
- Multiple clusters for testing

**Cons**:
- Slightly different from production Minikube/cloud K8s
- Requires manual image loading (no registry by default)
- LoadBalancer services need extra config (MetalLB)

**Alternatives Considered**:
- **k3s/k3d**: Lightweight K8s, but adds unnecessary complexity for learning
- **MicroK8s**: Ubuntu-optimized, limited Windows support
- **Docker Desktop K8s**: Built-in but limited features, less configurable

---

### Option 2: Docker Compose ✅ IMMEDIATE FALLBACK

**Decision**: Use Docker Compose as immediate orchestration solution

**Rationale**:
- Works on current hardware without SLAT
- Provides container orchestration (services, networks, volumes)
- Simpler than Kubernetes for local development
- Industry-standard for local multi-container apps
- Already available in Docker Desktop

**Usage**:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

**Pros**:
- Immediate usability (no K8s cluster required)
- Simple YAML syntax
- Fast startup/teardown
- Good for local development and testing

**Cons**:
- Not Kubernetes (limited learning value for K8s concepts)
- No native Helm support
- Missing K8s features (Deployments, Services, Secrets API)

---

## Docker Image Best Practices (Research)

### Multi-Stage Builds

**Decision**: Use multi-stage Dockerfiles for both frontend and backend

**Rationale**:
- Reduces final image size (removes build tools, dev dependencies)
- Separates build-time and runtime concerns
- Improves security (fewer attack vectors in production image)

**Backend (FastAPI) Pattern**:
```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY ./src ./src
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend (Next.js) Pattern**:
```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Runtime
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
CMD ["node", "server.js"]
```

**Alternatives Considered**:
- Single-stage builds: Simpler but 3-5x larger images
- Distroless images: More secure but harder to debug

---

## Secrets Management (Research)

### Kubernetes Secrets

**Decision**: Use native Kubernetes Secrets with Helm templating

**Implementation**:
```yaml
# helm/backend/templates/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "backend.fullname" . }}
type: Opaque
stringData:
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | quote }}
  DATABASE_URL: {{ .Values.secrets.databaseUrl | quote }}
  SECRET_KEY: {{ .Values.secrets.secretKey | quote }}
```

**Values override (NOT committed)**:
```yaml
# values-local.yaml (gitignored)
secrets:
  openaiApiKey: "sk-..."
  databaseUrl: "postgresql://..."
  secretKey: "..."
```

**Deployment**:
```bash
# Install with secrets from values file
helm install todo-backend ./helm/backend -f values-local.yaml

# Or via --set flags
helm install todo-backend ./helm/backend \
  --set secrets.openaiApiKey="sk-..." \
  --set secrets.databaseUrl="postgresql://..."
```

**Alternatives Considered**:
- External Secrets Operator: Over-engineered for local deployment
- Sealed Secrets: Requires additional controller, too complex
- ConfigMaps: Not suitable for sensitive data (not base64 encoded)

---

### Docker Compose Secrets

**Decision**: Use environment files (.env) with .gitignore protection

**Implementation**:
```yaml
# docker-compose.yml
services:
  backend:
    env_file:
      - .env  # Load from .env file (gitignored)
```

**Template** (.env.example - committed):
```bash
# Copy this file to .env and fill in your values
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secret-key-here
```

**Usage**:
```bash
# User copies template
cp .env.example .env

# Edit with actual values
nano .env

# Docker Compose automatically loads .env
docker-compose up
```

---

## Helm Chart Structure (Research)

**Decision**: Create two independent Helm charts (backend, frontend)

**Rationale**:
- Independent versioning and deployment lifecycle
- Simpler than umbrella chart for 2-service app
- Easier to test and debug individual services
- Matches microservices philosophy

**Chart Features**:
- **values.yaml**: Default configuration
- **values-local.yaml**: Minikube/kind-specific overrides
- **Templates**: Deployment, Service, Secrets, ConfigMap
- **_helpers.tpl**: Reusable template functions
- **NOTES.txt**: Post-install instructions

**Alternatives Considered**:
- Umbrella/parent chart with subcharts: Added complexity for 2 services
- Helmfile: External tool, unnecessary for simple deployment
- Kustomize: Different paradigm, less parameterization

---

## Service Exposure Strategy (Research)

### Kubernetes (kind/Minikube)

**Decision**: Use NodePort for development, document LoadBalancer for production

**Frontend Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
spec:
  type: NodePort
  ports:
    - port: 3000
      targetPort: 3000
      nodePort: 30080  # Accessible at http://localhost:30080
  selector:
    app: todo-frontend
```

**Backend Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  type: ClusterIP  # Internal only
  ports:
    - port: 8000
      targetPort: 8000
  selector:
    app: todo-backend
```

**Access Methods**:
1. **NodePort**: `http://localhost:30080` (frontend), requires port mapping
2. **Port Forward**: `kubectl port-forward svc/todo-backend 8000:8000`
3. **kind**: Extra config for ingress or LoadBalancer

**Alternatives Considered**:
- Ingress Controller: Overkill for local dev, adds complexity
- HostPort: Conflicts with host services, less flexible

---

## AI-Assisted DevOps Tools (Research)

### kubectl-ai

**Decision**: Document as optional enhancement, provide manual alternatives

**Installation**:
```bash
# Via pip
pip install kubectl-ai

# Configure OpenAI key
export OPENAI_API_KEY=sk-...
```

**Example Usage**:
```bash
kubectl-ai "deploy the todo backend with 2 replicas"
kubectl-ai "scale the frontend to handle more load"
kubectl-ai "check why pods are failing"
```

**Fallback**: Manual kubectl commands with clear documentation

---

### kagent

**Decision**: Document as optional tool, focus on native kubectl/helm

**Note**: kagent provides cluster analysis but is not critical for deployment. Use native tools:
- `kubectl top nodes/pods` for resource usage
- `kubectl describe` for detailed diagnostics
- `helm status` for release information

---

## Technology Stack Summary

| Component | Primary Choice | Alternative | Reason |
|-----------|---------------|-------------|---------|
| **Local K8s** | kind | Docker Compose | kind provides real K8s API without SLAT requirement |
| **Immediate Orchestration** | Docker Compose | Manual Docker | Simple, works now, no K8s cluster needed |
| **Container Platform** | Docker Desktop | Podman | Already installed, industry standard |
| **Package Manager** | Helm 3 | kubectl apply -f | Parameterization, lifecycle management |
| **Secrets** | K8s Secrets + .env | External Secrets | Simple, native, sufficient for local dev |
| **Image Strategy** | Multi-stage builds | Single-stage | Smaller images, better security |
| **Service Exposure** | NodePort (dev) | Ingress | Simple, no additional controllers |
| **AI Tools** | Optional (kubectl-ai) | Manual commands | Learning enhancement, not required |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **SLAT limitation blocks K8s** | Use kind (Docker-based K8s) or Docker Compose fallback |
| **Secrets accidentally committed** | .gitignore for .env and values-local.yaml, .example templates |
| **Image build failures** | Multi-stage builds with error handling, clear build scripts |
| **Service connectivity issues** | Document service DNS (backend:8000), test with curl/port-forward |
| **Kind cluster not accessible** | Document port mapping and kubectl port-forward |
| **Phase III code accidentally modified** | Clear file structure separation, code review checklist |

---

## Next Steps (Phase 1)

1. Create `data-model.md` defining container and K8s resource entities
2. Create Helm values schemas in `contracts/` directory
3. Generate `quickstart.md` with step-by-step deployment guide
4. Update agent context with Docker and Kubernetes technologies

**Status**: Research complete ✅ - Ready for Phase 1 design
