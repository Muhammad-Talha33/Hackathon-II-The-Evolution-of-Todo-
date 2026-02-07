# Feature Specification: Phase V Part B - Event-Driven Infrastructure with Dapr + Kafka

**Feature Branch**: `005-phase5-partb-event-driven-infra`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Convert the existing in-process event system into a real event-driven distributed architecture using Dapr + Kafka (Redpanda). Infrastructure + integration only. Business logic must NOT change."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Transparent Event Publishing (Priority: P0)

As a developer, I want the existing in-process EventBus to be replaced with Dapr Pub/Sub so that domain events are published to Kafka without changing any business logic or API behavior.

**Why this priority**: This is the foundational change that enables all other event-driven features. Without this, no other Phase B functionality can work. It must be invisible to end users.

**Independent Test**: Create a task via the API. Verify the `TaskCreated` event is published to the Kafka topic. Check that the API response and behavior are identical to Phase V Part A.

**Acceptance Scenarios**:

1. **Given** I create a task via `POST /tasks`, **When** the task is persisted, **Then** a `TaskCreated` event is published to the `tasks` Dapr pub/sub topic AND the API response is unchanged from Phase V Part A.
2. **Given** I update a task via `PUT /tasks/{id}`, **When** the update succeeds, **Then** a `TaskUpdated` event is published to Kafka AND the API behavior is identical to before.
3. **Given** I complete a task via `POST /tasks/{id}/toggle`, **When** the task becomes complete, **Then** a `TaskCompleted` event is published AND (if recurring) a `RecurringTaskGenerated` event follows.
4. **Given** I delete a task via `DELETE /tasks/{id}`, **When** the deletion succeeds, **Then** a `TaskDeleted` event is published.
5. **Given** the Kafka broker is temporarily unavailable, **When** I perform a task operation, **Then** the operation succeeds (graceful degradation) and the failure is logged.

---

### User Story 2 - Reminder Worker Consumes Events (Priority: P1)

As the system, I want a Reminder Worker service to consume `TaskReminderDue` events and log delivery so that reminder processing is decoupled from the API.

**Why this priority**: This demonstrates the async worker pattern and proves that events flow through Kafka to consumers. Logging-only delivery is a stub for future notification integration.

**Independent Test**: Create a task with `remind_at` in the past. Trigger the reminder cron binding. Verify the Reminder Worker logs the reminder delivery.

**Acceptance Scenarios**:

1. **Given** a task exists with `remind_at <= now` and `reminder_sent = false`, **When** the Dapr cron binding triggers, **Then** a `TaskReminderDue` event is published.
2. **Given** the Reminder Worker is running, **When** it receives a `TaskReminderDue` event, **Then** it logs: "Reminder delivered for task {task_id}: {title}".
3. **Given** the Reminder Worker receives a malformed event, **When** processing occurs, **Then** the error is logged and the worker continues (no crash).
4. **Given** the task has `reminder_sent = true`, **When** the cron binding triggers, **Then** no duplicate event is published.

---

### User Story 3 - Recurrence Worker Creates Next Task (Priority: P1)

As the system, I want a Recurrence Worker to consume `RecurringTaskGenerated` events and create the next task instance so that recurring task generation is async and decoupled.

**Why this priority**: This moves recurring task logic to an async worker, making the task completion flow faster and more resilient.

**Independent Test**: Complete a recurring task. Verify the Recurrence Worker receives the event and creates the next task instance in the database.

**Acceptance Scenarios**:

1. **Given** a task has `recurrence_pattern = "daily"` and `due_at = "2026-02-06"`, **When** the task is completed, **Then** a `RecurringTaskGenerated` event is published with `next_due_at = "2026-02-07"`.
2. **Given** the Recurrence Worker receives a `RecurringTaskGenerated` event, **When** processing completes, **Then** a new task exists in the database with the correct `due_at`, `parent_task_id`, and copied fields.
3. **Given** the Recurrence Worker fails to create the task (e.g., database error), **When** the failure occurs, **Then** the error is logged and the event can be retried (dead-letter behavior configured).
4. **Given** the Task API publishes the event, **When** the Recurrence Worker processes it, **Then** the API response time for task completion is unaffected (async processing).

