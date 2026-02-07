# Research: Phase V Part B - Event-Driven Infrastructure

**Feature**: `005-phase5-partb-event-driven-infra`
**Date**: 2026-02-06

---

## Research Summary

All technical unknowns have been researched and resolved. This document captures decisions, rationale, and alternatives considered.

---

## 1. Dapr Pub/Sub with Redpanda (Kafka-compatible)

### Decision
Use Dapr's Kafka pub/sub component configured for Redpanda as the message broker.

### Rationale
- **Redpanda** is 100% Kafka API-compatible but simpler to operate (single binary, no Zookeeper)
- **Dapr** abstracts the Kafka API behind a simple HTTP interface (`/v1.0/publish/{pubsub}/{topic}`)
- The existing `EventBus.emit()` interface can be preserved; only the implementation changes
- Dapr handles retries, dead-letter queues, and consumer group management

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Direct Kafka client (kafka-python) | More complex, requires managing partitions, offsets, consumer groups manually |
| RabbitMQ | Not Kafka-compatible, would require different Dapr component |
| Redis Streams | Less durable, not designed for event sourcing patterns |
| Native Dapr Component (in-memory) | Not suitable for production; no persistence |

### Implementation Notes
- Dapr sidecar listens on port 3500 by default
- Publish endpoint: `POST http://localhost:3500/v1.0/publish/taskpubsub/tasks`
- Payload must be JSON with CloudEvents-compatible structure

---

## 2. Dapr Sidecar in Docker Compose

### Decision
Run Dapr sidecars as separate containers linked via Docker network, using `--app-id` and `--dapr-http-port` flags.

### Rationale
- Dapr officially supports "self-hosted" mode with Docker Compose
- Each service gets its own sidecar container for isolation
- Sidecar and app communicate via localhost when using `network_mode: "service:<app>"` or via service names

### Architecture Pattern

```yaml
services:
  backend:
    ...
  backend-dapr:
    image: daprio/daprd:1.13.0
    command: ["./daprd", "--app-id", "backend", "--app-port", "8000", ...]
    network_mode: "service:backend"  # Share network with backend
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Kubernetes + Dapr operator | Out of scope (spec prohibits K8s) |
| Single Dapr sidecar for all services | Violates Dapr architecture; sidecars are per-app |
| Dapr CLI (`dapr run`) | Not compatible with Docker Compose orchestration |

---

## 3. Dapr Cron Binding for Reminders

### Decision
Use Dapr input binding with `bindings.cron` type to trigger reminder checks every 1 minute.

### Rationale
- Dapr cron bindings are declarative and restart-safe
- Backend receives HTTP POST at `/reminder-cron` when cron fires
- No external scheduler (crontab, systemd timers) needed

### Component Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/1 * * * *"  # Every minute
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| APScheduler (Python) | Runs inside app process; restart loses state |
| Celery Beat | Requires Redis/RabbitMQ; adds complexity |
| Kubernetes CronJob | Out of scope (no K8s) |
| External cron (systemd) | Not portable to Docker/cloud |

---

## 4. Worker Service Architecture

### Decision
Create two separate worker services (reminder-worker, recurrence-worker) as lightweight FastAPI apps with Dapr subscriptions.

### Rationale
- **Separation of concerns**: Each worker handles one event type
- **Independent scaling**: Workers can be scaled independently in future
- **Fault isolation**: One worker crashing doesn't affect the other
- **Simple implementation**: FastAPI makes Dapr subscription endpoints trivial

### Worker Structure

```
services/
├── reminder-worker/
│   ├── main.py          # FastAPI app with /dapr/subscribe and /events/task-reminder-due
│   ├── Dockerfile
│   └── requirements.txt
└── recurrence-worker/
    ├── main.py          # FastAPI app with /dapr/subscribe and /events/recurring-task-generated
    ├── Dockerfile
    └── requirements.txt
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Single worker with multiple handlers | Less clear separation; harder to scale |
| Background threads in main backend | Blocks backend process; not truly async |
| Celery workers | Overkill for this use case; adds broker dependency |

---

## 5. EventBus Refactoring Strategy

### Decision
Refactor `EventBus` to use `httpx` for async HTTP calls to Dapr sidecar, while preserving the `emit()` method signature.

### Rationale
- **Zero breaking changes**: All event emission points in `tasks.py`, `reminders.py`, `recurrence.py` remain unchanged
- **Graceful degradation**: If Dapr is unavailable, log and continue (fire-and-forget)
- **Testability**: In tests, Dapr endpoint can be mocked or replaced with in-memory bus

