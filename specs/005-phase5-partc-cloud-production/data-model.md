# Data Model: Phase V Part C - Cloud Production Deployment

**Created**: 2026-02-08
**Branch**: `005-phase5-partc-cloud-production`
**Status**: Complete

---

## Overview

Phase V Part C does not introduce new application data models. Instead, it defines **infrastructure entities** (Kubernetes resources, Dapr components, CI/CD artifacts) that enable cloud deployment. This document describes these infrastructure entities and their relationships.

---

## 1. Kubernetes Resource Entities

### 1.1 Namespace

Isolation boundary for environment separation.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Namespace identifier (`todo-staging`, `todo-production`) |
| labels | map | Environment labels for filtering |
| annotations | map | Metadata (e.g., owner, created-by) |

**Instances**:
- `todo-staging` - Pre-production environment
- `todo-production` - Live production environment
- `dapr-system` - Dapr control plane (managed)
- `observability` - Monitoring stack

---

### 1.2 Deployment

Manages pod replicas for each service.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Deployment identifier |
| namespace | string | Target namespace |
| replicas | int | Number of pod replicas |
| selector | LabelSelector | Pod selection criteria |
| template | PodTemplateSpec | Pod specification |
| strategy | DeploymentStrategy | Rolling update configuration |

**Instances**:
- `backend` - FastAPI API server
- `frontend` - Next.js web application
- `reminder-worker` - Reminder event processor
- `recurrence-worker` - Recurrence event processor

**Key Annotations for Dapr**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
  dapr.io/log-level: "info"
```

---

### 1.3 Service

Network endpoint for accessing pods.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Service identifier |
| namespace | string | Target namespace |
| type | ServiceType | ClusterIP, LoadBalancer, NodePort |
| ports | []Port | Port mappings |
| selector | map | Pod selection labels |

**Instances**:
| Service | Type | Port | Target |
|---------|------|------|--------|
| backend | ClusterIP | 8000 | Backend pods |
| frontend | ClusterIP | 3000 | Frontend pods |
| reminder-worker | ClusterIP | 8001 | Worker pods (internal) |
| recurrence-worker | ClusterIP | 8002 | Worker pods (internal) |

---

### 1.4 ConfigMap

Non-sensitive configuration data.

| Field | Type | Description |
|-------|------|-------------|
| name | string | ConfigMap identifier |
| namespace | string | Target namespace |
| data | map[string]string | Key-value configuration |

**Instances**:
- `backend-config` - ENVIRONMENT, LOG_LEVEL, DAPR_HTTP_PORT
- `frontend-config` - NEXT_PUBLIC_API_URL
- `worker-config` - APP_PORT, LOG_LEVEL

---

### 1.5 Secret

Sensitive configuration (credentials, keys).

| Field | Type | Description |
|-------|------|-------------|
| name | string | Secret identifier |
| namespace | string | Target namespace |
| type | SecretType | Opaque, kubernetes.io/tls, etc. |
| data | map[string][]byte | Base64-encoded secret data |

**Instances**:
| Secret | Keys | Used By |
|--------|------|---------|
| `db-credentials` | DATABASE_URL | Backend, Workers |
| `kafka-credentials` | brokers, username, password | Dapr pubsub |
| `app-secrets` | JWT_SECRET, OPENAI_API_KEY | Backend |

---

### 1.6 Ingress

External HTTP(S) routing to services.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Ingress identifier |
| namespace | string | Target namespace |
| rules | []IngressRule | Host/path routing rules |
| tls | []TLSConfig | TLS certificates (optional) |

**Configuration** (production only):
```yaml
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

## 2. Dapr Component Entities

### 2.1 Pub/Sub Component

Event messaging via Kafka.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Component name (`taskpubsub`) |
| type | string | `pubsub.kafka` |
| version | string | Component version |
| metadata | []MetadataItem | Connection configuration |

**Cloud Configuration**:
```yaml
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
  - name: consumerGroup
    value: "todo-consumers"
```

---

### 2.2 State Store Component

State management via Redis.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Component name (`statestore`) |
| type | string | `state.redis` |
| version | string | Component version |
| metadata | []MetadataItem | Connection configuration |

**Note**: Redis can be self-hosted in cluster or use managed Redis (DigitalOcean Managed Redis).

---

### 2.3 Secrets Component

Secrets retrieval from Kubernetes.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Component name (`kubernetes-secrets`) |
| type | string | `secretstores.kubernetes` |
| version | string | Component version |

**Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
```

---

### 2.4 Cron Binding Component

Scheduled trigger for reminders.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Component name (`cron-reminder`) |
| type | string | `bindings.cron` |
| metadata | []MetadataItem | Schedule configuration |

**Configuration**:
```yaml
metadata:
  - name: schedule
    value: "@every 1m"
  - name: route
    value: "/cron/check-reminders"
```

---

### 2.5 Dapr Configuration

Runtime settings for tracing and metrics.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Configuration name (`dapr-config`) |
| tracing | TracingSpec | Zipkin endpoint configuration |
| metric | MetricSpec | Prometheus enablement |

**Configuration**:
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

## 3. CI/CD Entities

### 3.1 GitHub Actions Workflow

Automated pipeline definition.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Workflow identifier |
| on | Trigger | Events that trigger the workflow |
| jobs | map[string]Job | Pipeline jobs |
| env | map[string]string | Environment variables |

**Workflows**:
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yaml` | push to main, PR | Lint, test, build, push images |
| `cd-staging.yaml` | ci.yaml success | Deploy to staging namespace |
| `cd-production.yaml` | manual dispatch | Deploy to production (requires approval) |

