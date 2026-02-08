# Tasks: Phase V Part B - Event-Driven Infrastructure

**Input**: Design documents from `/specs/005-phase5-partb-event-driven-infra/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Manual smoke tests only (no new automated tests requested). Zero regression on existing test suite is required.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## User Story Mapping

| User Story | Priority | Title |
|------------|----------|-------|
| US1 | P0 | Transparent Event Publishing |
| US2 | P1 | Reminder Worker Consumes Events |
| US3 | P1 | Recurrence Worker Creates Next Task |
| US4 | P0 | Local Development Environment |
| US5 | P0 | Zero Regression in Existing Features |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and base configuration files

- [x] T001 Create dapr/components/ directory structure
- [x] T002 [P] Create services/reminder-worker/ directory structure
- [x] T003 [P] Create services/recurrence-worker/ directory structure
- [x] T004 Add httpx>=0.27.0 to backend/requirements.txt

---

## Phase 2: Foundational - Dapr Components (Blocking Prerequisites)

**Purpose**: Core Dapr infrastructure that MUST be complete before ANY worker can function

**⚠️ CRITICAL**: No worker implementation can begin until Dapr components are configured

- [x] T005 [P] Create pub/sub component in dapr/components/pubsub.yaml per data-model.md spec
- [x] T006 [P] Create state store component in dapr/components/statestore.yaml per data-model.md spec
- [x] T007 [P] Create secret store component in dapr/components/secrets.yaml per data-model.md spec
- [x] T008 Create cron binding component in dapr/components/cron-reminder.yaml per data-model.md spec
- [x] T009 Create local secrets file at dapr/secrets/secrets.json with empty object

**Checkpoint**: Dapr components ready - Docker Compose and worker implementation can begin

---

## Phase 3: User Story 4 - Local Development Environment (Priority: P0) 🎯 MVP

**Goal**: Docker Compose setup with Redpanda + Dapr sidecars for local event-driven development

**Independent Test**: Run `docker-compose -f docker-compose.dapr.yml up`. All containers start healthy. Access Redpanda Console at localhost:8080.

### Implementation for User Story 4

- [x] T010 [US4] Create base docker-compose.dapr.yml with Redpanda service (ports 9092, 8080)
- [x] T011 [US4] Add Redis service to docker-compose.dapr.yml for Dapr state store
- [x] T012 [US4] Add backend service to docker-compose.dapr.yml with Dapr sidecar using network_mode
- [x] T013 [US4] Add frontend service to docker-compose.dapr.yml (reuse existing config)
- [x] T014 [US4] Add reminder-worker service placeholder to docker-compose.dapr.yml with Dapr sidecar
- [x] T015 [US4] Add recurrence-worker service placeholder to docker-compose.dapr.yml with Dapr sidecar
- [x] T016 [US4] Configure volume mounts for dapr/components/ in all Dapr sidecars
- [x] T017 [US4] Add depends_on with health checks for service startup order
- [x] T018 [US4] Test docker-compose.dapr.yml starts Redpanda and Redis (workers will fail - expected)

**Checkpoint**: Infrastructure running. Redpanda Console accessible. Ready for EventBus and worker implementation.

---

## Phase 4: User Story 1 - Transparent Event Publishing (Priority: P0) 🎯 MVP

**Goal**: EventBus publishes events via Dapr Pub/Sub to Kafka. API behavior unchanged.

**Independent Test**: Create a task via POST /tasks. Verify TaskCreated event appears in Redpanda Console. API response identical to Phase V Part A.

### Implementation for User Story 1

- [x] T019 [US1] Create backend/src/events/dapr_client.py with async httpx client for Dapr pub/sub
- [x] T020 [US1] Add DAPR_HTTP_PORT and PUBSUB_NAME environment variables to backend/src/config.py
- [x] T021 [US1] Refactor EventBus in backend/src/events/bus.py to use DaprClient for async emit
- [x] T022 [US1] Add graceful degradation in bus.py - log and continue if Dapr unavailable
- [x] T023 [US1] Update get_event_bus() dependency to support async initialization
- [x] T024 [US1] Verify all six event types serialize correctly to JSON via asdict()
- [x] T025 [US1] Test event publication: create task, verify event in Redpanda Console
- [x] T026 [US1] Test graceful degradation: stop Dapr sidecar, verify API still works

**Checkpoint**: Events flow from backend to Redpanda. Graceful degradation verified. Ready for workers.

---

## Phase 5: User Story 2 - Reminder Worker Consumes Events (Priority: P1)

**Goal**: Reminder Worker subscribes to TaskReminderDue events and logs delivery

**Independent Test**: Create task with remind_at in past. Trigger POST /tasks/check-reminders. Verify worker logs "Reminder delivered for task..."

### Implementation for User Story 2

- [x] T027 [P] [US2] Create services/reminder-worker/requirements.txt with FastAPI, uvicorn, pydantic, httpx
- [x] T028 [P] [US2] Create services/reminder-worker/Dockerfile based on backend Dockerfile pattern
- [x] T029 [US2] Create services/reminder-worker/main.py with FastAPI app skeleton
- [x] T030 [US2] Implement GET /dapr/subscribe endpoint returning topic subscription per contracts/worker-subscription.yaml
- [x] T031 [US2] Implement POST /events/task-reminder-due handler with event parsing
- [x] T032 [US2] Add event_type filtering - only process TaskReminderDue, ignore others
- [x] T033 [US2] Implement logging: "[ReminderWorker] Delivered reminder for task {task_id}: {title}"
- [x] T034 [US2] Return Dapr response status (SUCCESS/DROP) per contracts/worker-subscription.yaml
- [x] T035 [US2] Add health check endpoint GET /health
- [x] T036 [US2] Add error handling - log and return DROP for malformed events
- [x] T037 [US2] Update docker-compose.dapr.yml reminder-worker service with correct Dockerfile path
- [x] T038 [US2] Test end-to-end: create task with past remind_at, call check-reminders, verify worker log

**Checkpoint**: Reminder events flow from API → Redpanda → Reminder Worker. Logging stub works.

---

## Phase 6: User Story 3 - Recurrence Worker Creates Next Task (Priority: P1)

**Goal**: Recurrence Worker subscribes to RecurringTaskGenerated events and creates next task in DB

**Independent Test**: Complete a recurring task. Verify new task appears in database with correct due_at and parent_task_id.

### Implementation for User Story 3

- [x] T039 [P] [US3] Create services/recurrence-worker/requirements.txt with FastAPI, uvicorn, pydantic, sqlmodel, asyncpg, httpx
- [x] T040 [P] [US3] Create services/recurrence-worker/Dockerfile based on backend Dockerfile pattern
- [x] T041 [US3] Create services/recurrence-worker/main.py with FastAPI app skeleton
- [x] T042 [US3] Add DATABASE_URL environment variable configuration
- [x] T043 [US3] Create services/recurrence-worker/database.py with async SQLAlchemy session (copy pattern from backend)
- [x] T044 [US3] Create services/recurrence-worker/models.py with Task model (copy from backend for DB access)
- [x] T045 [US3] Implement GET /dapr/subscribe endpoint returning topic subscription
- [x] T046 [US3] Implement POST /events/recurring-task-generated handler with event parsing
- [x] T047 [US3] Add event_type filtering - only process RecurringTaskGenerated, ignore others
- [x] T048 [US3] Implement idempotency check: query for existing task with same parent_task_id and due_at
- [x] T049 [US3] Implement task creation in database from event payload
- [x] T050 [US3] Implement parent task lookup to copy description, priority, tags, recurrence_pattern
- [x] T051 [US3] Return Dapr response status (SUCCESS/RETRY/DROP) per contracts/worker-subscription.yaml
- [x] T052 [US3] Add health check endpoint GET /health
- [x] T053 [US3] Add error handling - log and return RETRY for DB errors, DROP for invalid events
- [x] T054 [US3] Update docker-compose.dapr.yml recurrence-worker service with correct Dockerfile path and DATABASE_URL
- [x] T055 [US3] Test end-to-end: complete recurring task, verify new task in DB with correct fields

**Checkpoint**: Recurring task events flow from API → Redpanda → Recurrence Worker → PostgreSQL. Next tasks created.

---

## Phase 7: Cron Binding Integration

**Purpose**: Wire Dapr cron binding to trigger reminder checks automatically

- [x] T056 Add /reminder-cron endpoint to backend/src/routers/tasks.py that calls check_and_emit_reminders
- [x] T057 Configure backend Dapr sidecar to bind reminder-cron to /reminder-cron endpoint
- [x] T058 Test cron trigger: wait 1 minute, verify check-reminders executes automatically

---

## Phase 8: User Story 5 - Zero Regression (Priority: P0)

**Goal**: All existing features work identically to Phase V Part A

**Independent Test**: Run existing test suite (100% pass). Manual smoke test auth, CRUD, chatbot, MCP tools.

### Verification for User Story 5

- [x] T059 [US5] Run pytest on backend/tests/ - verify 100% tests pass
- [x] T060 [US5] Manual test: signup new account, verify redirect to tasks page
- [x] T061 [US5] Manual test: signin existing account, verify task list loads
- [x] T062 [US5] Manual test: create task with all fields (due_at, remind_at, tags, priority, recurrence)
- [x] T063 [US5] Manual test: update task fields, verify changes persist
- [x] T064 [US5] Manual test: complete task, verify status toggle
- [x] T065 [US5] Manual test: complete recurring task, verify next instance created
- [x] T066 [US5] Manual test: delete task, verify removal from list
- [x] T067 [US5] Manual test: filter by status (incomplete, complete, overdue)
- [x] T068 [US5] Manual test: filter by tag and priority
- [x] T069 [US5] Manual test: search by title/description
- [x] T070 [US5] Manual test: chatbot - ask to create a task
- [x] T071 [US5] Manual test: chatbot - ask to list tasks
- [x] T072 [US5] Manual test: verify API response times under 500ms
- [x] T073 [US5] Verify graceful degradation: stop Dapr, confirm API still works

**Checkpoint**: All existing features verified. Zero regression confirmed.

---

## Phase 9: Polish & Documentation

**Purpose**: Documentation updates and final cleanup

- [x] T074 [P] Add "Dapr + Kafka Local Development" section to README.md
- [x] T075 [P] Document docker-compose.dapr.yml usage in README.md
- [x] T076 [P] Document troubleshooting steps (Redpanda, Dapr sidecars, workers) in README.md
- [x] T077 Run full docker-compose.dapr.yml up and validate per quickstart.md
- [x] T078 Verify Redpanda Console shows all event types with correct payloads
- [x] T079 Final code review: verify no hardcoded secrets, proper logging

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational - Dapr Components) ──────────────────┐
    │                                                       │
    ▼                                                       │
Phase 3 (US4: Docker Compose) ◄────────────────────────────┘
    │
    ▼
Phase 4 (US1: EventBus Refactor) ──────────────────────────┐
    │                                                       │
    ├───────────────────┬───────────────────┐              │
    ▼                   ▼                   ▼              │
Phase 5 (US2)      Phase 6 (US3)      Phase 7 (Cron)      │
Reminder Worker    Recurrence Worker   Binding             │
    │                   │                   │              │
    └───────────────────┴───────────────────┘              │
                        │                                   │
                        ▼                                   │
                Phase 8 (US5: Zero Regression) ◄───────────┘
                        │
                        ▼
                Phase 9 (Polish)
```