### Implementation Pattern

```python
class EventBus:
    def __init__(self, dapr_port: int = 3500):
        self.dapr_url = f"http://localhost:{dapr_port}/v1.0/publish/taskpubsub/tasks"
        self._client = httpx.AsyncClient()

    async def emit(self, event: Any) -> None:
        payload = asdict(event)
        try:
            await self._client.post(self.dapr_url, json=payload)
            logger.info("Event published: %s", event.event_type)
        except Exception as e:
            logger.warning("Failed to publish event: %s", e)
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Dapr Python SDK (dapr-ext-fastapi) | Adds dependency; HTTP is simpler |
| Synchronous requests | Blocks event loop; bad for performance |
| Kafka client directly | Bypasses Dapr; loses abstraction benefits |

---

## 6. Database Access from Workers

### Decision
Workers access Neon PostgreSQL directly using the same connection string as the backend.

### Rationale
- **Simplicity**: No need for Dapr service invocation or API calls
- **Performance**: Direct DB access is faster than HTTP round-trips
- **Consistency**: Uses the same SQLModel/SQLAlchemy stack as backend
- **Security**: Connection string passed via environment variable

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Dapr service invocation to backend | Adds latency; backend must expose internal endpoints |
| Separate database | Unnecessary complexity; violates DRY |
| Dapr state store | Not suitable for relational data |

---

## 7. Idempotency Strategy

### Decision
Workers implement idempotency checks before taking action.

### Rationale
- Kafka provides at-least-once delivery; duplicates are possible
- Idempotent workers prevent duplicate side effects

### Implementation

| Worker | Idempotency Check |
|--------|-------------------|
| Reminder Worker | Check if reminder was already logged (no persistent state needed; logging is idempotent) |
| Recurrence Worker | Query DB for existing task with same `parent_task_id` and `due_at` before insert |

---

## 8. Docker Compose File Strategy

### Decision
Create a new `docker-compose.dapr.yml` file; do not modify the existing `docker-compose.yml`.

### Rationale
- **Backward compatibility**: Existing simple deployments continue to work
- **Explicit opt-in**: Users choose the Dapr stack by using the dapr-specific file
- **Clear separation**: Infrastructure concerns isolated in their own file

### Usage

```bash
# Simple deployment (no Dapr/Kafka)
docker-compose up

# Full event-driven stack
docker-compose -f docker-compose.dapr.yml up
```

---

## 9. Secret Management

### Decision
Use Dapr local file secret store for local development; secrets in `.env` file.

### Rationale
- Local file secret store is simplest for development
- Production will use cloud-native secret stores (Azure Key Vault, AWS Secrets Manager)
- No changes to existing `.env` pattern

### Component Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: localsecretstore
spec:
  type: secretstores.local.file
  version: v1
  metadata:
    - name: secretsFile
      value: /secrets/secrets.json
```

---

## 10. Redpanda Console Access

### Decision
Expose Redpanda Console on port 8080 for local debugging.

### Rationale
- Visual inspection of topics and messages during development
- Helps debug event flow issues
- Read-only by default (safe for dev)

### Configuration

```yaml
redpanda:
  image: docker.redpanda.com/redpandadata/redpanda:v24.1.1
  ports:
    - "9092:9092"   # Kafka API
    - "8080:8080"   # Redpanda Console
```

---

## Summary of Resolved Unknowns

| Unknown | Resolution |
|---------|------------|
| How to integrate Dapr with Kafka? | Redpanda with Dapr Kafka pub/sub component |
| How to run Dapr sidecars in Docker? | Separate containers with `network_mode: "service:<app>"` |
| How to schedule reminder checks? | Dapr cron input binding |
| Worker architecture? | Two separate FastAPI apps with Dapr subscriptions |
| EventBus refactoring? | Async HTTP calls to Dapr sidecar |
| Database access from workers? | Direct connection using shared connection string |
| Idempotency? | DB checks before inserts; logging is naturally idempotent |
| Docker Compose strategy? | New `docker-compose.dapr.yml` file |
| Secret management? | Dapr local file secret store |
| Message visibility? | Redpanda Console on port 8080 |

---

## Dependencies Confirmed

| Dependency | Version | Purpose |
|------------|---------|---------|
| Dapr Runtime | 1.13.x | Sidecar for pub/sub, bindings |
| Redpanda | v24.1.x | Kafka-compatible message broker |
| httpx | 0.27.x | Async HTTP client for Dapr API |
| FastAPI | 0.115.x | Worker service framework |
| uvicorn | 0.30.x | Worker ASGI server |
