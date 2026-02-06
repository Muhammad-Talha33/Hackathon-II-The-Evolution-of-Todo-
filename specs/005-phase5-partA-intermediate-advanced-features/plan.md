# Implementation Plan: Phase V Part A - Intermediate & Advanced Task Features

**Branch**: `005-phase5-partA-intermediate-advanced-features` | **Date**: 2026-02-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/005-phase5-partA-intermediate-advanced-features/spec.md`

## Summary

Extend the existing FastAPI backend with 7 new task fields, 2 new enums, filtering/sorting/search on `GET /tasks`, recurring task generation on completion, a reminder-check endpoint, and 6 domain event definitions emitted through an in-process event bus. No infrastructure, deployment, or frontend UI changes.

**Strategy**: Bottom-up layered implementation:
1. Data layer first (model + enums + migration)
2. Event layer (definitions + bus)
3. Schema layer (request/response Pydantic models)
4. Service layer (recurrence logic, reminder check)
5. Router layer (filter/sort/search params, event emission, new endpoint)
6. Frontend type sync (api.ts only)

## Technical Context

**Backend**:
- Language: Python 3.11+
- Framework: FastAPI with async SQLAlchemy
- ORM: SQLModel (SQLAlchemy + Pydantic hybrid)
- Database: Neon PostgreSQL (cloud-hosted, supports `ARRAY`, `ILIKE`)
- Auth: JWT via `get_current_user` dependency
- Table creation: `SQLModel.metadata.create_all` in `database.py:38-41`

**Frontend** (minimal touch):
- Framework: Next.js + TypeScript
- Only file: `frontend/lib/api.ts` (type definitions)

**Existing Code Footprint**:
- Model: `backend/src/models/task.py` (38 lines, 2 fields + status enum)
- Schemas: `backend/src/schemas/task.py` (52 lines, TaskCreate/TaskUpdate/TaskResponse)
- Router: `backend/src/routers/tasks.py` (232 lines, 6 endpoints)
- MCP Tools: `backend/src/mcp_server/tools/task_tools.py` (249 lines, 5 sync functions)
- Models init: `backend/src/models/__init__.py` (exports Task, TaskStatus)

**Constraints**:
- No Kafka, Dapr, Redis, Kubernetes, or deployment changes
- Existing Docker structure (`docker/frontend`, `docker/backend`) untouched
- Backward compatible: existing API callers must not break
- No new Python packages (SQLAlchemy, Pydantic, dataclasses all available)

## Constitution Check

| Principle | Phase V-A Compliance |
|-----------|---------------------|
| **I. In-Memory Task Management** | NOT APPLICABLE (Phase III+ uses PostgreSQL) |
| **II. Separation of Concerns** | COMPLIANT: Events module is isolated from router logic; recurrence is a service function, not inline |
| **III. Input Validation** | COMPLIANT: All new fields validated via Pydantic schemas; tag format enforced; recurrence requires due_at |
| **IV. Deterministic Behavior** | COMPLIANT: Recurrence date math is explicit; overdue is computed from UTC now; events are logged deterministically |
| **V. Code Quality** | COMPLIANT: Type hints on all new code; enum-driven priorities; no magic strings |

---

## Architecture Decisions

### Decision 1: Tags as PostgreSQL ARRAY column (not a join table)

**Options considered**:
- (A) `ARRAY(String)` column on `tasks` table
- (B) Separate `task_tags` join table

**Choice**: Option A

**Rationale**: The spec confirms tags are simple string labels with no metadata (no tag descriptions, colors, or shared tags). PostgreSQL `ARRAY` supports `ANY()` for filtering, which covers FR-020. A join table adds unnecessary complexity for this scale. If tag requirements grow, migration to a join table is a future concern.

**Trade-off**: Cannot query "all unique tags across all tasks" efficiently. Acceptable for Part A.

### Decision 2: In-process EventBus using Python list + logging (not external broker)

**Options considered**:
- (A) Simple Python class with `list[Event]` and `logging.info()`
- (B) asyncio.Queue-based consumer pattern
- (C) Noop stub (just the dataclass definitions, no actual emit)

**Choice**: Option A

**Rationale**: The spec requires events to be "emitted" and "retrievable for testing" (SC-012). A simple list + logger satisfies both. asyncio.Queue adds complexity for no current consumer. A noop stub doesn't satisfy the testability requirement. The EventBus interface (`emit(event)`) is the seam for Phase V Part B Dapr migration -- only the internal implementation changes.

**Trade-off**: Events accumulate in memory if not cleared. Acceptable since there are no consumers yet and the list is per-process.

### Decision 3: Recurrence logic as a standalone service function (not inline in router)

**Options considered**:
- (A) Inline in `toggle_task_complete` handler
- (B) Separate `services/recurrence.py` module
- (C) Part of EventBus (event-triggered generation)

**Choice**: Option B

**Rationale**: Separation of concerns. The router handler should toggle status, then call `generate_next_recurring_task()`. This keeps the handler readable and the recurrence logic independently testable. Option C is premature -- event-triggered generation is a Phase V Part B pattern.

### Decision 4: Overdue as a computed filter (not a stored status)

**Options considered**:
- (A) Add `OVERDUE` to `TaskStatus` enum
- (B) Compute overdue at query time: `status == incomplete AND due_at < now AND due_at IS NOT NULL`

**Choice**: Option B

**Rationale**: Overdue is time-dependent. Storing it as a status would require a background job to keep it in sync. Computing at query time is accurate, simpler, and requires no scheduled work. The spec explicitly defines overdue as a filter (FR-019), not a status enum value.

### Decision 5: Priority sort using SQL CASE expression

**Options considered**:
- (A) Store priority as integer (1/2/3) and sort numerically
- (B) Store as enum string and use SQL `CASE` for ordering

**Choice**: Option B

**Rationale**: The spec requires the enum values `low`, `medium`, `high` in the API contract. Storing as integer would require constant translation. SQL `CASE WHEN priority = 'high' THEN 1 WHEN priority = 'medium' THEN 2 ELSE 3 END` provides correct ordering while keeping the stored value human-readable. This is a standard PostgreSQL pattern with negligible performance cost.

### Decision 6: Database migration via `create_all` with column defaults (no Alembic)

**Options considered**:
- (A) Alembic migration scripts
- (B) Manual `ALTER TABLE` SQL
- (C) SQLModel `create_all` (adds new columns if table exists with correct defaults)

**Choice**: Option B as primary, with C for development

**Rationale**: The project does not currently use Alembic. Introducing it for 7 columns is over-engineering for Part A. A single `ALTER TABLE` migration script is explicit and auditable. `create_all` handles new column addition in dev. The migration SQL is provided in the plan for production use.

---

## Module Breakdown

### Layer 1: Data Model (`backend/src/models/task.py`)

**Current state** (38 lines): `TaskStatus` enum + `Task` model with 7 fields.

**Changes**:
- Add `Priority` enum: `LOW = "low"`, `MEDIUM = "medium"`, `HIGH = "high"`
- Add `RecurrencePattern` enum: `DAILY = "daily"`, `WEEKLY = "weekly"`, `MONTHLY = "monthly"`
- Add 7 new columns to `Task`:
  - `priority: str` with default `Priority.MEDIUM` (stored as string enum)
  - `tags: List[str]` using `Column(ARRAY(String))` from `sqlalchemy.dialects.postgresql`
  - `due_at: Optional[datetime]` nullable
  - `remind_at: Optional[datetime]` nullable
  - `reminder_sent: bool` default `False`
  - `recurrence_pattern: Optional[str]` nullable (stored as string enum)
  - `parent_task_id: Optional[UUID]` FK to `tasks.id`, nullable

**FR coverage**: FR-001 through FR-007

**Code reference**: `backend/src/models/task.py:10-37`

### Layer 2: Events Module (`backend/src/events/`)

**New files**:

#### `backend/src/events/__init__.py`
Exports: `EventBus`, `get_event_bus`, all event classes.

#### `backend/src/events/models.py`
Six `@dataclass` classes, each with:
- `event_type: str` (class-level constant)
- `timestamp: datetime` (auto-set to `utcnow()`)
- Payload fields per spec event definitions

```
TaskCreatedEvent:    task_id, user_id, title, priority, tags, due_at, recurrence_pattern, created_at
TaskUpdatedEvent:    task_id, user_id, updated_fields, updated_at
TaskCompletedEvent:  task_id, user_id, title, completed_at, had_recurrence, was_overdue
TaskDeletedEvent:    task_id, user_id, title, deleted_at
TaskReminderDueEvent: task_id, user_id, title, remind_at, due_at
RecurringTaskGeneratedEvent: new_task_id, parent_task_id, user_id, title, next_due_at, recurrence_pattern
```

#### `backend/src/events/bus.py`
```python
class EventBus:
    def __init__(self):
        self._events: list = []
        self._logger = logging.getLogger("events")

    def emit(self, event) -> None:
        self._events.append(event)
        self._logger.info(f"Event emitted: {event.event_type} | {event}")

    def get_events(self) -> list:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()
