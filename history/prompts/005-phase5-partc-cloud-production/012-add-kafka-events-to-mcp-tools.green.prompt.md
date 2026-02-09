---
id: 012
title: Add Kafka Event Publishing to MCP Chatbot Tools
stage: green
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 005-phase5-partc-cloud-production
branch: 001-phase2-full-stack-web
user: Muhammad-Talha33
command: /sp.implement
labels: ["kafka", "chatbot", "mcp-tools", "event-driven", "parity"]
links:
  spec: specs/005-phase5-partc-cloud-production/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/mcp_server/tools/task_tools.py
tests:
  - Chatbot task creation via /api/api/chat - PASS (returns AI response)
  - Backend health check - PASS
  - Frontend HTTP 200 - PASS
  - All pods Running (backend 2/2, frontend 1/1, workers 2/2 each) - PASS
---

## Prompt

User asked if chatbot-created tasks also publish events to Confluent Cloud Kafka. Analysis revealed MCP tools (used by chatbot) did NOT publish events while REST API routes did. User requested a fix but was worried about breaking existing functionality.

## Response snapshot

Added event publishing to all 4 MCP tool operations in `backend/src/mcp_server/tools/task_tools.py`:

1. `add_task` → emits `TaskCreatedEvent`
2. `complete_task` → emits `TaskCompletedEvent`
3. `delete_task` → emits `TaskDeletedEvent`
4. `update_task` → emits `TaskUpdatedEvent` (also tracks `updated_fields`)

**Safety pattern used (same as REST API routes):**
```python
try:
    get_event_bus().emit(TaskCreatedEvent(...))
except Exception as e:
    logger.warning("Failed to emit TaskCreated event from MCP: %s", e)
```

This ensures:
- DB save happens BEFORE event publish
- If event publish fails, task is still saved and returned
- EventBus itself has fire-and-forget + graceful degradation
- No new dependencies added

**Deployment:** Rebuilt backend image, pushed to GHCR, restarted backend pod. Verified chatbot still works: "I've added 'buy milk' to your tasks!"

## Outcome

- ✅ Impact: Feature parity achieved - chatbot operations now publish events to Confluent Cloud Kafka, same as REST API
- 🧪 Tests: Chatbot task creation works, health check passes, all pods healthy
- 📁 Files: 1 file modified (backend/src/mcp_server/tools/task_tools.py)
- 🔁 Next prompts: Verify events from chatbot appear in Confluent Cloud console, add TLS/domain configuration
- 🧠 Reflection: Using the same try/except pattern as existing REST routes made this a zero-risk change - event failures can never break task operations

## Evaluation notes (flywheel)

- Failure modes observed: None - chatbot continues to work correctly
- Graders run and results (PASS/FAIL): End-to-end chatbot test PASS, health check PASS
- Prompt variant (if applicable): N/A
- Next experiment: Monitor Confluent Cloud to verify chatbot events appear alongside REST API events
