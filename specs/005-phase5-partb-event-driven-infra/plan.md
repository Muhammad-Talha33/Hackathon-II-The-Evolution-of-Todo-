# Implementation Plan: Phase V Part B - Event-Driven Infrastructure

**Branch**: `005-phase5-partb-event-driven-infra` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-phase5-partb-event-driven-infra/spec.md`

---

## Summary

Convert the existing in-process EventBus to a distributed event-driven architecture using **Dapr** for pub/sub abstraction and **Redpanda** (Kafka-compatible) as the message broker. This is an infrastructure-only change; business logic remains untouched. Two worker services (Reminder Worker, Recurrence Worker) will consume events asynchronously.

---

## Technical Context

**Language/Version**: Python 3.11+ (backend, workers)
**Primary Dependencies**: FastAPI 0.115.x, Dapr 1.13.x, httpx 0.27.x, Redpanda v24.x
**Storage**: Neon PostgreSQL (unchanged), Redis (optional Dapr state store)
**Testing**: pytest (existing backend tests), manual smoke tests
**Target Platform**: Docker Compose (local development)
**Project Type**: Web application with microservices workers
**Performance Goals**: Event publication <50ms, worker processing <5s
**Constraints**: Zero regression in existing features, graceful degradation when Dapr unavailable
**Scale/Scope**: Single Kafka partition, two workers, local development only

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Separation of Concerns | ✅ PASS | EventBus abstraction preserved; workers are separate services |
| Input Validation | ✅ PASS | Event schemas validated via dataclasses (unchanged) |
| Error Handling | ✅ PASS | Graceful degradation on Dapr failures |
| Code Quality | ✅ PASS | Type hints, docstrings in new worker code |

### Post-Design Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Separation of Concerns | ✅ PASS | Workers handle one event type each; clear boundaries |
| Input Validation | ✅ PASS | CloudEvents envelope validated by Dapr; payload by workers |
| Error Handling | ✅ PASS | Workers return Dapr response status (SUCCESS/RETRY/DROP) |
| Code Quality | ✅ PASS | FastAPI structure matches backend patterns |

**Gate Result**: ✅ PASSED - No violations requiring justification

---

## Project Structure

### Documentation (this feature)

```text
specs/005-phase5-partb-event-driven-infra/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Technology research
├── data-model.md        # Phase 1: Event schemas, Dapr components
├── quickstart.md        # Phase 1: Local development guide
├── contracts/           # Phase 1: API contracts
│   ├── dapr-pubsub.yaml       # Dapr publication API
│   └── worker-subscription.yaml # Worker event handlers
└── tasks.md             # Phase 2: Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
# Existing (modified)
backend/
├── src/
│   ├── events/
│   │   ├── __init__.py
│   │   ├── models.py      # Unchanged - event dataclasses
│   │   └── bus.py         # MODIFIED - Dapr HTTP pub/sub
│   ├── routers/
│   │   └── tasks.py       # Unchanged - event emission points
│   └── services/
│       ├── reminders.py   # Unchanged
│       └── recurrence.py  # Unchanged
└── requirements.txt       # ADD: httpx

# New infrastructure
dapr/
├── components/
│   ├── pubsub.yaml        # Kafka pub/sub for Redpanda
│   ├── statestore.yaml    # Redis state store (optional)
│   ├── secrets.yaml       # Local file secret store
│   └── cron-reminder.yaml # Cron binding for reminders

# New worker services
services/
├── reminder-worker/
│   ├── main.py            # FastAPI app with Dapr subscription
│   ├── Dockerfile
│   └── requirements.txt
└── recurrence-worker/
    ├── main.py            # FastAPI app with Dapr subscription
    ├── Dockerfile
    └── requirements.txt

# New Docker Compose
docker-compose.dapr.yml    # Full Dapr + Redpanda stack

