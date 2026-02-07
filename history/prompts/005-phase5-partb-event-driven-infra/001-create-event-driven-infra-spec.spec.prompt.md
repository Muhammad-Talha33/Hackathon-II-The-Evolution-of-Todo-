---
id: 001
title: Create Event-Driven Infrastructure Spec
stage: spec
date: 2026-02-06
surface: agent
model: claude-opus-4-5-20251101
feature: 005-phase5-partb-event-driven-infra
branch: 005-phase5-partb-event-driven-infra
user: default
command: /sp.specify
labels: ["dapr", "kafka", "redpanda", "event-driven", "infrastructure", "phase5"]
links:
  spec: specs/005-phase5-partb-event-driven-infra/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-phase5-partb-event-driven-infra/spec.md
  - specs/005-phase5-partb-event-driven-infra/checklists/requirements.md
  - history/prompts/005-phase5-partb-event-driven-infra/001-create-event-driven-infra-spec.spec.prompt.md
tests:
  - none (spec phase)
---

## Prompt

feature branch: 005-phase5-partB-event-driven-infra

Project Context:
Phase V Part A is fully completed.
All advanced + intermediate task features are implemented.
Domain events are already defined:
- TaskCreated
- TaskUpdated
- TaskCompleted
- TaskDeleted
- TaskReminderDue
- RecurringTaskGenerated

Frontend + backend are fully functional.
Auth, chatbot, MCP tools, and task flows work correctly.

We are now starting Phase V – Part B.

Goal of Phase V – Part B:
Convert the existing in-process event system into a real event-driven distributed architecture using Dapr + Kafka (Redpanda).

This phase is INFRASTRUCTURE + INTEGRATION only.
Business logic must NOT change.

STRICT SCOPE:

- Replace in-process EventBus with Dapr Pub/Sub
- Introduce Kafka (via Redpanda) as message broker
- Configure Dapr components:
  - pubsub
  - state store
  - secret store
- Implement reminder delivery via Dapr cron binding
- Enable service-to-service invocation using Dapr
- Introduce async processing for reminders and recurring tasks
- Add Dapr sidecars to backend services
- Add docker-compose for Redpanda + Dapr local dev

DO NOT:

- Change frontend UI or UX
- Modify task business logic
- Rewrite existing features
- Introduce cloud deployment
- Add Kubernetes or Minikube
- Over-engineer

Event Wiring:

All existing domain events must now:

- Publish through Dapr PubSub
- Be consumed by dedicated handler services/modules

Services to define (logical):

1. Task API (producer)
2. Reminder Worker (consumer)
3. Recurrence Worker (consumer)
4. Notification stub (logging only)

Reminder Flow:

- Dapr cron binding triggers reminder check
- ReminderWorker consumes TaskReminderDue
- Logs delivery (no email/SMS yet)

Recurring Flow:

- TaskCompleted emits RecurringTaskGenerated
- RecurrenceWorker creates next task

Architecture Rules:

- Event names remain unchanged
- Payload schemas unchanged
- Async boundaries explicit
- Dapr abstracts Kafka
- No direct service coupling

Deliverables:

- Dapr components (pubsub, bindings, state)
- Redpanda docker setup
- Updated backend to publish/subscribe via Dapr
- Worker services/modules
- Clear README section explaining local Dapr + Kafka startup
- Zero regression in existing features

Critical Requirement (NON-NEGOTIABLE):

The application must remain fully functional.

- Signup / signin must still work
- Tasks CRUD must behave exactly the same
- Chatbot + MCP tools must continue working
- Frontend/backend communication must not break
- No performance regressions
- All existing flows must remain intact

Design Philosophy:

Phase A built the brain.
Phase B builds the nervous system.

Event-driven.
Loosely coupled.
Production-minded.

Code must be clean, readable, and ready for cloud later.

## Response snapshot

Created comprehensive specification for Phase V Part B - Event-Driven Infrastructure:

**Branch**: `005-phase5-partb-event-driven-infra`

**Key Deliverables Specified**:
1. Refactored EventBus to publish via Dapr HTTP Pub/Sub API
2. Dapr component configurations (pubsub, statestore, secrets, cron-reminder)
3. Redpanda (Kafka-compatible) as message broker
4. Reminder Worker service (subscribes to TaskReminderDue, logs delivery)
5. Recurrence Worker service (subscribes to RecurringTaskGenerated, creates next task)
6. `docker-compose.dapr.yml` for full local development stack
7. README documentation for Dapr + Kafka local startup

**User Stories (5)**: Transparent Event Publishing (P0), Reminder Worker (P1), Recurrence Worker (P1), Local Dev Environment (P0), Zero Regression (P0)

**Functional Requirements (26)**: Covering Dapr integration, component configuration, worker services, backend updates, Docker Compose infrastructure

**Success Criteria (12)**: All measurable, including event delivery times, container health, test suite pass rate

**Scope**: Infrastructure-only. No business logic changes. No cloud deployment. No K8s.

**Architecture**: Event flow from Backend -> Dapr Sidecar -> Redpanda -> Worker Sidecars -> Workers

## Outcome

- ✅ Impact: Specification created for event-driven infrastructure phase
- 🧪 Tests: None (spec phase)
- 📁 Files: 2 created (spec.md, requirements.md checklist)
- 🔁 Next prompts: /sp.plan to create implementation plan, /sp.tasks to generate tasks
- 🧠 Reflection: Comprehensive spec built on Phase V Part A's domain event foundation. Clear separation between infrastructure (this phase) and business logic (unchanged).

## Evaluation notes (flywheel)

- Failure modes observed: None - user requirements were comprehensive
- Graders run and results (PASS/FAIL): Checklist validation PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
