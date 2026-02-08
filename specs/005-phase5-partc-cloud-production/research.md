# Research: Phase V Part C - Cloud Production Deployment

**Created**: 2026-02-08
**Branch**: `005-phase5-partc-cloud-production`
**Status**: Complete

---

## Research Summary

This document consolidates all research findings and technology decisions for Phase V Part C. All "NEEDS CLARIFICATION" items from the specification have been resolved.

---

## 1. Kubernetes Provider Decision

### Decision: DigitalOcean Kubernetes (DOKS)

**Rationale**:
- Cost-effective for small-to-medium deployments ($12/month per node vs $72/month for GKE)
- Simpler setup with integrated container registry, load balancers, and managed databases
- Native integration with DigitalOcean Spaces for storage if needed
- kubectl and Helm work identically to other providers
- No complex IAM configuration (compared to GKE/EKS)

**Alternatives Considered**:
| Provider | Pros | Cons | Decision |
|----------|------|------|----------|
| GKE | Most mature, best Dapr support, GCP ecosystem | Higher cost, complex IAM, overkill for this project | Rejected |
| EKS | AWS ecosystem, enterprise-grade | Most expensive, steepest learning curve | Rejected |
| DOKS | Simple, affordable, good enough | Fewer enterprise features | **Selected** |
| Self-hosted | Full control | Significant operational burden | Rejected |

**Implementation Notes**:
- Minimum cluster: 2 nodes (2 vCPU, 4GB RAM each) for HA
- Node pool autoscaling available but out of scope for Phase C
- Managed upgrades available for Kubernetes versions

---

## 2. Cloud Kafka Provider Decision

### Decision: Confluent Cloud (Free Tier for Dev/Staging, Basic for Prod)

**Rationale**:
- Free tier includes 100GB/month data transfer (sufficient for development)
- SASL/SSL authentication out of the box
- Fully Kafka-compatible (Dapr pubsub.kafka component works unchanged)
- Managed schema registry available (optional)
- Better documentation and community support than alternatives

**Alternatives Considered**:
| Provider | Pros | Cons | Decision |
|----------|------|------|----------|
| Confluent Cloud | Best Kafka compatibility, free tier | Premium pricing at scale | **Selected** |
| Aiven Kafka | Good DO integration, managed | No free tier, minimum $100/month | Rejected |
| Redpanda Cloud | Kafka-compatible, simpler | Newer, less documentation | Alternative |
| Amazon MSK | AWS native | No free tier, EKS-centric | Rejected |

**Configuration Pattern**:
```yaml
# Dapr pubsub component for Confluent Cloud
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      secretKeyRef:
        name: kafka-credentials
        key: brokers
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-credentials
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-credentials
        key: password
    - name: saslMechanism
      value: "PLAIN"
    - name: initialOffset
      value: "oldest"
    - name: consumerGroup
      value: "todo-consumers"
```

---

## 3. Container Registry Decision

### Decision: GitHub Container Registry (GHCR)

**Rationale**:
- Free for public repositories, generous limits for private
- Native GitHub Actions integration (no extra secrets for auth)
- Supports multi-platform images (arm64/amd64)
- Package visibility tied to repository permissions
- No separate account/billing required

**Alternatives Considered**:
| Registry | Pros | Cons | Decision |
|----------|------|------|----------|
| GHCR | Free, GH Actions native | Newer than Docker Hub | **Selected** |
| Docker Hub | Most popular, reliable | Rate limits, paid for private | Alternative |
| DigitalOcean Registry | DO native | $5/month, no GH integration | Rejected |
| Google Artifact Registry | GCP native | Requires GCP account | Rejected |

**Image Tagging Strategy**:
- Development: `ghcr.io/<org>/todo-backend:dev-<sha>`
- Staging: `ghcr.io/<org>/todo-backend:staging-<sha>`
- Production: `ghcr.io/<org>/todo-backend:v1.2.3` (semver)
- Latest: `ghcr.io/<org>/todo-backend:latest` (staging only, never prod)

---

## 4. Manifest Management Decision

### Decision: Kustomize with Base + Overlays

**Rationale**:
- Built into kubectl (no additional tooling)
- Simple patching model for environment differences
- Easier to understand than Helm for this project size
- Existing Helm charts can be migrated gradually
- Better GitOps compatibility (plain YAML, no templating)

**Alternatives Considered**:
| Tool | Pros | Cons | Decision |
|------|------|------|----------|
| Kustomize | kubectl-native, simple | Less powerful than Helm | **Selected** |
| Helm | Full templating, charts ecosystem | Complexity, template debugging | Existing, keep for optional use |
| Raw YAML | Simplest | Duplication, no patching | Rejected |
| cdk8s | Programmatic | Overkill, new dependency | Rejected |

