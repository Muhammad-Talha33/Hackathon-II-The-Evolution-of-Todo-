---
id: 047
title: Fix chatbot reminder feature
stage: green
date: 2026-02-06
surface: agent
model: claude-opus-4-5-20251101
feature: 005-phase5-partA-intermediate-advanced-features
branch: 004-phase4-local-k8s
user: user
command: /sp.implement
labels: ["bugfix", "mcp", "chatbot", "reminders"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/mcp_server/server.py
  - backend/src/mcp_server/tools/task_tools.py
tests:
  - N/A - import verification only
---

## Prompt

Everything else is fine and working properly. All the new features are also working correctly. There's just one issue with the chatbot, that chatbot is neither being adding or nor shown reminder feature in the existing task, if a reminder is attached. Aside from that, all other features are working fine.

Like this

"""
show my tasks

Here's your current task:

1. Buy eggs (incomplete)
   - Tags: shopping
   - Due: February 5, 2026, at 1:50 PM
   - This task repeats daily

Would you like to mark this as done, update it, or add a new task?
""", but this task have reminder 02/05/2026 12:45 PM

## Response snapshot

Fixed the MCP tools to support `remind_at` parameter for task creation and updates.

**Root Cause:** The MCP tool functions (`mcp_add_task`, `mcp_update_task`, `add_task`) were missing the `remind_at` parameter. While `_task_to_dict` was returning `remind_at` in the response, the chatbot had no way to CREATE or UPDATE tasks with reminders.

**Files Modified:**

1. `backend/src/mcp_server/server.py`:
   - Added `remind_at` and `recurrence_pattern` parameters to `mcp_add_task`
   - Added parsing logic for `remind_at` in task creation
   - Added `remind_at` parameter to `mcp_update_task`
   - Added logic to update `remind_at` and reset `reminder_sent` when modified

2. `backend/src/mcp_server/tools/task_tools.py`:
   - Added `remind_at` and `recurrence_pattern` parameters to `add_task`
   - Added parsing logic for `remind_at` in task creation

Now the chatbot can create and update tasks with reminders.

## Outcome

- Impact: Chatbot can now set and display reminders on tasks
- Tests: Import verification passed
- Files: 2 files modified
- Next prompts: Test chatbot with "Add task with reminder" commands
- Reflection: The _task_to_dict function already supported remind_at in responses, but the tool parameters were missing for input

## Evaluation notes (flywheel)

- Failure modes observed: Missing parameter in MCP tool function signatures
- Graders run and results (PASS/FAIL): PASS - imports verified
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - fix verified