### User Story Dependencies

| User Story | Depends On | Can Run In Parallel With |
|------------|------------|--------------------------|
| US4 (Docker Compose) | Phase 2 (Dapr Components) | - |
| US1 (EventBus) | US4 (needs Docker env running) | - |
| US2 (Reminder Worker) | US1, US4 | US3 |
| US3 (Recurrence Worker) | US1, US4 | US2 |
| US5 (Zero Regression) | US1, US2, US3, US4 | - |

### Within Each User Story

- Infrastructure/config before implementation
- Models before services
- Endpoints before handlers
- Core logic before error handling
- Implementation before testing

### Parallel Opportunities

**Phase 2 (all parallel)**:
```
T005 pubsub.yaml
T006 statestore.yaml  ─── Can run simultaneously
T007 secrets.yaml
```

**Phase 5 + Phase 6 (parallel after Phase 4)**:
```
US2: Reminder Worker ────┬─── Can implement simultaneously
US3: Recurrence Worker ──┘    (different services)
```

**Phase 9 (documentation parallel)**:
```
T074 README section 1
T075 README section 2  ─── Can write simultaneously
T076 README section 3
```

---

## Parallel Example: Worker Services

After Phase 4 (EventBus) is complete, workers can be built in parallel:

```bash
# Developer A: Reminder Worker (Phase 5)
T027 → T028 → T029 → T030-T038

# Developer B: Recurrence Worker (Phase 6)
T039 → T040 → T041 → T042-T055

# Both run simultaneously on different services
```

