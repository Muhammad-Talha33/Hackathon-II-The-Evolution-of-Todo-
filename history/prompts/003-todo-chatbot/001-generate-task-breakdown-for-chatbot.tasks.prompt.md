---
id: 001
title: Generate task breakdown for chatbot
stage: tasks
date: 2026-01-03
surface: agent
model: claude-sonnet-4-5
feature: 003-todo-chatbot
branch: 003-todo-chatbot
user: User
command: /sp.tasks
labels: ["tasks", "implementation-planning", "architecture", "mcp", "openai-agents"]
links:
  spec: specs/003-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-todo-chatbot/tasks.md
tests:
 - None (tests not included in specification)
---

## Prompt

User initiated `/sp.tasks` command for Feature specification from specs/003-todo-chatbot/spec.md

User provided critical architectural guidance:

**Stateless Architecture**:
- Do NOT use OpenAI Agents SDK session storage or any built-in memory
- Backend must be fully stateless
- Conversation state must be fetched from and persisted to database explicitly on every request
- Each request must independently reconstruct agent context from database

**MCP Server Separation**:
- Implement a clear MCP Server using the Official MCP SDK
- MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) must live in the MCP server layer
- FastAPI backend should act as an MCP client and must not directly implement task logic
- Keep boundaries clear: FastAPI → Agent → MCP Server → Database

**Agent Responsibilities**:
- Interpret natural language
- Decide which MCP tool(s) to call
- Generate a friendly confirmation message
- All data mutations must happen via MCP tools only

**Frontend Requirements**:
- Use OpenAI ChatKit as the frontend UI
- Do NOT build a custom chat UI unless required for minimal integration
- Assume ChatKit handles message rendering; backend only provides chat endpoint

**Scope Control**:
- Remove non-required features: rate limiting, performance benchmarking, retry logic, advanced security hardening, pagination, analytics
- Focus only on features explicitly defined in the Phase III specification

**Task Organization**:
- Database & Models
- MCP Server
- Agent Logic
- FastAPI Chat Endpoint
- Frontend (OpenAI ChatKit)
- Integration & Validation

**Phase Integrity**:
- Do NOT modify Phase I or Phase II code
- Phase III must be implemented independently

User also corrected technology choice: Use official OpenAI Agents SDK (openai-agents package) from https://openai.github.io/openai-agents-python/ instead of OpenAI Assistants API.

## Response snapshot

Generated comprehensive tasks.md with 78 tasks organized across 6 phases:

**Phase 1: Database & Models** (6 tasks)
- Created Conversation and Message SQLModel schemas
- Alembic migration for new tables
- Database verification

**Phase 2: MCP Server** (14 tasks)
- Install Official MCP SDK (`mcp` package)
- Implement 5 MCP tools using Official MCP SDK: add_task, list_tasks, complete_task, delete_task, update_task
- MCP server initialization and tool registration
- Database session injection and user_id validation

**Phase 3: Agent Logic** (11 tasks)
- Install OpenAI Agents SDK (`openai-agents` package)
- Create TodoAgent with stateless configuration (NO session storage)
- Update agent instructions for all 5 user stories
- Configure agent to use MCP tools
- Error handling for MCP tool failures

**Phase 4: FastAPI Chat Endpoint** (20 tasks)
- Stateless chat service: fetch conversation history from DB every request
- ChatRequest/ChatResponse Pydantic schemas
- POST /api/chat endpoint with JWT authentication
- GET /api/conversations and GET /api/conversations/{id}/messages endpoints
- Database session and auth dependencies

**Phase 5: Frontend - OpenAI ChatKit** (14 tasks)
- Install @openai/chatkit dependency
- Configure ChatKit component for chat UI
- Connect ChatKit to backend API
- Conversation history loading
- Error and loading state handling

**Phase 6: Integration & Validation** (13 tasks)
- End-to-end testing for all 5 user stories
- Stateless architecture verification
- MCP server isolation verification
- User data isolation testing
- Phase I/II regression testing

**Architecture Decisions**:
- Stateless backend: fetch/persist to database on every request
- MCP Server as separate process using Official MCP SDK
- FastAPI as MCP client
- OpenAI Agents SDK for agent logic (NO session storage)
- OpenAI ChatKit for frontend (not custom UI)
- Clear separation: FastAPI → Agent → MCP Server → Database

**MVP Strategy**: User Stories 1 + 2 (task creation + viewing) = 45 tasks (58% of total)

**Parallel Opportunities**: 12 tasks marked [P] can run in parallel

## Outcome

- ✅ Impact: Created actionable, dependency-ordered task breakdown for Phase III chatbot implementation with proper stateless architecture and MCP server separation
- 🧪 Tests: Not included per specification requirements
- 📁 Files: Created specs/003-todo-chatbot/tasks.md (78 tasks across 6 phases)
- 🔁 Next prompts: /sp.implement to execute tasks, or manual implementation following task order
- 🧠 Reflection: User guidance was critical to avoid over-engineering. Initial approach incorrectly used Assistants API and custom UI. Corrected to use OpenAI Agents SDK, Official MCP SDK, stateless architecture, and ChatKit. Clear architectural boundaries are essential.

## Evaluation notes (flywheel)

- Failure modes observed:
  1. Initially assumed OpenAI Assistants API instead of OpenAI Agents SDK
  2. Incorrectly planned custom chat UI instead of using ChatKit
  3. Over-engineered with rate limiting, retry logic, performance monitoring
  4. Didn't properly separate MCP server as independent component
- Graders run and results (PASS/FAIL): Manual validation - PASS (all user stories covered, stateless architecture enforced, MCP server separated, scope controlled)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate MCP SDK integration patterns in implementation phase, ensure stateless pattern is strictly followed
