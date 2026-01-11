# Implementation Plan: Phase III Todo AI Chatbot (Stateless + MCP)

**Branch**: `003-todo-chatbot` | **Date**: 2026-01-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-todo-chatbot/spec.md`

## Summary

Build a stateless AI-powered chatbot that allows users to manage their todo tasks through natural language conversation. The chatbot uses OpenAI Assistants API for natural language understanding and Model Context Protocol (MCP) tools for database operations. All conversation state is persisted in PostgreSQL, enabling horizontal scaling and session persistence.

**Technical Approach**:
- Backend: FastAPI with stateless POST /api/chat endpoint
- AI: OpenAI Assistants API with function calling
- MCP: Implement 5 tools (add_task, list_tasks, complete_task, delete_task, update_task) as FastAPI functions
- Database: Extend Neon PostgreSQL with Conversation and Message tables
- Frontend: Custom React chat UI with existing authentication

## Technical Context

**Language/Version**: Python 3.13+, TypeScript 5.x
**Primary Dependencies**: OpenAI Python SDK >=1.0.0, FastAPI (existing), SQLModel (existing), React 18 (existing)
**Storage**: Neon PostgreSQL (extend with conversations and messages tables)
**Testing**: pytest (backend), Jest + React Testing Library (frontend)
**Target Platform**: Linux server (Railway), Web browser
**Project Type**: Web (backend + frontend)
**Performance Goals**: <3s response time (95th percentile), 100 concurrent chat sessions
**Constraints**: 60 requests/minute per user (rate limiting), OpenAI API latency ~1-2s
**Scale/Scope**: Support 10K users, ~100 conversations per user, ~10 messages per conversation average

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Alignment with Phase I Constitution

**Principle I: In-Memory Task Management (NON-NEGOTIABLE)**
- ✅ **COMPLIANT**: Phase III does not modify Phase I. Tasks in Phase III are persisted in database (from Phase II), not in memory. Phase I CLI remains unchanged with in-memory storage.

**Principle II: Separation of Concerns**
- ✅ **COMPLIANT**: Clear architectural layers:
  - **API Layer**: FastAPI chat endpoint (stateless orchestration)
  - **AI Agent Layer**: OpenAI Assistants API (natural language processing)
  - **MCP Tools Layer**: Database operations with user authentication
  - **Data Layer**: PostgreSQL with SQLModel ORM

**Principle III: Input Validation and Error Handling (MANDATORY)**
- ✅ **COMPLIANT**:
  - User messages validated (non-empty, max length 10,000 chars)
  - MCP tools validate task_id existence and user ownership
  - All error cases return user-friendly messages
  - Rate limiting prevents abuse

**Principle IV: Deterministic and Explainable Behavior**
- ✅ **COMPLIANT**:
  - All conversation and message records timestamped
  - MCP tool calls logged for debugging
  - Database transactions ensure consistency
  - Agent responses stored in database for auditability

**Principle V: Code Quality and Maintainability**
- ✅ **COMPLIANT**:
  - Type hints for all Python functions (async/await patterns)
  - OpenAPI schema for chat API (self-documenting)
  - SQLModel schemas with validation
  - React components with TypeScript interfaces

### New Principles for Phase III

**Principle VI: Stateless Server Architecture**
- All conversation state MUST be stored in database, not server memory
- Server MUST NOT maintain WebSocket connections or long-polling
- Each request MUST be independently processable

**Rationale**: Enables horizontal scaling, prevents memory leaks, supports load balancing

**Principle VII: MCP-Only Database Access from AI Agent**
- AI agent MUST NOT have direct database connection
- All task operations MUST go through MCP tool functions
- MCP tools MUST enforce user authentication and authorization

**Rationale**: Security isolation, centralized authorization, prevents SQL injection from agent

**Principle VIII: Backward Compatibility**
- Phase I (CLI) and Phase II (Web) MUST remain fully functional
- No modifications to existing Task, User models or auth endpoints
- Chat feature is purely additive

**Rationale**: Protects existing functionality, enables incremental rollout

### Constitution Compliance Summary

**PASS**: All Phase I principles respected, new Phase III principles align with existing architecture.

No complexity violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/003-todo-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 research findings (completed)
├── data-model.md        # Phase 1 data model design (completed)
├── quickstart.md        # Phase 1 integration examples (completed)
├── contracts/           # Phase 1 API contracts (completed)
│   └── chat-api.yaml    # OpenAPI spec for chat endpoints
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created yet)
```

