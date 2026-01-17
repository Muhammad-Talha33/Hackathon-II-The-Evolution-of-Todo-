# Phase 1: Data Model - Container & Kubernetes Resources
## Phase IV - Local Kubernetes Deployment

**Date**: 2026-01-13
**Status**: Completed
**Branch**: `004-phase4-local-k8s`

## Overview

This document defines the deployment entities (containers, K8s resources) and their relationships. Unlike typical data models focused on application data, this deployment-centric model describes infrastructure components.

## Entity Catalog

### 1. Backend Container Image

**Purpose**: Containerized FastAPI application with dependencies

**Attributes**:
- **Image Name**: `todo-backend` (repository name)
- **Tag**: `latest` (development), `vX.Y.Z` (versioned releases)
- **Base Image**: `python:3.11-slim` (official Python slim image)
- **Exposed Ports**: `8000` (HTTP API)
- **Working Directory**: `/app`
- **Entry Point**: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
- **Build Context**: `./backend` (relative to repo root)
- **Dockerfile Path**: `./docker/backend/Dockerfile`

**Build Arguments**:
- `PYTHON_VERSION`: Python base image version (default: 3.11)
- `APP_ENV`: Application environment (default: production)

**Environment Variables** (runtime):
- `OPENAI_API_KEY`: OpenAI API key (secret)
- `DATABASE_URL`: PostgreSQL connection string (secret)
- `SECRET_KEY`: JWT signing key (secret)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Token expiration (config)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token TTL (config)
- `CORS_ORIGINS`: Allowed CORS origins (config)
- `ENVIRONMENT`: deployment environment (dev/staging/prod)

**Volumes**: None (stateless application)

**Health Check**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

---

### 2. Frontend Container Image

**Purpose**: Containerized Next.js application (production build)

**Attributes**:
- **Image Name**: `todo-frontend`
- **Tag**: `latest` (development), `vX.Y.Z` (versioned)
- **Base Image**: `node:18-alpine` (lightweight Node.js)
- **Exposed Ports**: `3000` (HTTP)
- **Working Directory**: `/app`
- **Entry Point**: `node server.js` (Next.js standalone server)
- **Build Context**: `./frontend`
- **Dockerfile Path**: `./docker/frontend/Dockerfile`

**Build Arguments**:
- `NODE_VERSION`: Node.js base image version (default: 18)
- `NEXT_PUBLIC_API_URL`: Backend API URL (build-time)

