# Deployment Contracts: Phase V Part C

**Created**: 2026-02-08
**Branch**: `005-phase5-partc-cloud-production`

---

## Overview

Phase V Part C does not introduce new API endpoints. The application APIs remain unchanged from Phase B. This document defines **deployment contracts** - the expected behaviors and interfaces for infrastructure operations.

---

## 1. Health Check Contracts

### Backend Health Endpoint

**Endpoint**: `GET /health`

**Response** (Success - 200):
```json
{
  "status": "healthy",
  "timestamp": "2026-02-08T12:00:00Z"
}
```

**Response** (Failure - 503):
```json
{
  "status": "unhealthy",
  "error": "Database connection failed"
}
```

---

### Backend Ready Endpoint

**Endpoint**: `GET /health/ready`

**Response** (Success - 200):
```json
{
  "status": "ready",
  "database": "connected",
  "dapr": "connected"
}
```

**Response** (Not Ready - 503):
```json
{
  "status": "not_ready",
  "database": "disconnected",
  "dapr": "connected"
}
```

---

### Worker Health Endpoint

**Endpoint**: `GET /health`

**Response** (Success - 200):
```json
{
  "status": "healthy",
  "worker": "reminder-worker",
  "timestamp": "2026-02-08T12:00:00Z"
}
```

---

## 2. Kubernetes Deployment Contracts

### Deployment Specification Contract

Every deployment MUST include:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <service-name>
  namespace: <environment>
  labels:
    app: <service-name>
    environment: <staging|production>
spec:
  replicas: <count>
  selector:
    matchLabels:
      app: <service-name>
  template:
    metadata:
      labels:
        app: <service-name>
      annotations:
        dapr.io/enabled: "true"          # Required for Dapr
        dapr.io/app-id: "<service-name>"
        dapr.io/app-port: "<port>"
    spec:
      containers:
        - name: <service-name>
          image: ghcr.io/<org>/<image>:<tag>
          ports:
            - containerPort: <port>
          resources:
            requests:
              cpu: <request>
              memory: <request>
            limits:
              cpu: <limit>
              memory: <limit>
          livenessProbe:
            httpGet:
              path: /health
              port: <port>
            initialDelaySeconds: 15
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: <port>
            initialDelaySeconds: 5
            periodSeconds: 5
          envFrom:
            - configMapRef:
                name: <service>-config
            - secretRef:
                name: <secret-name>
```

---

### Service Specification Contract

Every service MUST include:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <service-name>
  namespace: <environment>
spec:
  type: ClusterIP
  selector:
    app: <service-name>
  ports:
    - port: <external-port>
      targetPort: <container-port>
      protocol: TCP
```

---

## 3. Dapr Component Contracts

### Pub/Sub Component Contract

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
  namespace: <environment>
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
    - name: consumerGroup
      value: "todo-consumers"
    - name: initialOffset
      value: "oldest"
```

---

### State Store Component Contract

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: <environment>
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis.todo-<env>.svc.cluster.local:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-credentials
        key: password
```

---

## 4. Secret Contracts

### Required Secrets

| Secret Name | Required Keys | Description |
|-------------|---------------|-------------|
| `db-credentials` | DATABASE_URL | PostgreSQL connection string |
| `kafka-credentials` | brokers, username, password | Kafka SASL credentials |
| `app-secrets` | JWT_SECRET, OPENAI_API_KEY | Application secrets |

### Secret Template Contract

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <secret-name>
  namespace: <environment>
type: Opaque
stringData:
  KEY_NAME: "<value>"  # Template only, never commit actual values
```

---

## 5. CI/CD Pipeline Contracts

### CI Workflow Contract

**Trigger**: Push to main branch or Pull Request

**Required Jobs**:
1. `lint` - Code quality checks
2. `test` - Unit and integration tests
3. `build` - Docker image build
4. `push` - Push to container registry (main branch only)

**Expected Outputs**:
- Test results (pass/fail)
- Docker images tagged with commit SHA
- Build artifacts cached

---

### CD Staging Contract

**Trigger**: Successful CI workflow on main branch

**Required Steps**:
1. Pull latest images from registry
2. Apply Kustomize overlays for staging
3. Wait for rollout completion
4. Run smoke tests

**Expected Behavior**:
- Deployment completes within 5 minutes
- All pods reach Running state
- Health checks pass

---

### CD Production Contract

**Trigger**: Manual workflow dispatch with approval

**Required Steps**:
1. Require environment approval
2. Pull specific image tag (not latest)
3. Apply Kustomize overlays for production
4. Rolling deployment with zero downtime
5. Verify deployment health

**Expected Behavior**:
- Approval required before deployment
- Rollback triggered automatically on failure
- Deployment completes with zero downtime

---

## 6. Observability Contracts

### Metrics Contract

All services MUST expose Prometheus metrics at `/metrics`:

**Required Metrics**:
- `http_requests_total{method, path, status}` - Request count
- `http_request_duration_seconds{method, path}` - Request latency histogram
- `http_requests_in_progress` - Current request count

---

### Logging Contract

All services MUST emit structured JSON logs:

```json
{
  "timestamp": "2026-02-08T12:00:00.000Z",
  "level": "INFO",
  "service": "backend",
  "message": "Request processed",
  "trace_id": "abc123",
  "span_id": "def456",
  "method": "POST",
  "path": "/api/tasks",
  "status": 201,
  "duration_ms": 45
}
```

---

### Tracing Contract

All services MUST propagate trace context headers:

**Required Headers**:
- `traceparent` - W3C Trace Context
- `tracestate` - W3C Trace State (optional)

Dapr handles trace propagation automatically when configured.

---

## 7. Environment Contract

### Staging Environment

| Aspect | Value |
|--------|-------|
| Namespace | `todo-staging` |
| Backend Replicas | 1 |
| Frontend Replicas | 1 |
| Worker Replicas | 1 each |
| Resource Limits | Standard (see research.md) |
| Ingress | Optional (NodePort/LoadBalancer for testing) |

### Production Environment

| Aspect | Value |
|--------|-------|
| Namespace | `todo-production` |
| Backend Replicas | 3 |
| Frontend Replicas | 2 |
| Worker Replicas | 2 each |
| Resource Limits | Elevated (see research.md) |
| Ingress | Required with HTTPS |

---

## 8. Rollout Contract

### Rolling Update Strategy

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # One extra pod during update
    maxUnavailable: 0  # Zero downtime
```

### Health Check Gates

- New pods must pass readiness probe before receiving traffic
- Old pods continue serving until new pods are ready
- Deployment fails if pods don't become ready within 5 minutes

### Rollback Triggers

- Readiness probe fails for 3 consecutive checks
- Liveness probe fails for 3 consecutive checks
- Container exits with non-zero code

---

## Summary

These contracts define the expected interfaces and behaviors for Phase V Part C deployment infrastructure. Key points:

1. **Health endpoints** must return consistent JSON responses
2. **Kubernetes resources** must follow specified templates
3. **Dapr components** must use Kubernetes secrets for credentials
4. **CI/CD pipelines** must include required stages and approvals
5. **Observability** must include metrics, structured logs, and tracing
6. **Deployments** must support zero-downtime rolling updates

All contracts are enforced through Kubernetes manifests and CI/CD pipeline definitions.