---

### 3.2 Container Image

Docker image artifact.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Image name (e.g., `todo-backend`) |
| registry | string | Container registry (GHCR) |
| tag | string | Version tag |
| digest | string | SHA256 digest |

**Tagging Convention**:
| Environment | Tag Pattern | Example |
|-------------|-------------|---------|
| Development | `dev-<sha>` | `dev-abc1234` |
| Staging | `staging-<sha>` | `staging-abc1234` |
| Production | `v<semver>` | `v1.0.0` |

---

## 4. Observability Entities

### 4.1 Prometheus

Metrics collection and storage.

| Field | Type | Description |
|-------|------|-------------|
| scrapeConfigs | []ScrapeConfig | Targets to scrape metrics from |
| rules | []Rule | Alerting rules |
| retention | string | Data retention period |

**Scrape Targets**:
- Backend: `/metrics` on port 8000
- Frontend: `/metrics` on port 3000 (if exposed)
- Dapr sidecars: `:9090/metrics`
- Workers: `/metrics` on respective ports

---

### 4.2 Grafana Dashboard

Metrics visualization.

| Field | Type | Description |
|-------|------|-------------|
| title | string | Dashboard title |
| panels | []Panel | Visualization panels |
| datasource | string | Prometheus connection |

**Panels**:
- Request rate (req/sec)
- Latency (p50, p95, p99)
- Error rate (%)
- Pod health (up/down)
- Event throughput (Kafka)

---

### 4.3 Zipkin Trace

Distributed trace record.

| Field | Type | Description |
|-------|------|-------------|
| traceId | string | Unique trace identifier |
| spans | []Span | Individual operations |
| duration | int64 | Total trace duration (μs) |

**Trace Flow**:
```
Frontend → Backend → Dapr Sidecar → Kafka → Worker Sidecar → Worker
```

---

## 5. Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Kubernetes Cluster                            │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Namespace: todo-production                  │   │
│  │                                                                  │   │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │   │
│  │   │  Deployment  │    │  Deployment  │    │  Deployment  │     │   │
│  │   │   backend    │    │   frontend   │    │   worker     │     │   │
│  │   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │   │
│  │          │ uses              │ uses              │ uses        │   │
│  │          ▼                   ▼                   ▼             │   │
│  │   ┌──────────────────────────────────────────────────────┐     │   │
│  │   │                     Secrets                          │     │   │
│  │   │  db-credentials | kafka-credentials | app-secrets    │     │   │
│  │   └──────────────────────────────────────────────────────┘     │   │
│  │          │                                                     │   │
│  │          ▼                                                     │   │
│  │   ┌──────────────────────────────────────────────────────┐     │   │
│  │   │                  Dapr Components                      │     │   │
│  │   │  pubsub (Kafka) | statestore (Redis) | cron-binding  │     │   │
│  │   └──────────────────────────────────────────────────────┘     │   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Namespace: observability                       │  │
│  │   ┌────────────┐   ┌────────────┐   ┌────────────┐              │  │
│  │   │ Prometheus │   │  Grafana   │   │   Zipkin   │              │  │
│  │   └────────────┘   └────────────┘   └────────────┘              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
         │                           │                           │
         ▼                           ▼                           ▼
┌────────────────┐      ┌────────────────────┐      ┌────────────────┐
│  GHCR Registry │      │   Confluent Cloud  │      │ Neon PostgreSQL│
│  (Images)      │      │   (Kafka)          │      │ (Database)     │
└────────────────┘      └────────────────────┘      └────────────────┘
```

---

## 6. Validation Rules

### Namespace Validation
- Name must be lowercase alphanumeric with hyphens
- Must not conflict with system namespaces (`kube-*`, `dapr-*`)

### Deployment Validation
- Replicas must be >= 1 for production
- Resource requests must be <= limits
- Health probes must be defined

### Secret Validation
- Must exist before dependent deployments
- Keys must match expected references in manifests
- Never commit actual values to source control

### Dapr Component Validation
- Name must match application references (`taskpubsub`)
- Secret references must exist in namespace
- Type must be valid Dapr component type

---

## 7. State Transitions

### Deployment Rollout States
```
Pending → Progressing → Available
                      ↓
                   Failed → Rolled Back
```

### Pod Lifecycle States
```
Pending → ContainerCreating → Running → Terminating → Terminated
                                ↓
                             CrashLoopBackOff → Restart
```

### CI/CD Pipeline States
```
Queued → In Progress → Success/Failure
                         ↓
                    Approval Requested → Approved → Deployed
                                       ↓
                                    Rejected
```

---

## Summary

This data model defines the infrastructure entities for Phase V Part C. Key points:

1. **No application data model changes** - Existing Task, User, Event models remain unchanged
2. **Kubernetes resources** form the deployment layer (Deployments, Services, Secrets)
3. **Dapr components** enable event-driven architecture on Kubernetes
4. **CI/CD entities** automate the deployment pipeline
5. **Observability entities** provide production monitoring

All entities are defined as YAML manifests in the `k8s/` directory structure.
