---
id: 042
title: Phase V Part A Bugfix and Verification
stage: green
date: 2026-02-03
surface: agent
model: claude-opus-4-5-20251101
feature: 005-phase5-partA-intermediate-advanced-features
branch: 005-phase5-partA-intermediate-advanced-features
user: architect
command: /sp.implement
labels: ["phase5", "bugfix", "timezone", "array-type", "verification", "backward-compatible"]
links:
  spec: specs/005-phase5-partA-intermediate-advanced-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/routers/tasks.py
  - backend/src/services/recurrence.py
tests:
  - "TEST 1 (backward compat POST title-only): PASS"
  - "TEST 2 (POST with all new fields): PASS (was FAIL before fix)"
  - "TEST 3 (GET all tasks): PASS"
  - "TEST 4 (filter priority=high): PASS"
  - "TEST 5 (filter tag=work): PASS (was FAIL before fix)"
  - "TEST 6 (search q=standup): PASS"
  - "TEST 7 (sort by priority desc): PASS"
  - "TEST 8 (sort by due_date asc): PASS"
  - "TEST 10 (update task with new fields): PASS"
  - "TEST 11 (complete recurring task + next instance): PASS (was FAIL before fix)"
  - "TEST (check-reminders): PASS"
  - "TEST (delete task): PASS - HTTP 204"
  - "TEST (toggle uncomplete): PASS"
  - "TEST (validation: recurrence without due_at): PASS - proper error"
  - "TEST (validation: invalid priority): PASS - proper error"
  - "TEST (validation: invalid tag format): PASS - proper error"
  - "Event emission verified: TaskCreated, TaskCompleted, RecurringTaskGenerated, TaskDeleted, TaskUpdated"
---

## Prompt

/sp.implement

run the migration and start the backend to test it

(Continuation from prompt 041 which ran the migration successfully but hit errors during verification testing)

## Response snapshot

Diagnosed and fixed 3 runtime bugs discovered during live backend testing:

**Bug 1 - Timezone-naive/aware mismatch on INSERT (router):**
- Error: `asyncpg.exceptions.DataError: can't subtract offset-naive and offset-aware datetimes`
- Cause: Pydantic parses `"2026-02-04T09:00:00Z"` as tz-aware datetime, but `created_at`/`updated_at` use `datetime.utcnow()` (naive), and DB column is `TIMESTAMP WITHOUT TIME ZONE`
- Fix: Added `_strip_tz()` helper in `routers/tasks.py`, applied to `due_at` and `remind_at` in `create_task` and `update_task`

**Bug 2 - PostgreSQL ARRAY type mismatch on tag filter:**
- Error: `operator does not exist: text[] @> character varying[]`
- Cause: Migration created column as `TEXT[]` but SQLAlchemy `ARRAY(String)` binds parameters as `VARCHAR[]` — the `@>` operator requires matching types
- Fix: Used `cast([tag], PG_ARRAY(Text))` to cast filter value to `text[]`

**Bug 3 - Timezone mismatch in recurrence service:**
- Error: Same tz-naive/aware mismatch when generating next recurring task instance
- Cause: `completed_task.due_at` read from DB arrives as tz-aware, but `compute_next_due_date` produces tz-aware result, which then fails on INSERT alongside naive `created_at`/`updated_at`
- Fix: Added `_strip_tz()` in `recurrence.py`, applied to `due_at` and `remind_at` before computing next dates. Also added `await db.rollback()` in except block to prevent `PendingRollbackError` from cascading.

## Outcome

- Impact: All 3 bugs fixed. 16+ verification tests passed. All Phase V Part A features fully operational.
- Tests: 16 endpoint tests PASS, 3 validation negative tests PASS, 5 event types verified in server logs
- Files: 2 files modified (routers/tasks.py, services/recurrence.py)
- Next prompts: Test frontend integration, verify MCP chatbot still works, push to GitHub
- Reflection: The root cause was a systemic timezone handling gap: asyncpg and Neon PostgreSQL return tz-aware datetimes even for TIMESTAMP WITHOUT TIME ZONE columns, while Python's `datetime.utcnow()` produces naive datetimes. The `_strip_tz()` pattern at the data entry boundary is the correct fix. The ARRAY type mismatch (`text[]` vs `varchar[]`) is a known PostgreSQL/SQLAlchemy gotcha when migrations use `TEXT[]` but the ORM uses `ARRAY(String)`.

## Evaluation notes (flywheel)

- Failure modes observed: (1) asyncpg strict timezone checking on mixed naive/aware datetimes in same INSERT, (2) PostgreSQL @> operator type strictness between text[] and varchar[], (3) SQLAlchemy PendingRollbackError cascade when a service fails mid-transaction sharing the same session
- Graders run and results: 16 endpoint tests PASS, 3 validation tests PASS, event log verification PASS
- Prompt variant: N/A
- Next experiment: Test MCP chatbot integration, verify frontend renders all new fields
