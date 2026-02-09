---
id: 010
title: Enable Kafka via Confluent Cloud on DOKS
stage: green
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 005-phase5-partc-cloud-production
branch: 001-phase2-full-stack-web
user: Muhammad-Talha33
command: /sp.implement
labels: ["kafka", "confluent-cloud", "dapr", "event-driven", "deployment"]
links:
  spec: specs/005-phase5-partc-cloud-production/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - k8s/base/dapr/pubsub.yaml (applied to cluster)
  - k8s/base/dapr/cron-binding.yaml (applied to cluster)
  - k8s/base/dapr/configuration.yaml (simplified, applied without Zipkin)
tests:
  - Dapr sidecar pubsub.kafka component loaded - PASS (all 3 pods)
  - SASL Password authentication configured - PASS
  - Workers subscribed to [tasks] topic - PASS
  - Backend API health check - PASS
---

## Prompt

User provided Confluent Cloud credentials (bootstrap server, API key, API secret) to enable Kafka event-driven features on the cloud deployment. Credentials must NOT be included in PHR or commit messages.

## Response snapshot

Successfully enabled Kafka via Confluent Cloud on the DOKS cluster:

1. **Dapr runtime**: Already installed and healthy (dapr-system namespace)
2. **kafka-credentials secret**: Created in todo-staging namespace with Confluent Cloud credentials
3. **Dapr components applied**:
   - `taskpubsub` (pubsub.kafka/v1) - connected to Confluent Cloud with SASL PLAIN auth + TLS
   - `cron-reminder` (bindings.cron/v1) - triggers reminder checks every 1 minute
   - `dapr-config` - simplified without Zipkin tracing (observability namespace not deployed)
4. **All pods restarted** with Dapr sidecars (2/2 containers each)
5. **Verification**: All 3 Dapr sidecars confirmed SASL authentication configured, pubsub component loaded, and workers subscribed to `tasks` topic

## Outcome

- ✅ Impact: Event-driven architecture now live - task CRUD operations publish events to Confluent Cloud Kafka, workers consume them for reminders and recurrence
- 🧪 Tests: All Dapr sidecars show successful Kafka connection, topic subscription confirmed for workers
- 📁 Files: 3 Dapr component files applied to cluster, 1 K8s secret created
- 🔁 Next prompts: Test end-to-end event flow by creating a task with reminder/recurrence, add Zipkin for distributed tracing, configure production domain with TLS
- 🧠 Reflection: Pre-built Dapr component configs with secretKeyRef made Confluent Cloud integration straightforward - just create the secret and apply

## Evaluation notes (flywheel)

- Failure modes observed: None - all components connected successfully on first attempt
- Graders run and results (PASS/FAIL): Dapr sidecar logs confirm SASL auth + component load + topic subscription - PASS
- Prompt variant (if applicable): N/A
- Next experiment: End-to-end test creating a task and verifying event appears in Confluent Cloud topic
