# Containerization Architecture

## Phase IV - Deployment Architecture Decisions

**Last Updated**: 2026-01-18

This document describes the containerization architecture for the Todo AI Chatbot.

---

## Overview

The application uses a microservices architecture with two containerized services:

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Container Runtime                             │
│                (Docker / Kubernetes)                             │
│                                                                  │
│  ┌────────────────────────┐    ┌────────────────────────────┐  │
│  │      Frontend          │    │       Backend              │  │
│  │      Container         │    │       Container            │  │
│  │                        │    │                            │  │
│  │  ┌──────────────────┐ │    │  ┌──────────────────────┐  │  │
│  │  │    Next.js       │ │    │  │      FastAPI         │  │  │
│  │  │    React UI      │─┼────┼─▶│      REST API        │  │  │
│  │  │    Port 3000     │ │    │  │      Port 8000       │  │  │
│  │  └──────────────────┘ │    │  └──────────┬───────────┘  │  │
│  │                        │    │             │              │  │
│  └────────────────────────┘    └─────────────┼──────────────┘  │
│                                              │                  │
└──────────────────────────────────────────────┼──────────────────┘
                                               │
                          ┌────────────────────┴────────────────────┐
                          │                                          │
                          ▼                                          ▼
                ┌─────────────────┐                      ┌─────────────────┐
                │  Neon Database  │                      │   OpenAI API    │
                │   (PostgreSQL)  │                      │   (External)    │
                └─────────────────┘                      └─────────────────┘
```

---

## Service Architecture

### Backend Service

| Aspect | Decision |
|--------|----------|
| **Base Image** | `python:3.11-slim` |
| **Build Strategy** | Multi-stage (builder + runtime) |
| **Runtime** | Uvicorn ASGI server |
| **Port** | 8000 |
| **User** | Non-root (`appuser`) |
| **Health Check** | `GET /health` |

**Rationale:**
- Slim base image reduces size (~150MB vs ~900MB full)
- Multi-stage build excludes build tools from runtime
- Non-root user improves security posture

### Frontend Service

| Aspect | Decision |
|--------|----------|
| **Base Image** | `node:18-alpine` |
| **Build Strategy** | Multi-stage (deps + builder + runtime) |
| **Runtime** | Next.js production server |
| **Port** | 3000 |
| **Output** | Standalone build |
| **Health Check** | `GET /` |

**Rationale:**
- Alpine base minimizes image size (~100MB)
- Three-stage build optimizes layer caching
- Standalone output includes only required files

---

## Image Strategy

### Size Optimization

```
Before Optimization:
  Backend:  ~1.2GB (full Python image)
  Frontend: ~800MB (with node_modules)

After Optimization:
  Backend:  ~250MB (slim + multi-stage)
  Frontend: ~150MB (alpine + standalone)

Total Reduction: 80%
```

### Layer Caching

```dockerfile
# Backend Dockerfile - Optimized layer order
COPY requirements.txt .          # Changes rarely
RUN pip install -r requirements.txt
COPY ./src ./src                 # Changes frequently
```

### Security Hardening

```dockerfile
# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Read-only filesystem (where possible)
# No shell access in production
```

---

## Networking

### Docker Compose Network

```yaml
networks:
  todo-network:
    driver: bridge
    name: todo-network
```

**Service Discovery:**
- Services communicate via container names
- Backend accessible at `http://backend:8000`
- Frontend accessible at `http://frontend:3000`

### Kubernetes Network

```yaml
# ClusterIP for internal communication
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  type: ClusterIP
  ports:
    - port: 8000

# NodePort for external access
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
spec:
  type: NodePort
  ports:
    - port: 3000
      nodePort: 30080
```

---

## Configuration Management

### Environment Variables

| Variable | Container | Purpose |
|----------|-----------|---------|
| `DATABASE_URL` | Backend | Database connection |
| `SECRET_KEY` | Backend | JWT signing |
| `OPENAI_API_KEY` | Backend | AI API access |
| `CORS_ORIGINS` | Backend | Allowed origins |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend URL |
| `NODE_ENV` | Frontend | Production/development |

### Configuration Sources

1. **Docker Compose**: `.env` file
2. **Kubernetes**: ConfigMaps + Secrets
3. **Helm**: `values.yaml` + `values-local.yaml`

---

## Health Checks

### Backend Health

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 15s
```

**Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Frontend Health

```yaml
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 15s
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
```

---

## Resource Management

### Recommended Limits

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Backend | 250m | 500m | 256Mi | 512Mi |
| Frontend | 100m | 250m | 128Mi | 256Mi |

### Scaling Considerations

- **Backend**: CPU-intensive (AI processing)
  - Scale horizontally for more concurrent requests
  - Each replica handles OpenAI API calls independently

- **Frontend**: Memory-intensive (React rendering)
  - Single replica usually sufficient for development
  - Add replicas for high traffic scenarios

---

## Deployment Strategies

### Docker Compose (Track A)

**Pros:**
- Simple setup
- No Kubernetes required
- Works without SLAT

**Cons:**
- No built-in scaling
- Manual failover
- Limited orchestration

**Use When:**
- Local development
- Simple deployments
- SLAT not available

### Kubernetes/Helm (Track B)

**Pros:**
- Declarative configuration
- Built-in scaling (HPA)
- Rolling updates
- Self-healing

**Cons:**
- More complex setup
- Requires K8s cluster
- Higher resource overhead

**Use When:**
- Production deployments
- Need for scaling
- Multi-environment management

---

## Dual-Track Decision Matrix

| Factor | Docker Compose | Kubernetes |
|--------|---------------|------------|
| Setup Complexity | Low | Medium-High |
| Local Development | Excellent | Good |
| Scaling | Manual | Automatic |
| Resource Usage | Lower | Higher |
| Production Ready | Limited | Yes |
| SLAT Required | No | No (with kind) |

---

## Security Considerations

### Container Security

1. **Non-root users**: Both containers run as non-root
2. **Minimal images**: Slim/Alpine base images
3. **No secrets in images**: Environment injection only
4. **Health checks**: Ensure containers are responsive

### Network Security

1. **Internal network**: Services on private network
2. **Limited exposure**: Only necessary ports exposed
3. **CORS configuration**: Restrict allowed origins

### Secret Management

1. **Environment variables**: Injected at runtime
2. **Never in images**: No secrets baked into containers
3. **Gitignore**: Secret files excluded from version control

---

## Performance Optimization

### Build Performance

```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Use cache mounts for dependencies
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
```

### Runtime Performance

- **Connection pooling**: Reuse database connections
- **Keep-alive**: Maintain HTTP connections
- **Compression**: Gzip responses where appropriate

---

## Future Considerations

### Cloud Migration Path

1. **Container Registry**: Push images to ECR/GCR/ACR
2. **Managed Kubernetes**: Deploy to EKS/GKE/AKS
3. **Managed Database**: Already using Neon (cloud)
4. **Ingress Controller**: NGINX or cloud load balancer

### Observability

1. **Logging**: Structured JSON logs to stdout
2. **Metrics**: Prometheus-compatible endpoints
3. **Tracing**: OpenTelemetry integration

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Build and Push
  run: |
    docker build -t todo-backend ./backend
    docker push registry/todo-backend:$TAG

- name: Deploy
  run: |
    helm upgrade todo-backend ./helm/backend
```

---

## References

- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Kubernetes Patterns](https://k8spatterns.io/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
