# Quickstart: Phase III Todo AI Chatbot

**Feature**: 003-todo-chatbot
**Date**: 2026-01-03
**Audience**: Developers implementing the chatbot feature

## Overview

This guide provides quick-start examples for the most common integration scenarios when building the AI chatbot feature. It demonstrates end-to-end flows from user input to database updates via MCP tools.

## Prerequisites

- Phase II backend and database running
- OpenAI API key with Assistants API access
- Python 3.13+ environment
- PostgreSQL database with conversations and messages tables

## Scenario 1: User Creates a Task via Chat

**User Flow**: User types "Add buy groceries to my tasks" → Task is created → Confirmation shown

### Frontend (React + TypeScript)

```typescript
// frontend/src/components/ChatInterface.tsx
import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';

function ChatInterface() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { getAccessToken } = useAuth();

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    setLoading(true);

    // Optimistically add user message to UI
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }]);

    try {
      const token = await getAccessToken();
      const response = await api.sendChatMessage(token, {
        message: userMessage,
        conversation_id: conversationId
      });

      // Add assistant response to UI
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.message,
        created_at: response.created_at
      }]);

      // Store conversation ID for subsequent messages
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }
    } catch (error) {
      console.error('Chat error:', error);
      // Show error message to user
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
            <div className="message-time">{new Date(msg.created_at).toLocaleTimeString()}</div>
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
```

### Backend (FastAPI + Python)

```python
# backend/src/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from openai import AsyncOpenAI
import os

from ..models.conversation import Conversation, Message
from ..models.task import Task
from ..models.user import User
from ..database import get_session
from ..auth import get_current_user
from ..schemas.chat import ChatRequest, ChatResponse
from ..tools.mcp import get_mcp_tools, execute_tool_call

router = APIRouter(prefix="/api", tags=["chat"])
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_session)
):
    # 1. Get or create conversation
    if request.conversation_id:
        statement = select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user.id
        )
        conversation = db.exec(statement).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Create OpenAI thread if first message
    if not conversation.openai_thread_id:
        thread = await client.beta.threads.create()
        conversation.openai_thread_id = thread.id
        db.add(conversation)
        db.commit()

    # 3. Add user message to thread
    await client.beta.threads.messages.create(
        thread_id=conversation.openai_thread_id,
        role="user",
        content=request.message
    )

    # 4. Run assistant with MCP tools
    run = await client.beta.threads.runs.create(
        thread_id=conversation.openai_thread_id,
        assistant_id=ASSISTANT_ID,
        tools=get_mcp_tools()
    )

    # 5. Wait for completion and handle tool calls
    while run.status in ["queued", "in_progress", "requires_action"]:
        if run.status == "requires_action":
            # Execute MCP tool calls
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                result = await execute_tool_call(
                    tool_name=tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments),
                    user_id=user.id,
                    db=db
                )
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result)
                })

            # Submit tool outputs
            run = await client.beta.threads.runs.submit_tool_outputs(
                thread_id=conversation.openai_thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        else:
            # Wait and re-fetch run status
            await asyncio.sleep(0.5)
            run = await client.beta.threads.runs.retrieve(
                thread_id=conversation.openai_thread_id,
                run_id=run.id
            )

    # 6. Get assistant's response
    messages_response = await client.beta.threads.messages.list(
        thread_id=conversation.openai_thread_id,
        order="desc",
        limit=1
    )
    assistant_message = messages_response.data[0].content[0].text.value

    # 7. Save messages to database
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=assistant_message
    )
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        message=assistant_message,
        created_at=assistant_msg.created_at
    )
```

### MCP Tool Implementation

```python
# backend/src/tools/mcp.py
from typing import Dict, Any
from sqlmodel import select
from ..models.task import Task

def get_mcp_tools():
    """Return MCP tool definitions for OpenAI Assistants API"""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List user's tasks, optionally filtered by status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "incomplete", "complete"],
                            "description": "Filter tasks by status"
                        }
                    }
                }
            }
        }
        # ... other tools (complete_task, delete_task, update_task)
    ]

async def execute_tool_call(
    tool_name: str,
    arguments: Dict[str, Any],
    user_id: str,
    db
) -> Dict[str, Any]:
    """Execute an MCP tool call and return result"""

    if tool_name == "add_task":
        # Create task in database
        task = Task(
            user_id=user_id,
            title=arguments["title"],
            description=arguments.get("description", ""),
            status="incomplete"
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status
            }
        }

    elif tool_name == "list_tasks":
        # Query tasks from database
        statement = select(Task).where(Task.user_id == user_id)

        status_filter = arguments.get("status", "all")
        if status_filter != "all":
            statement = statement.where(Task.status == status_filter)

        tasks = db.exec(statement).all()

        return {
            "success": True,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status
                }
                for task in tasks
            ]
        }

    # ... other tool implementations
```

