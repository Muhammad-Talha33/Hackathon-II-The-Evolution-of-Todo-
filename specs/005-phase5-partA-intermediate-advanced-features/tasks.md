# Tasks: Phase V Part A - Intermediate & Advanced Task Features

**Input**: Design documents from `specs/005-phase5-partA-intermediate-advanced-features/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)
**Branch**: `005-phase5-partA-intermediate-advanced-features`

**NON-NEGOTIABLE CONSTRAINT**: The application must remain fully functional after every task. All existing features (signup, signin, task CRUD, toggle complete, chat, MCP tools) must continue to work with zero regressions. All new fields have safe defaults. No API or type errors may be introduced.

**Tests**: Not explicitly requested. No test tasks included. Validation is inline via acceptance scenarios.

**Organization**: Tasks grouped by implementation layer first (foundational), then by user story for feature-specific work. This respects the bottom-up dependency chain from plan.md while mapping clearly to spec.md user stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Database Migration & Model Layer

**Purpose**: Extend the Task model with 7 new fields and 2 new enums. This is the foundation that ALL subsequent phases depend on. No existing behavior is changed -- only additive columns with safe defaults.

**CRITICAL**: After this phase, the existing app MUST still work identically. All new columns have defaults (`priority='medium'`, `tags='{}'`, others `NULL` or `FALSE`), so existing rows and API calls are unaffected.

- [x] T001 Add `Priority` enum (low/medium/high) and `RecurrencePattern` enum (daily/weekly/monthly) to `backend/src/models/task.py` above the existing `TaskStatus` enum. Import `List` from typing and `ARRAY`, `String`, `Boolean` from sqlalchemy. FR-004, FR-006.

- [x] T002 Add 7 new columns to the `Task` model in `backend/src/models/task.py`: `priority` (String, default 'medium'), `tags` (ARRAY(String), default []), `due_at` (Optional datetime, nullable), `remind_at` (Optional datetime, nullable), `reminder_sent` (Boolean, default False), `recurrence_pattern` (Optional String, nullable), `parent_task_id` (Optional UUID, FK to tasks.id ON DELETE SET NULL, nullable). Use `sa_column=Column(...)` for `tags` and `parent_task_id` just like the existing `user_id` FK pattern. FR-001 through FR-007.

- [x] T003 Update `backend/src/models/__init__.py` to export `Priority` and `RecurrencePattern` alongside existing `Task` and `TaskStatus` exports.

- [x] T004 Run database migration: Execute `ALTER TABLE tasks ADD COLUMN IF NOT EXISTS` for all 7 new columns against the Neon PostgreSQL database. Use the exact SQL from plan.md (priority VARCHAR(6) DEFAULT 'medium', tags TEXT[] DEFAULT '{}', due_at TIMESTAMPTZ, remind_at TIMESTAMPTZ, reminder_sent BOOLEAN DEFAULT FALSE, recurrence_pattern VARCHAR(7), parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL). Verify existing rows receive defaults and no data is lost.

**Checkpoint**: App starts, existing CRUD works identically. New columns exist with defaults. `GET /tasks` returns tasks (new fields not yet in response schema).

---

## Phase 2: Event System (Foundational)

**Purpose**: Create the domain event definitions and in-process EventBus. This is infrastructure that ALL user story event emission depends on. No existing code is changed.

**CRITICAL**: This phase creates NEW files only. Zero changes to existing files. App behavior is completely unchanged.

- [x] T005 [P] Create `backend/src/events/__init__.py` that imports and re-exports all 6 event classes from `events.models` and `EventBus` + `get_event_bus` from `events.bus`.

- [x] T006 [P] Create `backend/src/events/models.py` with 6 Python dataclasses: `TaskCreatedEvent` (event_type, timestamp, task_id, user_id, title, priority, tags, due_at, recurrence_pattern, created_at), `TaskUpdatedEvent` (event_type, timestamp, task_id, user_id, updated_fields, updated_at), `TaskCompletedEvent` (event_type, timestamp, task_id, user_id, title, completed_at, had_recurrence, was_overdue), `TaskDeletedEvent` (event_type, timestamp, task_id, user_id, title, deleted_at), `TaskReminderDueEvent` (event_type, timestamp, task_id, user_id, title, remind_at, due_at), `RecurringTaskGeneratedEvent` (event_type, timestamp, new_task_id, parent_task_id, user_id, title, next_due_at, recurrence_pattern). Each class has `event_type` as a class-level string constant and `timestamp` defaulting to `datetime.utcnow()`. FR-030, FR-032.

- [x] T007 [P] Create `backend/src/events/bus.py` with `EventBus` class containing: `__init__` (empty list + logger), `emit(event)` (append to list + log info), `get_events()` (return copy of list), `clear()` (empty list). Add module-level singleton `_bus = EventBus()` and `get_event_bus()` dependency function returning it. FR-031.

**Checkpoint**: Three new files exist. No existing files changed. App works identically.

---

## Phase 3: Schema Layer

**Purpose**: Extend TaskCreate, TaskUpdate, and TaskResponse Pydantic schemas with all new fields. This is required before the router can accept/return new fields.

**CRITICAL**: All new fields in TaskCreate/TaskUpdate are optional with defaults. Existing API requests without these fields continue to work. TaskResponse adds fields but removes none -- backward compatible.

- [x] T008 Extend `TaskCreate` in `backend/src/schemas/task.py`: Add optional fields `due_at` (Optional[datetime], default None), `remind_at` (Optional[datetime], default None), `priority` (Optional[str], default "medium"), `tags` (Optional[List[str]], default []), `recurrence_pattern` (Optional[str], default None). Add Pydantic `model_validator` (mode='after'): if `recurrence_pattern` is set and `due_at` is None, raise ValueError (FR-012). Add validator for `priority` to constrain to low/medium/high. Add validator for `tags`: each tag 1-50 chars, alphanumeric+hyphens only, deduplicate. Add validator for `recurrence_pattern` to constrain to daily/weekly/monthly/None. FR-027.

- [x] T009 Extend `TaskUpdate` in `backend/src/schemas/task.py`: Add same optional fields as TaskCreate (due_at, remind_at, priority, tags, recurrence_pattern). Reuse same validators for priority, tags, recurrence_pattern. Add same model_validator: if recurrence_pattern is explicitly set (not None) and due_at is not provided AND not already set, raise ValueError. FR-028.

- [x] T010 Extend `TaskResponse` in `backend/src/schemas/task.py`: Add fields `due_at` (Optional[datetime]), `remind_at` (Optional[datetime]), `reminder_sent` (bool), `priority` (str), `tags` (List[str]), `recurrence_pattern` (Optional[str]), `parent_task_id` (Optional[UUID]). Do NOT remove any existing fields (id, user_id, title, description, status, created_at, updated_at). FR-029.

**Checkpoint**: Schemas are ready. Existing API calls still validate because all new create/update fields have defaults. Response now includes new fields once router passes them through.

---

## Phase 4: Services Layer

**Purpose**: Implement recurrence date computation and reminder checking as standalone service functions. No router changes yet.

**CRITICAL**: These are NEW files only. No existing files modified. App unchanged.

- [x] T011 [P] Create `backend/src/services/recurrence.py` with two functions. First: `compute_next_due_date(current_due: datetime, pattern: str) -> datetime` -- daily adds 1 day via timedelta, weekly adds 7 days via timedelta, monthly adds 1 calendar month using `calendar.monthrange` to clamp to last day of target month (e.g., Jan 31 -> Feb 28). Second: `async def generate_next_recurring_task(completed_task: Task, db: AsyncSession, event_bus: EventBus) -> Optional[Task]` -- checks recurrence_pattern is not None, computes next_due via compute_next_due_date, computes next_remind_at preserving original remind_at-to-due_at offset if remind_at existed, creates new Task copying title/description/priority/tags/recurrence_pattern/user_id with parent_task_id=completed_task.id and status=INCOMPLETE, persists to DB, emits RecurringTaskGeneratedEvent, returns new task. Wrapped in try/except: on failure logs error and returns None (reliability requirement). FR-008 through FR-012.

- [x] T012 [P] Create `backend/src/services/reminders.py` with function `async def check_and_emit_reminders(user_id: UUID, db: AsyncSession, event_bus: EventBus) -> List[Task]`. Query tasks WHERE user_id=uid AND remind_at <= utcnow() AND reminder_sent=False AND status != 'complete'. For each matching task: emit TaskReminderDueEvent via event_bus, set reminder_sent=True. Commit changes. Return list of affected tasks. FR-013, FR-014.

**Checkpoint**: Two new service files. No existing files changed. App works identically.

---

## Phase 5: Router Updates - Core CRUD with Event Emission

**Purpose**: Update existing CRUD handlers to pass through new fields and emit events. This is where the router starts using new model fields, updated schemas, and event bus.

**CRITICAL**: Backward compatibility is paramount. The `create_task` handler must accept requests with ONLY `title` (no new fields) and still work. The `get_tasks` handler must return all tasks with new fields populated from defaults. The toggle_complete handler must work for non-recurring tasks exactly as before.

### US4 - Priority + US5 - Tags + US2 - Due Dates (Create/Update integration)

- [x] T013 Update `create_task` handler in `backend/src/routers/tasks.py`: Add `event_bus: EventBus = Depends(get_event_bus)` parameter. Pass new fields from TaskCreate to Task constructor: `priority=task_data.priority`, `tags=task_data.tags`, `due_at=task_data.due_at`, `remind_at=task_data.remind_at`, `recurrence_pattern=task_data.recurrence_pattern`. After commit+refresh, emit `TaskCreatedEvent` with task fields (wrap in try/except, log on failure). Add imports for EventBus, get_event_bus, and event models. Verify: POST /tasks with only {title} still works (defaults apply). FR-027, FR-030.

- [x] T014 Update `update_task` handler in `backend/src/routers/tasks.py`: Add `event_bus` dependency. Track which fields changed by comparing before/after values. Add field update logic for: `due_at`, `remind_at`, `priority`, `tags`, `recurrence_pattern` (same pattern as existing title/description: update if provided). After commit, emit `TaskUpdatedEvent` with `updated_fields` list (wrap in try/except). Verify: PUT /tasks/{id} with only {title} still works. FR-028, FR-030.

- [x] T015 Update `delete_task` handler in `backend/src/routers/tasks.py`: Add `event_bus` dependency. Capture `task.title` and `task.user_id` before deletion. After commit, emit `TaskDeletedEvent` (wrap in try/except). Verify: DELETE /tasks/{id} still returns 204. FR-030.

### US1 - Recurring Tasks (Completion integration)

- [x] T016 [US1] Update `toggle_task_complete` handler in `backend/src/routers/tasks.py`: Add `event_bus` dependency. After toggling to COMPLETE: compute `was_overdue` (due_at is not None and due_at < utcnow()), emit `TaskCompletedEvent` with had_recurrence=(recurrence_pattern is not None) and was_overdue. Then call `await generate_next_recurring_task(task, db, event_bus)` from recurrence service (import it). After toggling to INCOMPLETE: emit `TaskUpdatedEvent` with updated_fields=["status"]. All event emission and recurrence generation wrapped in try/except (if they fail, the completion itself still succeeds). Verify: toggling a task without recurrence_pattern still works exactly as before. FR-008, FR-030.

**Checkpoint**: All CRUD operations work with new fields. Events are emitted. Completing a recurring task generates the next instance. Existing behavior preserved.

---

## Phase 6: Router Updates - Filter, Sort, Search

**Purpose**: Enhance `GET /tasks` with query parameters for filtering, sorting, and searching. Default behavior (no params) returns the same results as before.

**CRITICAL**: `GET /tasks` with NO query parameters MUST return identical results to the current implementation (all user tasks, ordered by created_at desc). This is the backward compatibility guarantee.

### US7 - Filter & Sort

- [x] T017 [US7] Add query parameters to `get_tasks` handler in `backend/src/routers/tasks.py`: `status: Optional[str] = Query(None)`, `priority: Optional[str] = Query(None)`, `tag: Optional[str] = Query(None)`, `q: Optional[str] = Query(None)`, `sort_by: Optional[str] = Query("created_at")`, `order: Optional[str] = Query("desc")`. Import `Query` from fastapi. Refactor the handler to build the SQLAlchemy query dynamically instead of the current static query. Base query: `select(Task).where(Task.user_id == current_user.id)`. FR-015, FR-018, FR-020, FR-021, FR-022.

- [x] T018 [US7] Implement status filtering in `get_tasks` in `backend/src/routers/tasks.py`: If status=="incomplete", add `.where(Task.status == TaskStatus.INCOMPLETE)`. If status=="complete", add `.where(Task.status == TaskStatus.COMPLETE)`. If status=="overdue", add `.where(Task.status == TaskStatus.INCOMPLETE, Task.due_at < datetime.utcnow(), Task.due_at.isnot(None))`. FR-018, FR-019.

- [x] T019 [US7] Implement priority and tag filtering in `get_tasks` in `backend/src/routers/tasks.py`: If priority param is provided, add `.where(Task.priority == priority)`. If tag param is provided, use SQLAlchemy `any_()` on the tags ARRAY column: `.where(Task.tags.any(tag))` or equivalent `literal(tag) == any_(Task.tags)`. FR-020, FR-021.

- [x] T020 [US7] Implement sorting in `get_tasks` in `backend/src/routers/tasks.py`: If sort_by=="created_at", use `Task.created_at`. If sort_by=="due_date", use `Task.due_at` with `nullslast()` for asc and `nullsfirst()` for desc (import from sqlalchemy). If sort_by=="priority", use `case((Task.priority == 'high', 1), (Task.priority == 'medium', 2), else_=3)` (import `case` from sqlalchemy). Apply `asc()` or `desc()` based on order param. Default: `Task.created_at.desc()` (matches current behavior). FR-022 through FR-026.

### US6 - Search

- [x] T021 [US6] Implement search in `get_tasks` in `backend/src/routers/tasks.py`: If q param is provided and non-empty, add `.where(or_(Task.title.ilike(f"%{q}%"), Task.description.ilike(f"%{q}%")))`. Import `or_` from sqlalchemy. Ensure that an empty q parameter does not filter anything. FR-015, FR-016, FR-017.

**Checkpoint**: `GET /tasks` with no params returns same results as before. Filters, sorts, and search all work as specified. All combinations (e.g., status=overdue&sort_by=due_date&q=report) work correctly.

---

## Phase 7: Reminders Endpoint

**Purpose**: Add the `POST /tasks/check-reminders` endpoint. This is US3-specific functionality.

### US3 - Reminders

- [x] T022 [US3] Add `check_reminders` endpoint to `backend/src/routers/tasks.py`: `@router.post("/check-reminders", response_model=List[TaskResponse])`. Route MUST be registered BEFORE the `/{task_id}` routes to avoid FastAPI matching "check-reminders" as a task_id UUID. Handler takes `current_user`, `db`, and `event_bus` dependencies. Calls `check_and_emit_reminders(current_user.id, db, event_bus)` from reminders service. Returns the list of tasks whose reminders were triggered. FR-013, FR-014.

**Checkpoint**: POST /tasks/check-reminders works for authenticated users. Finds due reminders, emits events, sets reminder_sent=True. Does not trigger reminders for completed tasks or already-sent reminders.

---

## Phase 8: MCP Tools Backward-Compatible Update

**Purpose**: Update MCP task tools to include new fields in responses and accept new fields in create/update. This ensures the AI chatbot works correctly with the extended task model.

**CRITICAL**: All changes are ADDITIVE. Existing MCP tool function signatures keep their current parameters as-is. New parameters are OPTIONAL with defaults. The chatbot must continue to work exactly as before -- it can call `add_task(user_id, title)` without any new params and it works.

- [x] T023 Update `add_task` function in `backend/src/mcp_server/tools/task_tools.py`: Add optional parameters `priority: Optional[str] = None`, `due_at: Optional[str] = None`, `tags: Optional[List[str]] = None`. If provided, pass them to the Task constructor (convert due_at string to datetime if provided). Include new fields in the response dictionary. Existing calls with only (user_id, title) must still work.

- [x] T024 Update `list_tasks` function in `backend/src/mcp_server/tools/task_tools.py`: Add new fields to each task dictionary in the response: `priority`, `tags`, `due_at` (isoformat or None), `remind_at` (isoformat or None), `recurrence_pattern`, `parent_task_id` (str or None). No parameter changes.

- [x] T025 Update `update_task` function in `backend/src/mcp_server/tools/task_tools.py`: Add optional parameters `priority: Optional[str] = None`, `due_at: Optional[str] = None`, `remind_at: Optional[str] = None`, `tags: Optional[List[str]] = None`, `recurrence_pattern: Optional[str] = None`. Update fields if provided (same pattern as existing title/description). Include new fields in response dictionary.

- [x] T026 Update `complete_task` function in `backend/src/mcp_server/tools/task_tools.py`: No parameter changes. Only update the response dictionary to include new fields (`priority`, `tags`, `due_at`, etc.) so the chatbot sees full task state after completion. Note: Recurrence generation is NOT added here (sync function; recurrence is async in the API route only).

**Checkpoint**: Chatbot continues to work. `add_task(user_id, "Buy milk")` still works. `list_tasks` returns tasks with new fields. No functionality is broken.

---

## Phase 9: Frontend Type Sync

**Purpose**: Update TypeScript interfaces in `frontend/lib/api.ts` to match the extended backend response schema. Add query parameter support to `getTasks` and add `checkReminders` method.

**CRITICAL**: Only TYPE definitions and the ApiClient class change. No UI components change. Existing callers of `getTasks(accessToken)` must still work (new params are optional).

- [x] T027 [P] Update `Task` interface in `frontend/lib/api.ts`: Add fields `priority: 'low' | 'medium' | 'high'`, `tags: string[]`, `due_at: string | null`, `remind_at: string | null`, `reminder_sent: boolean`, `recurrence_pattern: 'daily' | 'weekly' | 'monthly' | null`, `parent_task_id: string | null`. Keep all existing fields unchanged. FR-029, SC-014.

- [x] T028 [P] Update `TaskCreate` interface in `frontend/lib/api.ts`: Add optional fields `priority?: 'low' | 'medium' | 'high'`, `tags?: string[]`, `due_at?: string`, `remind_at?: string`, `recurrence_pattern?: 'daily' | 'weekly' | 'monthly'`. Keep existing `title` and `description` unchanged. FR-027.

- [x] T029 [P] Update `TaskUpdate` interface in `frontend/lib/api.ts`: Add optional fields `priority?: 'low' | 'medium' | 'high'`, `tags?: string[]`, `due_at?: string`, `remind_at?: string`, `recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | null`. Keep existing fields unchanged. FR-028.

- [x] T030 Update `getTasks` method in `ApiClient` class in `frontend/lib/api.ts`: Add optional `params?: { status?: string; priority?: string; tag?: string; q?: string; sort_by?: string; order?: string }` parameter. Build query string from params and append to '/tasks' URL. Existing callers passing only `accessToken` must still work (params defaults to undefined, no query string appended).

- [x] T031 Add `checkReminders` method to `ApiClient` class in `frontend/lib/api.ts`: `async checkReminders(accessToken: string): Promise<Task[]>` that POSTs to `/tasks/check-reminders` with auth header.

**Checkpoint**: Frontend compiles. Existing task page works. API client types match backend response schema. No runtime errors.

---

## Phase 10: Integration Verification & Regression Check

**Purpose**: Verify end-to-end functionality and zero regressions across the entire application.

- [x] T032 Verify backward compatibility: Start the backend. Call `POST /tasks` with body `{"title": "Test task"}` (no new fields). Verify 201 response includes all new fields with defaults (priority="medium", tags=[], due_at=null, etc.). Call `GET /tasks` with no query params. Verify response includes all tasks ordered by created_at desc (same as before). Call `PUT /tasks/{id}` with `{"title": "Updated"}` only. Verify 200 response with updated title and unchanged defaults. Call `DELETE /tasks/{id}`. Verify 204. Call `PATCH /tasks/{id}/complete`. Verify toggle works for non-recurring task (no new task generated). SC-013.

- [x] T033 Verify new features end-to-end: Call `POST /tasks` with `{"title": "Daily standup", "priority": "high", "tags": ["work", "meeting"], "due_at": "2026-02-03T09:00:00Z", "recurrence_pattern": "daily"}`. Verify 201 with all fields populated. Complete the task via `PATCH /tasks/{id}/complete`. Verify a new task was generated with due_at="2026-02-04T09:00:00Z" and parent_task_id pointing to completed task. Call `GET /tasks?status=overdue` and `GET /tasks?tag=work&sort_by=priority&order=desc`. Verify correct filtering and sorting. Call `GET /tasks?q=standup`. Verify search returns matching task. SC-001 through SC-012.

- [x] T034 Verify MCP/chatbot integration: Start the full app (backend + frontend). Open the chat interface. Send "Add a task called Buy groceries". Verify the task is created via chatbot. Send "Show my tasks". Verify the response includes the new task with all fields (including new defaults). Send "Complete the Buy groceries task". Verify completion works. Send "Delete the Buy groceries task". Verify deletion works. Confirm no errors in backend logs related to MCP tools or missing fields.

- [x] T035 Verify frontend type safety: Start the frontend. Navigate to the tasks page. Verify tasks load and display correctly (existing UI reads the same fields as before plus ignores unknown fields). Verify no TypeScript compilation errors. Verify no console errors in browser. Verify create/update/delete task flows work through the UI exactly as before.

**Checkpoint**: Full application verified. All existing features work. All new features work. No regressions. Zero errors.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Model Layer (T001-T004)           -- BLOCKS everything
    ↓
Phase 2: Event System (T005-T007)           -- BLOCKS event emission in Phases 5-7
    ↓
Phase 3: Schema Layer (T008-T010)           -- BLOCKS router changes in Phases 5-7
    ↓
Phase 4: Services Layer (T011-T012)         -- BLOCKS recurrence/reminder in Phases 5, 7
    ↓
Phase 5: Router CRUD + Events (T013-T016)   -- BLOCKS Phase 6 (same file)
    ↓
Phase 6: Router Filter/Sort/Search (T017-T021) -- BLOCKS Phase 7 (same file, route order matters)
    ↓
Phase 7: Reminders Endpoint (T022)          -- Independent from Phases 8-9
    ↓
Phase 8: MCP Tools (T023-T026)             -- Can parallel with Phase 7
    ↓
Phase 9: Frontend Types (T027-T031)         -- Can parallel with Phases 7-8
    ↓
Phase 10: Integration Verification (T032-T035) -- REQUIRES all above complete
```

