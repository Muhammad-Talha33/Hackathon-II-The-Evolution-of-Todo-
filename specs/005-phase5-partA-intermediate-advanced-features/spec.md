# Feature Specification: Phase V Part A - Intermediate & Advanced Task Features

**Feature Branch**: `005-phase5-partA-intermediate-advanced-features`
**Created**: 2026-02-02
**Status**: Draft
**Input**: User description: "Implement all advanced and intermediate task management features AND define a clean event-driven contract (events only, no Kafka/Dapr wiring yet). Focus on application-level features and event definitions only."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recurring Tasks (Priority: P0)

As a user, I want to create tasks that repeat on a daily, weekly, or monthly schedule so that I do not have to manually re-create routine tasks.

**Why this priority**: Recurring tasks are a core differentiator from a basic todo app. Users with habits, routines, or periodic work need this to avoid repetitive task creation. This drives long-term engagement.

**Independent Test**: Create a recurring task with `recurrence_pattern: "daily"`. Complete it. Verify a new task instance is generated with the next due date. The original task remains complete; the new instance is incomplete.

**Acceptance Scenarios**:

1. **Given** I create a task with `recurrence_pattern: "daily"` and `due_at: "2026-02-03T09:00:00Z"`, **When** I complete the task, **Then** a new incomplete task is created with `due_at: "2026-02-04T09:00:00Z"` and the same title, description, priority, and tags.
2. **Given** I create a task with `recurrence_pattern: "weekly"` and `due_at: "2026-02-03"`, **When** I complete it, **Then** the next instance has `due_at: "2026-02-10"`.
3. **Given** I create a task with `recurrence_pattern: "monthly"` and `due_at: "2026-01-31"`, **When** I complete it, **Then** the next instance has `due_at: "2026-02-28"` (last day of February, not March 3rd).
4. **Given** I create a task with `recurrence_pattern: null`, **When** I complete it, **Then** no new task is generated.
5. **Given** a recurring task generates its next instance, **When** I query the new task, **Then** it has `parent_task_id` pointing to the original task and its own unique `id`.

---

### User Story 2 - Due Dates and Overdue Detection (Priority: P0)

As a user, I want to assign due dates to tasks and see which tasks are overdue so that I can prioritize urgent work.

**Why this priority**: Due dates are fundamental to task management. Without them, users cannot prioritize or plan. Overdue detection is a direct consequence that provides critical visibility.

**Independent Test**: Create a task with `due_at` in the past. Query tasks with `status=overdue` filter. Verify the task appears. Create a task with `due_at` in the future and verify it does not appear in the overdue filter.

**Acceptance Scenarios**:

1. **Given** I create a task with `due_at: "2026-02-01T12:00:00Z"` and the current time is `2026-02-02T00:00:00Z`, **When** I query tasks with `status=overdue`, **Then** this task is included in the results.
2. **Given** I create a task with `due_at: "2026-02-05T12:00:00Z"` and the current time is `2026-02-02T00:00:00Z`, **When** I query tasks with `status=overdue`, **Then** this task is NOT included.
3. **Given** I update a task to set `due_at: "2026-02-10T09:00:00Z"`, **When** I read the task back, **Then** `due_at` is persisted correctly.
4. **Given** a task has `due_at: null`, **When** I query with `status=overdue`, **Then** this task is NOT included (tasks without due dates are never overdue).
5. **Given** a task is overdue AND complete, **When** I query with `status=overdue`, **Then** this task is NOT included (completed tasks cannot be overdue).

---

### User Story 3 - Reminders (Priority: P1)

As a user, I want to set a reminder time on a task so that the system can alert me before a deadline.

**Why this priority**: Reminders complement due dates but are not blocking for core functionality. The system emits a `TaskReminderDue` event; the actual notification delivery is a future concern (Phase V Part B or later).

**Independent Test**: Create a task with `remind_at` in the past. Call the reminder check endpoint or service. Verify a `TaskReminderDue` event payload is returned/emitted for that task.

**Acceptance Scenarios**:

