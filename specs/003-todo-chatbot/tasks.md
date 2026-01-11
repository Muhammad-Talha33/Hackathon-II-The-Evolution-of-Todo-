# Tasks: Todo AI Chatbot (Phase III)

**Input**: Design documents from `/specs/003-todo-chatbot/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/chat-api.yaml

**Architecture**: Stateless backend with clear separation: FastAPI → Agent → MCP Server → Database

**Organization**: Tasks are grouped by architectural layer to enable clean implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Web application with `backend/` and `frontend/` directories at repository root.

---

## Phase 1: Database & Models

**Purpose**: Extend database schema to support conversation persistence (stateless backend requirement)

- [X] T001 [P] Create Conversation SQLModel in backend/src/models/conversation.py with fields: id, user_id, created_at, updated_at
- [X] T002 [P] Create Message SQLModel in backend/src/models/message.py with fields: id, conversation_id, role, content, created_at
- [X] T003 Update User model in backend/src/models/user.py to add conversations relationship
- [X] T004 Create Alembic migration script in backend/alembic/versions/ to add conversations and messages tables with indexes
- [X] T005 Run Alembic migration: alembic upgrade head
- [X] T006 Verify tables exist in Neon PostgreSQL console

**Checkpoint**: Database schema ready - conversations and messages tables exist

---

## Phase 2: MCP Server (using Official MCP SDK)

**Purpose**: Build MCP server that exposes task operations as tools

**Architecture**: MCP Server runs as separate process/service, uses Official MCP SDK

- [X] T007 Add mcp dependency to backend/requirements.txt (official MCP Python SDK)
- [X] T008 Install dependencies: pip install -r backend/requirements.txt
- [X] T009 Create backend/src/mcp_server/ directory for MCP server implementation
- [X] T010 Create MCP server initialization in backend/src/mcp_server/server.py using FastMCP or mcp.server
- [X] T011 [P] [US1] Implement add_task tool in backend/src/mcp_server/tools/task_tools.py that creates Task with user_id, title, description
- [X] T012 [P] [US2] Implement list_tasks tool in backend/src/mcp_server/tools/task_tools.py that queries Tasks by user_id with optional status filter
- [X] T013 [P] [US3] Implement complete_task tool in backend/src/mcp_server/tools/task_tools.py that updates Task.status to 'complete'
- [X] T014 [P] [US4] Implement delete_task tool in backend/src/mcp_server/tools/task_tools.py that removes Task by id
- [X] T015 [P] [US4] Implement update_task tool in backend/src/mcp_server/tools/task_tools.py that updates Task.title and Task.description
- [X] T016 Register all 5 tools with MCP server in backend/src/mcp_server/server.py
- [X] T017 Add database session injection to MCP server tools for database access
- [X] T018 Add user_id parameter validation to all MCP tools to enforce data isolation
- [X] T019 Create MCP server startup script in backend/src/mcp_server/main.py
- [X] T020 Add OPENAI_API_KEY to backend/.env file

**Checkpoint**: MCP server can run independently and expose 5 task management tools

---

## Phase 3: Agent Logic (OpenAI Agents SDK - Stateless)

**Purpose**: Create agent that interprets natural language and calls MCP tools

**CRITICAL**: Agent must be stateless - NO session storage, reconstruct context from database each request

- [X] T021 Add openai-agents dependency to backend/requirements.txt
- [X] T022 Install dependencies: pip install -r backend/requirements.txt
- [X] T023 Create backend/src/agents/ directory for agent configuration
- [X] T024 [US1] Create TodoAgent class in backend/src/agents/todo_agent.py with instructions for task creation
- [X] T025 [US2] Update TodoAgent instructions to include task listing and formatting guidance
- [X] T026 [US3] Update TodoAgent instructions to include task completion examples
- [X] T027 [US4] Update TodoAgent instructions to include deletion and update examples
- [X] T028 [US5] Update TodoAgent instructions for multi-turn context handling
- [X] T029 Configure agent to use MCP tools (connect agent to MCP server)
- [X] T030 Implement get_agent() factory function in backend/src/agents/todo_agent.py that returns stateless Agent instance
- [X] T031 Add error handling for MCP tool call failures in agent configuration

**Checkpoint**: Agent can interpret natural language and call MCP tools (tested via Runner)

---

## Phase 4: FastAPI Chat Endpoint (MCP Client)

**Purpose**: Stateless REST API that fetches conversation history, calls agent, persists messages

**Architecture**: FastAPI acts as MCP client, fetches state from DB every request

- [X] T032 Create backend/src/schemas/chat.py for Pydantic request/response models
- [X] T033 [P] [US1] Create ChatRequest schema in backend/src/schemas/chat.py with fields: message (str, max 10000), conversation_id (Optional[str])
- [X] T034 [P] [US1] Create ChatResponse schema in backend/src/schemas/chat.py with fields: conversation_id (str), message (str), created_at (datetime)
- [X] T035 Create backend/src/services/chat_service.py for chat orchestration logic
- [X] T036 [US1] Implement get_or_create_conversation() in backend/src/services/chat_service.py to fetch or create conversation by user_id
- [X] T037 [US5] Implement load_conversation_history() in backend/src/services/chat_service.py to fetch last 50 messages from database
- [X] T038 [US1] Implement save_message() in backend/src/services/chat_service.py to persist user and assistant messages
- [X] T039 [US1] Implement process_chat_message() in backend/src/services/chat_service.py that: 1) loads history from DB, 2) calls agent via Runner, 3) saves messages
- [X] T040 Ensure process_chat_message() is fully stateless - no session storage, reconstruct context every call
- [X] T041 Create backend/src/api/chat.py for chat endpoint
- [X] T042 [US1] Implement POST /api/chat endpoint in backend/src/api/chat.py using ChatRequest/ChatResponse schemas
- [X] T043 Add JWT authentication dependency to chat endpoint to get current user
- [X] T044 Add database session dependency to chat endpoint
- [X] T045 Connect chat endpoint to chat_service.process_chat_message()
- [X] T046 Add error handling for agent failures and MCP server errors in chat endpoint
- [X] T047 Register chat router in backend/src/main.py
- [X] T048 [P] [US5] Create GET /api/conversations endpoint in backend/src/api/conversations.py to list user's conversations
- [X] T049 [P] [US5] Create GET /api/conversations/{id}/messages endpoint to retrieve message history
- [X] T050 [US5] Create ConversationSummary schema in backend/src/schemas/chat.py
- [X] T051 [US5] Register conversations router in backend/src/main.py

**Checkpoint**: Backend API is fully functional and stateless - can create tasks, view tasks, complete tasks, delete tasks, update tasks via natural language

---

## Phase 5: Frontend (OpenAI ChatKit)

**Purpose**: Integrate OpenAI ChatKit for chat UI

**CRITICAL**: Use ChatKit for UI, do NOT build custom chat components

- [ ] T052 Add @openai/chatkit dependency to frontend/package.json
- [ ] T053 Install frontend dependencies: npm install
- [ ] T054 [US1] Create chat page in frontend/src/app/chat/page.tsx
- [ ] T055 [US1] Import and configure ChatKit component in chat page
- [ ] T056 [US1] Connect ChatKit to POST /api/chat endpoint in frontend/src/lib/api.ts
- [ ] T057 [US1] Add sendChatMessage API method in frontend/src/lib/api.ts
- [ ] T058 [US1] Pass user authentication token to chat API calls
- [ ] T059 [US1] Handle ChatKit message submission and response rendering
- [ ] T060 [US5] Add getConversations API method in frontend/src/lib/api.ts
- [ ] T061 [US5] Add getConversationMessages API method in frontend/src/lib/api.ts
- [ ] T062 [US5] Implement conversation history loading in ChatKit configuration
- [ ] T063 Add chat navigation link to main navigation in frontend
- [ ] T064 Add loading state handling in ChatKit configuration
- [ ] T065 Add error message display in ChatKit configuration

**Checkpoint**: Frontend chat UI is functional with OpenAI ChatKit, users can interact with agent

---

## Phase 6: Integration & Validation

**Purpose**: Test end-to-end flows for all user stories

- [ ] T066 [US1] Test: Send "Add buy groceries to my tasks" → verify task created in database
- [ ] T067 [US1] Test: Verify confirmation message returned from agent
- [ ] T068 [US2] Test: Send "Show me my tasks" → verify task list returned in conversational format
- [ ] T069 [US2] Test: Verify empty state response when user has no tasks
- [ ] T070 [US3] Test: Send "Mark the grocery task as done" → verify task status updated to complete
- [ ] T071 [US4] Test: Send "Delete the grocery task" → verify task removed from database
- [ ] T072 [US4] Test: Send "Change report task to presentation task" → verify task title updated
- [ ] T073 [US5] Test: Multi-turn conversation - send "Add buy groceries" then "And also get milk" → verify both tasks created
- [ ] T074 [US5] Test: Conversation persistence - create conversation, logout, login, resume conversation
- [ ] T075 Test: Verify stateless backend - restart backend server, verify conversations persist from database
- [ ] T076 Test: Verify MCP server isolation - agent cannot access database directly, only via tools
- [ ] T077 Test: Verify user data isolation - user A cannot access user B's tasks via chat
- [ ] T078 Verify Phase I CLI and Phase II Web UI still function correctly (no regressions)

**Checkpoint**: All user stories validated, stateless architecture verified, Phase I/II unchanged

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Database & Models)**: No dependencies - can start immediately
- **Phase 2 (MCP Server)**: Depends on Phase 1 (needs database models)
- **Phase 3 (Agent Logic)**: Depends on Phase 2 (needs MCP server tools)
- **Phase 4 (FastAPI Endpoint)**: Depends on Phase 1 and Phase 3 (needs models and agent)
- **Phase 5 (Frontend)**: Depends on Phase 4 (needs backend API)
- **Phase 6 (Integration)**: Depends on all previous phases

### User Story Mapping

**User Story 1 (P1 - Task Creation)**:
- Database: T001-T006
- MCP Server: T011 (add_task tool)
- Agent: T024, T030
- Backend: T033-T034, T036, T038-T047
- Frontend: T054-T059
- Validation: T066-T067

**User Story 2 (P1 - Task Viewing)**:
- MCP Server: T012 (list_tasks tool)
- Agent: T025
- Validation: T068-T069

**User Story 3 (P2 - Task Completion)**:
- MCP Server: T013 (complete_task tool)
- Agent: T026
- Validation: T070

**User Story 4 (P3 - Delete/Update)**:
- MCP Server: T014-T015 (delete_task, update_task tools)
- Agent: T027
- Validation: T071-T072

**User Story 5 (P3 - Multi-Turn Context)**:
- Backend: T037, T048-T051
- Agent: T028
- Frontend: T060-T062
- Validation: T073-T075

### Parallel Opportunities

**Within Phase 1 (Database)**:
- T001-T002: Models can be created in parallel

**Within Phase 2 (MCP Server)**:
- T011-T015: All 5 MCP tools can be implemented in parallel

**Within Phase 4 (Backend)**:
- T033-T034: Schemas can be created in parallel
- T048-T049: Conversation endpoints can be created in parallel

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only) - Recommended

1. **Phase 1**: Complete database setup (T001-T006)
2. **Phase 2**: Build MCP server with add_task and list_tasks tools only (T007-T012, T016-T020)
3. **Phase 3**: Create agent with basic instructions (T021-T025, T029-T031)
4. **Phase 4**: Build stateless chat endpoint (T032-T047)
5. **Phase 5**: Integrate ChatKit frontend (T052-T065)
6. **Phase 6**: Validate US1 and US2 (T066-T069)
7. **STOP and VALIDATE**: Test task creation and viewing via chat
8. Deploy MVP if ready

**MVP delivers**: Hands-free task capture and viewing via natural language chat

### Incremental Delivery (All User Stories)

After MVP:
1. Add complete_task tool + validation (T013, T026, T070)
2. Add delete_task and update_task tools + validation (T014-T015, T027, T071-T072)
3. Add multi-turn context support (T037, T048-T051, T060-T062, T073-T075)
4. Final integration testing (T076-T078)

---

## Task Count Summary

- **Phase 1 (Database & Models)**: 6 tasks
- **Phase 2 (MCP Server)**: 14 tasks
- **Phase 3 (Agent Logic)**: 11 tasks
- **Phase 4 (FastAPI Endpoint)**: 20 tasks
- **Phase 5 (Frontend - ChatKit)**: 14 tasks
- **Phase 6 (Integration & Validation)**: 13 tasks
- **Total**: 78 tasks

**MVP Scope (US1 + US2)**: ~45 tasks (58% of total)
**Full Feature**: 78 tasks

**Parallel Opportunities**: 12 tasks marked [P] can run in parallel

---

## Architecture Notes

### Stateless Backend (Critical)

- **Every request**: Fetch conversation + messages from database
- **Every request**: Reconstruct agent context from database history
- **Every request**: Persist new messages to database
- **NO session storage**: Agent must not use OpenAI Agents SDK session/memory features
- **NO in-memory state**: Backend can restart without losing conversations

### MCP Server Separation

- **MCP Server**: Separate process using Official MCP SDK (`mcp` package)
- **FastAPI**: Acts as MCP client, calls MCP server tools
- **Boundary**: FastAPI → Agent → MCP Server → Database
- **Agent**: Never touches database directly, only through MCP tools
- **Tools**: add_task, list_tasks, complete_task, delete_task, update_task

### OpenAI ChatKit Frontend

- **ChatKit**: Official OpenAI React library for chat UI
- **NO custom UI**: Use ChatKit components for message rendering
- **Backend**: Only provides POST /api/chat endpoint
- **Integration**: Connect ChatKit to backend API endpoint

### Phase Integrity

- **Phase I (CLI)**: NOT modified - remains functional
- **Phase II (Web)**: NOT modified - remains functional
- **Phase III (Chatbot)**: Purely additive - new tables, new endpoints, new UI page
- **Backward Compatibility**: All existing features continue to work

---

## Key Dependencies

**Backend**:
- `openai-agents` - OpenAI Agents SDK for agent logic
- `mcp` - Official MCP Python SDK for MCP server
- `sqlmodel` (existing) - Database ORM
- `fastapi` (existing) - REST API framework
- `alembic` (existing) - Database migrations

**Frontend**:
- `@openai/chatkit` - OpenAI ChatKit React library for chat UI
- `react` (existing) - Frontend framework
- `next.js` (existing) - React framework

**External**:
- OpenAI API - Agent natural language processing
- Neon PostgreSQL (existing) - Database for conversations and messages

---

## Sources

- [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Package on PyPI](https://pypi.org/project/mcp/)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/docs/sdk)
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