```

FastAPI dependency:
```python
_bus = EventBus()

def get_event_bus() -> EventBus:
    return _bus
```

**FR coverage**: FR-030, FR-031, FR-032

### Layer 3: Schemas (`backend/src/schemas/task.py`)

**Current state** (52 lines): `TaskCreate` (title, description), `TaskUpdate` (title, description), `TaskResponse` (all current fields).

**Changes**:

#### `TaskCreate` (extends)
Add optional fields:
- `due_at: Optional[datetime] = None`
- `remind_at: Optional[datetime] = None`
- `priority: Optional[str] = "medium"` with Pydantic validator constraining to `low|medium|high`
- `tags: Optional[List[str]] = []` with per-item validator (1-50 chars, alphanumeric + hyphens)
- `recurrence_pattern: Optional[str] = None` with validator constraining to `daily|weekly|monthly|null`

Add model-level validator: if `recurrence_pattern` is set, `due_at` must also be set (FR-012).
Add tag deduplication in validator.

#### `TaskUpdate` (extends)
Same optional fields as `TaskCreate`. Same validators.

#### `TaskResponse` (extends)
Add:
- `due_at: Optional[datetime]`
- `remind_at: Optional[datetime]`
- `reminder_sent: bool`
- `priority: str`
- `tags: List[str]`
- `recurrence_pattern: Optional[str]`
- `parent_task_id: Optional[UUID]`

**FR coverage**: FR-027, FR-028, FR-029

### Layer 4: Services (`backend/src/services/`)

#### `backend/src/services/recurrence.py` (new)

Single function:
```python
def compute_next_due_date(current_due: datetime, pattern: str) -> datetime:
    """Compute the next due date based on recurrence pattern."""