## Scenario 2: User Lists Tasks

**User Flow**: User types "Show me my tasks" → Agent calls list_tasks → Returns formatted list

### Expected Flow

1. User sends: "Show me my tasks"
2. Backend creates/retrieves conversation
3. OpenAI Assistant processes message
4. Agent calls `list_tasks()` MCP tool
5. `list_tasks()` queries database for user's tasks
6. Agent formats response: "You have 3 tasks: ..."
7. Backend saves messages to database
8. Frontend displays response

The code is the same as Scenario 1 - the difference is the agent's behavior based on user intent.

## Scenario 3: User Completes a Task

**User Flow**: User types "Mark the grocery task as done" → Agent identifies task → Calls complete_task → Confirmation

### MCP Tool: complete_task

```python
# backend/src/tools/mcp.py (additional tool)

# In get_mcp_tools():
{
    "type": "function",
    "function": {
        "name": "complete_task",
        "description": "Mark a task as complete",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The UUID of the task to complete"
                }
            },
            "required": ["task_id"]
        }
    }
}

# In execute_tool_call():
elif tool_name == "complete_task":
    task_id = arguments["task_id"]

    # Fetch task and verify ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = db.exec(statement).first()

    if not task:
        return {
            "success": False,
            "error": "Task not found or you don't have permission to modify it"
        }

    # Update task status
    task.status = "complete"
    db.add(task)
    db.commit()

    return {
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "status": task.status
        }
    }
```

## Scenario 4: Multi-Turn Conversation

**User Flow**: User has conversation history → Sends follow-up message → Agent uses context

### Example Conversation

```
User: "Add buy groceries to my tasks"
Assistant: "I've added 'buy groceries' to your tasks. You now have 3 incomplete tasks."

User: "Actually, change it to buy milk"
Assistant: "I've updated your task from 'buy groceries' to 'buy milk'."

User: "Now mark it as done"
Assistant: "Great! I've marked 'buy milk' as complete. You now have 2 incomplete tasks."
```

**How it works**:
- Same `conversation_id` is passed for all subsequent messages
- OpenAI thread maintains context via `thread_id`
- Agent references previous messages to understand "it", "the task", etc.
- Message history is retrieved from database when conversation is resumed

## Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-...your-api-key
OPENAI_ASSISTANT_ID=asst_...your-assistant-id
DATABASE_URL=postgresql://user:password@host/dbname
JWT_SECRET=your-jwt-secret
```

## Testing the Integration

### 1. Create OpenAI Assistant

```bash
# Create assistant via OpenAI API or dashboard
curl https://api.openai.com/v1/assistants \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-turbo-preview",
    "name": "Todo Assistant",
    "instructions": "You are a helpful assistant that manages todo tasks. Use the provided tools to help users create, view, complete, update, and delete their tasks. Always confirm actions and provide friendly responses.",
    "tools": [...]
  }'
```

### 2. Test Chat Endpoint

```bash
# Authenticate first (use Phase II auth endpoints)
TOKEN="your-jwt-token"

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add buy groceries to my tasks",
    "conversation_id": null
  }'

# Response:
# {
#   "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
#   "message": "I've added 'buy groceries' to your tasks. You now have 1 incomplete task.",
#   "created_at": "2026-01-03T10:30:18Z"
# }
```

### 3. Verify Database

```sql
-- Check conversation created
SELECT * FROM conversations WHERE user_id = 'your-user-id';

-- Check messages saved
SELECT * FROM messages WHERE conversation_id = '550e8400-e29b-41d4-a716-446655440000';

-- Check task created via MCP tool
SELECT * FROM tasks WHERE user_id = 'your-user-id' AND title = 'buy groceries';
```

## Common Patterns

### Pattern 1: Error Handling in MCP Tools

```python
async def execute_tool_call(tool_name, arguments, user_id, db):
    try:
        if tool_name == "add_task":
            # ... implementation
            return {"success": True, "task": {...}}
    except Exception as e:
        # Log error for debugging
        logger.error(f"MCP tool error: {tool_name}", exc_info=e)

        # Return structured error to agent
        return {
            "success": False,
            "error": "An error occurred while adding the task. Please try again."
        }
```

### Pattern 2: Loading Conversation History on Resume

```python
# When user returns to existing conversation
async def load_conversation_history(conversation_id, user_id, db):
    # Verify ownership
    conversation = db.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conversation:
        raise HTTPException(status_code=404)

    # Get recent messages for context
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(50)
    ).all()

    return conversation, list(reversed(messages))
```

## Next Steps

1. Implement backend chat endpoint (`/api/chat`)
2. Implement MCP tool functions
3. Create OpenAI assistant with tool definitions
4. Build frontend chat UI
5. Test end-to-end flows
6. Deploy and monitor

For detailed implementation steps, see `tasks.md` (generated by `/sp.tasks` command).