### Source Code (repository root)

**Backend Extensions** (existing backend/ directory):

```text
backend/
├── src/
│   ├── api/
│   │   ├── chat.py          # NEW: POST /api/chat endpoint
│   │   ├── conversations.py # NEW: GET /api/conversations endpoints
│   │   └── ... (existing Phase II endpoints)
│   ├── models/
│   │   ├── conversation.py  # NEW: Conversation SQLModel
│   │   ├── message.py       # NEW: Message SQLModel
│   │   ├── task.py          # EXISTING: No changes
│   │   └── user.py          # EXISTING: Add conversations relationship
│   ├── tools/
│   │   └── mcp.py           # NEW: MCP tool definitions and execution
│   ├── schemas/
│   │   └── chat.py          # NEW: Pydantic schemas for chat API
│   ├── services/
│   │   ├── chat_service.py  # NEW: Chat business logic
│   │   └── openai_client.py # NEW: OpenAI API wrapper
│   ├── database.py          # EXISTING: No changes
│   ├── auth.py              # EXISTING: Reused for chat authentication
│   └── main.py              # EXISTING: Register new chat routers
├── alembic/
│   └── versions/
│       └── xxx_add_conversations_messages.py # NEW: Database migration
├── tests/
│   ├── test_chat_api.py     # NEW: Chat endpoint tests
│   ├── test_mcp_tools.py    # NEW: MCP tool tests
│   └── ... (existing tests)
└── requirements.txt         # EXTEND: Add openai>=1.0.0, slowapi>=0.1.9
```

**Frontend Extensions** (existing frontend/ directory):

```text
frontend/
├── src/
│   ├── components/
│   │   ├── chat/            # NEW: Chat UI components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── ConversationList.tsx
│   │   └── ... (existing components)
│   ├── pages/
│   │   ├── chat.tsx         # NEW: Chat page route
│   │   └── ... (existing pages)
│   ├── lib/
│   │   └── api.ts           # EXTEND: Add chat API methods
│   ├── contexts/
│   │   └── AuthContext.tsx  # EXISTING: Reused for chat auth
│   └── types/
│       └── chat.ts          # NEW: TypeScript interfaces for chat
├── tests/
│   └── chat/                # NEW: Chat component tests
└── package.json             # No new dependencies needed
```

**Structure Decision**:
- **Web application structure (Option 2)** with backend/ and frontend/ directories
- New chat feature is implemented as additional modules within existing structure
- No new top-level directories required - extends Phase II architecture
- Database migrations handled via Alembic (existing tool)

## Complexity Tracking

**No violations requiring justification** - all complexity aligns with constitution principles.

## Phase 0: Research *(Completed)*

See [research.md](./research.md) for detailed findings.

**Key Decisions**:
- Use OpenAI Assistants API (not separate Agents SDK)
- Implement MCP tools as FastAPI dependency injection functions
- Build custom React chat UI (no OpenAI ChatKit dependency found)
- Store conversations and messages in PostgreSQL with indexed queries
- Use slowapi for rate limiting (60 req/min per user)

## Phase 1: Design *(Completed)*

### Data Model

See [data-model.md](./data-model.md) for complete entity schemas.

**New Entities**:
1. **Conversation**: Links user to OpenAI thread, tracks creation/update times
2. **Message**: Stores user and assistant messages chronologically

**Relationships**:
- User → Conversation (1:N)
- Conversation → Message (1:N)
- Task accessed via MCP tools only (no direct relationship to Conversation)

### API Contracts

See [contracts/chat-api.yaml](./contracts/chat-api.yaml) for OpenAPI specification.

**Endpoints**:
1. `POST /api/chat` - Send message, get AI response
2. `GET /api/conversations` - List user's conversations
3. `GET /api/conversations/{id}/messages` - Get conversation history

### Integration Patterns

See [quickstart.md](./quickstart.md) for code examples.

**Scenarios Covered**:
1. User creates task via chat
2. User lists tasks
3. User completes task
4. Multi-turn conversation with context