**Directory Structure**:
```
k8s/
├── base/                    # Shared resources
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── backend/
│   ├── frontend/
│   ├── workers/
│   └── dapr/
└── overlays/
    ├── staging/
    │   ├── kustomization.yaml
    │   └── patches/
    └── production/
        ├── kustomization.yaml
        ├── ingress.yaml
        └── patches/
```

---

## 5. CI/CD Platform Decision

### Decision: GitHub Actions with Environment Protection

**Rationale**:
- Already using GitHub for source control
- Native GHCR integration
- Environment protection rules for production approval
- Free for public repos, generous limits for private
- Reusable workflows for consistency

**Pipeline Architecture**:
```
Push to main
    │
    ▼
┌─────────────────┐
│   CI Workflow    │  (ci.yaml)
│  - Lint          │
│  - Test          │
│  - Build images  │
│  - Push to GHCR  │
└────────┬────────┘
         │ on: push to main
         ▼
┌─────────────────┐
│  CD Staging      │  (cd-staging.yaml)
│  - Deploy to     │
│    staging ns    │
│  - Smoke tests   │
└────────┬────────┘
         │ on: workflow_dispatch (manual)
         ▼
┌─────────────────┐
│  CD Production   │  (cd-production.yaml)
│  - Require       │
│    approval      │
│  - Deploy to     │
│    production ns │
│  - Verify        │
└─────────────────┘
```

---

## 6. Observability Stack Decision

### Decision: In-Cluster Stack (Prometheus + Grafana + Zipkin)

**Rationale**:
- Self-hosted in cluster for cost control
- Dapr has native Prometheus/Zipkin integration
- Grafana provides dashboards without additional cost
- Can migrate to managed solutions later if needed

**Components**:
| Component | Purpose | Deployment |
|-----------|---------|------------|
| Prometheus | Metrics collection | Helm chart (prometheus-community) |
| Grafana | Dashboards | Helm chart (grafana) |
| Zipkin | Distributed tracing | Simple deployment YAML |
| Loki (optional) | Log aggregation | Out of scope for Phase C |

**Dapr Configuration for Observability**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.observability.svc.cluster.local:9411/api/v2/spans"
  metric:
    enabled: true
```

---

## 7. Secrets Management Strategy

### Decision: Kubernetes Secrets with External Secrets Operator (Optional)

**Rationale**:
- Kubernetes Secrets are sufficient for Phase C scope
- Encrypted at rest in etcd (cluster default)
- RBAC controls access per namespace
- External Secrets Operator can be added later for vault integration

**Secret Categories**:
| Secret Name | Contents | Used By |
|-------------|----------|---------|
| `db-credentials` | DATABASE_URL | Backend, Workers |
| `kafka-credentials` | brokers, username, password | Dapr pubsub component |
| `app-secrets` | JWT_SECRET, API keys | Backend |

**Rotation Procedure**:
1. Update Kubernetes Secret: `kubectl create secret generic <name> --from-literal=key=value --dry-run=client -o yaml | kubectl apply -f -`
2. Trigger rolling restart: `kubectl rollout restart deployment/<name>`
3. Verify new pods use new secret

---

## 8. Environment Separation Strategy

### Decision: Namespace-Based Isolation

**Rationale**:
- Simplest model for small team
- Single cluster, multiple namespaces
- ResourceQuota can limit resource consumption per namespace
- NetworkPolicy can isolate traffic (optional enhancement)

**Namespace Structure**:
| Namespace | Purpose | Replica Counts |
|-----------|---------|----------------|
| `todo-staging` | Pre-production testing | Backend: 1, Frontend: 1, Workers: 1 |
| `todo-production` | Live traffic | Backend: 3, Frontend: 2, Workers: 2 |
| `dapr-system` | Dapr control plane | Managed by Dapr |
| `observability` | Prometheus, Grafana, Zipkin | 1 each |

**Kustomize Overlay Pattern**:
```yaml
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: todo-production
resources:
  - ../../base
  - namespace.yaml
  - ingress.yaml
patches:
  - path: patches/replica-count.yaml
  - path: patches/resource-limits.yaml
```

---

## 9. Dapr on Kubernetes Installation

### Decision: Dapr CLI with Helm Backend

**Rationale**:
- `dapr init -k` is the official recommended approach
- Uses Helm under the hood but abstracts complexity
- Supports HA mode for production
- Easy upgrades with `dapr upgrade -k`

**Installation Commands**:
```bash
# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize Dapr on Kubernetes (HA mode for production)
dapr init -k --enable-ha --enable-mtls

