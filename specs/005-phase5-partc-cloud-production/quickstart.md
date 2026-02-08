# Quickstart: Phase V Part C - Cloud Production Deployment

**Created**: 2026-02-08
**Branch**: `005-phase5-partc-cloud-production`

---

## Prerequisites

Before starting Phase V Part C implementation, ensure you have:

### Required Tools
- [ ] `kubectl` v1.28+ - Kubernetes CLI
- [ ] `dapr` CLI v1.13+ - Dapr management
- [ ] `kustomize` v5+ (or kubectl with built-in kustomize)
- [ ] `helm` v3.12+ - For observability stack
- [ ] `doctl` - DigitalOcean CLI (if using DOKS)
- [ ] `gh` - GitHub CLI (for Actions debugging)
- [ ] `docker` - For building images locally

### Required Accounts
- [ ] DigitalOcean account with Kubernetes cluster
- [ ] Confluent Cloud account (free tier)
- [ ] GitHub repository with Actions enabled
- [ ] Neon PostgreSQL database (existing from Phase B)

### Existing Artifacts (from Phase B)
- [ ] Working `docker-compose.dapr.yml` stack
- [ ] Backend, Frontend, Worker Docker images
- [ ] Dapr components for local development
- [ ] Event flow verified locally

---

## Quick Verification Commands

### Verify Tools
```bash
# Check all tools are installed
kubectl version --client
dapr --version
kustomize version
helm version
doctl version
gh version
docker version
```

### Verify Local Stack
```bash
# Ensure Phase B still works
docker-compose -f docker-compose.dapr.yml up -d
# Wait for services to be healthy
docker-compose -f docker-compose.dapr.yml ps
# Create a task to verify event flow
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Verify event flow"}'
# Check Redpanda console for events
open http://localhost:8080
```

---

## Implementation Order

### Phase C-1: Base Infrastructure (P0)
1. Create Kustomize base manifests
2. Set up namespace structure
3. Create Dapr component manifests (cloud Kafka)
4. Create secrets templates

### Phase C-2: Staging Deployment (P0)
1. Create staging overlay
2. Deploy to staging namespace
3. Verify pod health
4. Test event flow through cloud Kafka

### Phase C-3: CI/CD Pipeline (P1)
1. Create GitHub Actions CI workflow
2. Set up container registry authentication
3. Create staging deployment workflow
4. Test automated deployment

### Phase C-4: Observability (P2)
1. Deploy Prometheus and Grafana
2. Configure Dapr tracing to Zipkin
3. Create basic dashboards
4. Verify metrics and traces

### Phase C-5: Production Readiness (P2)
1. Create production overlay
2. Configure Ingress with TLS
3. Set up production approval workflow
4. Complete production readiness checklist

---

## Key Commands Reference

### Kubernetes Operations
```bash
# Apply Kustomize overlay
kubectl apply -k k8s/overlays/staging

# Check deployment status
kubectl get pods -n todo-staging

# View pod logs
kubectl logs -f deployment/backend -n todo-staging

# Check Dapr sidecar
kubectl logs -f deployment/backend -c daprd -n todo-staging

# Rollback deployment
kubectl rollout undo deployment/backend -n todo-staging
```

### Dapr Operations
```bash
# Install Dapr on cluster
dapr init -k --enable-ha --enable-mtls

# Check Dapr status
dapr status -k

# List Dapr components
kubectl get components.dapr.io -n todo-staging

# View Dapr dashboard
dapr dashboard -k
```

### Secret Management
```bash
# Create secret from literal
kubectl create secret generic db-credentials \
  --from-literal=DATABASE_URL="postgresql://..." \
  -n todo-staging

# View secret (base64 encoded)
kubectl get secret db-credentials -n todo-staging -o yaml

# Update secret
kubectl create secret generic db-credentials \
  --from-literal=DATABASE_URL="new-url" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart deployment to pick up new secret
kubectl rollout restart deployment/backend -n todo-staging
```

### CI/CD Operations
```bash
# Trigger workflow manually
gh workflow run cd-production.yaml

# View workflow runs
gh run list

# View workflow logs
gh run view <run-id> --log
```

---

## Directory Structure After Implementation

```
k8s/
├── base/
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── workers/
│   │   ├── reminder-worker-deployment.yaml
│   │   └── recurrence-worker-deployment.yaml
│   └── dapr/
│       ├── pubsub.yaml
│       ├── statestore.yaml
│       ├── cron-binding.yaml
│       └── configuration.yaml
├── overlays/
│   ├── staging/
│   │   ├── kustomization.yaml
│   │   ├── namespace.yaml
│   │   ├── secrets.yaml.template
│   │   └── patches/
│   │       ├── replica-count.yaml
│   │       └── resource-limits.yaml
│   └── production/
│       ├── kustomization.yaml
│       ├── namespace.yaml
│       ├── ingress.yaml
│       ├── secrets.yaml.template
│       └── patches/
│           ├── replica-count.yaml
│           └── resource-limits.yaml
└── observability/
    ├── prometheus-values.yaml
    ├── grafana-values.yaml
    ├── grafana-dashboards/
    │   └── todo-app.json
    └── zipkin.yaml

.github/
└── workflows/
    ├── ci.yaml
    ├── cd-staging.yaml
    └── cd-production.yaml

docs/
├── production-readiness-checklist.md
└── deployment-guide.md
```

---

## Validation Checkpoints

### After Phase C-1
- [ ] Base manifests apply without errors: `kubectl apply -k k8s/base --dry-run=client`
- [ ] All resource templates are valid YAML

### After Phase C-2
- [ ] All pods in staging are Running: `kubectl get pods -n todo-staging`
- [ ] Backend health check passes: `kubectl exec ... -- curl localhost:8000/health`
- [ ] Events flow to cloud Kafka (check Confluent Cloud UI)

### After Phase C-3
- [ ] CI workflow passes on push to main
- [ ] Docker images pushed to GHCR
- [ ] Staging deployment triggers automatically

### After Phase C-4
- [ ] Prometheus scrapes all services
- [ ] Grafana dashboard shows metrics
- [ ] Zipkin shows distributed traces

### After Phase C-5
- [ ] Production overlay applies correctly
- [ ] Ingress routes traffic to services
- [ ] Production approval workflow requires manual approval
- [ ] Production readiness checklist is 100% complete

---

## Troubleshooting Quick Reference

### Pod Not Starting
```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace>
kubectl logs <pod-name> -c daprd -n <namespace>  # Dapr sidecar logs
```

### Dapr Component Issues
```bash
kubectl get components.dapr.io -n <namespace>
kubectl describe component taskpubsub -n <namespace>
dapr components -k -n <namespace>
```

### Image Pull Errors
```bash
kubectl get events -n <namespace> | grep pull
# Verify secret exists
kubectl get secret ghcr-pull-secret -n <namespace>
```

### Service Connectivity
```bash
kubectl exec -it deployment/backend -n <namespace> -- /bin/sh
curl http://frontend:3000  # Test internal connectivity
```

---

## Next Steps

After completing this quickstart:

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Execute tasks in order (respect dependencies)
3. Validate each checkpoint before proceeding
4. Complete production readiness checklist before launch

---

## Related Documents

- [Specification](./spec.md) - Full feature requirements
- [Research](./research.md) - Technology decisions
- [Data Model](./data-model.md) - Infrastructure entities
- [Contracts](./contracts/deployment-contracts.md) - Interface definitions
- [Plan](./plan.md) - Implementation plan