### User Story to Task Mapping

| User Story | Priority | Tasks | Key Phase |
|-----------|----------|-------|-----------|
| US1 - Recurring Tasks | P0 | T001-T004 (model), T006 (events), T008-T010 (schemas), T011 (service), T016 (router) | Phase 5 |
| US2 - Due Dates & Overdue | P0 | T001-T004 (model), T008-T010 (schemas), T013-T014 (router), T018 (filter) | Phase 5-6 |
| US3 - Reminders | P1 | T001-T004 (model), T006-T007 (events), T012 (service), T022 (endpoint) | Phase 7 |
| US4 - Priority | P0 | T001-T003 (model), T008-T010 (schemas), T013-T014 (router), T019-T020 (filter/sort) | Phase 5-6 |
| US5 - Tags | P0 | T001-T004 (model), T008-T010 (schemas), T013-T014 (router), T019 (filter) | Phase 5-6 |
| US6 - Search | P1 | T021 (search in router) | Phase 6 |
| US7 - Filter & Sort | P0 | T017-T020 (router filter/sort) | Phase 6 |
| Event Contract | -- | T005-T007 (events module), T013-T016 (emission in CRUD) | Phase 2, 5 |

### Parallel Opportunities

**Within Phase 2** (all create new files, no conflicts):
- T005, T006, T007 can all run in parallel

