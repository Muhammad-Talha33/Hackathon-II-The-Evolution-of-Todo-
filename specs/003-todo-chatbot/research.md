# Research: Phase III Todo AI Chatbot Technical Architecture

**Feature**: 003-todo-chatbot
**Date**: 2026-01-03
**Status**: Complete

## Overview

This document consolidates research findings for implementing a stateless AI-powered chatbot using OpenAI Agents SDK and Model Context Protocol (MCP) to manage tasks through natural language.

## Technology Decisions

### 1. OpenAI Agents SDK Architecture

**Decision**: Use OpenAI Python SDK's Assistants API (not a separate "Agents SDK") with stateless request pattern

**Rationale**:
- OpenAI's Assistants API supports tool calling (function calling) for integrating with external systems
- Stateless pattern: Store conversation threads in PostgreSQL, pass thread history to API on each request
- Native support for multi-turn conversations through thread management
- Well-documented, production-ready, actively maintained

**Alternatives Considered**:
- LangChain Agents: More complex, additional abstraction layer, overkill for our use case
- Custom NLP: Requires significant ML expertise, lower accuracy, longer development time
- Rasa: Open source but requires training data, complex setup, harder to iterate

**Implementation Approach**:
```python
# Backend pattern (stateless)
@app.post("/api/chat")
async def chat(request: ChatRequest, user: User = Depends(get_current_user)):
    # 1. Retrieve conversation from database
    conversation = await get_or_create_conversation(user.id, request.conversation_id)

    # 2. Retrieve message history from database
    messages = await get_messages(conversation.id)

    # 3. Call OpenAI Assistants API with tools
    response = await openai.beta.threads.messages.create(
        thread_id=conversation.openai_thread_id,
        role="user",
        content=request.message
    )

    run = await openai.beta.threads.runs.create(
        thread_id=conversation.openai_thread_id,
        assistant_id=ASSISTANT_ID,
        tools=[{...MCP tools...}]
    )

    # 4. Save user message and assistant response to database
    await save_message(conversation.id, "user", request.message)
    await save_message(conversation.id, "assistant", assistant_response)

    return ChatResponse(message=assistant_response)
```

**Key Dependencies**:
- `openai>=1.0.0` - OpenAI Python SDK with Assistants API support
- Compatible with Python 3.13+

### 2. Model Context Protocol (MCP) Implementation

**Decision**: Implement MCP tools as FastAPI dependency injection with database access

**Rationale**:
- MCP provides standardized interface for AI agents to interact with external systems
- Tools defined as Python functions with JSON schema for parameters
- Enforcement of user authentication through dependency injection
- Clean separation: agent doesn't access database directly

**Alternatives Considered**:
- Direct database access from agent: Violates specification requirement, security risk
- REST API calls to separate service: Adds network latency, deployment complexity
- GraphQL: Overkill for simple CRUD operations

**Implementation Approach**:
```python
# MCP Tool Definition
async def add_task_tool(
    title: str,
    description: str = "",
    user_id: str = Depends(get_user_from_context)
) -> Dict[str, Any]:
    """
    Add a new task for the authenticated user.

    Args:
        title: Task title (required)
        description: Task description (optional)
        user_id: Injected from authentication context

    Returns:
        Created task with id, title, description, status, timestamps
    """
    async with get_db_session() as db:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            status="incomplete"
        )
        db.add(task)
        await db.commit()
        return task.dict()

# Tool Schema for OpenAI
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"}
                },
                "required": ["title"]
            }
        }
    },
    # ... other tools
]
```

**MCP Tools**:
1. `add_task(title, description)` - Create new task
2. `list_tasks(status)` - Get user's tasks filtered by status
3. `complete_task(task_id)` - Mark task as complete
4. `delete_task(task_id)` - Delete a task
5. `update_task(task_id, title, description)` - Update task details

**Key Dependencies**:
- No additional MCP SDK required - implement as FastAPI functions
- Use OpenAI's native function calling feature

### 3. Frontend: OpenAI ChatKit Integration

**Decision**: Use OpenAI's ChatGPT UI components (if available) or build custom React chat UI with established patterns

**Rationale**:
- OpenAI ChatKit may be enterprise/internal product - research shows no public npm package
- Standard React chat UI patterns are well-established and production-ready
- Full control over authentication, styling, and backend integration

**Alternatives Considered**:
- Stream Chat SDK: Third-party dependency, overkill for simple chat
- Socket.io for real-time: Adds complexity, not needed for request-response pattern
- Server-Sent Events (SSE): Useful for streaming but not required for MVP

**Implementation Approach** (Custom React Chat UI):
```typescript
// frontend/src/components/ChatInterface.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const { getAccessToken } = useAuth();

  async function sendMessage() {
    if (!input.trim()) return;

    setLoading(true);
    try {
      const token = await getAccessToken();
      const response = await api.sendChatMessage(token, {
        message: input,
        conversation_id: currentConversationId
      });

      setMessages([...messages,
        { role: 'user', content: input, ...},
        { role: 'assistant', content: response.message, ...}
      ]);
      setInput('');
    } catch (error) {
      // Error handling
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map(msg => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
      </div>
      <ChatInput
        value={input}
        onChange={setInput}
        onSend={sendMessage}
        disabled={loading}
      />
    </div>
  );
}
```

**Key Dependencies**:
- No special ChatKit dependency - use existing React + TypeScript stack
- Reuse authentication from Phase II (JWT tokens)
- Tailwind CSS for styling (already in project)

### 4. Database Schema for Conversations and Messages

**Decision**: Add two new tables to existing Neon PostgreSQL database using SQLModel