---

## Implementation Strategy

### MVP First (US4 + US1)

1. Complete Phase 1: Setup directories
2. Complete Phase 2: Dapr components
3. Complete Phase 3: Docker Compose (US4)
4. Complete Phase 4: EventBus refactor (US1)
5. **STOP and VALIDATE**: Events appear in Redpanda Console
6. This is the minimum viable event-driven infrastructure

### Incremental Delivery

1. **MVP**: Setup + Components + Docker + EventBus = Events flowing
2. **+Reminder**: Add US2 = Reminder events consumed
3. **+Recurrence**: Add US3 = Recurring tasks async
4. **+Cron**: Add Phase 7 = Automatic reminder scheduling
5. **+Validation**: US5 = Full regression test
6. **+Docs**: Phase 9 = Production-ready

### Critical Path

```
T001-T004 → T005-T009 → T010-T018 → T019-T026 → T059-T073 → T074-T079
(Setup)     (Components)  (Docker)    (EventBus)  (Regression) (Docs)
```

---

## Task Count Summary

| Phase | Task Range | Count |
|-------|------------|-------|
| Phase 1: Setup | T001-T004 | 4 |
| Phase 2: Foundational | T005-T009 | 5 |
| Phase 3: US4 Docker | T010-T018 | 9 |
| Phase 4: US1 EventBus | T019-T026 | 8 |
| Phase 5: US2 Reminder | T027-T038 | 12 |
| Phase 6: US3 Recurrence | T039-T055 | 17 |
| Phase 7: Cron | T056-T058 | 3 |
| Phase 8: US5 Regression | T059-T073 | 15 |
| Phase 9: Polish | T074-T079 | 6 |
| **TOTAL** | | **79** |

### Tasks Per User Story

| User Story | Tasks | Parallel Tasks |
|------------|-------|----------------|
| US1 (EventBus) | 8 | 0 |
| US2 (Reminder) | 12 | 2 |
| US3 (Recurrence) | 17 | 2 |
| US4 (Docker) | 9 | 0 |
| US5 (Regression) | 15 | 0 |

---

## Notes

- [P] tasks = different files, no dependencies
- [USx] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No automated tests requested - manual smoke tests for regression
- Workers can be developed in parallel by separate developers
- Existing backend tests must pass without modification (zero code changes to tests)
