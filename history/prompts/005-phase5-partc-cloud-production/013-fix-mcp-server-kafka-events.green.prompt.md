---
id: 013
title: Fix MCP Server Kafka Event Publishing
stage: green
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 005-phase5-partc-cloud-production
branch: 001-phase2-full-stack-web
user: Muhammad-Talha33
command: /sp.implement
labels: ["kafka", "chatbot", "mcp-server", "event-driven", "bugfix"]
links:
  spec: specs/005-phase5-partc-cloud-production/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/mcp_server/server.py
tests:
  - Chatbot task creation publishes TaskCreated to Dapr - PASS (HTTP 204)
  - Dapr log confirms event published - PASS
  - Backend health check - PASS
  - All pods Running - PASS
---

## Prompt

User reported that chatbot-created tasks did not appear in Confluent Cloud despite the earlier fix to task_tools.py. Investigation revealed the chatbot uses a different file (server.py) with async @function_tool decorated functions, not the sync task_tools.py that was previously modified.

## Response snapshot

Root cause: Two separate MCP tool files exist in the codebase:
1. `backend/src/mcp_server/server.py` - Async @function_tool functions used by OpenAI Agents SDK (the ACTUAL chatbot tools)
2. `backend/src/mcp_server/tools/task_tools.py` - Sync functions (previously modified, but NOT used by chatbot)

Fix: Added identical event publishing to `server.py` with same try/except pattern for all 4 operations (add, complete, delete, update).

Verification from backend logs:
```
POST http://localhost:3500/v1.0/publish/taskpubsub/tasks "HTTP/1.1 204 No Content"
Event published via Dapr: TaskCreated | task_id=3c736fda-...
```

Rebuilt backend Docker image, pushed to GHCR, redeployed.

## Outcome

- ✅ Impact: Chatbot task operations now correctly publish events to Confluent Cloud Kafka
- 🧪 Tests: Dapr sidecar returns 204 for publish, event log confirms TaskCreated event
- 📁 Files: 1 file modified (backend/src/mcp_server/server.py)
- 🔁 Next prompts: Verify event appears in Confluent Cloud console, test complete/delete/update events from chatbot
- 🧠 Reflection: Always verify which code path is actually executed - there were two MCP tool files and only server.py is used by the chatbot runtime

## Evaluation notes (flywheel)

- Failure modes observed: Modified wrong file (task_tools.py instead of server.py) - codebase had two similar MCP tool implementations
- Graders run and results (PASS/FAIL): Dapr publish 204 + event log confirmation - PASS
- Prompt variant (if applicable): N/A
- Next experiment: Add code comment to task_tools.py noting it's not used by chatbot to prevent future confusion
