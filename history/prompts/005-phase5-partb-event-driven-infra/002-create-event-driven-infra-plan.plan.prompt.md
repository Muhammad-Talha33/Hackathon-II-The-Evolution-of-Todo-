---
id: 002
title: Create Event-Driven Infrastructure Plan
stage: plan
date: 2026-02-06
surface: agent
model: claude-opus-4-5-20251101
feature: 005-phase5-partb-event-driven-infra
branch: 005-phase5-partb-event-driven-infra
user: default
command: /sp.plan
labels: ["dapr", "kafka", "redpanda", "event-driven", "infrastructure", "planning"]
links:
  spec: specs/005-phase5-partb-event-driven-infra/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-phase5-partb-event-driven-infra/plan.md
  - specs/005-phase5-partb-event-driven-infra/research.md
  - specs/005-phase5-partb-event-driven-infra/data-model.md
  - specs/005-phase5-partb-event-driven-infra/quickstart.md
  - specs/005-phase5-partb-event-driven-infra/contracts/dapr-pubsub.yaml
  - specs/005-phase5-partb-event-driven-infra/contracts/worker-subscription.yaml
tests:
  - none (plan phase)
---

## Prompt

Feature specification from specs/005-phase5-partb-event-driven-infra/spec.md

## Response snapshot

Created comprehensive implementation plan for Phase V Part B - Event-Driven Infrastructure:

**Research (research.md)**:
- Dapr Pub/Sub with Redpanda (Kafka-compatible) - decision and rationale
- Dapr Sidecar in Docker Compose pattern
- Dapr Cron Binding for reminders (every 1 minute)
- Worker Service Architecture (2 separate FastAPI apps)
- EventBus Refactoring Strategy (httpx async HTTP to Dapr)
- Database Access from Workers (direct connection)
- Idempotency Strategy (DB checks for duplicates)
- Docker Compose file strategy (new docker-compose.dapr.yml)
- Secret Management (Dapr local file store)
- Redpanda Console on port 8080

**Data Model (data-model.md)**:
- Event schemas (unchanged from Phase V Part A)
- CloudEvents envelope format
- Dapr component schemas (pubsub, statestore, secrets, cron)
- Kafka topic structure (single `tasks` topic)
- Dapr subscription schema for workers

**Contracts**:
- `dapr-pubsub.yaml` - OpenAPI 3.0 spec for Dapr publication API
- `worker-subscription.yaml` - OpenAPI 3.0 spec for worker event handlers

**Implementation Strategy (6 phases)**:
1. Infrastructure Foundation (Dapr components, docker-compose.dapr.yml)
2. EventBus Refactoring (httpx, graceful degradation)
3. Reminder Worker (subscription, logging)
4. Recurrence Worker (subscription, DB task creation)
5. Cron Binding (reminder-cron component)
6. Integration Testing (zero regression verification)

**Quickstart Guide (quickstart.md)**:
- Prerequisites and setup instructions
- Service verification commands
- Event flow testing procedures
- Troubleshooting guide

**Constitution Check**: ✅ PASSED - No violations

## Outcome

- ✅ Impact: Complete implementation plan with all Phase 0 and Phase 1 artifacts
- 🧪 Tests: None (plan phase)
- 📁 Files: 6 created (plan.md, research.md, data-model.md, quickstart.md, 2 contracts)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Comprehensive research resolved all technical unknowns. Architecture follows existing backend patterns (FastAPI, SQLModel). Workers are minimal and focused.

## Evaluation notes (flywheel)

- Failure modes observed: None - existing codebase provided clear patterns to follow
- Graders run and results (PASS/FAIL): Constitution check PASS (pre and post design)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