1. **Given** I create a task with `remind_at: "2026-02-02T08:00:00Z"`, **When** I read the task, **Then** `remind_at` is stored.
2. **Given** a task has `remind_at` in the past and `reminder_sent: false`, **When** the reminder check runs, **Then** a `TaskReminderDue` event is emitted and `reminder_sent` is set to `true`.
3. **Given** a task has `reminder_sent: true`, **When** the reminder check runs again, **Then** no duplicate event is emitted.
4. **Given** a task is completed, **When** the reminder check runs, **Then** no reminder event is emitted regardless of `remind_at`.

---

### User Story 4 - Priority Levels (Priority: P0)

As a user, I want to assign priority levels to tasks so that I can focus on the most important items first.

**Why this priority**: Priority is one of the simplest and most impactful features for task management. It directly enables sorting and filtering which are core UX requirements.

**Independent Test**: Create three tasks with priorities `high`, `medium`, `low`. Query tasks sorted by priority. Verify the order is high, medium, low.

**Acceptance Scenarios**:

1. **Given** I create a task with `priority: "high"`, **When** I read the task, **Then** `priority` is `"high"`.
2. **Given** I create a task without specifying `priority`, **When** I read the task, **Then** `priority` defaults to `"medium"`.
3. **Given** I update a task's priority from `"low"` to `"high"`, **When** I read the task, **Then** `priority` is `"high"`.
4. **Given** tasks exist with all three priority levels, **When** I query with `sort_by=priority`, **Then** tasks are ordered: high, medium, low.

---

### User Story 5 - Tags (Priority: P0)

As a user, I want to attach tags to tasks and filter by them so that I can organize tasks into categories.

**Why this priority**: Tags provide flexible categorization without rigid hierarchies. Combined with filtering, this is a high-value organizational feature.

**Independent Test**: Create a task with `tags: ["work", "urgent"]`. Query tasks with `tag=work`. Verify the tagged task appears. Query with `tag=personal`. Verify it does not appear.

**Acceptance Scenarios**:

1. **Given** I create a task with `tags: ["work", "urgent"]`, **When** I read the task, **Then** `tags` contains `["work", "urgent"]`.
2. **Given** a task has `tags: ["work", "urgent"]`, **When** I query with `tag=work`, **Then** the task is included.
3. **Given** a task has `tags: ["work"]`, **When** I query with `tag=personal`, **Then** the task is NOT included.
4. **Given** I update a task to set `tags: ["work", "meeting"]`, **When** I read the task, **Then** `tags` is `["work", "meeting"]` (previous tags replaced).
5. **Given** I create a task without tags, **When** I read it, **Then** `tags` is an empty list `[]`.

---

### User Story 6 - Search (Priority: P1)

As a user, I want to search tasks by title and description so that I can quickly find specific tasks.

**Why this priority**: Search is important for users with many tasks. It is a read-only operation that does not affect data integrity, making it lower risk but still valuable.

**Independent Test**: Create a task with title "Buy groceries" and description "milk and eggs". Search for "groceries". Verify the task is returned. Search for "milk". Verify the task is returned. Search for "laundry". Verify it is not returned.

**Acceptance Scenarios**:

1. **Given** a task exists with title "Buy groceries", **When** I search with `q=groceries`, **Then** the task is returned.
2. **Given** a task exists with description "milk and eggs", **When** I search with `q=milk`, **Then** the task is returned.
3. **Given** a task with title "Buy groceries", **When** I search with `q=buy`, **Then** the task is returned (case-insensitive).
4. **Given** no tasks match the query, **When** I search with `q=xyz123`, **Then** an empty list is returned.

---

### User Story 7 - Filter & Sort (Priority: P0)

As a user, I want to filter tasks by status and sort them by various fields so that I can view tasks in the order that matters to me.

**Why this priority**: Filtering and sorting are fundamental list management features. Without them, the task list becomes unusable at scale.

**Independent Test**: Create tasks with different statuses, due dates, and priorities. Apply filters and sort parameters. Verify correct ordering and filtering.

**Acceptance Scenarios**:

1. **Given** tasks exist with statuses `incomplete`, `complete`, and one overdue, **When** I filter with `status=incomplete`, **Then** only incomplete (non-overdue) tasks are returned.
2. **Given** tasks exist with statuses `incomplete`, `complete`, and one overdue, **When** I filter with `status=overdue`, **Then** only overdue tasks are returned.
3. **Given** tasks exist with statuses `incomplete`, `complete`, and one overdue, **When** I filter with `status=complete`, **Then** only completed tasks are returned.
4. **Given** tasks have different `due_at` values, **When** I sort with `sort_by=due_date&order=asc`, **Then** tasks are ordered by `due_at` ascending (nulls last).
5. **Given** tasks have different priorities, **When** I sort with `sort_by=priority&order=desc`, **Then** tasks are ordered high, medium, low.
6. **Given** tasks have different `created_at` values, **When** I sort with `sort_by=created_at&order=desc`, **Then** newest tasks appear first.
7. **Given** I combine filter and sort: `status=incomplete&sort_by=due_date&order=asc`, **When** the query executes, **Then** only incomplete tasks are returned, ordered by due date ascending.

---

### Edge Cases

- What happens when a recurring task has no `due_at`?
  - Recurrence requires `due_at`. The API returns a 422 validation error if `recurrence_pattern` is set but `due_at` is null.

- What happens when `remind_at` is after `due_at`?
  - This is allowed. The user may want a reminder after a deadline (e.g., follow-up). No validation prevents this.

- What happens when tags contain duplicates (`["work", "work"]`)?
  - Duplicates are silently deduplicated on save. The stored value will be `["work"]`.

- What happens when a monthly recurring task is due on Jan 31 and the next month is February?
  - The system uses the last day of the target month. Jan 31 -> Feb 28 (or Feb 29 in leap years).

- What happens when search query is empty?
  - An empty `q` parameter returns all tasks (no filtering applied).

- What happens when sorting by `due_date` and some tasks have `due_at: null`?
  - Tasks with null `due_at` are placed last in ascending order, first in descending order.

- What happens when a user tries to set an invalid priority?
  - The API returns a 422 validation error. Only `low`, `medium`, `high` are accepted.

- What happens when a tag name is empty or exceeds the limit?
  - Tags must be 1-50 characters, alphanumeric with hyphens. Invalid tags cause a 422 error.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Task Model Extensions

- **FR-001**: The Task model MUST support an optional `due_at` field (datetime, nullable). Default: `null`.
- **FR-002**: The Task model MUST support an optional `remind_at` field (datetime, nullable). Default: `null`.
- **FR-003**: The Task model MUST support a `reminder_sent` field (boolean). Default: `false`.
- **FR-004**: The Task model MUST support a `priority` field (enum: `low`, `medium`, `high`). Default: `medium`.
- **FR-005**: The Task model MUST support a `tags` field (list of strings). Default: empty list `[]`.
- **FR-006**: The Task model MUST support an optional `recurrence_pattern` field (enum: `daily`, `weekly`, `monthly`, or `null`). Default: `null`.
- **FR-007**: The Task model MUST support an optional `parent_task_id` field (UUID FK to tasks.id, nullable). Default: `null`. This links a generated recurring instance to its origin task.

#### Recurring Tasks

- **FR-008**: When a task with `recurrence_pattern != null` is completed, the system MUST generate a new task instance with the next logical `due_at`.
- **FR-009**: The generated task MUST copy `title`, `description`, `priority`, `tags`, `recurrence_pattern`, and `remind_at` offset from the parent task.
- **FR-010**: The generated task MUST have `status: incomplete`, a new UUID, and `parent_task_id` set to the completed task's ID.
- **FR-011**: Daily recurrence adds 1 day. Weekly adds 7 days. Monthly adds 1 calendar month (handling month-end edge cases).
- **FR-012**: If `recurrence_pattern` is set, `due_at` MUST also be set. The API MUST return 422 if `recurrence_pattern` is provided without `due_at`.

#### Reminders

