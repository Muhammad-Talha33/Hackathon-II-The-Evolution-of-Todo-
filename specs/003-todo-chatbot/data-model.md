# Data Model: Phase III Todo AI Chatbot

**Feature**: 003-todo-chatbot
**Date**: 2026-01-03
**Status**: Complete

## Overview

This document defines the data entities for the AI chatbot feature. The chatbot extends the existing Phase II data model by adding conversation and message tracking while maintaining full compatibility with existing Task and User entities.

## Entity Relationship Diagram

```
┌──────────────┐
│     User     │ (Existing from Phase II)
│              │
│ - id         │
│ - email      │
│ - password   │
└──────┬───────┘
       │
       │ 1:N (one user has many conversations)
       │
       ▼
┌──────────────┐
│ Conversation │ (New in Phase III)
│              │
│ - id         │
│ - user_id    ├──────────┐
│ - thread_id  │          │
│ - created_at │          │ 1:N (one conversation has many messages)
│ - updated_at │          │
└──────────────┘          │
                          ▼
                   ┌──────────────┐
                   │   Message    │ (New in Phase III)
                   │              │
                   │ - id         │
                   │ - conv_id    │
                   │ - role       │
                   │ - content    │
                   │ - created_at │
                   └──────────────┘

┌──────────────┐
│     Task     │ (Existing from Phase I/II)
│              │
│ - id         │  ← Accessed via MCP tools only
│ - user_id    │
│ - title      │
│ - description│
│ - status     │
│ - created_at │
│ - updated_at │
└──────────────┘
```

## Entities

### 1. Conversation (New)

Represents a chat session between a user and the AI agent.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique conversation identifier |
| user_id | UUID | FOREIGN KEY → users.id, NOT NULL, INDEXED | Owner of the conversation |
| openai_thread_id | String | NULLABLE, UNIQUE | OpenAI Assistants API thread identifier |
| created_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When conversation started |
| updated_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last message timestamp |

**Relationships**:
- `user`: Many-to-One → User (one conversation belongs to one user)
- `messages`: One-to-Many → Message (one conversation has many messages)

