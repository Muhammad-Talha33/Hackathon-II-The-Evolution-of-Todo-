---
id: 039
title: Phase V Part A Implementation Plan
stage: plan
date: 2026-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: 005-phase5-partA-intermediate-advanced-features
branch: 005-phase5-partA-intermediate-advanced-features
user: architect
command: /sp.plan
labels: ["phase5", "plan", "architecture", "event-driven", "recurring-tasks", "filter-sort", "search"]
links:
  spec: specs/005-phase5-partA-intermediate-advanced-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-phase5-partA-intermediate-advanced-features/plan.md
tests:
  - null
---

## Prompt

/sp.plan

Context:
- Use the feature specification from specs/005-phase5-partA-intermediate-advanced-features/spec.md
- Project is Phase V Part A: backend-level features only, no Kubernetes, Minikube, Dapr, Kafka, or cloud infra.
- Existing Docker structure (docker/frontend and docker/backend) must not be changed.
- Focus on implementation architecture, code dependencies, and how advanced & intermediate features will be implemented.

Goal:
- Generate a clear backend implementation plan for all Phase V Part A features.
- Include architectural decisions, module breakdown, API endpoints, event handling strategy, and data flow.
- Reference all 7 user stories, 32 functional requirements, and 6 domain events.
- Plan should prepare for future Dapr + Kafka integration without introducing infra yet.

Constraints:
- Strictly backend-focused; frontend changes only if needed.
- Do not introduce over-engineering.
- No deployment, Kubernetes, or cloud configuration included.

Output:
- A structured implementation plan, ready to be converted into tasks via /sp.tasks

## Response snapshot

Created comprehensive implementation plan at `specs/005-phase5-partA-intermediate-advanced-features/plan.md` covering:

- **6 architectural decisions** with options considered, rationale, and trade-offs:
  1. Tags as PostgreSQL ARRAY column (not join table)
  2. In-process EventBus using Python list + logging
  3. Recurrence logic as standalone service function
  4. Overdue as computed filter (not stored status)
  5. Priority sort using SQL CASE expression
  6. Database migration via ALTER TABLE (no Alembic)

- **8-layer module breakdown** with exact code references:
  1. Data Model (task.py: 2 enums, 7 columns)
  2. Events Module (3 new files: models.py, bus.py, __init__.py)
  3. Schemas (extend TaskCreate/TaskUpdate/TaskResponse)
  4. Services (recurrence.py + reminders.py)
  5. Router (filter/sort/search params + event emission + check-reminders endpoint)
  6. Models Init (export new enums)
  7. MCP Tools (add new field params to existing tools)
  8. Frontend Types (api.ts interface updates)

- **4 data flow diagrams**: Create task, Complete recurring task, Filter+Sort+Search, Check reminders
- **8-phase dependency chain** for implementation order
- **File change summary**: 5 files to create, 6 to modify, Docker/K8s/Helm untouched
- **3 risks** identified with mitigations
- **17-item validation checklist**

## Outcome

- Impact: Complete implementation architecture for Phase V Part A, ready for /sp.tasks conversion
- Tests: 17 validation checks defined covering all user stories and FRs
- Files: specs/005-phase5-partA-intermediate-advanced-features/plan.md (new)
- Next prompts: /sp.tasks to generate task breakdown from this plan
- Reflection: Plan maintains strict scope boundaries (no infra), uses existing patterns (sa_column for FK, FastAPI DI), and prepares EventBus seam for Phase V Part B migration.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (plan creation)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.tasks for task generation
