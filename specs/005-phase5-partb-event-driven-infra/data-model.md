# Data Model: Phase V Part B - Event-Driven Infrastructure

**Feature**: `005-phase5-partb-event-driven-infra`
**Date**: 2026-02-06

---

## Overview

Phase V Part B introduces **no changes to the database schema**. All existing entities from Phase V Part A remain unchanged. This document focuses on the **event message schemas** and **Dapr component configurations** that define the event-driven data contracts.

---

## Existing Entities (Unchanged)

### Task Model

The Task entity remains exactly as defined in Phase V Part A:

```
Task:
  id: UUID (PK)
  user_id: UUID (FK -> users.id)
  title: str (1-500 chars)
  description: str | null
  status: TaskStatus (incomplete | complete)
  priority: Priority (low | medium | high)
  tags: list[str]
  due_at: datetime | null
  remind_at: datetime | null
  reminder_sent: bool
  recurrence_pattern: RecurrencePattern | null
  parent_task_id: UUID | null (FK -> tasks.id)
  created_at: datetime
  updated_at: datetime
```

### User Model

No changes to the User entity.

---

## Event Schemas (Unchanged Payload, New Transport)

All event payloads remain identical to Phase V Part A. The only change is the **transport mechanism** (Dapr Pub/Sub instead of in-process).

### CloudEvents Envelope

Dapr wraps all events in CloudEvents format. The application payload is in the `data` field:

```json
{
  "specversion": "1.0",
  "type": "com.todo.TaskCreated",
  "source": "backend",
  "id": "<uuid>",
  "time": "2026-02-06T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    // Event payload here
  }
}
```

### Event Payloads

#### TaskCreated

```json
{
  "event_type": "TaskCreated",
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "priority": "low|medium|high",
  "tags": ["string"],
  "due_at": "datetime|null",
  "recurrence_pattern": "daily|weekly|monthly|null",
  "created_at": "datetime",
  "timestamp": "datetime"
}
```

#### TaskUpdated

```json
{
  "event_type": "TaskUpdated",
  "task_id": "uuid",
  "user_id": "uuid",
  "updated_fields": ["string"],
  "updated_at": "datetime",
  "timestamp": "datetime"
}
```

#### TaskCompleted

```json
{
  "event_type": "TaskCompleted",
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "completed_at": "datetime",
  "had_recurrence": "boolean",
  "was_overdue": "boolean",
  "timestamp": "datetime"
}
```

#### TaskDeleted

```json
{
  "event_type": "TaskDeleted",
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "deleted_at": "datetime",
  "timestamp": "datetime"
}
```

#### TaskReminderDue

```json
{
  "event_type": "TaskReminderDue",
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "remind_at": "datetime",
  "due_at": "datetime|null",
  "timestamp": "datetime"
}
```

#### RecurringTaskGenerated

```json
{
  "event_type": "RecurringTaskGenerated",
  "new_task_id": "uuid",
  "parent_task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "next_due_at": "datetime",
  "recurrence_pattern": "daily|weekly|monthly",
  "timestamp": "datetime"
}
```

---

## Dapr Component Schemas

### Pub/Sub Component (pubsub.yaml)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda:9092"
    - name: consumerGroup
      value: "todo-consumers"
    - name: clientID
      value: "todo-backend"
    - name: authType
      value: "none"
    - name: disableTls
      value: "true"
```

### State Store Component (statestore.yaml)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
    - name: redisPassword
      value: ""
```

### Secret Store Component (secrets.yaml)

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
      value: "/secrets/secrets.json"
    - name: nestedSeparator
      value: ":"
```

### Cron Binding Component (cron-reminder.yaml)

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
      value: "*/1 * * * *"
  scopes:
    - backend
```

---

## Kafka Topic Schema

### Topic: `tasks`

Single topic for all task-related events. Event routing is done by workers based on `event_type` field.

```
Topic Name: tasks
Partitions: 1 (local dev)
Replication Factor: 1 (local dev)
Retention: 7 days
```

### Consumer Groups

| Consumer Group | App ID | Events Consumed |
|----------------|--------|-----------------|
| `reminder-worker` | reminder-worker | TaskReminderDue |
| `recurrence-worker` | recurrence-worker | RecurringTaskGenerated |

---

## Dapr Subscription Schema

Workers declare subscriptions via `/dapr/subscribe` endpoint.

### Reminder Worker Subscription

```json
[
  {
    "pubsubname": "taskpubsub",
    "topic": "tasks",
    "route": "/events/task-reminder-due",
    "metadata": {
      "rawPayload": "true"
    }
  }
]
```

### Recurrence Worker Subscription

```json
[
  {
    "pubsubname": "taskpubsub",
    "topic": "tasks",
    "route": "/events/recurring-task-generated",
    "metadata": {
      "rawPayload": "true"
    }
  }
]
```

---

## Configuration Environment Variables

### Backend Service

| Variable | Description | Example |
|----------|-------------|---------|
| `DAPR_HTTP_PORT` | Dapr sidecar HTTP port | `3500` |
| `DAPR_GRPC_PORT` | Dapr sidecar gRPC port | `50001` |
| `PUBSUB_NAME` | Dapr pub/sub component name | `taskpubsub` |
| `TOPIC_NAME` | Kafka topic for events | `tasks` |

### Worker Services

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `DAPR_HTTP_PORT` | Dapr sidecar HTTP port | `3500` |
| `APP_PORT` | Worker HTTP server port | `8001` (reminder), `8002` (recurrence) |

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Event Publication                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Backend API                     Dapr Sidecar                  Redpanda     │
│  ┌─────────┐                    ┌───────────┐                ┌───────────┐  │
│  │         │  HTTP POST         │           │  Kafka Proto   │           │  │
│  │ EventBus│───────────────────▶│ daprd     │───────────────▶│  Topic:   │  │
│  │ .emit() │  /v1.0/publish/    │           │                │  tasks    │  │
│  │         │  taskpubsub/tasks  │           │                │           │  │
│  └─────────┘                    └───────────┘                └───────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              Event Consumption                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Redpanda          Dapr Sidecar                 Worker Service              │
│  ┌───────────┐    ┌───────────┐                ┌────────────────┐           │
│  │           │    │           │  HTTP POST     │                │           │
│  │  Topic:   │───▶│ daprd     │───────────────▶│ /events/...    │           │
│  │  tasks    │    │           │  (to worker)   │                │           │
│  │           │    │           │                │ Process event  │           │
│  └───────────┘    └───────────┘                └────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Validation Rules

### Event Payload Validation

All events are validated using Python dataclasses (existing models in `backend/src/events/models.py`). No changes needed.

### Dapr Component Validation

Dapr validates component YAML at sidecar startup. Invalid components cause sidecar to fail with clear error messages.

### Topic Auto-Creation

Redpanda auto-creates topics on first publish. No manual topic creation required for local dev.