## Phase 2: File Structure & Implementation Order

### Backend Implementation Order

**Iteration 1: Database Foundation**
1. `backend/src/models/conversation.py` - Conversation SQLModel
2. `backend/src/models/message.py` - Message SQLModel
3. `backend/src/models/user.py` - Add conversations relationship
4. `backend/alembic/versions/xxx_add_conversations_messages.py` - Migration script
5. Run migration: `alembic upgrade head`

**Iteration 2: MCP Tools**
6. `backend/src/tools/mcp.py` - Define 5 MCP tools:
   - `add_task(title, description)` → Creates Task
   - `list_tasks(status)` → Queries Tasks with optional filter
   - `complete_task(task_id)` → Updates Task.status to 'complete'
   - `delete_task(task_id)` → Deletes Task
   - `update_task(task_id, title, description)` → Updates Task fields
7. `backend/tests/test_mcp_tools.py` - Unit tests for each tool

**Iteration 3: OpenAI Integration**
8. `backend/src/services/openai_client.py` - Wrapper for OpenAI Assistants API:
   - `create_thread()` → Initialize conversation
   - `send_message(thread_id, content)` → Add user message
   - `run_assistant(thread_id, tools)` → Execute with MCP tools
   - `handle_tool_calls(run, user_id, db)` → Execute MCP functions
9. `backend/src/services/chat_service.py` - Business logic:
   - `get_or_create_conversation(user_id, conversation_id)`
   - `save_messages(conversation_id, user_msg, assistant_msg)`
   - `process_chat_message(user_id, message, conversation_id)`

**Iteration 4: API Endpoints**
10. `backend/src/schemas/chat.py` - Pydantic request/response models
11. `backend/src/api/chat.py` - POST /api/chat endpoint
12. `backend/src/api/conversations.py` - GET conversations endpoints
13. `backend/src/main.py` - Register new routers
14. `backend/tests/test_chat_api.py` - Integration tests

**Iteration 5: Rate Limiting & Error Handling**
15. Add slowapi to `backend/requirements.txt`
16. Configure rate limiting in `backend/src/api/chat.py`
17. Implement error handling middleware
18. Add logging for chat interactions

### Frontend Implementation Order

**Iteration 6: Chat UI Components**
19. `frontend/src/types/chat.ts` - TypeScript interfaces
20. `frontend/src/components/chat/ChatMessage.tsx` - Message bubble component
21. `frontend/src/components/chat/ChatInput.tsx` - Input field with send button
22. `frontend/src/components/chat/ChatInterface.tsx` - Main chat container
23. `frontend/src/components/chat/ConversationList.tsx` - Sidebar with conversation history

**Iteration 7: API Integration**
24. `frontend/src/lib/api.ts` - Extend with chat methods:
    - `sendChatMessage(token, request)`
    - `getConversations(token)`
    - `getConversationMessages(token, conversationId)`
25. `frontend/src/pages/chat.tsx` - Chat page route
26. Update navigation to include chat link

**Iteration 8: Styling & Polish**
27. Add Tailwind CSS classes to chat components
28. Implement loading states and error messages
29. Add message timestamps and read indicators
30. Responsive design for mobile

**Iteration 9: Testing**
31. `frontend/tests/chat/ChatInterface.test.tsx` - Component tests
32. `frontend/tests/chat/ChatMessage.test.tsx` - Message rendering tests
33. Manual end-to-end testing

### Environment Setup

**New Environment Variables**:
```bash
# backend/.env
OPENAI_API_KEY=sk-...
OPENAI_ASSISTANT_ID=asst_...

# Existing vars (no changes)
DATABASE_URL=postgresql://...
JWT_SECRET=...
```

**OpenAI Assistant Creation** (one-time setup):
```bash
curl https://api.openai.com/v1/assistants \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-turbo-preview",
    "name": "Todo Assistant",
    "instructions": "You are a helpful assistant that manages todo tasks. Use the provided tools to help users create, view, complete, update, and delete their tasks. Always confirm actions and provide friendly responses."
  }'
```

## Testing Strategy

### Backend Tests

**Unit Tests** (pytest):
1. MCP tool functions (mock database)
2. Chat service logic (mock OpenAI API)
3. Pydantic schema validation