# Verify installation
dapr status -k
```

**Required Dapr Version**: 1.13+ (for improved Kubernetes support)

---

## 10. Health Check Strategy

### Decision: Kubernetes Native Probes + Dapr Health

**Liveness Probe**: Checks if container is running
- Backend: `GET /health` → 200 OK
- Frontend: `GET /` → 200 OK
- Workers: `GET /health` → 200 OK

**Readiness Probe**: Checks if container can serve traffic
- Backend: `GET /health/ready` → 200 OK (includes DB check)
- Frontend: `GET /` → 200 OK
- Workers: `GET /health` → 200 OK

**Dapr Sidecar Health**:
- Dapr exposes `/v1.0/healthz` on sidecar port (3500)
- Application should not serve traffic until sidecar is ready
- Use `dapr.io/sidecar-readiness-probe` annotation

**Probe Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

---

## 11. Ingress and TLS Strategy

### Decision: DigitalOcean Load Balancer + NGINX Ingress Controller

**Rationale**:
- DO LB integrates natively with DOKS
- NGINX Ingress is well-documented and reliable
- TLS termination at ingress level
- Can use Let's Encrypt with cert-manager (optional for Phase C)

**Architecture**:
```
Internet
    │
    ▼
DO Load Balancer (auto-provisioned)
    │
    ▼
NGINX Ingress Controller (ClusterIP)
    │
    ├──→ /api/* → Backend Service
    └──→ /* → Frontend Service
```

**Ingress Configuration**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: todo.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 3000
```

---

## 12. Resource Limits Strategy

### Decision: Conservative Defaults with Room for Growth

**Rationale**:
- Start with Phase 4 limits as baseline
- Increase for production to handle traffic spikes
- Use requests to ensure scheduling, limits to prevent runaway processes

**Resource Allocations**:
| Service | Requests (CPU/Memory) | Limits (CPU/Memory) |
|---------|----------------------|---------------------|
| Backend (staging) | 250m / 256Mi | 500m / 512Mi |
| Backend (prod) | 500m / 512Mi | 1000m / 1Gi |
| Frontend (staging) | 100m / 128Mi | 250m / 256Mi |
| Frontend (prod) | 250m / 256Mi | 500m / 512Mi |
| Workers (staging) | 100m / 128Mi | 250m / 256Mi |
| Workers (prod) | 250m / 256Mi | 500m / 512Mi |

---

## 13. Local Development Continuity

### Decision: Preserve docker-compose.dapr.yml Unchanged

**Rationale**:
- Local development must continue to work exactly as before
- Developers should not need cloud access for local work
- Cloud-specific configuration lives in k8s/overlays, not in existing files

**Key Files Unchanged**:
- `docker-compose.dapr.yml` - Local event-driven stack
- `docker-compose.yml` - Simple local stack
- `dapr/components/*` - Local Dapr components
- All backend/frontend/worker source code

**Cloud-Specific Files (New)**:
- `k8s/base/dapr/*.yaml` - Cloud Dapr components with secret references
- `k8s/overlays/*/` - Environment-specific configurations
- `.github/workflows/*.yaml` - CI/CD pipelines

---

## 14. Rollback Strategy

### Decision: Kubernetes Native Rolling Deployment

**Rationale**:
- Built into Kubernetes Deployments
- Automatic rollback on failed health checks
- Manual rollback available via `kubectl rollout undo`
- Revision history maintained for audit

**Deployment Strategy Configuration**:
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  revisionHistoryLimit: 5
```

**Rollback Commands**:
```bash
# View rollout history
kubectl rollout history deployment/backend -n todo-production

# Rollback to previous version
kubectl rollout undo deployment/backend -n todo-production

# Rollback to specific revision
kubectl rollout undo deployment/backend -n todo-production --to-revision=2
```

---

## Summary of Decisions

| Category | Decision | Confidence |
|----------|----------|------------|
| Kubernetes Provider | DigitalOcean Kubernetes (DOKS) | High |
| Kafka Provider | Confluent Cloud | High |
| Container Registry | GitHub Container Registry (GHCR) | High |
| Manifest Management | Kustomize (base + overlays) | High |
| CI/CD Platform | GitHub Actions | High |
| Observability | Prometheus + Grafana + Zipkin | High |
| Secrets Management | Kubernetes Secrets | High |
| Environment Separation | Namespace-based isolation | High |
| Dapr Installation | dapr init -k (HA mode) | High |
| Ingress | NGINX Ingress + DO Load Balancer | High |
| TLS | Manual for Phase C (cert-manager optional) | Medium |

All decisions prioritize simplicity, cost-effectiveness, and alignment with existing Phase B patterns while enabling production-grade reliability.
