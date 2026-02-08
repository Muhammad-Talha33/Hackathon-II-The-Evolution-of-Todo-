---
id: 006
title: Deployment Guide Walkthrough Request
stage: explainer
date: 2026-02-08
surface: agent
model: claude-opus-4-5-20251101
feature: 005-phase5-partc-cloud-production
branch: 001-phase2-full-stack-web
user: developer
command: /sp.implement
labels: ["deployment", "guide", "walkthrough", "kubernetes"]
links:
  spec: specs/005-phase5-partc-cloud-production/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - docs/deployment-guide.md
  - docs/production-readiness-checklist.md
tests:
  - N/A
---

## Prompt

but i wanted to deploy how i acheive that thing check docs folder there is deployment guide and tell me what next things i should to deploy

## Response snapshot

Provided step-by-step deployment walkthrough based on docs/deployment-guide.md:

1. **Install Required Tools** - kubectl, kustomize, helm, dapr, gh
2. **Create Kubernetes Cluster** - DigitalOcean DOKS or Google GKE options
3. **Setup External Services** - Confluent Cloud (Kafka), Neon (PostgreSQL)
4. **Build & Push Docker Images** - GHCR authentication and docker build/push
5. **Install Cluster Components** - Dapr and NGINX Ingress via Helm
6. **Create Secrets** - db-credentials, kafka-credentials, app-secrets
7. **Deploy Application** - kubectl apply -k k8s/overlays/staging
8. **Deploy Observability** - Prometheus, Grafana, Zipkin (optional)

Asked clarifying questions about user's current infrastructure setup to provide targeted next steps.

## Outcome

- ✅ Impact: Provided clear deployment roadmap from documentation
- 🧪 Tests: N/A (deployment guidance)
- 📁 Files: Read 2 documentation files
- 🔁 Next prompts: User provides infrastructure details for specific next steps
- 🧠 Reflection: User needs actual deployment, not just manifests

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): Deployment guidance request
- Next experiment (smallest change to try): Create interactive deployment script
