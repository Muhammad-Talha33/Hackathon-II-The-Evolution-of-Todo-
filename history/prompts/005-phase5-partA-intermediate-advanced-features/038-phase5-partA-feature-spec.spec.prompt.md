---
id: 038
title: Phase V Part A Feature Specification
stage: spec
date: 2026-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: 005-phase5-partA-intermediate-advanced-features
branch: 005-phase5-partA-intermediate-advanced-features
user: architect
command: /sp.specify
labels: ["phase5", "spec", "advanced-features", "event-driven", "recurring-tasks", "due-dates", "reminders", "priority", "tags", "search", "filter-sort"]
links:
  spec: specs/005-phase5-partA-intermediate-advanced-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-phase5-partA-intermediate-advanced-features/spec.md
tests:
  - null
---

## Prompt

/sp.specify

feature branch: 005-phase5-partA-intermediate-advanced-features

Project Context:
This project has completed Phase IV successfully.
Docker structure is finalized using separate docker/frontend and docker/backend directories.
No Kubernetes, Minikube, Dapr, or Kafka is implemented yet.
We are now starting Phase V – Part A only.

Goal of Phase V – Part A:
Implement all advanced and intermediate task management features
AND define a clean event-driven contract (events only, no Kafka/Dapr wiring yet).

Scope (STRICT):
- Do NOT add Minikube, Kubernetes, Dapr, Kafka, or any cloud configuration.
- Do NOT change existing folder structure.
- Do NOT introduce over-engineering.
- Focus only on application-level features and event definitions.

Features to Implement:

Advanced Features:
1. Recurring Tasks
   - Support daily, weekly, and monthly recurrence.
   - When a recurring task is completed, generate the next task instance logically.
   - Keep recurrence logic simple and explicit.

2. Due Dates
   - Each task can have an optional due_at timestamp.
   - System must identify overdue tasks.

3. Reminders
   - Each task can have an optional remind_at timestamp.
   - When reminder time is reached, a reminder event should be emitted.

Intermediate Features:
4. Priority
   - Support priority levels (low, medium, high).

5. Tags
   - Allow multiple tags per task.
   - Support filtering tasks by tags.

6. Search
   - Enable searching tasks by title and description.

7. Filter & Sort
   - Filter by status (completed / pending / overdue).
   - Sort by due date, priority, or creation time.

Event-Driven Contract (IMPORTANT):
- The Chat/Task API must NOT directly call other services.
- The API must ONLY emit events.

Define these domain events clearly (no infrastructure code):
1. TaskCreated
2. TaskUpdated
3. TaskCompleted
4. TaskDeleted
5. TaskReminderDue
6. RecurringTaskGenerated

For each event, specify:
- Event name
- Trigger condition
- Payload schema (fields only)
- Which future service would consume it (conceptually)

Architecture Rules:
- Events are conceptual only at this stage.
- No Kafka topics, no Dapr components yet.
- Just define clean event boundaries and responsibilities.

Deliverables Expected:
- Updated backend logic implementing all features.
- Clear event definitions documented in code comments or a spec file.
- No deployment or infra changes.

Design Philosophy:
- Business logic first.
- Event-driven mindset without infra coupling.
- Code must be easy to migrate to Dapr + Kafka in Phase V Part B.

## Response snapshot

Created comprehensive feature specification at `specs/005-phase5-partA-intermediate-advanced-features/spec.md` covering:

- 7 user stories with detailed acceptance scenarios (Recurring Tasks P0, Due Dates P0, Reminders P1, Priority P0, Tags P0, Search P1, Filter & Sort P0)
- 32 functional requirements (FR-001 through FR-032)
- 6 domain event definitions with trigger conditions, payload schemas, and future consumer mapping
- Updated Task model with 7 new fields (due_at, remind_at, reminder_sent, priority, tags, recurrence_pattern, parent_task_id)
- 2 new enums (Priority, RecurrencePattern)
- API contract changes for GET/POST/PUT endpoints with new query params and body fields
- New POST /tasks/check-reminders endpoint
- Edge cases for month-end recurrence, null due dates, tag deduplication
- Strict scope boundaries: no Kafka, no Dapr, no K8s, no frontend UI changes
- Event architecture: in-process EventBus with emit/log pattern, ready for Dapr migration
- File impact summary: 3 new files, 4 modified files

## Outcome

- Impact: Comprehensive spec defines all Phase V Part A features and event contracts
- Tests: Acceptance scenarios defined for all 7 user stories with specific given/when/then conditions
- Files: specs/005-phase5-partA-intermediate-advanced-features/spec.md (new)
- Next prompts: /sp.plan to create implementation architecture, /sp.tasks to generate task breakdown
- Reflection: Spec balances feature completeness with strict scope boundaries. Event-driven contract is cleanly separated from infrastructure concerns, enabling smooth Phase V Part B migration.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (spec creation)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.plan for architecture design