**Environment Variables** (runtime):
- `NEXT_PUBLIC_API_URL`: Backend API endpoint (http://backend:8000 in K8s)
- `NODE_ENV`: production

**Volumes**: None (static build output)

**Health Check**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1
```

---

### 3. Backend Kubernetes Deployment

**Purpose**: Manages backend pod replicas and rolling updates

**Attributes**:
- **Resource Type**: `apps/v1/Deployment`
- **Name**: `todo-backend` (or templated: `{{ .Release.Name }}-backend`)
- **Namespace**: `default` (configurable via Helm)
- **Replicas**: `1` (local dev), `2+` (production)
- **Selector**: `app: todo-backend, tier: api`
- **Strategy**: `RollingUpdate` (maxSurge: 1, maxUnavailable: 0)

**Pod Template**:
```yaml
spec:
  containers:
    - name: backend
      image: todo-backend:latest
      ports:
        - containerPort: 8000
          name: http
      envFrom:
        - secretRef:
            name: todo-backend-secrets
        - configMapRef:
            name: todo-backend-config
      resources:
        requests:
          memory: "256Mi"
          cpu: "250m"
        limits:
          memory: "512Mi"
          cpu: "500m"
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

**Relationships**:
- **Uses**: Backend Container Image
- **References**: Backend Secrets, Backend ConfigMap
- **Managed By**: Backend Helm Chart

---

### 4. Frontend Kubernetes Deployment

**Purpose**: Manages frontend pod replicas and rolling updates

**Attributes**:
- **Resource Type**: `apps/v1/Deployment`
- **Name**: `todo-frontend`
- **Namespace**: `default`
- **Replicas**: `1` (local), `2+` (production)
- **Selector**: `app: todo-frontend, tier: web`
- **Strategy**: `RollingUpdate` (maxSurge: 1, maxUnavailable: 0)

**Pod Template**:
```yaml
spec:
  containers:
    - name: frontend
      image: todo-frontend:latest
      ports:
        - containerPort: 3000
          name: http
      envFrom:
        - configMapRef:
            name: todo-frontend-config
      resources:
        requests:
          memory: "128Mi"
          cpu: "100m"
        limits:
          memory: "256Mi"
          cpu: "250m"
      livenessProbe:
        httpGet:
          path: /
          port: 3000
        initialDelaySeconds: 10
        periodSeconds: 20
      readinessProbe:
        httpGet:
          path: /
          port: 3000
        initialDelaySeconds: 5
        periodSeconds: 10
```

**Relationships**:
- **Uses**: Frontend Container Image
- **References**: Frontend ConfigMap
- **Managed By**: Frontend Helm Chart

---

### 5. Backend Kubernetes Service

**Purpose**: Stable network endpoint for backend API within cluster

**Attributes**:
- **Resource Type**: `v1/Service`
- **Name**: `todo-backend`
- **Namespace**: `default`
- **Type**: `ClusterIP` (internal-only access)
- **Selector**: `app: todo-backend`
- **Ports**:
  - **name**: `http`
  - **port**: `8000` (service port)
  - **targetPort**: `8000` (container port)
  - **protocol**: TCP

**DNS Name**: `todo-backend.default.svc.cluster.local` (or `todo-backend` within same namespace)

**Session Affinity**: None (stateless API)

**Relationships**:
- **Routes To**: Backend Deployment pods
- **Consumed By**: Frontend pods (via environment variable)

---

### 6. Frontend Kubernetes Service

**Purpose**: External access point for web interface

**Attributes**:
- **Resource Type**: `v1/Service`
- **Name**: `todo-frontend`
- **Namespace**: `default`
- **Type**: `NodePort` (development) or `LoadBalancer` (production)
- **Selector**: `app: todo-frontend`
- **Ports**:
  - **name**: `http`
  - **port**: `3000` (service port)
  - **targetPort**: `3000` (container port)
  - **nodePort**: `30080` (static assignment for NodePort)
  - **protocol**: TCP

**Access URLs**:
- **NodePort**: `http://localhost:30080` (kind/Minikube)
- **LoadBalancer**: `http://<LoadBalancer-IP>:3000` (cloud K8s)

**Relationships**:
- **Routes To**: Frontend Deployment pods
- **Accessed By**: End users via browser

---

### 7. Backend Kubernetes Secret

**Purpose**: Store sensitive environment variables for backend

**Attributes**:
- **Resource Type**: `v1/Secret`
- **Name**: `todo-backend-secrets`
- **Namespace**: `default`
- **Type**: `Opaque`

**Data Fields** (base64-encoded):
- `OPENAI_API_KEY`: OpenAI API key
- `DATABASE_URL`: Neon PostgreSQL connection string
- `SECRET_KEY`: JWT signing secret
- `REFRESH_TOKEN_EXPIRE_DAYS`: "7" (example)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: "60" (example)

**Source**:
- **Helm**: `values-local.yaml` (gitignored) or `--set` flags
- **Direct**: `kubectl create secret generic todo-backend-secrets --from-literal=...`

**Relationships**:
- **Consumed By**: Backend Deployment (envFrom.secretRef)
- **Managed By**: Backend Helm Chart

---

### 8. Backend Kubernetes ConfigMap

**Purpose**: Store non-sensitive configuration for backend

**Attributes**:
- **Resource Type**: `v1/ConfigMap`
- **Name**: `todo-backend-config`
- **Namespace**: `default`

**Data Fields** (plaintext):
- `CORS_ORIGINS`: `"http://localhost:30080,http://todo-frontend:3000"`
- `ENVIRONMENT`: `"development"`
- `LOG_LEVEL`: `"INFO"`

**Relationships**:
- **Consumed By**: Backend Deployment (envFrom.configMapRef)

---

### 9. Frontend Kubernetes ConfigMap

**Purpose**: Store non-sensitive configuration for frontend

**Attributes**:
- **Resource Type**: `v1/ConfigMap`
- **Name**: `todo-frontend-config`
- **Namespace**: `default`

**Data Fields**:
- `NEXT_PUBLIC_API_URL`: `"http://todo-backend:8000"` (in-cluster) or `"http://localhost:8000"` (Docker Compose)
- `NODE_ENV`: `"production"`

**Relationships**:
- **Consumed By**: Frontend Deployment (envFrom.configMapRef)

---

### 10. Backend Helm Chart

**Purpose**: Package and lifecycle management for backend K8s resources

**Attributes**:
- **Chart Name**: `todo-backend`
- **Version**: `1.0.0` (Chart version, not app version)
- **App Version**: `1.0.0` (matches Phase III application version)
- **Description**: "Helm chart for Todo AI Chatbot backend (FastAPI)"
- **Chart Location**: `helm/backend/`

**Files**:
- `Chart.yaml`: Metadata
- `values.yaml`: Default configuration
- `values-local.yaml`: Local overrides (gitignored)
- `templates/deployment.yaml`: Backend Deployment
- `templates/service.yaml`: Backend Service
- `templates/secrets.yaml`: Backend Secret (from values)
- `templates/configmap.yaml`: Backend ConfigMap
- `templates/_helpers.tpl`: Template functions
- `templates/NOTES.txt`: Post-install instructions

**Values Schema** (key parameters):
```yaml
replicaCount: 1
image:
  repository: todo-backend
  tag: latest
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 8000
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
secrets:
  openaiApiKey: ""  # User must provide
  databaseUrl: ""   # User must provide
  secretKey: ""     # User must provide
```

**Relationships**:
- **Installs**: Backend Deployment, Backend Service, Backend Secret, Backend ConfigMap
- **Depends On**: Backend Container Image (must be built first)

---

### 11. Frontend Helm Chart

**Purpose**: Package and lifecycle management for frontend K8s resources

**Attributes**:
- **Chart Name**: `todo-frontend`
- **Version**: `1.0.0`
- **App Version**: `1.0.0`
- **Description**: "Helm chart for Todo AI Chatbot frontend (Next.js)"
- **Chart Location**: `helm/frontend/`

**Files**: (Same structure as backend chart)

**Values Schema**:
```yaml
replicaCount: 1
image:
  repository: todo-frontend
  tag: latest
  pullPolicy: IfNotPresent
service:
  type: NodePort
  port: 3000
  nodePort: 30080
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "250m"
config:
  apiUrl: "http://todo-backend:8000"
  nodeEnv: "production"
```

**Relationships**:
- **Installs**: Frontend Deployment, Frontend Service, Frontend ConfigMap
- **Depends On**: Frontend Container Image, Backend Service (for API connectivity)

---

### 12. Docker Compose Stack (Alternative Orchestration)

**Purpose**: Local container orchestration without Kubernetes

**Attributes**:
- **File**: `docker-compose.yml` (repo root)
- **Services**: `backend`, `frontend`
- **Networks**: `todo-network` (bridge network)
- **Volumes**: None (stateless containers)

**Service Definitions**:

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: ../docker/backend/Dockerfile
    image: todo-backend:latest
    container_name: todo-backend
    ports:
      - "8000:8000"
    env_file:
      - .env  # Contains secrets (gitignored)
    networks:
      - todo-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/frontend/Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=http://backend:8000
    image: todo-frontend:latest
    container_name: todo-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NODE_ENV=production
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - todo-network
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    restart: unless-stopped

networks:
  todo-network:
    driver: bridge
```

**Relationships**:
- **Uses**: Backend Container Image, Frontend Container Image
- **Manages**: Container lifecycle, networking, health checks
- **Alternative To**: Kubernetes orchestration (when K8s cluster unavailable)

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT TRACK A                      │
│                      (Docker Compose - Immediate)               │
└─────────────────────────────────────────────────────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  │                               │
          ┌───────▼────────┐             ┌────────▼───────┐
          │  Backend Image │             │ Frontend Image │
          │  (Dockerfile)  │             │  (Dockerfile)  │
          └───────┬────────┘             └────────┬───────┘
                  │                               │
          ┌───────▼────────┐             ┌────────▼───────┐
          │ Backend        │◄────────────┤ Frontend       │
          │ Container      │  depends_on │ Container      │
          │ (port 8000)    │             │ (port 3000)    │
          └────────────────┘             └────────────────┘
                  │                               │
                  └───────────┬───────────────────┘
                              │
                      ┌───────▼────────┐
                      │  todo-network  │
                      │  (bridge)      │
                      └────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT TRACK B                      │
│                    (Kubernetes - Future Ready)                  │
└─────────────────────────────────────────────────────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  │                               │
          ┌───────▼────────┐             ┌────────▼───────┐
          │ Backend Helm   │             │ Frontend Helm  │
          │ Chart          │             │ Chart          │
          └───────┬────────┘             └────────┬───────┘
                  │                               │
          ┌───────▼────────┐             ┌────────▼───────┐
          │ Backend        │             │ Frontend       │
          │ Deployment     │             │ Deployment     │
          └───────┬────────┘             └────────┬───────┘
                  │                               │
          ┌───────▼────────┐             ┌────────▼───────┐
          │ Backend        │             │ Frontend       │
          │ Pods (1+)      │             │ Pods (1+)      │
          └───────┬────────┘             └────────┬───────┘
                  │                               │
          ┌───────▼────────┐             ┌────────▼───────┐
          │ Backend        │◄────────────┤ Frontend       │
          │ Service        │   calls     │ Service        │
          │ (ClusterIP)    │ via DNS     │ (NodePort)     │
          └───────┬────────┘             └────────┬───────┘
                  │                               │
          ┌───────▼────────┐                      │
          │ Secrets &      │                      │
          │ ConfigMaps     │                      │
          └────────────────┘                      │
                                                  │
                                          ┌───────▼────────┐
                                          │  External      │
                                          │  Access        │
                                          │ (localhost:    │
                                          │  30080)        │
                                          └────────────────┘
```

---

## State Transitions

### Container Lifecycle
```
[Dockerfile] --build--> [Image] --run--> [Container] --stop--> [Stopped]
                                              │
                                              └--restart--> [Container]
```

### Kubernetes Deployment Lifecycle
```
[Helm Install] --> [Deployment Created] --> [Pods Pending] --> [Pods Running]
                                                │
[Helm Upgrade] -------------------------------->│
                                                │
[Helm Uninstall] <------------------------------┘
```

---

## Validation Rules

### Container Images
- ✅ Must have health checks defined
- ✅ Must use non-root user where possible
- ✅ Must not include secrets in image layers
- ✅ Must tag images with version (not just 'latest' in production)

### Kubernetes Resources
- ✅ Deployments must define resource requests and limits
- ✅ Deployments must include liveness and readiness probes
- ✅ Secrets must never be committed to version control
- ✅ Services must match Deployment selector labels

### Helm Charts
- ✅ Chart version must follow semantic versioning
- ✅ values.yaml must not contain secrets (use values-local.yaml)
- ✅ Templates must use {{ .Values }} for all configurable fields
- ✅ NOTES.txt must provide clear post-install instructions

---

## Next Steps

This data model will be referenced in:
1. **contracts/**: Helm values schemas and secret templates
2. **quickstart.md**: Deployment guide with entity initialization order
3. **tasks.md**: Implementation tasks for creating each entity

**Status**: Data model complete ✅ - Ready for contract generation