- **FR-013**: The system MUST provide a mechanism (endpoint or service method) to check for tasks where `remind_at <= now` AND `reminder_sent == false` AND `status != complete`.
- **FR-014**: When a due reminder is detected, a `TaskReminderDue` event payload MUST be constructed and `reminder_sent` MUST be set to `true`.

#### Search

- **FR-015**: The `GET /tasks` endpoint MUST accept an optional `q` query parameter for full-text search.
- **FR-016**: Search MUST match against `title` and `description` fields, case-insensitive.
- **FR-017**: Search MUST use SQL `ILIKE` with `%query%` pattern matching.

#### Filtering

- **FR-018**: The `GET /tasks` endpoint MUST accept an optional `status` query parameter with values: `incomplete`, `complete`, `overdue`.
- **FR-019**: The `overdue` filter MUST return tasks where `status == incomplete` AND `due_at < now` AND `due_at IS NOT NULL`.
- **FR-020**: The `GET /tasks` endpoint MUST accept an optional `tag` query parameter that filters tasks containing the specified tag.
- **FR-021**: The `GET /tasks` endpoint MUST accept an optional `priority` query parameter (values: `low`, `medium`, `high`).

#### Sorting

- **FR-022**: The `GET /tasks` endpoint MUST accept optional `sort_by` and `order` query parameters.
- **FR-023**: Valid `sort_by` values: `created_at` (default), `due_date`, `priority`.
- **FR-024**: Valid `order` values: `asc`, `desc` (default: `desc`).
- **FR-025**: When sorting by `priority`, the order MUST be: `high` > `medium` > `low`.
- **FR-026**: When sorting by `due_date`, tasks with `null` `due_at` MUST appear last in ascending order.

#### API Schema Updates

- **FR-027**: `TaskCreate` schema MUST accept optional fields: `due_at`, `remind_at`, `priority`, `tags`, `recurrence_pattern`.
- **FR-028**: `TaskUpdate` schema MUST accept optional fields: `due_at`, `remind_at`, `priority`, `tags`, `recurrence_pattern`.
- **FR-029**: `TaskResponse` schema MUST include all new fields: `due_at`, `remind_at`, `reminder_sent`, `priority`, `tags`, `recurrence_pattern`, `parent_task_id`.

#### Event-Driven Contract

- **FR-030**: The system MUST define and emit conceptual domain events at the application layer. Events are represented as Python dataclasses or Pydantic models in a dedicated `events/` module.
- **FR-031**: Events MUST NOT trigger external service calls. They are recorded in-process for future infrastructure wiring.
- **FR-032**: The following events MUST be defined with trigger conditions and payload schemas:
  - `TaskCreated` - emitted after a task is persisted
  - `TaskUpdated` - emitted after a task's fields are modified
  - `TaskCompleted` - emitted after a task's status changes to `complete`
  - `TaskDeleted` - emitted after a task is removed
  - `TaskReminderDue` - emitted when a reminder check finds due reminders
  - `RecurringTaskGenerated` - emitted after a new recurring task instance is created

---

## Event-Driven Contract *(mandatory for this feature)*

### Event Definitions

#### 1. TaskCreated

| Field | Description |
|-------|-------------|
| **Event Name** | `TaskCreated` |
| **Trigger** | After a new task is successfully persisted to the database |
| **Payload** | `task_id: UUID`, `user_id: UUID`, `title: str`, `priority: str`, `tags: list[str]`, `due_at: datetime | null`, `recurrence_pattern: str | null`, `created_at: datetime` |
| **Future Consumer** | Notification Service (welcome/confirmation), Analytics Service |

#### 2. TaskUpdated

| Field | Description |
|-------|-------------|
| **Event Name** | `TaskUpdated` |
| **Trigger** | After any task field is modified (title, description, due_at, priority, tags, remind_at, recurrence_pattern) |
| **Payload** | `task_id: UUID`, `user_id: UUID`, `updated_fields: list[str]`, `updated_at: datetime` |
| **Future Consumer** | Sync Service, Analytics Service |

#### 3. TaskCompleted