```

Logic:
- `daily`: `current_due + timedelta(days=1)`
- `weekly`: `current_due + timedelta(days=7)`
- `monthly`: Add 1 month using `calendar.monthrange` for month-end handling. If current day > last day of target month, clamp to last day.

Single function:
```python
async def generate_next_recurring_task(
    completed_task: Task, db: AsyncSession, event_bus: EventBus
) -> Optional[Task]:
    """If the task has recurrence, create the next instance and emit RecurringTaskGenerated."""
```

Logic:
1. Check `completed_task.recurrence_pattern is not None`
2. Compute `next_due = compute_next_due_date(completed_task.due_at, completed_task.recurrence_pattern)`
3. Compute `next_remind_at` if original had `remind_at` (preserve the offset: `remind_at - due_at + next_due`)
4. Create new `Task` copying title, description, priority, tags, recurrence_pattern, user_id
5. Set `parent_task_id = completed_task.id`, `status = INCOMPLETE`, `due_at = next_due`, `remind_at = next_remind_at`
6. Persist, emit `RecurringTaskGeneratedEvent`, return new task
7. On failure: log error, return None (FR reliability requirement)

**FR coverage**: FR-008 through FR-012

#### `backend/src/services/reminders.py` (new)

Single function:
```python
async def check_and_emit_reminders(
    user_id: UUID, db: AsyncSession, event_bus: EventBus
) -> List[Task]:
    """Find due reminders, emit events, mark reminder_sent=True."""