**Within Phase 4** (different files):
- T011 (recurrence.py) and T012 (reminders.py) can run in parallel

**Within Phase 9** (different sections of same file, but safe as parallel type updates):
- T027, T028, T029 can run in parallel

**Across Phases** (once Phase 6 is complete):
- Phase 7, Phase 8, Phase 9 can run in parallel (different files)

---

## Implementation Strategy

### MVP First: Phases 1-5

1. Complete Phase 1 (Model) -- new columns exist, app works
2. Complete Phase 2 (Events) -- event infra ready, app unchanged
3. Complete Phase 3 (Schemas) -- API can accept/return new fields
4. Complete Phase 4 (Services) -- recurrence + reminder logic ready
5. Complete Phase 5 (Router CRUD) -- create/update/delete/complete use new fields + events

**STOP and VALIDATE**: At this point, all CRUD operations work with new fields. Recurring task generation works. Events are emitted. All existing behavior preserved.

### Full Feature: Phases 6-9

6. Complete Phase 6 (Filter/Sort/Search) -- GET /tasks is fully queryable
7. Complete Phase 7 (Reminders endpoint) -- reminder checking works
8. Complete Phase 8 (MCP tools) -- chatbot aware of new fields
9. Complete Phase 9 (Frontend types) -- TypeScript types match backend

### Verification: Phase 10

10. Complete Phase 10 -- full regression + integration verification

### Incremental Delivery

Each phase completion is a safe commit point. The app works after every phase. No big-bang integration.

---

## Notes

- [P] tasks = different files, no dependencies on each other
- [US#] label maps task to its primary user story for traceability
- Many tasks serve multiple user stories (model extension, schema extension) -- these are in foundational phases
- Route registration order matters: `/check-reminders` MUST be before `/{task_id}` routes
- All event emission is try/except wrapped -- failures never block business operations
- PostgreSQL ARRAY requires `sqlalchemy.dialects.postgresql.ARRAY` import
- SQL CASE for priority sorting requires `sqlalchemy.sql.expression.case` import
- ILIKE for search requires SQLAlchemy `ilike()` method on string columns
- `nullslast()` / `nullsfirst()` from `sqlalchemy` for due_date sort null handling
- Total: **35 tasks** across 10 phases