| Field | Description |
|-------|-------------|
| **Event Name** | `TaskCompleted` |
| **Trigger** | After a task's status changes from `incomplete` to `complete` |
| **Payload** | `task_id: UUID`, `user_id: UUID`, `title: str`, `completed_at: datetime`, `had_recurrence: bool`, `was_overdue: bool` |
| **Future Consumer** | Gamification Service, Analytics Service, Recurring Task Generator |

#### 4. TaskDeleted

| Field | Description |
|-------|-------------|
| **Event Name** | `TaskDeleted` |
| **Trigger** | After a task is removed from the database |
| **Payload** | `task_id: UUID`, `user_id: UUID`, `title: str`, `deleted_at: datetime` |
| **Future Consumer** | Analytics Service, Cleanup Service |

#### 5. TaskReminderDue

| Field | Description |
|-------|-------------|
| **Event Name** | `TaskReminderDue` |
| **Trigger** | When a reminder check finds tasks where `remind_at <= now` AND `reminder_sent == false` AND `status != complete` |
| **Payload** | `task_id: UUID`, `user_id: UUID`, `title: str`, `remind_at: datetime`, `due_at: datetime | null` |
| **Future Consumer** | Notification Service (email, push, in-app) |

#### 6. RecurringTaskGenerated

| Field | Description |
|-------|-------------|
| **Event Name** | `RecurringTaskGenerated` |
| **Trigger** | After a new task instance is created from a completed recurring task |
| **Payload** | `new_task_id: UUID`, `parent_task_id: UUID`, `user_id: UUID`, `title: str`, `next_due_at: datetime`, `recurrence_pattern: str` |
| **Future Consumer** | Notification Service, Calendar Sync Service |

### Event Architecture Rules

1. Events are **conceptual only** at this stage. They are defined as Python dataclasses in `backend/src/events/`.
2. An `EventBus` class provides a simple in-process `emit(event)` method that logs the event and stores it in a list (for testing/debugging).
3. No Kafka topics, no Dapr pub/sub, no external message brokers.
4. The event bus is injected into route handlers via FastAPI dependency injection.
5. In Phase V Part B, the `EventBus.emit()` will be replaced with Dapr/Kafka publishing without changing the call sites.

---

## Key Entities *(mandatory)*

### Updated Task Model

```
Task:
  id: UUID (PK, auto-generated)
  user_id: UUID (FK -> users.id, CASCADE)
  title: str (1-500 chars, required)
  description: str | null
  status: TaskStatus (incomplete | complete, default: incomplete)
  priority: Priority (low | medium | high, default: medium)        # NEW
  tags: list[str] (default: [])                                     # NEW
  due_at: datetime | null (default: null)                           # NEW
  remind_at: datetime | null (default: null)                        # NEW
  reminder_sent: bool (default: false)                              # NEW
  recurrence_pattern: RecurrencePattern | null (default: null)      # NEW
  parent_task_id: UUID | null (FK -> tasks.id, default: null)       # NEW
  created_at: datetime (auto)
  updated_at: datetime (auto)
```

### New Enums

```
Priority:
  LOW = "low"
  MEDIUM = "medium"
  HIGH = "high"

RecurrencePattern:
  DAILY = "daily"
  WEEKLY = "weekly"
  MONTHLY = "monthly"
```

### Domain Events

