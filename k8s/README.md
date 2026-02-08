# Kubernetes Deployment - Todo Application

This directory contains Kubernetes manifests for deploying the Todo application to a managed Kubernetes cluster (DigitalOcean DOKS or GKE).

## Directory Structure

```
k8s/
├── base/                           # Shared base manifests
│   ├── kustomization.yaml          # Base kustomization
│   ├── namespace.yaml              # Namespace definition
│   ├── backend/                    # Backend API manifests
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── frontend/                   # Frontend manifests
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── workers/                    # Worker manifests
│   │   ├── reminder-worker-deployment.yaml
│   │   ├── reminder-worker-service.yaml
│   │   ├── recurrence-worker-deployment.yaml
│   │   └── recurrence-worker-service.yaml
│   └── dapr/                       # Dapr components
│       ├── pubsub.yaml
│       ├── statestore.yaml
│       ├── secrets.yaml
│       ├── cron-binding.yaml
│       └── configuration.yaml
├── overlays/
│   ├── staging/                    # Staging environment
│   │   ├── kustomization.yaml
│   │   ├── namespace.yaml
│   │   ├── secrets.yaml.template
│   │   └── patches/
│   │       ├── replica-count.yaml
│   │       └── resource-limits.yaml
│   └── production/                 # Production environment
│       ├── kustomization.yaml
│       ├── namespace.yaml
│       ├── ingress.yaml
│       ├── secrets.yaml.template
│       └── patches/
│           ├── replica-count.yaml
│           └── resource-limits.yaml
└── observability/                  # Monitoring stack
    ├── namespace.yaml
    ├── prometheus-values.yaml
    ├── grafana-values.yaml
    ├── grafana-dashboards/
    │   └── todo-app.json
    └── zipkin.yaml
```

## Prerequisites

### Required Tools
- `kubectl` v1.28+
- `kustomize` v5+ (or use `kubectl -k`)
- `helm` v3.12+ (for observability stack)
- `dapr` CLI v1.13+

### Required Accounts
- Kubernetes cluster (DigitalOcean DOKS or GKE)
- Container registry (GHCR)
- Cloud Kafka (Confluent Cloud)
- PostgreSQL database (Neon)

## Dapr Installation (T032, T033-T036)

Dapr must be installed on the cluster before deploying the application.

### Install Dapr on Kubernetes

```bash
# Install Dapr CLI (if not already installed)
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Initialize Dapr on Kubernetes with HA mode
dapr init -k --enable-ha --enable-mtls

# Verify Dapr installation
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
dapr-operator          dapr-system  True     Running  1         1.13.x   ...
dapr-sidecar-injector  dapr-system  True     Running  1         1.13.x   ...
dapr-placement-server  dapr-system  True     Running  1         1.13.x   ...
dapr-dashboard         dapr-system  True     Running  1         0.14.x   ...
```

### Dapr Sidecar Injection

The backend and worker deployments include Dapr annotations for automatic sidecar injection:

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
  dapr.io/log-level: "info"
  dapr.io/config: "dapr-config"
```

### Dapr Components

The following Dapr components are configured:
- **taskpubsub**: Kafka pub/sub for event messaging
- **statestore**: Redis state store (optional)
- **kubernetes-secrets**: Kubernetes secret store
- **cron-reminder**: Cron binding for reminder checks
- **dapr-config**: Configuration with Zipkin tracing

## Deployment Commands (T051)

### Deploy to Staging

```bash
# Create secrets first (see secrets.yaml.template for required secrets)
kubectl create secret generic db-credentials \
  --from-literal=DATABASE_URL="postgresql://..." \
  -n todo-staging

kubectl create secret generic kafka-credentials \
  --from-literal=brokers="..." \
  --from-literal=username="..." \
  --from-literal=password="..." \
  -n todo-staging

kubectl create secret generic app-secrets \
  --from-literal=JWT_SECRET="..." \
  -n todo-staging

# Deploy application
kubectl apply -k k8s/overlays/staging

# Verify deployment
kubectl get pods -n todo-staging
kubectl get services -n todo-staging
kubectl get components.dapr.io -n todo-staging
```

### Deploy to Production

```bash
# Create production secrets
kubectl create secret generic db-credentials \
  --from-literal=DATABASE_URL="postgresql://..." \
  -n todo-production

kubectl create secret generic kafka-credentials \
  --from-literal=brokers="..." \
  --from-literal=username="..." \
  --from-literal=password="..." \
  -n todo-production

kubectl create secret generic app-secrets \
  --from-literal=JWT_SECRET="..." \
  -n todo-production

# Deploy application
kubectl apply -k k8s/overlays/production

# Verify deployment
kubectl get pods -n todo-production
kubectl get ingress -n todo-production
```

### Build and Preview Manifests

```bash
# Preview staging manifests without applying
kustomize build k8s/overlays/staging

# Preview production manifests
kustomize build k8s/overlays/production

# Dry run to validate
kubectl apply -k k8s/overlays/staging --dry-run=client
```

## Observability Deployment (T068)

### Deploy Prometheus

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Create observability namespace
kubectl create namespace observability

# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  -n observability \
  -f k8s/observability/prometheus-values.yaml
```

### Deploy Grafana

```bash
# Add Grafana Helm repo
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Grafana
helm install grafana grafana/grafana \
  -n observability \
  -f k8s/observability/grafana-values.yaml

# Get Grafana admin password
kubectl get secret grafana -n observability -o jsonpath="{.data.admin-password}" | base64 --decode
```

### Deploy Zipkin

```bash
kubectl apply -f k8s/observability/zipkin.yaml -n observability
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n todo-staging
kubectl describe pod <pod-name> -n todo-staging
kubectl logs <pod-name> -n todo-staging
kubectl logs <pod-name> -c daprd -n todo-staging  # Dapr sidecar logs
```

### Check Dapr Components

```bash
kubectl get components.dapr.io -n todo-staging
kubectl describe component taskpubsub -n todo-staging
dapr components -k -n todo-staging
```

### Check Dapr Dashboard

```bash
dapr dashboard -k
```

### Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/backend -n todo-staging

# Rollback to previous version
kubectl rollout undo deployment/backend -n todo-staging

# Rollback to specific revision
kubectl rollout undo deployment/backend -n todo-staging --to-revision=2
```

## Environment Differences (T048-T052)

| Aspect | Staging | Production |
|--------|---------|------------|
| Namespace | `todo-staging` | `todo-production` |
| Backend Replicas | 1 | 3 |
| Frontend Replicas | 1 | 2 |
| Worker Replicas | 1 each | 2 each |
| Resource Limits | Conservative | Elevated |
| Ingress | None | NGINX |
| Image Tags | `staging` | Semver (v1.0.0) |

## Related Documentation

- [Deployment Guide](../docs/deployment-guide.md)
- [Production Readiness Checklist](../docs/production-readiness-checklist.md)
- [Quickstart](../specs/005-phase5-partc-cloud-production/quickstart.md)