**Indexes**:
- `idx_conversation_user_id` on `user_id` (for fetching user's conversations)
- `idx_conversation_updated_at` on `updated_at` (for sorting by recent activity)

**Business Rules**:
- Each conversation is owned by exactly one user
- Conversations are never deleted (soft delete if needed in future)
- `updated_at` is updated whenever a new message is added
- `openai_thread_id` is created on first message and reused for thread continuity

**Validation**:
- `user_id` must reference an existing user
- `openai_thread_id` is managed by backend, not user-provided

**Example**:
```python
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "openai_thread_id": "thread_abc123xyz789",
  "created_at": "2026-01-03T10:30:00Z",
  "updated_at": "2026-01-03T10:35:00Z"
}
```

---

### 2. Message (New)

Represents a single message in a conversation (either from user or assistant).

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique message identifier |
| conversation_id | UUID | FOREIGN KEY → conversations.id, NOT NULL, INDEXED | Parent conversation |
| role | Enum | NOT NULL, CHECK (role IN ('user', 'assistant')) | Message sender |
| content | Text | NOT NULL | Message text content |
| created_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP, INDEXED | When message was sent |

**Relationships**:
- `conversation`: Many-to-One → Conversation (many messages belong to one conversation)

**Indexes**:
- `idx_message_conversation_id` on `conversation_id` (for retrieving conversation history)
- `idx_message_created_at` on `created_at` (for chronological ordering)
- Composite index `idx_message_conv_created` on `(conversation_id, created_at)` (for paginated history retrieval)

**Business Rules**:
- Messages are immutable once created (no updates or deletes)
- Messages are always associated with a conversation
- `role` alternates between 'user' and 'assistant' in well-formed conversations
- Messages are ordered chronologically within a conversation

**Validation**:
- `role` must be exactly 'user' or 'assistant'
- `content` must not be empty
- `conversation_id` must reference an existing conversation
- `content` maximum length: 10,000 characters (prevent abuse)

**Example**:
```python
{
  "id": "650e8400-e29b-41d4-a716-446655440001",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "user",
  "content": "Add buy groceries to my tasks",
  "created_at": "2026-01-03T10:30:15Z"
}

{
  "id": "650e8400-e29b-41d4-a716-446655440002",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "assistant",
  "content": "I've added 'buy groceries' to your tasks. Your task list now has 3 incomplete items.",
  "created_at": "2026-01-03T10:30:18Z"
}
```

---

### 3. Task (Existing - No Changes)

Represents a user's todo item. Accessed exclusively through MCP tools by the AI agent.

**Fields** (for reference):

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique task identifier |
| user_id | UUID | FOREIGN KEY → users.id, NOT NULL | Task owner |
| title | String | NOT NULL | Task title |
| description | Text | NULLABLE | Task details |
| status | Enum | NOT NULL, CHECK (status IN ('incomplete', 'complete')) | Task status |
| created_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When task was created |
| updated_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification |

**Access Pattern for Phase III**:
- Direct database queries are prohibited for the AI agent
- All task operations go through MCP tools:
  - `add_task(title, description)` → Creates Task
  - `list_tasks(status)` → Queries Tasks
  - `complete_task(task_id)` → Updates Task.status
  - `update_task(task_id, title, description)` → Updates Task
  - `delete_task(task_id)` → Deletes Task

---

### 4. User (Existing - Extended Relationships)

Represents an authenticated user. No schema changes, only relationship updates.

**New Relationships**:
- `conversations`: One-to-Many → Conversation (one user has many conversations)

**No Schema Changes Required** - relationships managed in SQLModel via backref.

---

## State Transitions

### Conversation State Machine

```
[New User Session]
       │
       ▼
[Create Conversation]
       │
       ├──> (openai_thread_id = null)
       │
       ▼
[User sends first message]
       │
       ├──> Create OpenAI thread
       ├──> Set openai_thread_id
       ├──> Save user message
       ├──> Get assistant response
       ├──> Save assistant message
       ▼
[Conversation Active]
       │
       ├──> User sends message
       ├──> Retrieve conversation history
       ├──> Send to OpenAI with thread_id
       ├──> Save messages
       ├──> Update conversation.updated_at
       │
       └──> (Repeat)
```

### Message Flow

```
User Input
    │
    ▼
[Validate & Authenticate]
    │
    ▼
[Get or Create Conversation]
    │
    ▼
[Retrieve Message History]
    │ (last 50 messages for context)
    ▼
[Send to OpenAI Assistants API]
    │ (with thread_id and tools)
    ▼
[Agent Processes & Calls MCP Tools]
    │
    ├──> add_task() → Creates Task in DB
    ├──> list_tasks() → Queries Tasks
    ├──> complete_task() → Updates Task
    └──> etc.
    │
    ▼
[Get Assistant Response]
    │
    ▼
[Save User Message to DB]
    │
    ▼
[Save Assistant Message to DB]
    │
    ▼
[Update Conversation.updated_at]
    │
    ▼
[Return Response to Client]
```

## Database Migration

### New Tables SQL (PostgreSQL)

```sql
-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    openai_thread_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversation_user_id ON conversations(user_id);
CREATE INDEX idx_conversation_updated_at ON conversations(updated_at);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_message_conversation_id ON messages(conversation_id);
CREATE INDEX idx_message_created_at ON messages(created_at);
CREATE INDEX idx_message_conv_created ON messages(conversation_id, created_at);

-- Trigger to update conversation.updated_at when message is added
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = NEW.created_at
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();
```

### SQLModel Schemas (Python)

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
    openai_thread_id: Optional[str] = Field(default=None, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    user: "User" = Relationship(back_populates="conversations")


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: str = Field(index=True, regex="^(user|assistant)$")
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")


# Update to existing User model (add relationship only)
class User(SQLModel, table=True):
    # ... existing fields ...

    # New relationship
    conversations: List[Conversation] = Relationship(back_populates="user")
```

## Data Integrity Rules

1. **Referential Integrity**:
   - All `conversation.user_id` must reference existing `users.id`
   - All `message.conversation_id` must reference existing `conversations.id`
   - Deleting a conversation cascades to delete all messages
   - Deleting a user cascades to delete all conversations (and messages)

2. **Temporal Integrity**:
   - `message.created_at` must be >= `conversation.created_at`
   - `conversation.updated_at` must be >= `conversation.created_at`
   - Messages in a conversation are ordered by `created_at` ascending

3. **Authorization**:
   - Users can only access their own conversations
   - Users can only view/create messages in their own conversations
   - MCP tools enforce user_id matches authenticated user

## Performance Considerations

1. **Indexing**:
   - Composite index on `(conversation_id, created_at)` for fast history retrieval
   - Index on `user_id` for listing user's conversations
   - Index on `updated_at` for sorting conversations by recent activity

2. **Query Optimization**:
   - Limit message history retrieval (e.g., last 50 messages) to avoid large payloads
   - Use `SELECT COUNT(*)` for pagination instead of loading all messages
   - Consider partitioning messages table by date if volume grows large

3. **Data Growth**:
   - Expected: ~10 messages per conversation average
   - Storage: ~1KB per message (text content)
   - With 10K users, 100 conversations each: ~10M messages = ~10GB storage (manageable)

## Data Retention Policy

**For MVP**:
- Conversations and messages are retained indefinitely
- No automatic archival or deletion

**Future Considerations**:
- Archive conversations older than 6 months to cold storage
- Delete conversations with no messages after 30 days
- Implement soft delete for user-requested deletions
