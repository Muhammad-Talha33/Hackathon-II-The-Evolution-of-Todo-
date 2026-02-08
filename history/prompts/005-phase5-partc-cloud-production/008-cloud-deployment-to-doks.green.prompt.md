---
id: 008
title: Deploy Application to DigitalOcean Kubernetes
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-5
feature: 005-phase5-partc-cloud-production
branch: 001-phase2-full-stack-web
user: Muhammad-Talha33
command: /sp.implement
labels: ["deployment", "kubernetes", "doks", "ghcr", "cloud"]
links:
  spec: specs/005-phase5-partc-cloud-production/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - k8s/overlays/staging/kustomization.yaml
  - k8s/overlays/staging/patches/resource-limits.yaml
  - k8s/overlays/staging/patches/imagepullsecret.yaml
  - k8s/overlays/staging/ingress.yaml
  - k8s/base/backend/deployment.yaml
tests:
  - curl http://139.59.194.7/api/health - PASS
  - curl http://139.59.194.7/ - PASS
  - kubectl get pods -n todo-staging - All Running
---

## Prompt

User requested to deploy the application to cloud production. Provided GitHub token and DigitalOcean credentials. Images were already built locally. Requested to skip Kafka for now due to missing Confluent Cloud credentials.

## Response snapshot

Successfully deployed the Todo application to DigitalOcean Kubernetes (DOKS):

1. **Logged into GHCR** using provided GitHub token
2. **Tagged and pushed 4 Docker images** to ghcr.io/muhammad-talha33/:
   - todo-backend:staging
   - todo-frontend:staging
   - todo-reminder-worker:staging
   - todo-recurrence-worker:staging
3. **Updated Kubernetes manifests**:
   - Fixed image names in kustomization.yaml
   - Reduced resource requests to fit single-node cluster
   - Added imagePullSecrets for GHCR authentication
   - Added SECRET_KEY env var for backend
4. **Created image pull secret** (ghcr-secret) for private registry access
5. **Disabled Kafka pubsub** component to allow app to run without event-driven features
6. **Created staging ingress** for external access
7. **Verified deployment**: All 4 pods running, API responding, frontend accessible

**Application URL**: http://139.59.194.7

## Outcome

- ✅ Impact: Full application deployed to cloud Kubernetes cluster and publicly accessible
- 🧪 Tests: Backend health check PASS, Frontend loading PASS, All pods Running
- 📁 Files: 5 files modified/created in k8s/overlays/staging/
- 🔁 Next prompts: Add Confluent Cloud Kafka credentials, set up TLS/SSL, configure production domain
- 🧠 Reflection: Resource constraints on single-node cluster required reducing CPU requests. Private GHCR images required imagePullSecrets. Dapr pubsub component fails without valid Kafka credentials.

## Evaluation notes (flywheel)

- Failure modes observed: Token scope mismatch (write:packages required), insufficient CPU on node, missing SECRET_KEY env var, placeholder Kafka credentials
- Graders run and results (PASS/FAIL): Manual verification PASS - all services accessible
- Prompt variant (if applicable): N/A
- Next experiment: Pre-validate token scopes before attempting image push