**Integration Tests** (pytest + TestClient):
1. POST /api/chat with mock OpenAI responses
2. Conversation creation and retrieval
3. Message persistence
4. Rate limiting behavior
5. Authentication/authorization

**Contract Tests**:
1. OpenAPI schema validation
2. Request/response format compliance

### Frontend Tests

**Component Tests** (Jest + RTL):
1. ChatMessage rendering (user vs assistant)
2. ChatInput send functionality
3. ChatInterface state management
4. Error message display

**Integration Tests**:
1. Full chat flow (mock API)
2. Conversation switching
3. Message history loading

### Manual Testing Scenarios

1. Create task via chat → Verify in Phase II web UI
2. Update task in web UI → Verify reflected in chat
3. Multi-turn conversation with context
4. Rate limiting (send 61 messages in 1 minute)
5. Concurrent users (simulate with multiple browser tabs)

## Deployment Checklist

### Prerequisites
- [ ] OpenAI API key obtained
- [ ] OpenAI Assistant created and ID recorded
- [ ] Database migration tested locally
- [ ] Environment variables configured in Railway

### Backend Deployment
- [ ] Update `backend/requirements.txt` with new dependencies
- [ ] Run database migration on production: `alembic upgrade head`
- [ ] Set `OPENAI_API_KEY` and `OPENAI_ASSISTANT_ID` in Railway
- [ ] Deploy backend to Railway
- [ ] Verify health check endpoint
- [ ] Test POST /api/chat with curl

### Frontend Deployment
- [ ] No changes to frontend/.env.local needed (uses existing NEXT_PUBLIC_API_URL)
- [ ] Deploy frontend to Vercel
- [ ] Verify chat page renders
- [ ] Test chat functionality end-to-end

### Post-Deployment Validation
- [ ] Create conversation via chat
- [ ] Verify task created in database
- [ ] Check conversation and messages saved
- [ ] Monitor OpenAI API usage and costs
- [ ] Review logs for errors
- [ ] Test rate limiting with rapid requests

## Risk Mitigation

### Risk 1: OpenAI API Costs
**Mitigation**:
- Implement strict rate limiting (60 req/min per user)
- Set OpenAI API spending limits
- Monitor usage via OpenAI dashboard
- Cache assistant responses where possible

### Risk 2: OpenAI API Latency
**Mitigation**:
- Set 30s timeout on API requests
- Show loading indicators to users
- Implement retry logic with exponential backoff
- Provide fallback message on timeout

### Risk 3: Agent Misinterpretation
**Mitigation**:
- Comprehensive assistant instructions
- Always confirm task operations before executing
- Provide examples in assistant training
- Log all agent interactions for improvement

### Risk 4: Database Performance
**Mitigation**:
- Index conversation_id and created_at on messages table
- Limit message history retrieval (last 50 messages)
- Use connection pooling (already configured)
- Monitor query performance

### Risk 5: Conversation Data Growth
**Mitigation**:
- Track database size in production
- Plan archival strategy if messages exceed 1M
- Implement message pagination in UI
- Consider message retention policy (e.g., 6 months)

## Success Metrics

Track these metrics post-deployment:

**Performance**:
- P95 response time < 3 seconds ✓
- 100 concurrent chat sessions without degradation ✓
- Database query time < 100ms ✓

**Accuracy**:
- 90% of user intents correctly interpreted ✓
- Zero unauthorized access incidents ✓
- 100% of ambiguous requests get clarification ✓

**Reliability**:
- 99.9% uptime (excluding OpenAI outages)
- Graceful error handling in 100% of failure cases ✓
- Zero data loss incidents ✓

**User Experience**:
- Task creation in < 10 seconds ✓
- Conversation history persists across sessions ✓
- Multi-turn context maintained for 5+ messages ✓

## Phase 3: Implementation Tasks

**Next Command**: `/sp.tasks` to generate detailed, testable task breakdown.

The `/sp.tasks` command will create `tasks.md` with:
- Dependency-ordered task list
- Acceptance criteria for each task
- Test cases for validation
- Estimated complexity
- Phase grouping (Setup, Core, Integration, Polish)

---

**Plan Status**: ✅ Complete
**Ready For**: `/sp.tasks` command to generate implementation task list
