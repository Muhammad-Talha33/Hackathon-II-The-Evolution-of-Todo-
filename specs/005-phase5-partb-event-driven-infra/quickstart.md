# Quickstart: Phase V Part B - Event-Driven Infrastructure

**Feature**: `005-phase5-partb-event-driven-infra`
**Date**: 2026-02-06

---

## Prerequisites

Before starting Phase V Part B implementation:

### Required Tools

- **Docker Desktop** 4.x+ with Docker Compose v2
- **Python 3.11+** (for local development/testing)
- **Git** (for version control)

### Existing Setup (from Phase V Part A)

- Backend with domain events (`backend/src/events/`)
- Frontend (unchanged)
- Neon PostgreSQL database
- `.env` file with database credentials

---

## Quick Setup

### 1. Start the Event-Driven Stack

```bash
# From repository root
docker-compose -f docker-compose.dapr.yml up -d
```

This starts:
- Redpanda (Kafka-compatible broker)
- Backend + Dapr sidecar
- Frontend
- Reminder Worker + Dapr sidecar
- Recurrence Worker + Dapr sidecar
- Redis (optional state store)

### 2. Verify Services

```bash
# Check all containers are running
docker-compose -f docker-compose.dapr.yml ps

# Expected output:
# NAME                   STATUS
# todo-backend           running (healthy)
# todo-backend-dapr      running
# todo-frontend          running (healthy)
# redpanda               running (healthy)
# reminder-worker        running (healthy)
# reminder-worker-dapr   running
# recurrence-worker      running (healthy)
# recurrence-worker-dapr running
```

### 3. Access Services

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Redpanda Console | http://localhost:8080 |

---

## Verify Event Flow

### 1. Create a Task

```bash
# Sign in first (use existing account or create one via frontend)
TOKEN="your-jwt-token"

curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test event flow",
    "priority": "high"
  }'
```

### 2. Check Redpanda Console

1. Open http://localhost:8080
2. Navigate to Topics → `tasks`
3. View Messages tab
4. You should see a `TaskCreated` event

### 3. Check Worker Logs

```bash
# Reminder worker logs
docker logs reminder-worker -f

# Recurrence worker logs
docker logs recurrence-worker -f
```

---

## Test Reminder Flow

### 1. Create Task with Past Reminder

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Reminder test",
    "remind_at": "2026-02-01T00:00:00Z"
  }'
```

### 2. Trigger Reminder Check

The cron binding triggers automatically every minute. Or manually:

```bash
curl -X POST http://localhost:8000/tasks/check-reminders \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Verify Worker Received Event

```bash
docker logs reminder-worker | grep "Reminder delivered"
# Expected: [ReminderWorker] Delivered reminder for task xxx: Reminder test
```

---

## Test Recurrence Flow

### 1. Create Recurring Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily standup",
    "due_at": "2026-02-06T09:00:00Z",
    "recurrence_pattern": "daily"
  }'
```

### 2. Complete the Task

```bash
TASK_ID="<task-id-from-response>"
curl -X PATCH http://localhost:8000/tasks/$TASK_ID/complete \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Verify Next Task Created

```bash
# List tasks - should see original (complete) and new instance (incomplete)
curl http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Troubleshooting

### Dapr Sidecar Not Starting

```bash
# Check sidecar logs
docker logs todo-backend-dapr

# Common issues:
# - Component YAML syntax errors
# - Redpanda not reachable (check network)
```

### Events Not Appearing in Redpanda

```bash
# Verify pub/sub component loaded
docker exec todo-backend-dapr \
  curl http://localhost:3500/v1.0/metadata | jq .components

# Check backend logs for publish errors
docker logs todo-backend | grep "Failed to publish"
```

### Workers Not Processing Events

```bash
# Check worker subscription
docker exec reminder-worker \
  curl http://localhost:8001/dapr/subscribe | jq

# Check Dapr sidecar delivery
docker logs reminder-worker-dapr | grep "event"
```

### Redpanda Console Not Loading

```bash
# Verify Redpanda is healthy
docker logs redpanda | tail -20

# Check port binding
docker port redpanda
```

---

## Stop the Stack

```bash
docker-compose -f docker-compose.dapr.yml down

# To also remove volumes (clean slate)
docker-compose -f docker-compose.dapr.yml down -v
```

---

## Development Workflow

### Modify Backend Event Publishing

1. Edit `backend/src/events/bus.py`
2. Rebuild: `docker-compose -f docker-compose.dapr.yml build backend`
3. Restart: `docker-compose -f docker-compose.dapr.yml up -d backend`

### Modify Worker Logic

1. Edit `services/reminder-worker/main.py` or `services/recurrence-worker/main.py`
2. Rebuild: `docker-compose -f docker-compose.dapr.yml build reminder-worker`
3. Restart: `docker-compose -f docker-compose.dapr.yml up -d reminder-worker`

### Modify Dapr Components

1. Edit files in `dapr/components/`
2. Restart sidecars:
   ```bash
   docker-compose -f docker-compose.dapr.yml restart \
     todo-backend-dapr reminder-worker-dapr recurrence-worker-dapr
   ```

---

## Next Steps

After completing Phase V Part B:

1. Run existing test suite to verify zero regression
2. Manual smoke test of auth, CRUD, chatbot, MCP tools
3. Monitor Redpanda Console during testing
4. Document any issues in PHR