---

### User Story 4 - Local Development Environment (Priority: P0)

As a developer, I want a docker-compose setup with Redpanda + Dapr sidecars so that I can run the full event-driven stack locally without cloud dependencies.

**Why this priority**: Without a working local dev environment, no development or testing can proceed. This is a hard prerequisite.

**Independent Test**: Run `docker-compose up`. Verify all services start. Create a task and observe events flowing through Redpanda.

**Acceptance Scenarios**:

1. **Given** I run `docker-compose -f docker-compose.dapr.yml up`, **When** all services are healthy, **Then** the following containers are running: backend, frontend, redpanda, dapr-sidecar-backend, reminder-worker, recurrence-worker.
2. **Given** Redpanda is running, **When** I access the Redpanda console at `localhost:8080`, **Then** I can see the `tasks` topic with published messages.
3. **Given** the backend is running with its Dapr sidecar, **When** I call `POST /tasks`, **Then** the event appears in Redpanda within 1 second.
4. **Given** I stop Redpanda, **When** I restart it, **Then** Dapr reconnects automatically and event flow resumes.

---

### User Story 5 - Zero Regression in Existing Features (Priority: P0)

As an end user, I want the application to behave exactly as before (auth, CRUD, chatbot, MCP tools) so that the infrastructure changes are invisible to me.

**Why this priority**: This is a non-negotiable constraint. Any regression would invalidate the entire phase.

**Independent Test**: Run the full existing test suite. Verify 100% of tests pass. Manually test signup, signin, task CRUD, chatbot, and MCP tools.

**Acceptance Scenarios**:

1. **Given** I sign up with a new account, **When** the signup completes, **Then** I can sign in and see an empty task list (identical to Phase V Part A).
2. **Given** I create, read, update, delete tasks via the API, **When** each operation completes, **Then** the response payloads are byte-identical to Phase V Part A.
3. **Given** I use the chatbot to create a task, **When** the task is created, **Then** it appears in my task list as before.
4. **Given** I use MCP tools, **When** I perform any operation, **Then** the behavior is unchanged.
5. **Given** I run the existing backend test suite, **When** all tests execute, **Then** 100% pass with no modifications to test code.

---

### Edge Cases

- What happens when Kafka/Redpanda is down during event publication?
  - The operation succeeds (graceful degradation). The failure is logged. Events are not persisted to an outbox (out of scope for Part B).

- What happens when a worker crashes mid-processing?
  - The event remains in Kafka (not acknowledged). On worker restart, it will be redelivered.

- What happens when a worker receives duplicate events (at-least-once delivery)?
  - Reminder Worker: Checks `reminder_sent` flag before logging (idempotent). Recurrence Worker: Checks for existing child task with same `parent_task_id` and `due_at` (idempotent).

- What happens when the cron binding fires but no reminders are due?
  - The reminder check query returns empty. No events are published. No worker processing occurs.

- What happens when docker-compose is run on a Windows host?
  - Redpanda and Dapr both support Windows via Docker. Volume mounts use Windows-compatible paths.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Dapr Pub/Sub Integration