```
backend/src/events/
  __init__.py
  models.py       # Event dataclasses (TaskCreated, TaskUpdated, etc.)
  bus.py           # EventBus with in-process emit + log
```

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 7 new task fields are persisted and retrievable via the API.
- **SC-002**: Creating a task with `priority`, `tags`, `due_at`, `remind_at`, and `recurrence_pattern` returns a response containing all fields.
- **SC-003**: Completing a recurring task generates a new instance with the correct next `due_at`.
- **SC-004**: Monthly recurrence from Jan 31 correctly produces Feb 28 (non-leap) or Feb 29 (leap year).
- **SC-005**: Filtering by `status=overdue` returns only incomplete tasks with `due_at` in the past.
- **SC-006**: Filtering by `tag=<value>` returns only tasks containing that tag.
- **SC-007**: Sorting by `priority` orders tasks as high > medium > low.
- **SC-008**: Sorting by `due_date` places null-due-date tasks last (ascending).
- **SC-009**: Search with `q=<term>` matches title and description case-insensitively.
- **SC-010**: The reminder check identifies due reminders, emits `TaskReminderDue`, and sets `reminder_sent=true`.
- **SC-011**: All 6 domain events are defined with correct payloads and emitted at the right trigger points.
- **SC-012**: The `EventBus` logs all emitted events and supports retrieval for testing.
- **SC-013**: Existing task CRUD operations (create, read, update, delete, toggle complete) continue to work without regression.
- **SC-014**: The frontend API client is updated with new type definitions matching the extended backend schemas.

---

## Scope & Boundaries *(mandatory)*

### In Scope

- Extending the Task database model with 7 new fields
- Adding `Priority` and `RecurrencePattern` enums
- Implementing recurring task generation on completion
- Implementing due date storage and overdue detection
- Implementing reminder storage and reminder-due checking
- Adding priority assignment with default value
- Adding tag storage with filtering support
- Adding search by title and description
- Adding filter parameters (status, tag, priority) to `GET /tasks`
- Adding sort parameters (sort_by, order) to `GET /tasks`
- Defining 6 domain event models as Python dataclasses
- Implementing an in-process `EventBus` for event emission and logging
- Emitting events from task route handlers
- Updating `TaskCreate`, `TaskUpdate`, and `TaskResponse` schemas
- Updating the frontend `api.ts` type definitions
- Database migration for new columns

### Out of Scope

- Kafka topics, Dapr components, or any message broker infrastructure
- Minikube, Kubernetes, or any deployment changes
- Notification delivery (email, push, SMS) -- events are defined but not consumed
- Frontend UI changes for new features (separate ticket)
- Background job scheduler for reminders (manual endpoint for now)
- Subtasks or task hierarchies beyond `parent_task_id` for recurrence
- Task assignment to multiple users
- File attachments on tasks
- Custom recurrence rules (e.g., every 3 days, every Tuesday)
- Real-time WebSocket notifications
- Performance optimization (indexing) beyond what SQLAlchemy provides by default

---

## Assumptions *(mandatory)*

- The PostgreSQL database (Neon) supports `ARRAY` column types for tags storage.
- The database can be migrated without data loss using Alembic or manual SQL.
- All existing tasks will receive default values for new fields: `priority=medium`, `tags=[]`, `due_at=null`, `remind_at=null`, `reminder_sent=false`, `recurrence_pattern=null`, `parent_task_id=null`.
- The frontend will consume new fields from the API even if UI components are not built yet (no breaking changes).
- The event bus is sufficient for Phase V Part A; no external consumers are needed yet.
- `ILIKE` SQL pattern matching is acceptable for search (no full-text search index required at this scale).
- Tag storage as a PostgreSQL `ARRAY` column is sufficient (no separate tags table needed).
- UTC is the canonical timezone for all datetime fields.

---

## Dependencies *(mandatory)*

### Internal Dependencies

- **Phase III/IV Backend**: Existing `Task` model, `TaskStatus` enum, task router, auth system, database session management.
- **Phase III/IV Frontend**: Existing `api.ts` client, `Task` interface, task page.

### External Dependencies

- **Neon PostgreSQL**: Must support `ARRAY` column type and `ILIKE` queries (both are standard PostgreSQL features).
- **SQLModel/SQLAlchemy**: Must support `ARRAY` type mapping (via `sqlalchemy.dialects.postgresql.ARRAY`).

### No New External Dependencies

- No Kafka, Dapr, Redis, or other infrastructure.
- No new Python packages required beyond the existing stack.

---

## Non-Functional Requirements *(mandatory)*

### Performance

- `GET /tasks` with filters and sort MUST respond in < 500ms for up to 1000 tasks per user.
- Search with `ILIKE` MUST respond in < 500ms for up to 1000 tasks per user.
- Recurring task generation on completion MUST add < 100ms to the toggle-complete response time.