**Rationale**:
- Extends existing database without requiring migration
- SQLModel provides type-safe ORM with Pydantic integration
- Maintains data isolation per user
- Supports conversation threading for context retention

**Schema Design**:
```python
# backend/src/models/conversation.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    openai_thread_id: Optional[str] = None  # For OpenAI Assistants API
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="conversations")

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: str = Field(index=True)  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

### 5. Stateless Conversation Management Pattern

**Decision**: Store all conversation state in PostgreSQL, retrieve on each request

**Pattern**:
1. Client sends message with `conversation_id` (optional on first message)
2. Server retrieves conversation and message history from database
3. Server passes history to OpenAI Assistants API
4. Agent processes message, calls MCP tools as needed
5. Server saves both user message and assistant response to database
6. Server returns assistant response to client

**Benefits**:
- Truly stateless server - can scale horizontally
- Conversation persistence across sessions
- No memory leaks from long-running conversations
- Easy to implement conversation export/archival later

### 6. Rate Limiting Strategy

**Decision**: Implement token bucket rate limiting per user using Redis (or in-memory for MVP)

**Rationale**:
- Prevents abuse and controls OpenAI API costs
- Per-user limits (60 requests/minute from spec)
- Graceful degradation with clear error messages

**Implementation**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=lambda: get_current_user().id)

@app.post("/api/chat")
@limiter.limit("60/minute")
async def chat(request: ChatRequest, user: User = Depends(get_current_user)):
    # ... chat logic
```

**Key Dependencies**:
- `slowapi>=0.1.9` - Rate limiting for FastAPI

### 7. Error Handling and Graceful Degradation

**Decision**: Implement comprehensive error handling at three levels

**Levels**:
1. **MCP Tool Errors**: Catch database/validation errors, return structured error to agent
2. **OpenAI API Errors**: Handle rate limits, timeouts, invalid responses
3. **Client Errors**: Return user-friendly messages, never expose internal details

**Error Response Format**:
```python
class ChatErrorResponse:
    error: str  # User-friendly message
    error_code: str  # Programmatic identifier
    retry_after: Optional[int] = None  # For rate limiting
```

## Architecture Summary

```
┌─────────────┐
│   React     │  Frontend: Custom chat UI with Tailwind CSS
│   Frontend  │  - Message display (user/assistant)
└──────┬──────┘  - Input with send button
       │         - Loading states
       │ HTTPS + JWT
       ▼
┌─────────────┐
│   FastAPI   │  Backend: POST /api/chat (stateless)
│   Backend   │  - Retrieve conversation from PostgreSQL
└──────┬──────┘  - Pass history to OpenAI Assistants API
       │         - Execute MCP tool calls
       │         - Save messages to PostgreSQL
       ▼
┌─────────────┐
│   OpenAI    │  AI Agent: Assistants API
│ Assistants  │  - Natural language understanding
└──────┬──────┘  - Tool calling (MCP tools)
       │         - Response generation
       ▼
┌─────────────┐
│  MCP Tools  │  Database Operations (via FastAPI)
│  (FastAPI)  │  - add_task, list_tasks, complete_task
└──────┬──────┘  - delete_task, update_task
       │         - User authentication enforced
       ▼
┌─────────────┐
│ PostgreSQL  │  Data Storage
│  (Neon)     │  - Users (existing)
└─────────────┘  - Tasks (existing)
                 - Conversations (new)
                 - Messages (new)
```

## Dependencies Summary

**Backend**:
- `openai>=1.0.0` - OpenAI Assistants API
- `slowapi>=0.1.9` - Rate limiting
- `sqlmodel` (existing) - Database ORM
- `fastapi` (existing) - Web framework
- `asyncpg` (existing) - PostgreSQL driver

**Frontend**:
- React 18 (existing)
- TypeScript (existing)
- Tailwind CSS (existing)
- No additional dependencies for chat UI

**Infrastructure**:
- Neon PostgreSQL (existing)
- OpenAI API access (new - requires API key and billing setup)

## Security Considerations

1. **Authentication**: Reuse Phase II JWT authentication
2. **Authorization**: All MCP tools verify user_id matches authenticated user
3. **Rate Limiting**: Per-user limits to prevent abuse
4. **Input Validation**: Sanitize user messages before sending to OpenAI
5. **Error Messages**: Never expose internal errors, database details, or API keys
6. **Logging**: Log chat interactions for debugging but redact sensitive info

## Performance Optimization

1. **Database Indexing**: Index conversation_id, user_id, created_at on messages table
2. **Connection Pooling**: Reuse database connections (already configured in Phase II)
3. **OpenAI API Timeouts**: Set reasonable timeouts (30s) to prevent hanging requests
4. **Message Pagination**: Limit conversation history retrieved (e.g., last 50 messages)
5. **Caching**: Cache frequently used prompts/system messages

## Deployment Considerations

1. **Environment Variables**:
   - `OPENAI_API_KEY` - OpenAI API credentials
   - `OPENAI_ASSISTANT_ID` - Pre-created assistant ID
   - Existing vars from Phase II (DATABASE_URL, JWT_SECRET, etc.)

2. **Database Migration**:
   - Add conversations and messages tables via Alembic migration
   - No changes to existing tables

3. **Backward Compatibility**:
   - Phase I (CLI) and Phase II (Web) remain untouched
   - Chat feature is additive, doesn't modify existing endpoints

## Next Steps

1. Create data-model.md with detailed entity schemas
2. Define API contracts in contracts/ directory
3. Generate tasks.md with implementation steps
4. Begin implementation following TDD approach (tests first)