- **FR-001**: The `EventBus` class MUST be refactored to publish events via Dapr Pub/Sub HTTP API (`/v1.0/publish/{pubsubname}/{topic}`).
- **FR-002**: All six domain events MUST be published to a single `tasks` topic in Kafka.
- **FR-003**: Event payloads MUST be serialized as JSON with the existing field structure (no schema changes).
- **FR-004**: The Dapr pub/sub component MUST be named `taskpubsub` and configured for Redpanda (Kafka protocol).
- **FR-005**: If Dapr sidecar is unavailable, event publication MUST fail gracefully (log error, don't crash).

#### Dapr Components Configuration

- **FR-006**: A Dapr pub/sub component file MUST be created at `dapr/components/pubsub.yaml` configuring Redpanda.
- **FR-007**: A Dapr state store component file MUST be created at `dapr/components/statestore.yaml` (Redis-based for worker state, optional).
- **FR-008**: A Dapr secret store component file MUST be created at `dapr/components/secrets.yaml` (local file-based for local dev).
- **FR-009**: A Dapr cron binding file MUST be created at `dapr/components/cron-reminder.yaml` triggering reminder checks every 1 minute.

#### Reminder Worker Service

- **FR-010**: A `reminder-worker` service MUST be created that subscribes to `TaskReminderDue` events via Dapr.
- **FR-011**: On receiving a `TaskReminderDue` event, the worker MUST log: `"[ReminderWorker] Delivered reminder for task {task_id}: {title}"`.
- **FR-012**: The worker MUST expose a Dapr subscription endpoint at `POST /dapr/subscribe` returning the topic subscription.
- **FR-013**: The worker MUST expose an event handler at `POST /events/task-reminder-due`.

#### Recurrence Worker Service

- **FR-014**: A `recurrence-worker` service MUST be created that subscribes to `RecurringTaskGenerated` events via Dapr.
- **FR-015**: On receiving a `RecurringTaskGenerated` event, the worker MUST create a new task in the database with:
  - `id`: new UUID
  - `user_id`: from event
  - `title`: from event
  - `due_at`: `next_due_at` from event
  - `parent_task_id`: from event
  - `recurrence_pattern`: from event
  - Other fields copied from parent task (looked up by `parent_task_id`)
- **FR-016**: The worker MUST be idempotent: if a task already exists with matching `parent_task_id` and `due_at`, skip creation.
- **FR-017**: The worker MUST use Dapr service invocation or direct database connection to create tasks.

#### Backend API Updates

- **FR-018**: The backend's reminder check endpoint MUST publish `TaskReminderDue` events via Dapr instead of in-process emission.
- **FR-019**: The backend MUST NOT block on Dapr pub/sub responses (fire-and-forget with error logging).
- **FR-020**: The existing FastAPI dependency injection for `EventBus` MUST be preserved (interface unchanged, implementation swapped).

#### Docker Compose Infrastructure

- **FR-021**: A new `docker-compose.dapr.yml` file MUST be created with: Redpanda, backend + Dapr sidecar, frontend, reminder-worker + sidecar, recurrence-worker + sidecar.
- **FR-022**: Redpanda MUST expose port 9092 (Kafka API) and port 8080 (Redpanda Console).
- **FR-023**: Each Dapr sidecar MUST be configured with `--app-id`, `--app-port`, `--dapr-http-port`, and `--components-path`.
- **FR-024**: Workers MUST wait for Redpanda to be healthy before starting.

#### Dapr Service-to-Service Invocation

- **FR-025**: The Recurrence Worker MAY use Dapr service invocation (`/v1.0/invoke/{app-id}/method/{endpoint}`) to look up parent task details.
- **FR-026**: Direct database access from workers is acceptable as an alternative to service invocation.

---

### Key Entities *(mandatory)*

#### New Configuration Files

```
dapr/
  components/
    pubsub.yaml       # Dapr pub/sub for Redpanda
    statestore.yaml   # Dapr state store (Redis, optional)
    secrets.yaml      # Dapr secrets (local file)
    cron-reminder.yaml # Cron binding for reminder checks
```

#### New Worker Services

```
services/
  reminder-worker/
    main.py           # FastAPI app with Dapr subscription
    Dockerfile        # Worker container image
  recurrence-worker/
    main.py           # FastAPI app with Dapr subscription
    Dockerfile        # Worker container image
```

#### Modified Files

```
backend/src/events/
  bus.py              # Refactored to use Dapr HTTP pub/sub

docker-compose.dapr.yml  # New compose file for Dapr stack
```

#### Dapr Topic Structure

```
Topic: tasks
  Events:
    - TaskCreated
    - TaskUpdated
    - TaskCompleted
    - TaskDeleted
    - TaskReminderDue
    - RecurringTaskGenerated

Consumer Groups:
  - reminder-worker (filters for TaskReminderDue)
  - recurrence-worker (filters for RecurringTaskGenerated)
```

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All six domain events are published to the `tasks` Kafka topic via Dapr.
- **SC-002**: Event payloads in Kafka match the exact JSON structure from Phase V Part A (no schema changes).
- **SC-003**: Reminder Worker logs delivery for every `TaskReminderDue` event within 5 seconds of publication.
- **SC-004**: Recurrence Worker creates the next task instance within 5 seconds of receiving `RecurringTaskGenerated`.
- **SC-005**: Task completion API response time remains under 500ms (async worker processing does not block).
- **SC-006**: `docker-compose.dapr.yml up` brings up all 6+ containers healthy within 60 seconds.
- **SC-007**: Redpanda Console shows published events with correct payloads.
- **SC-008**: 100% of existing backend tests pass without modification.
- **SC-009**: Manual smoke test of signup, signin, task CRUD, chatbot, and MCP tools all succeed.
- **SC-010**: Application remains fully functional when Dapr/Kafka is temporarily unavailable (graceful degradation).
- **SC-011**: Workers are idempotent: duplicate event delivery does not create duplicate tasks or duplicate log entries.
- **SC-012**: Dapr cron binding triggers reminder checks every 1 minute.

---

## Scope & Boundaries *(mandatory)*

### In Scope

- Refactoring `EventBus` to publish via Dapr HTTP API
- Creating Dapr component configurations (pubsub, statestore, secrets, cron)
- Adding Redpanda (Kafka-compatible) to docker-compose
- Creating Reminder Worker service (logging-only notification)
- Creating Recurrence Worker service (task creation)
- Adding Dapr sidecars to docker-compose for backend and workers
- Creating `docker-compose.dapr.yml` for the full Dapr stack
- Documenting local Dapr + Kafka startup in README
- Ensuring zero regression in existing features
- Graceful degradation when Dapr/Kafka is unavailable

### Out of Scope

- Cloud deployment (Azure, AWS, GCP)
- Kubernetes or Minikube deployment
- Real notification delivery (email, SMS, push)
- Frontend UI changes
- New API endpoints (beyond what exists)
- Outbox pattern for guaranteed delivery
- Dead-letter queue UI
- Monitoring/alerting dashboards
- Performance tuning or optimization
- Schema registry
- Multiple Kafka partitions or consumer scaling
- Changes to business logic

---

## Assumptions *(mandatory)*

- Redpanda is fully Kafka-compatible and works with Dapr's Kafka pub/sub component.
- Dapr sidecars can run in Docker Compose without Kubernetes.
- Workers can share the same database connection string as the backend (Neon PostgreSQL).
- The existing `EventBus` interface (`emit()` method) can be preserved while swapping the implementation.
- At-least-once delivery is acceptable (idempotent consumers handle duplicates).
- Logging is sufficient for reminder "delivery" in Part B (actual notifications deferred).
- Local development on Windows works via Docker Desktop with WSL2.
- The 1-minute cron interval is sufficient for reminder checks (real-time delivery not required).

---

## Dependencies *(mandatory)*

### Internal Dependencies

- **Phase V Part A**: Domain event models (`TaskCreated`, `TaskUpdated`, etc.), `EventBus` interface, task router event emission points.
- **Existing Backend**: FastAPI app, SQLModel models, Neon PostgreSQL connection.
- **Existing Frontend**: No changes, but must continue working.

### External Dependencies

- **Dapr Runtime**: v1.13+ for pub/sub, bindings, and service invocation.
- **Redpanda**: v24.x (Kafka-compatible message broker).
- **Docker Compose**: v2.x for container orchestration.
- **Redis** (optional): For Dapr state store if worker state is needed.

### New Python Packages (Workers)

- `fastapi`: Web framework for subscription endpoints.
- `uvicorn`: ASGI server.
- `httpx`: HTTP client for Dapr API calls.
- `pydantic`: Event schema validation.
- `sqlmodel` or `psycopg2`: Database access for Recurrence Worker.

---

## Non-Functional Requirements *(mandatory)*

### Performance

- Task API response times MUST NOT increase by more than 50ms due to Dapr integration.
- Event publication to Dapr MUST be fire-and-forget (async, no blocking wait for Kafka ack).
- Workers MUST process events within 5 seconds of publication under normal load.

### Reliability

- If Dapr sidecar is unavailable, API operations MUST succeed (graceful degradation).
- Workers MUST handle malformed events without crashing.
- Workers MUST reconnect to Dapr/Kafka after transient failures.

### Security

- Dapr components MUST NOT expose sensitive credentials in plain text (use secrets component).
- Worker database connections MUST use the same secure credentials as backend.
- Dapr HTTP APIs are internal-only (not exposed outside Docker network).

### Observability

- All event publications MUST be logged with event type and task_id.
- All worker event processing MUST be logged with status (success/failure).
- Redpanda Console provides visibility into topic messages.

### Backward Compatibility

- API request/response schemas are unchanged.
- Frontend requires no modifications.
- Existing tests pass without changes.
- `docker-compose.yml` (non-Dapr) remains functional for simple deployments.

---

## Architecture Overview *(mandatory)*

### Event Flow Diagram

```
┌─────────────┐      ┌────────────────┐      ┌─────────────┐      ┌──────────────┐
│   Frontend  │──────▶  Backend API   │──────▶ Dapr Sidecar│──────▶   Redpanda   │
│   (Next.js) │      │   (FastAPI)    │      │  (HTTP API) │      │   (Kafka)    │
└─────────────┘      └────────────────┘      └─────────────┘      └──────┬───────┘
                                                                         │
                            ┌────────────────────────────────────────────┼─────────────────────────────┐
                            │                                            │                             │
                            ▼                                            ▼                             ▼
                  ┌─────────────────┐                         ┌─────────────────┐           ┌─────────────────┐
                  │ Reminder Worker │                         │Recurrence Worker│           │  (Future)       │
                  │   + Sidecar     │                         │   + Sidecar     │           │ Notification    │
                  └────────┬────────┘                         └────────┬────────┘           │    Service      │
                           │                                           │                    └─────────────────┘
                           │ Log delivery                              │ Create task
                           ▼                                           ▼
                      (Console)                                  ┌─────────────┐
                                                                 │    Neon     │
                                                                 │ PostgreSQL  │
                                                                 └─────────────┘
```

### Component Responsibilities

| Component              | Responsibility                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------ |
| Backend API            | Publish domain events via Dapr. Handle HTTP requests. No change to business logic.  |
| Dapr Sidecar (Backend) | Translate pub/sub calls to Kafka. Handle retry logic.                               |
| Redpanda               | Store and distribute events. Kafka-compatible broker.                               |
| Reminder Worker        | Subscribe to `TaskReminderDue`. Log delivery (stub for notifications).              |
| Recurrence Worker      | Subscribe to `RecurringTaskGenerated`. Create next task instance.                   |
| Dapr Cron Binding      | Trigger reminder checks on schedule (1-minute interval).                            |

---

## File Impact Summary

### Files to Create

- `dapr/components/pubsub.yaml` - Pub/sub component for Redpanda
- `dapr/components/statestore.yaml` - State store component (optional)
- `dapr/components/secrets.yaml` - Secrets component
- `dapr/components/cron-reminder.yaml` - Cron binding for reminders
- `services/reminder-worker/main.py` - Reminder worker FastAPI app
- `services/reminder-worker/Dockerfile` - Reminder worker container
- `services/recurrence-worker/main.py` - Recurrence worker FastAPI app
- `services/recurrence-worker/Dockerfile` - Recurrence worker container
- `docker-compose.dapr.yml` - Full Dapr stack compose file

### Files to Modify

- `backend/src/events/bus.py` - Refactor to use Dapr HTTP API
- `README.md` - Add section on Dapr + Kafka local development

### Files Unchanged (Business Logic Preserved)

- `backend/src/events/models.py` - Event schemas unchanged
- `backend/src/routers/tasks.py` - Event emission points unchanged
- `backend/src/models/task.py` - Task model unchanged
- `backend/src/schemas/task.py` - API schemas unchanged
- `frontend/**/*` - No frontend changes

---

## Open Questions

- **Q1**: Should the Recurrence Worker use Dapr service invocation or direct database access?
  - **Answer**: Direct database access is simpler and avoids adding complexity. The worker shares the same Neon connection string as the backend.

- **Q2**: Should there be a Redis container for Dapr state store?
  - **Answer**: Optional. Include in docker-compose but state store is not strictly required for Part B. Workers can be stateless.

- **Q3**: Should the original `docker-compose.yml` be modified or a new file created?
  - **Answer**: Create a new `docker-compose.dapr.yml` file. Keep the original for simple deployments without Dapr/Kafka.
