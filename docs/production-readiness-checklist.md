# Production Readiness Checklist

This checklist ensures the Todo application is properly prepared for production deployment.

## Pre-Deployment Checks

### Infrastructure
- [ ] Kubernetes cluster is running and accessible
- [ ] kubectl configured with correct context
- [ ] Dapr installed on cluster (`dapr status -k` shows healthy)
- [ ] NGINX Ingress controller installed
- [ ] Container registry (GHCR) credentials configured

### Secrets
- [ ] `db-credentials` secret created with valid DATABASE_URL
- [ ] `kafka-credentials` secret created with Confluent Cloud credentials
  - [ ] brokers endpoint verified
  - [ ] API key and secret validated
- [ ] `app-secrets` secret created with JWT_SECRET
- [ ] All secrets verified in target namespace

### Images
- [ ] Backend image built and pushed to GHCR
- [ ] Frontend image built and pushed to GHCR
- [ ] Reminder worker image built and pushed to GHCR
- [ ] Recurrence worker image built and pushed to GHCR
- [ ] All images tagged with release version

### Configuration
- [ ] Kustomize overlay builds successfully (`kustomize build k8s/overlays/production`)
- [ ] Resource limits appropriate for workload
- [ ] Replica counts configured for HA
- [ ] Ingress host configured correctly
- [ ] TLS certificate configured (if applicable)

---

## Security Checks

### Authentication & Authorization
- [ ] JWT_SECRET is strong (min 256 bits)
- [ ] JWT expiration configured appropriately
- [ ] API endpoints require authentication where needed
- [ ] CORS configured for production domains only

### Network Security
- [ ] Services use ClusterIP (not exposed externally)
- [ ] Ingress terminates TLS
- [ ] Network policies in place (if required)
- [ ] mTLS enabled for Dapr sidecars

### Secrets Management
- [ ] No secrets in source control
- [ ] Secrets encrypted at rest in Kubernetes
- [ ] Secret rotation procedure documented
- [ ] Access to secrets limited to required pods

### Container Security
- [ ] Images scanned for vulnerabilities
- [ ] Non-root user in containers
- [ ] Read-only root filesystem (if applicable)
- [ ] Resource limits prevent DoS

---

## Reliability Checks

### High Availability
- [ ] Backend has 3+ replicas
- [ ] Frontend has 2+ replicas
- [ ] Workers have 2+ replicas
- [ ] Pod anti-affinity configured (if multi-node)

### Health Checks
- [ ] Liveness probes configured
- [ ] Readiness probes configured
- [ ] Startup probes configured (for slow-starting containers)
- [ ] Health endpoints respond correctly

### Resilience
- [ ] Rolling update strategy configured
- [ ] Pod disruption budgets in place
- [ ] Graceful shutdown handling
- [ ] Circuit breakers configured in Dapr

### Database
- [ ] Connection pooling configured
- [ ] Database can handle expected load
- [ ] Backups scheduled and tested
- [ ] Connection string uses SSL

### Message Queue
- [ ] Kafka topics created with proper partitioning
- [ ] Consumer groups configured
- [ ] Dead letter topics configured
- [ ] Retention policy appropriate

---

## Observability Checks

### Logging
- [ ] Structured logging (JSON) enabled
- [ ] Log levels appropriate for production
- [ ] Log aggregation configured
- [ ] Sensitive data not logged

### Metrics
- [ ] Prometheus scraping configured
- [ ] Key metrics identified:
  - [ ] Request rate
  - [ ] Error rate
  - [ ] Latency percentiles
  - [ ] Queue depth
- [ ] Grafana dashboards imported

### Tracing
- [ ] Zipkin/Jaeger deployed
- [ ] Dapr tracing enabled
- [ ] Trace sampling rate configured
- [ ] Critical paths traced

### Alerting
- [ ] Alert rules defined for:
  - [ ] Pod restarts
  - [ ] High error rate (>1%)
  - [ ] High latency (p99 > 1s)
  - [ ] Low availability
- [ ] Alert notification channels configured
- [ ] On-call rotation established

---

## Deployment Checks

### Process
- [ ] Deployment pipeline tested in staging
- [ ] Rollback procedure documented and tested
- [ ] Deployment window scheduled (if applicable)
- [ ] Stakeholders notified

### Validation
- [ ] Smoke tests pass after deployment
- [ ] Integration tests pass
- [ ] Performance baseline established
- [ ] No error spikes in logs

---

## Post-Deployment Verification

### Immediate (0-5 minutes)
- [ ] All pods in Running state
- [ ] No crash loops (CrashLoopBackOff)
- [ ] Health endpoints responding
- [ ] Ingress routing correctly

### Short-term (5-30 minutes)
- [ ] API requests completing successfully
- [ ] Frontend loading correctly
- [ ] Tasks can be created/updated/deleted
- [ ] Reminders being processed
- [ ] Recurrence patterns executing

### Monitoring
- [ ] Metrics appearing in Grafana
- [ ] Traces visible in Zipkin
- [ ] No error spikes
- [ ] Resource utilization within limits

---

## Rollback Procedures

### Automatic Rollback Triggers
- Deployment fails to reach Ready state in 10 minutes
- Error rate exceeds 5% within first 15 minutes
- Health checks fail for >2 pods

### Manual Rollback Steps

```bash
# 1. Check current state
kubectl get pods -n todo-production
kubectl describe deployment/backend -n todo-production

# 2. View rollout history
kubectl rollout history deployment/backend -n todo-production

# 3. Rollback to previous version
kubectl rollout undo deployment/backend -n todo-production
kubectl rollout undo deployment/frontend -n todo-production
kubectl rollout undo deployment/reminder-worker -n todo-production
kubectl rollout undo deployment/recurrence-worker -n todo-production

# 4. Wait for rollback
kubectl rollout status deployment/backend -n todo-production

# 5. Verify rollback
kubectl get pods -n todo-production
```

### Post-Rollback Actions
1. Investigate root cause of failure
2. Document incident in post-mortem
3. Fix issues in staging before re-attempting deployment
4. Notify stakeholders of rollback

---

## Emergency Contacts

| Role | Contact |
|------|---------|
| On-call Engineer | TBD |
| Platform Team | TBD |
| Database Admin | TBD |
| Security Team | TBD |

---

## Sign-off

| Check | Completed By | Date |
|-------|--------------|------|
| Pre-deployment | | |
| Security | | |
| Reliability | | |
| Observability | | |
| Deployment | | |
| Post-deployment | | |

---

**Last Updated**: Phase 5C Implementation
**Version**: 1.0