### Security

- All new fields are user-scoped. A user MUST NOT see or modify another user's tasks, tags, or events.
- Event payloads MUST NOT contain sensitive data (passwords, tokens).
- Tag values MUST be sanitized (no HTML, no SQL injection vectors). Use Pydantic validation.

### Reliability

- If recurring task generation fails, the original task completion MUST still succeed. The failure is logged and can be retried.
- If event emission fails, the business operation MUST still succeed. Events are best-effort at this stage.

### Backward Compatibility

- Existing `POST /tasks` requests without new fields MUST continue to work. New fields have defaults.
- Existing `GET /tasks` requests without filter/sort params MUST return the same results as before (default sort: `created_at desc`).
- The `TaskResponse` schema adds new fields but does not remove any existing fields.

---

## API Contract Changes *(mandatory)*

### GET /tasks (Updated)

**New Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | (none) | Filter: `incomplete`, `complete`, `overdue` |
| `priority` | string | No | (none) | Filter: `low`, `medium`, `high` |
| `tag` | string | No | (none) | Filter: tasks containing this tag |
| `q` | string | No | (none) | Search: match title/description |
| `sort_by` | string | No | `created_at` | Sort field: `created_at`, `due_date`, `priority` |
| `order` | string | No | `desc` | Sort order: `asc`, `desc` |

### POST /tasks (Updated)

**New Request Body Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `due_at` | datetime | No | null | Due date/time (ISO 8601) |
| `remind_at` | datetime | No | null | Reminder date/time (ISO 8601) |
| `priority` | string | No | `"medium"` | Priority: `low`, `medium`, `high` |
| `tags` | list[string] | No | `[]` | Tag strings (1-50 chars each) |
| `recurrence_pattern` | string | No | null | Recurrence: `daily`, `weekly`, `monthly` |

### PUT /tasks/{task_id} (Updated)

**New Request Body Fields**: Same as POST (all optional).

### TaskResponse (Updated)

**New Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `due_at` | datetime \| null | Due date/time |
| `remind_at` | datetime \| null | Reminder date/time |
| `reminder_sent` | boolean | Whether reminder has been emitted |
| `priority` | string | Priority level |
| `tags` | list[string] | Tag list |
| `recurrence_pattern` | string \| null | Recurrence pattern |
| `parent_task_id` | UUID \| null | Parent recurring task |

### POST /tasks/check-reminders (New)

**Description**: Check for due reminders and emit events. Returns list of tasks that had reminders triggered.

**Auth**: Required (scoped to current user's tasks).

**Response**: `list[TaskResponse]` -- tasks whose reminders were just triggered.

---

## Open Questions

- **Q1**: Should the frontend UI for these features be included in Part A or deferred to a separate ticket?
  - **Answer**: Deferred. Part A focuses on backend logic and API contract. Frontend UI updates will be a separate effort. Only `api.ts` type definitions are updated.

- **Q2**: Should there be a background scheduler for reminder checks?
  - **Answer**: No. A manual `POST /tasks/check-reminders` endpoint is sufficient for Part A. Background scheduling is out of scope.

- **Q3**: Should tags be stored as a PostgreSQL `ARRAY` or in a separate join table?
  - **Answer**: PostgreSQL `ARRAY` column. It's simpler, sufficient for our scale, and avoids a join table. If tagging needs become complex (tag metadata, shared tags), we can migrate to a join table later.

---

## File Impact Summary

### Files to Create

- `backend/src/events/__init__.py` -- Events package init
- `backend/src/events/models.py` -- Domain event dataclasses
- `backend/src/events/bus.py` -- In-process EventBus

### Files to Modify

- `backend/src/models/task.py` -- Add new fields, enums
- `backend/src/schemas/task.py` -- Extend create/update/response schemas
- `backend/src/routers/tasks.py` -- Add filter, sort, search, reminders, recurring logic, event emission
- `frontend/lib/api.ts` -- Update TypeScript interfaces
