---
id: 044
title: Fix Hydration Error and MCP Tool Sync
stage: green
date: 2026-02-03
surface: agent
model: claude-opus-4-5-20251101
feature: 005-phase5-partA-intermediate-advanced-features
branch: 004-phase4-local-k8s
user: human
command: /sp.implement
labels: ["hydration", "chatbot", "mcp-tools", "frontend", "bugfix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/components/ChatWidget.tsx
  - backend/src/mcp_server/server.py
tests:
  - TypeScript compilation check (0 errors)
  - MCP server import verification (all 5 tools import OK)
---

## Prompt

but in phase v you didnt modify server.py this error appeared after new before that i didn't have any issue on frontend or backend

[User reported two issues after Phase V changes:]
1. Frontend: React hydration mismatch error on ChatWidget component
2. Backend: Chatbot agent failing to delete tasks ("technical error"), MCP tools out of sync with new Task model

## Response snapshot

Fixed two issues caused by Phase V Task model changes not being propagated to related files:

**Fix 1 - Frontend Hydration Error (ChatWidget.tsx):**
The ChatWidget called `Cookies.get("access_token")` during render (line 104). On the server (SSR), no cookies exist so it returns null (renders nothing). On the client, the cookie exists so it renders the button. This mismatch caused the hydration error. Fixed by deferring the auth check to a `useEffect` hook with an `isAuthenticated` state variable, ensuring server and client render the same initial output (null).

**Fix 2 - MCP Tools Out of Sync (server.py):**
Phase V added 7 new columns to the Task model (priority, tags, due_at, remind_at, reminder_sent, recurrence_pattern, parent_task_id) but didn't update the MCP tools in server.py. The tools were still creating/serializing tasks with only the old fields. Updated:
- Added `_task_to_dict()` helper matching all new Task fields
- Updated `mcp_add_task` to accept priority, due_at, tags
- Updated `mcp_update_task` to accept priority, due_at, tags, recurrence_pattern
- Updated all tool responses to use `_task_to_dict()` for consistent serialization

## Outcome

- Impact: Fixed frontend hydration error and synced MCP tools with new Task model
- Tests: TypeScript compiles cleanly (0 errors); MCP imports verified
- Files: frontend/components/ChatWidget.tsx, backend/src/mcp_server/server.py
- Next prompts: Test chatbot end-to-end with new task features (priority, tags, due dates via chat)
- Reflection: When adding model fields, all consumers (REST router, MCP tools, schemas) must be updated together

## Evaluation notes (flywheel)

- Failure modes observed: Phase V model changes not propagated to MCP tool layer; SSR/client cookie access mismatch
- Graders run and results (PASS/FAIL): PASS - TypeScript clean, Python imports clean
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add integration test that verifies MCP tool responses match TaskResponse schema
