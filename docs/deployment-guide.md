# Todo Application Deployment Guide

This guide covers deploying the Todo application to a managed Kubernetes cluster.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Cloud Provider Setup](#cloud-provider-setup)
4. [Confluent Cloud Setup](#confluent-cloud-setup)
5. [Container Registry Setup](#container-registry-setup)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Secrets Management](#secrets-management)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Observability Setup](#observability-setup)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

```bash
# kubectl v1.28+
kubectl version --client

# kustomize v5+ (or use kubectl -k)
kustomize version

# Helm v3.12+
helm version

# Dapr CLI v1.13+
dapr --version

# GitHub CLI (for GHCR)
gh --version
```

### Required Accounts

- **Kubernetes Cluster**: DigitalOcean DOKS or Google GKE
- **Container Registry**: GitHub Container Registry (GHCR)
- **Managed Kafka**: Confluent Cloud
- **PostgreSQL Database**: Neon or similar

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 todo-production namespace               │ │
│  │                                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │ │
│  │  │   Backend   │  │  Frontend   │  │    Workers     │  │ │
│  │  │  (3 pods)   │  │  (2 pods)   │  │   (2 each)     │  │ │
│  │  │  + Dapr     │  │             │  │   + Dapr       │  │ │
│  │  └──────┬──────┘  └──────┬──────┘  └───────┬────────┘  │ │
│  │         │                │                  │           │ │
│  │         └────────┬───────┴──────────────────┘           │ │
│  │                  │                                      │ │
│  │         ┌────────▼────────┐                             │ │
│  │         │     Ingress     │                             │ │
│  │         │     (NGINX)     │                             │ │
│  │         └────────┬────────┘                             │ │
│  └──────────────────┼──────────────────────────────────────┘ │
│                     │                                        │
└─────────────────────┼────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐  ┌─────▼─────┐  ┌────▼────┐
   │ Neon DB │  │ Confluent │  │  GHCR   │
   │(Postgres)│  │  Cloud    │  │ Images  │
   └──────────┘  └───────────┘  └─────────┘
```

---

## Cloud Provider Setup

### DigitalOcean DOKS

```bash
# Install doctl CLI
brew install doctl  # macOS
# or download from https://github.com/digitalocean/doctl

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --node-pool "name=default;size=s-2vcpu-4gb;count=3" \
  --version 1.28.2-do.0

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster

# Verify connection
kubectl get nodes
```

### Google GKE

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Create cluster
gcloud container clusters create todo-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium \
  --release-channel regular

# Get credentials
gcloud container clusters get-credentials todo-cluster --zone us-central1-a

# Verify connection
kubectl get nodes
```

---

## Confluent Cloud Setup

### Create Cluster

1. Sign up at https://confluent.cloud
2. Create a new cluster (Basic tier is sufficient)
3. Note the **Bootstrap server** endpoint

### Create Topics

Create the following topics with default settings:

- `task-created`
- `task-updated`
- `task-completed`
- `task-deleted`
- `reminder-due`
- `recurrence-trigger`

### Create API Keys

1. Go to **API Keys** in your cluster
2. Create a new key with **Global access**
3. Note the **Key** and **Secret**

### Example Confluent Cloud Settings

```
Bootstrap Servers: pkc-xxxxx.us-east-1.aws.confluent.cloud:9092
API Key: ABCDEFGHIJKLMNOP
API Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Container Registry Setup

### GitHub Container Registry (GHCR)

```bash
# Authenticate with GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USER --password-stdin

# Build and tag images
docker build -t ghcr.io/YOUR_ORG/todo-backend:v1.0.0 -f docker/backend/Dockerfile .
docker build -t ghcr.io/YOUR_ORG/todo-frontend:v1.0.0 -f docker/frontend/Dockerfile .
docker build -t ghcr.io/YOUR_ORG/todo-reminder-worker:v1.0.0 -f docker/workers/reminder-worker/Dockerfile .
docker build -t ghcr.io/YOUR_ORG/todo-recurrence-worker:v1.0.0 -f docker/workers/recurrence-worker/Dockerfile .

# Push images
docker push ghcr.io/YOUR_ORG/todo-backend:v1.0.0
docker push ghcr.io/YOUR_ORG/todo-frontend:v1.0.0
docker push ghcr.io/YOUR_ORG/todo-reminder-worker:v1.0.0
docker push ghcr.io/YOUR_ORG/todo-recurrence-worker:v1.0.0
```

---

## Kubernetes Deployment

### Install Dapr

```bash
# Install Dapr on Kubernetes with HA mode
dapr init -k --enable-ha --enable-mtls

# Verify installation
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION
dapr-operator          dapr-system  True     Running  1         1.13.x
dapr-sidecar-injector  dapr-system  True     Running  1         1.13.x
dapr-placement-server  dapr-system  True     Running  1         1.13.x
dapr-dashboard         dapr-system  True     Running  1         0.14.x
```

### Install NGINX Ingress

```bash
# Using Helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

### Deploy to Staging

```bash
# Create namespace
kubectl apply -f k8s/overlays/staging/namespace.yaml

# Create secrets (see Secrets Management section)
# ...

# Deploy application
kubectl apply -k k8s/overlays/staging

# Verify deployment
kubectl get pods -n todo-staging
kubectl get services -n todo-staging
kubectl get components.dapr.io -n todo-staging
```

### Deploy to Production

```bash
# Create namespace
kubectl apply -f k8s/overlays/production/namespace.yaml

# Create secrets (see Secrets Management section)
# ...

# Deploy application
kubectl apply -k k8s/overlays/production

# Verify deployment
kubectl get pods -n todo-production
kubectl get services -n todo-production
kubectl get ingress -n todo-production
```

---

## Secrets Management

### Required Secrets

| Secret Name | Keys | Description |
|-------------|------|-------------|
| `db-credentials` | `DATABASE_URL` | PostgreSQL connection string |
| `kafka-credentials` | `brokers`, `username`, `password` | Confluent Cloud credentials |
| `app-secrets` | `JWT_SECRET`, `OPENAI_API_KEY` | Application secrets |

### Creating Secrets

```bash
# Database credentials
kubectl create secret generic db-credentials \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/todo?sslmode=require" \
  -n todo-production

# Kafka credentials (Confluent Cloud)
kubectl create secret generic kafka-credentials \
  --from-literal=brokers="pkc-xxxxx.us-east-1.aws.confluent.cloud:9092" \
  --from-literal=username="YOUR_API_KEY" \
  --from-literal=password="YOUR_API_SECRET" \
  -n todo-production

# Application secrets
kubectl create secret generic app-secrets \
  --from-literal=JWT_SECRET="your-strong-256-bit-secret" \
  --from-literal=OPENAI_API_KEY="sk-xxxxx" \
  -n todo-production
```

### Secret Rotation Procedure

1. **Generate new secret value**
   ```bash
   # For JWT_SECRET
   openssl rand -base64 32
   ```

2. **Create new secret version**
   ```bash
   kubectl create secret generic app-secrets \
     --from-literal=JWT_SECRET="NEW_SECRET_VALUE" \
     --from-literal=OPENAI_API_KEY="sk-xxxxx" \
     -n todo-production \
     --dry-run=client -o yaml | kubectl apply -f -
   ```

3. **Restart deployments to pick up new secret**
   ```bash
   kubectl rollout restart deployment/backend -n todo-production
   kubectl rollout restart deployment/reminder-worker -n todo-production
   kubectl rollout restart deployment/recurrence-worker -n todo-production
   ```

4. **Verify new secret is in use**
   ```bash
   kubectl exec -it deployment/backend -n todo-production -- printenv JWT_SECRET | head -c 10
   ```

---

## CI/CD Pipeline

### Required GitHub Secrets

Configure these secrets in your repository settings:

| Secret Name | Description |
|-------------|-------------|
| `KUBE_CONFIG_STAGING` | Base64-encoded kubeconfig for staging |
| `KUBE_CONFIG_PRODUCTION` | Base64-encoded kubeconfig for production |

### Encoding Kubeconfig

```bash
# Get kubeconfig and encode
cat ~/.kube/config | base64 -w0
```

### Pipeline Overview

```
Push to main
    │
    ▼
┌─────────────────┐
│   CI Pipeline   │
│  - Lint         │
│  - Test         │
│  - Build        │
│  - Push images  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ CD Staging      │
│ (automatic)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ CD Production   │
│ (manual trigger)│
└─────────────────┘
```

### Manual Deployment

```bash
# Use the deployment script
./scripts/deploy-k8s.sh -e production

# Or use Kustomize directly
kubectl apply -k k8s/overlays/production
```

---

## Observability Setup

### Deploy Prometheus

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace observability

helm install prometheus prometheus-community/prometheus \
  -n observability \
  -f k8s/observability/prometheus-values.yaml
```

### Deploy Grafana

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install grafana grafana/grafana \
  -n observability \
  -f k8s/observability/grafana-values.yaml

# Get admin password
kubectl get secret grafana -n observability -o jsonpath="{.data.admin-password}" | base64 --decode
```

### Deploy Zipkin

```bash
kubectl apply -f k8s/observability/zipkin.yaml -n observability
```

### Access Dashboards

```bash
# Grafana
kubectl port-forward svc/grafana 3000:80 -n observability
# Access at http://localhost:3000

# Prometheus
kubectl port-forward svc/prometheus-server 9090:80 -n observability
# Access at http://localhost:9090

# Zipkin
kubectl port-forward svc/zipkin 9411:9411 -n observability
# Access at http://localhost:9411

# Dapr Dashboard
dapr dashboard -k
# Access at http://localhost:8080
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-production

# Check events
kubectl get events -n todo-production --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n todo-production
kubectl logs <pod-name> -c daprd -n todo-production  # Dapr sidecar
```

### Dapr Component Issues

```bash
# List Dapr components
kubectl get components.dapr.io -n todo-production

# Describe component
kubectl describe component taskpubsub -n todo-production

# Check Dapr sidecar logs
kubectl logs deployment/backend -c daprd -n todo-production
```

### Kafka Connection Issues

```bash
# Verify secret exists
kubectl get secret kafka-credentials -n todo-production

# Check secret values (careful - displays secrets)
kubectl get secret kafka-credentials -n todo-production -o jsonpath='{.data.brokers}' | base64 -d

# Test connectivity from pod
kubectl exec -it deployment/backend -n todo-production -- \
  curl -v telnet://pkc-xxxxx.us-east-1.aws.confluent.cloud:9092
```

### Ingress Not Working

```bash
# Check ingress
kubectl get ingress -n todo-production
kubectl describe ingress todo-ingress -n todo-production

# Check ingress controller logs
kubectl logs -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx
```

### Database Connection Issues

```bash
# Verify secret
kubectl get secret db-credentials -n todo-production

# Test from pod
kubectl exec -it deployment/backend -n todo-production -- \
  python -c "import asyncpg; print('PostgreSQL driver OK')"
```

---

## Appendix

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET` | Yes | Secret for JWT signing |
| `ENVIRONMENT` | No | `staging` or `production` |
| `LOG_LEVEL` | No | `debug`, `info`, `warning`, `error` |
| `DAPR_HTTP_PORT` | No | Dapr HTTP port (default: 3500) |
| `OPENAI_API_KEY` | No | For AI features |

### Useful Commands

```bash
# Scale deployment
kubectl scale deployment/backend --replicas=5 -n todo-production

# View resource usage
kubectl top pods -n todo-production

# Force restart
kubectl rollout restart deployment/backend -n todo-production

# View rollout history
kubectl rollout history deployment/backend -n todo-production

# Rollback
kubectl rollout undo deployment/backend -n todo-production
```

---

**Last Updated**: Phase 5C Implementation