```

Logic:
1. Query: `WHERE user_id = :uid AND remind_at <= now() AND reminder_sent = false AND status != 'complete'`
2. For each matching task: emit `TaskReminderDueEvent`, set `reminder_sent = True`
3. Commit, return list of affected tasks

**FR coverage**: FR-013, FR-014

### Layer 5: Router (`backend/src/routers/tasks.py`)

**Current state** (232 lines): 6 endpoints, simple CRUD, no query params on GET.

**Changes to `get_tasks`** (currently line 17-38):

Add query parameters:
```python
async def get_tasks(
    status: Optional[str] = None,       # FR-018: incomplete|complete|overdue
    priority: Optional[str] = None,     # FR-021: low|medium|high
    tag: Optional[str] = None,          # FR-020: filter by tag
    q: Optional[str] = None,            # FR-015: search title/description
    sort_by: Optional[str] = "created_at",  # FR-022: created_at|due_date|priority
    order: Optional[str] = "desc",      # FR-024: asc|desc
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
```

Query building logic:
1. Base: `SELECT * FROM tasks WHERE user_id = :uid`
2. If `status == "incomplete"`: `AND status = 'incomplete'`
3. If `status == "complete"`: `AND status = 'complete'`
4. If `status == "overdue"`: `AND status = 'incomplete' AND due_at < now() AND due_at IS NOT NULL` (FR-019)
5. If `priority`: `AND priority = :priority`
6. If `tag`: `AND :tag = ANY(tags)` (PostgreSQL array contains)
7. If `q`: `AND (title ILIKE '%q%' OR description ILIKE '%q%')` (FR-017)
8. Sort:
   - `sort_by == "created_at"`: `ORDER BY created_at`
   - `sort_by == "due_date"`: `ORDER BY due_at NULLS LAST` (asc) or `NULLS FIRST` (desc) (FR-026)
   - `sort_by == "priority"`: `ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END`
9. Direction: `ASC` or `DESC` based on `order` param

**FR coverage**: FR-015 through FR-026

**Changes to `create_task`** (currently line 41-72):

- Read new fields from `TaskCreate` schema: `due_at`, `remind_at`, `priority`, `tags`, `recurrence_pattern`
- Pass them to `Task()` constructor
- After commit: emit `TaskCreatedEvent` via `EventBus`

**Changes to `update_task`** (currently line 109-154):

- Read new fields from `TaskUpdate` schema
- Track which fields changed (for `TaskUpdatedEvent.updated_fields`)
- Update only provided fields
- After commit: emit `TaskUpdatedEvent`

**Changes to `delete_task`** (currently line 157-187):

- Capture task title and user_id before deletion
- After commit: emit `TaskDeletedEvent`

**Changes to `toggle_task_complete`** (currently line 189-231):

- After toggling to COMPLETE:
  - Determine `was_overdue`: `task.due_at is not None and task.due_at < utcnow() and task.status was INCOMPLETE`
  - Emit `TaskCompletedEvent`
  - Call `generate_next_recurring_task()` (FR-008)
- After toggling to INCOMPLETE:
  - Emit `TaskUpdatedEvent` (status field changed)
- Event emission and recurrence generation are wrapped in try/except (reliability requirement)

**New endpoint: `POST /tasks/check-reminders`**:

```python
@router.post("/check-reminders", response_model=List[TaskResponse])
async def check_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
):
```

Calls `check_and_emit_reminders(current_user.id, db, event_bus)`.

**FR coverage**: FR-030 through FR-032

### Layer 6: Models Init & Main

**`backend/src/models/__init__.py`** (currently line 1-7):
- Add exports: `Priority`, `RecurrencePattern`

**`backend/src/main.py`** (no changes needed):
- Router is already mounted at `/tasks`. New endpoints are part of the same router.

### Layer 7: MCP Tools Awareness (`backend/src/mcp_server/tools/task_tools.py`)

**Current state**: 5 sync functions using `Session` (not `AsyncSession`). They create/list/complete/delete/update tasks.

**Changes** (minimal, backward compatible):
- `add_task`: Accept optional `priority`, `due_at`, `tags` params. Pass through to `Task()` constructor. Existing calls without these params still work.
- `list_tasks`: Include new fields in response dictionaries (`priority`, `tags`, `due_at`, etc.)
- `complete_task`: No recurrence logic here (MCP tools are sync; recurrence service is async). The MCP `complete_task` sets status only. Recurrence is handled by the async API route.
- `update_task`: Accept optional `priority`, `due_at`, `remind_at`, `tags`, `recurrence_pattern` params.

**FR coverage**: Maintains feature parity between REST API and MCP tools (where applicable).

### Layer 8: Frontend Types (`frontend/lib/api.ts`)

**Changes to existing interfaces**:

```typescript
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: 'incomplete' | 'complete';
  priority: 'low' | 'medium' | 'high';          // NEW
  tags: string[];                                  // NEW
  due_at: string | null;                           // NEW
  remind_at: string | null;                        // NEW
  reminder_sent: boolean;                          // NEW
  recurrence_pattern: 'daily' | 'weekly' | 'monthly' | null;  // NEW
  parent_task_id: string | null;                   // NEW
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';           // NEW
  tags?: string[];                                  // NEW
  due_at?: string;                                  // NEW
  remind_at?: string;                               // NEW
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly';  // NEW
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';           // NEW
  tags?: string[];                                  // NEW
  due_at?: string;                                  // NEW
  remind_at?: string;                               // NEW
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | null;  // NEW
}
```

**New method on `ApiClient`**:
```typescript
async checkReminders(accessToken: string): Promise<Task[]> {
  return this.request<Task[]>('/tasks/check-reminders', {
    method: 'POST',
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}
```

**Update `getTasks`** to accept optional query params:
```typescript
async getTasks(
  accessToken: string,
  params?: { status?: string; priority?: string; tag?: string; q?: string; sort_by?: string; order?: string }
): Promise<Task[]>
```

Build query string from params object. Existing callers pass no params, which preserves default behavior.

**FR coverage**: FR-029, SC-014

---

## Database Migration

The following SQL adds all 7 new columns with defaults that do not break existing rows:

```sql
-- Add new columns to tasks table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(6) NOT NULL DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS remind_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(7);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL;
```

This is run once against the Neon database. `create_all` in dev will handle new columns from SQLModel metadata.

---

## Data Flow Diagrams

### Flow 1: Create Task with New Fields

```
Client POST /tasks {title, priority, tags, due_at, recurrence_pattern}
  → TaskCreate schema validates (Pydantic)
  → Router: create Task model instance with all fields
  → DB: INSERT INTO tasks (...)
  → Router: event_bus.emit(TaskCreatedEvent)
  → Return TaskResponse (all fields)
```

### Flow 2: Complete Recurring Task

```
Client PATCH /tasks/{id}/complete
  → Router: load task, verify ownership
  → Toggle status to COMPLETE
  → DB: UPDATE tasks SET status='complete'
  → event_bus.emit(TaskCompletedEvent)
  → generate_next_recurring_task(task, db, event_bus)
      → compute_next_due_date(due_at, pattern)
      → create new Task (INCOMPLETE, next due_at, copied fields)
      → DB: INSERT INTO tasks (...)
      → event_bus.emit(RecurringTaskGeneratedEvent)
  → Return original TaskResponse (completed)
```

### Flow 3: Get Tasks with Filter + Sort + Search

```
Client GET /tasks?status=overdue&sort_by=due_date&order=asc&q=report
  → Router: build SQLAlchemy query
      → WHERE user_id = :uid
      → AND status = 'incomplete' AND due_at < now() AND due_at IS NOT NULL  (overdue)
      → AND (title ILIKE '%report%' OR description ILIKE '%report%')         (search)
      → ORDER BY due_at ASC NULLS LAST                                       (sort)
  → DB: execute query
  → Return List[TaskResponse]
```

### Flow 4: Check Reminders

```
Client POST /tasks/check-reminders
  → Router: call check_and_emit_reminders(user_id, db, event_bus)
      → Query: remind_at <= now() AND reminder_sent = false AND status != 'complete'
      → For each: emit TaskReminderDueEvent, set reminder_sent = true
      → DB: UPDATE tasks SET reminder_sent = true
  → Return List[TaskResponse] (affected tasks)
```

---

## Implementation Order (Dependency Chain)

The implementation must follow this dependency order:

```
Phase 0: Database migration SQL
    ↓
Phase 1: Models (enums + task fields)
    ↓
Phase 2: Events module (dataclasses + bus)
    ↓
Phase 3: Schemas (create/update/response)
    ↓
Phase 4: Services (recurrence + reminders)
    ↓
Phase 5: Router updates (filter/sort/search + event emission + new endpoint)
    ↓
Phase 6: MCP tools update
    ↓
Phase 7: Frontend types (api.ts)
    ↓
Phase 8: Integration verification
```

Each phase depends only on the one above it. Phases within a layer can be parallelized (e.g., recurrence service and reminder service can be built simultaneously).

---

## File Change Summary

### Files to Create (3)

| File | Purpose | Lines (est.) |
|------|---------|-------------|
| `backend/src/events/__init__.py` | Package init, re-exports | ~10 |
| `backend/src/events/models.py` | 6 event dataclasses | ~80 |
| `backend/src/events/bus.py` | EventBus class + DI dependency | ~35 |
| `backend/src/services/recurrence.py` | Next-due-date computation + recurring task generation | ~70 |
| `backend/src/services/reminders.py` | Reminder check + event emission | ~40 |

### Files to Modify (6)

| File | Current Lines | Change Description |
|------|--------------|-------------------|
| `backend/src/models/task.py` | 38 | Add 2 enums, 7 columns (~30 lines added) |
| `backend/src/models/__init__.py` | 7 | Add Priority, RecurrencePattern exports (~2 lines) |
| `backend/src/schemas/task.py` | 52 | Extend 3 schemas + validators (~60 lines added) |
| `backend/src/routers/tasks.py` | 232 | Query params, event emission, new endpoint (~120 lines added) |
| `backend/src/mcp_server/tools/task_tools.py` | 249 | Add new field params + response fields (~40 lines changed) |
| `frontend/lib/api.ts` | 213 | Update 3 interfaces, add method + query params (~30 lines changed) |

### Files Unchanged

- `backend/src/main.py` -- No new routers needed
- `backend/src/database.py` -- No changes
- `backend/src/config.py` -- No new env vars
- `backend/src/dependencies/auth.py` -- No changes
- `docker/` -- Untouched
- `k8s/`, `helm/` -- Untouched

---

## Risk Analysis

### Risk 1: PostgreSQL ARRAY type compatibility with SQLModel

**Likelihood**: Low
**Impact**: Medium (would block tags feature)
**Mitigation**: SQLModel supports SQLAlchemy `Column()` override, which is already used for `user_id` FK in the current model. Use `sa_column=Column(ARRAY(String))` for tags. This is a proven pattern.

### Risk 2: Monthly recurrence date math edge cases

**Likelihood**: Medium (month boundaries are tricky)
**Impact**: Low (incorrect next date, easily correctable)
**Mitigation**: Use Python `calendar.monthrange` for last-day-of-month detection. Explicitly test: Jan 31 → Feb 28, Jan 29 → Feb 28 (non-leap), Jan 29 → Feb 29 (leap), Feb 28 → Mar 28.

### Risk 3: Event bus memory growth in long-running processes

**Likelihood**: Low (no consumers yet, low event volume)
**Impact**: Low (memory grows slowly with events)
**Mitigation**: EventBus has `clear()` method. For Phase V Part A, this is a non-issue since events are only for logging/testing. In Part B, the bus will be replaced with Dapr pub/sub.

---

## Validation Checklist

- [ ] All 7 new fields persist and round-trip through the API
- [ ] `POST /tasks` without new fields still works (backward compat)
- [ ] `GET /tasks` without query params returns same results as before
- [ ] `status=overdue` filter returns correct results
- [ ] `tag=work` filter returns only matching tasks
- [ ] `sort_by=priority` orders high > medium > low
- [ ] `sort_by=due_date` with nulls-last behavior
- [ ] `q=term` searches title and description case-insensitively
- [ ] Completing a daily recurring task creates next-day instance
- [ ] Completing a monthly recurring task handles month-end
- [ ] Completing a non-recurring task generates no new task
- [ ] `POST /tasks/check-reminders` finds due reminders and sets `reminder_sent`
- [ ] All 6 events are emitted at correct trigger points
- [ ] EventBus logs events and supports `get_events()`
- [ ] Frontend `api.ts` types match backend response schema
- [ ] MCP tools include new fields in responses
- [ ] No regressions on existing CRUD operations