# Existing (unchanged)
docker-compose.yml         # Simple deployment without Dapr
frontend/                  # No changes
```

**Structure Decision**: Web application pattern with new microservices workers. Workers are separate Python services with their own Dockerfiles, following the backend FastAPI pattern.

---

## Architecture Overview

### Event Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 PRODUCTION FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────────┐  │
│  │ Frontend │────▶│ Backend API  │────▶│ Dapr Sidecar│────▶│   Redpanda     │  │
│  │ (Next.js)│     │  (FastAPI)   │     │  (HTTP)     │     │ (Kafka broker) │  │
│  └──────────┘     └──────────────┘     └─────────────┘     └───────┬────────┘  │
│                                                                     │           │
│                   ┌─────────────────────────────────────────────────┤           │
│                   │                                                 │           │
│                   ▼                                                 ▼           │
│         ┌─────────────────────┐                      ┌─────────────────────┐   │
│         │   Reminder Worker   │                      │  Recurrence Worker  │   │
│         │   (TaskReminderDue) │                      │(RecurringTaskGenerated)│ │
│         └──────────┬──────────┘                      └──────────┬──────────┘   │
│                    │                                            │              │
│                    │ Log delivery                               │ Create task  │
│                    ▼                                            ▼              │
│               (Console)                                    ┌───────────┐       │
│                                                            │ PostgreSQL│       │
│                                                            └───────────┘       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| Backend API | HTTP API for tasks. Publishes events via Dapr sidecar. |
| Dapr Sidecar (backend) | Translates pub/sub HTTP calls to Kafka protocol. |
| Redpanda | Kafka-compatible message broker. Stores events. |
| Reminder Worker | Subscribes to `TaskReminderDue`. Logs delivery stub. |
| Recurrence Worker | Subscribes to `RecurringTaskGenerated`. Creates next task in DB. |
| Dapr Cron Binding | Triggers `/reminder-cron` endpoint every minute. |

---

## Implementation Strategy

### Phase 1: Infrastructure Foundation

1. Create Dapr component YAML files
2. Create `docker-compose.dapr.yml` with Redpanda + sidecars
3. Verify Dapr + Redpanda connectivity

### Phase 2: EventBus Refactoring

1. Add `httpx` to backend requirements
2. Refactor `EventBus` to use Dapr HTTP API
3. Add graceful degradation (log on failure, don't crash)
4. Verify events appear in Redpanda

### Phase 3: Reminder Worker

1. Create `services/reminder-worker/` structure
2. Implement Dapr subscription endpoint
3. Implement event handler (logging only)
4. Add to docker-compose.dapr.yml
5. Verify end-to-end flow

### Phase 4: Recurrence Worker

1. Create `services/recurrence-worker/` structure
2. Implement Dapr subscription endpoint
3. Implement event handler (DB task creation)
4. Add idempotency check
5. Add to docker-compose.dapr.yml
6. Verify end-to-end flow

### Phase 5: Cron Binding

1. Create cron-reminder.yaml component
2. Add `/reminder-cron` endpoint to backend
3. Verify cron triggers reminder check

### Phase 6: Integration Testing

1. Run existing backend test suite
2. Manual smoke test all features
3. Verify zero regression
4. Document any issues

---

## Key Technical Decisions

### 1. EventBus Implementation

**Before (Phase V Part A)**:
```python
class EventBus:
    def emit(self, event: Any) -> None:
        self._events.append(event)
        logger.info("Event emitted: %s", event.event_type)
```

**After (Phase V Part B)**:
```python
class EventBus:
    async def emit(self, event: Any) -> None:
        payload = asdict(event)
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"http://localhost:{self.dapr_port}/v1.0/publish/taskpubsub/tasks",
                    json=payload,
                    timeout=5.0
                )
            logger.info("Event published: %s", event.event_type)
        except Exception as e:
            logger.warning("Failed to publish event: %s", e)
```

### 2. Worker Subscription Pattern

Workers expose `/dapr/subscribe` for Dapr to discover subscriptions:

```python
@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "taskpubsub",
            "topic": "tasks",
            "route": "/events/task-reminder-due"
        }
    ]
```

### 3. Dapr Response Status

Workers return status to control Kafka acknowledgment:

| Status | Meaning | When to Use |
|--------|---------|-------------|
| `SUCCESS` | Event processed | Normal completion |
| `RETRY` | Temporary failure | DB error, network issue |
| `DROP` | Permanent failure | Invalid event, don't retry |

### 4. Docker Network Mode

Sidecars share network with their apps:

```yaml
backend-dapr:
  network_mode: "service:backend"
```

This allows sidecar to reach app on `localhost`.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Dapr sidecar fails to start | Validate component YAML before deploy; clear error messages |
| Events lost during Redpanda restart | Events persisted to disk; auto-recovery on restart |
| Worker crashes mid-processing | Event remains uncommitted; redelivered on restart |
| Database connection from workers | Same connection string as backend; already tested |
| Performance regression | Fire-and-forget publish; no blocking on Kafka ack |

---

## Dependencies to Add

### Backend

```
# backend/requirements.txt
httpx>=0.27.0  # Async HTTP client for Dapr API
```

### Worker Services

```
# services/reminder-worker/requirements.txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.5.0
httpx>=0.27.0

# services/recurrence-worker/requirements.txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.5.0
sqlmodel>=0.0.14
asyncpg>=0.30.0
httpx>=0.27.0
```

---

## Complexity Tracking

> No complexity violations detected. All changes follow existing patterns.

| Aspect | Complexity | Justification |
|--------|------------|---------------|
| New services (2 workers) | Low | Minimal FastAPI apps, single responsibility |
| Docker Compose additions | Medium | Standard Dapr sidecar pattern |
| EventBus refactor | Low | Interface unchanged, implementation swap |
| Database access from workers | Low | Reuses existing connection pattern |

---

## Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Events in Redpanda | 100% of emitted events | Redpanda Console inspection |
| Reminder Worker processing | <5s from publish | Log timestamps |
| Recurrence Worker processing | <5s, task created | DB query |
| Backend test suite | 100% pass | `pytest` execution |
| Manual smoke test | All features work | Checklist verification |
| Graceful degradation | API works when Dapr down | Stop Dapr, verify API |

---

## Artifacts Generated

| Artifact | Path | Status |
|----------|------|--------|
| Research | `research.md` | ✅ Complete |
| Data Model | `data-model.md` | ✅ Complete |
| Dapr API Contract | `contracts/dapr-pubsub.yaml` | ✅ Complete |
| Worker API Contract | `contracts/worker-subscription.yaml` | ✅ Complete |
| Quickstart Guide | `quickstart.md` | ✅ Complete |

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement in order: Infrastructure → EventBus → Workers → Cron → Testing
3. Verify zero regression before merging
