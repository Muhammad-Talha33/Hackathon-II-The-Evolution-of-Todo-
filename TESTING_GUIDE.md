# Backend Testing Guide - Phase III Todo Chatbot

**Purpose**: Validate backend implementation before frontend integration

**Prerequisites**:
- Backend server running on http://localhost:8000
- OpenAI API key configured in `backend/.env`
- Database migrations applied
- User account created for testing

---

## Table of Contents

1. [Setup & Prerequisites](#setup--prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Verification](#database-verification)
4. [API Testing with curl](#api-testing-with-curl)
5. [Authentication Flow](#authentication-flow)
6. [Chat Endpoint Testing](#chat-endpoint-testing)
7. [MCP Server Verification](#mcp-server-verification)
8. [Error Handling Tests](#error-handling-tests)
9. [Troubleshooting](#troubleshooting)

---

## Setup & Prerequisites

### 1. Check Python Environment

```bash
cd backend
python --version  # Should be Python 3.10+
```

### 2. Verify Dependencies

```bash
pip list | grep -E "openai-agents|mcp|fastapi|sqlmodel"
```

**Expected output**:
```
fastapi>=0.115.0
mcp>=1.0.0
openai-agents>=0.1.0
sqlmodel>=0.0.14
```

### 3. Check Database Connection

```bash
# Verify DATABASE_URL in .env
grep DATABASE_URL backend/.env
```

---

## Environment Configuration

### 1. OpenAI API Key Setup

**CRITICAL**: Add your actual OpenAI API key to `backend/.env`:

```bash
# Open backend/.env and replace placeholder
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
```

**How to get an API key**:
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and paste into `.env` file

### 2. Verify Environment Variables

```bash
cd backend
python -c "from src.config import settings; print(f'DB: {settings.DATABASE_URL[:30]}...'); print(f'OpenAI Key: {settings.OPENAI_API_KEY[:10]}...')"
```

---

## Database Verification

### 1. Check Tables Exist

Run Alembic migrations if not already done:

```bash
cd backend
alembic upgrade head
```

### 2. Verify Schema

```bash
# Connect to your Neon database and run:
# \dt
# Should show: users, tasks, conversations, messages
```

### 3. Create Test User

```bash
# Use the signup endpoint (see Authentication Flow section)
```

---

## API Testing with curl

### Base URL
```bash
export API_BASE="http://localhost:8000"
```

### Start Backend Server

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

**Expected output**:
```
INFO:     🚀 Starting Phase 2 Todo API in development mode
INFO:     📊 Database: ...
INFO:     🌐 CORS enabled for: ...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## Authentication Flow

### 1. Signup (Create Test User)

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }' | jq
```

**Expected response** (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Save the access token**:
```bash
export ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 2. Signin (Existing User)

```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }' | jq
```

### 3. Test Protected Endpoint

```bash
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

**Expected response** (200):
```json
[]  # Empty task list for new user
```

---

## Chat Endpoint Testing

### Test 1: Create New Conversation (Task Creation - US1)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add buy groceries to my tasks",
    "conversation_id": null
  }' | jq
```

**Expected response** (200):
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "I've added 'buy groceries' to your tasks!",
  "created_at": "2026-01-04T10:00:00Z"
}
```

**Validation checklist**:
- ✅ Returns conversation_id (UUID format)
- ✅ Agent response confirms task creation
- ✅ Friendly, conversational tone
- ✅ No technical errors in message

### Test 2: Continue Conversation (Task Viewing - US2)

**Use the conversation_id from Test 1**:

```bash
export CONV_ID="123e4567-e89b-12d3-a456-426614174000"

curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Show me my tasks\",
    \"conversation_id\": \"$CONV_ID\"
  }" | jq
```

**Expected response** (200):
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "You have 1 task:\n\n1. buy groceries (incomplete)\n\nNeed help with anything else?",
  "created_at": "2026-01-04T10:01:00Z"
}
```

**Validation checklist**:
- ✅ Same conversation_id as Test 1
- ✅ Agent lists the task created in Test 1
- ✅ Conversational format (not raw JSON)
- ✅ Multi-turn context maintained

### Test 3: Task Completion (US3)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Mark the grocery task as done\",
    \"conversation_id\": \"$CONV_ID\"
  }" | jq
```

**Expected response** (200):
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Great job! I've marked 'buy groceries' as complete! 🎉",
  "created_at": "2026-01-04T10:02:00Z"
}
```

### Test 4: Verify Task in Database

```bash
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

**Expected response**:
```json
[
  {
    "id": "...",
    "title": "buy groceries",
    "description": null,
    "status": "complete",
    "created_at": "2026-01-04T10:00:00Z",
    "updated_at": "2026-01-04T10:02:00Z"
  }
]
```

**Validation**:
- ✅ Task exists in database
- ✅ Status changed to "complete"
- ✅ MCP tools successfully called by agent

---

## Conversation History Testing

### Test 5: List Conversations

```bash
curl -X GET http://localhost:8000/api/conversations \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

**Expected response** (200):
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2026-01-04T10:00:00Z",
    "updated_at": "2026-01-04T10:02:00Z",
    "message_count": 6
  }
]
```

**Validation**:
- ✅ Shows conversation from Tests 1-3
- ✅ message_count = 6 (3 user messages + 3 assistant responses)

### Test 6: Get Conversation Messages

```bash
curl -X GET "http://localhost:8000/api/conversations/$CONV_ID/messages" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

**Expected response** (200):
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "messages": [
    {
      "id": "msg1",
      "role": "user",
      "content": "Add buy groceries to my tasks",
      "created_at": "2026-01-04T10:00:00Z"
    },
    {
      "id": "msg2",
      "role": "assistant",
      "content": "I've added 'buy groceries' to your tasks!",
      "created_at": "2026-01-04T10:00:01Z"
    },
    {
      "id": "msg3",
      "role": "user",
      "content": "Show me my tasks",
      "created_at": "2026-01-04T10:01:00Z"
    },
    {
      "id": "msg4",
      "role": "assistant",
      "content": "You have 1 task...",
      "created_at": "2026-01-04T10:01:01Z"
    },
    {
      "id": "msg5",
      "role": "user",
      "content": "Mark the grocery task as done",
      "created_at": "2026-01-04T10:02:00Z"
    },
    {
      "id": "msg6",
      "role": "assistant",
      "content": "Great job! I've marked 'buy groceries' as complete!",
      "created_at": "2026-01-04T10:02:01Z"
    }
  ]
}
```

**Validation**:
- ✅ Messages in chronological order (oldest first)
- ✅ Alternating user/assistant roles
- ✅ Stateless architecture: History persisted in database

---

## MCP Server Verification

### Verify MCP Tools Are Called

**Check backend logs** while running Test 1-3. You should see:

```
INFO:     Agent calling MCP tool: mcp_add_task
INFO:     Agent calling MCP tool: mcp_list_tasks
INFO:     Agent calling MCP tool: mcp_complete_task
```

### Direct MCP Tool Test (Advanced)

**Create a simple test script** (`backend/test_mcp.py`):

```python
from src.mcp_server.server import get_mcp_server, set_session
from src.database import AsyncSessionLocal
import asyncio

async def test_mcp():
    async with AsyncSessionLocal() as session:
        set_session(session)
        mcp = get_mcp_server()

        # Test add_task
        result = mcp.mcp_add_task(
            user_id="test-user-id",
            title="Test task",
            description="Testing MCP"
        )
        print(f"Add task result: {result}")

asyncio.run(test_mcp())
```

Run:
```bash
cd backend
python test_mcp.py
```

---

## Error Handling Tests

### Test 7: Invalid Conversation ID

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "conversation_id": "invalid-uuid"
  }' | jq
```

**Expected response** (400):
```json
{
  "detail": "Invalid conversation_id format: invalid-uuid"
}
```

### Test 8: Unauthorized Access to Conversation

**Create a second user** and try to access first user's conversation:

```bash
# Signup second user
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user2@example.com",
    "password": "TestPass123!"
  }' | jq

export ACCESS_TOKEN_2="<second-user-token>"

# Try to access first user's conversation
curl -X GET "http://localhost:8000/api/conversations/$CONV_ID/messages" \
  -H "Authorization: Bearer $ACCESS_TOKEN_2" | jq
```

**Expected response** (403):
```json
{
  "detail": "You do not have permission to access this conversation"
}
```

### Test 9: Empty Message Validation

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "   ",
    "conversation_id": null
  }' | jq
```

**Expected response** (422):
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "Message cannot be empty",
      "type": "value_error"
    }
  ]
}
```

### Test 10: Missing Authentication

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "conversation_id": null
  }' | jq
```

**Expected response** (401):
```json
{
  "detail": "Not authenticated"
}
```

---

## Stateless Architecture Verification

### Test 11: Backend Restart Persistence

1. **Create a conversation** (Test 1)
2. **Stop the backend server** (Ctrl+C)
3. **Restart the backend server**:
   ```bash
   python -m uvicorn src.main:app --reload --port 8000
   ```
4. **Continue the conversation** with same conversation_id:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d "{
       \"message\": \"What tasks do I have?\",
       \"conversation_id\": \"$CONV_ID\"
     }" | jq
   ```

**Expected behavior**:
- ✅ Agent remembers previous conversation
- ✅ No "session lost" errors
- ✅ Context loaded from database successfully

**Validation**:
- ✅ Stateless backend confirmed
- ✅ No in-memory session storage
- ✅ Database-first architecture working

---

## Troubleshooting

### Issue 1: "Could not import openai-agents"

**Solution**:
```bash
cd backend
pip install openai-agents>=0.1.0
```

### Issue 2: "Database connection failed"

**Solution**:
```bash
# Check DATABASE_URL in .env
# Test connection:
python -c "from src.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Issue 3: "OpenAI API key not found"

**Solution**:
```bash
# Verify OPENAI_API_KEY in backend/.env
grep OPENAI_API_KEY backend/.env

# If missing, add:
echo "OPENAI_API_KEY=sk-proj-your-key-here" >> backend/.env
```

### Issue 4: "Agent execution failed"

**Check backend logs** for specific error:
```bash
# Look for errors in terminal running uvicorn
# Common issues:
# - Invalid OpenAI API key
# - MCP server not initialized
# - Database session not injected
```

### Issue 5: "MCP tool call failed"

**Solution**:
```bash
# Verify MCP server is initialized
# Check backend/src/mcp_server/server.py imports correctly
python -c "from src.mcp_server.server import get_mcp_server; print('MCP Server OK')"
```

### Issue 6: Agent returns generic response instead of calling tools

**Possible causes**:
1. OpenAI API key invalid or quota exceeded
2. Agent instructions not loaded correctly
3. MCP tools not passed to agent

**Debug**:
```python
# Add debug logging in chat_service.py process_chat_message()
print(f"Agent tools: {[t.__name__ for t in tools]}")
print(f"User message: {message}")
```

---

## Success Criteria Checklist

**Before proceeding to Phase 5 (Frontend), verify all these pass**:

### Core Functionality
- [ ] ✅ Backend server starts without errors
- [ ] ✅ Database tables exist (users, tasks, conversations, messages)
- [ ] ✅ User signup/signin works
- [ ] ✅ JWT authentication works on protected endpoints

### Chat Endpoint (US1-US5)
- [ ] ✅ POST /api/chat creates new conversation
- [ ] ✅ POST /api/chat continues existing conversation
- [ ] ✅ Agent can create tasks via MCP tools
- [ ] ✅ Agent can list tasks in conversational format
- [ ] ✅ Agent can complete tasks
- [ ] ✅ Multi-turn context maintained across messages

### Conversation History
- [ ] ✅ GET /api/conversations lists user's conversations
- [ ] ✅ GET /api/conversations/{id}/messages retrieves message history
- [ ] ✅ Message count accurate
- [ ] ✅ Messages in chronological order

### Error Handling
- [ ] ✅ Invalid conversation_id returns 400
- [ ] ✅ Unauthorized access returns 403
- [ ] ✅ Empty message returns 422
- [ ] ✅ Missing auth returns 401

### Stateless Architecture
- [ ] ✅ Backend restart doesn't lose conversation context
- [ ] ✅ Conversation history loaded from database every request
- [ ] ✅ No session storage used by agent

### MCP Integration
- [ ] ✅ MCP tools successfully called by agent
- [ ] ✅ Tasks created via MCP appear in database
- [ ] ✅ Database session injected to MCP server correctly

### User Authorization
- [ ] ✅ Users can only access their own conversations
- [ ] ✅ Users can only see their own tasks
- [ ] ✅ User data isolation enforced

---

## Next Steps

**If all tests pass**:
✅ Backend is ready for frontend integration
✅ Proceed to Phase 5: Frontend (OpenAI ChatKit)

**If tests fail**:
❌ Review error messages
❌ Check backend logs
❌ Verify environment configuration
❌ Fix issues before proceeding

---

## Quick Test Script

**Save this as `backend/quick_test.sh`**:

```bash
#!/bin/bash

echo "=== Quick Backend Test ==="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

API_BASE="http://localhost:8000"

# Test 1: Health check
echo -n "1. Health check... "
HEALTH=$(curl -s $API_BASE/health | jq -r '.status')
if [ "$HEALTH" = "healthy" ]; then
  echo -e "${GREEN}PASS${NC}"
else
  echo -e "${RED}FAIL${NC}"
  exit 1
fi

# Test 2: Signup
echo -n "2. User signup... "
SIGNUP=$(curl -s -X POST $API_BASE/auth/signup \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test$(date +%s)@example.com\",\"password\":\"TestPass123!\"}")
TOKEN=$(echo $SIGNUP | jq -r '.access_token')
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
  echo -e "${GREEN}PASS${NC}"
else
  echo -e "${RED}FAIL${NC}"
  exit 1
fi

# Test 3: Chat endpoint
echo -n "3. Chat endpoint... "
CHAT=$(curl -s -X POST $API_BASE/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add test task","conversation_id":null}')
CONV_ID=$(echo $CHAT | jq -r '.conversation_id')
if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ]; then
  echo -e "${GREEN}PASS${NC}"
else
  echo -e "${RED}FAIL${NC}"
  exit 1
fi

# Test 4: Conversations list
echo -n "4. Conversations list... "
CONVS=$(curl -s -X GET $API_BASE/api/conversations \
  -H "Authorization: Bearer $TOKEN")
COUNT=$(echo $CONVS | jq 'length')
if [ "$COUNT" -gt 0 ]; then
  echo -e "${GREEN}PASS${NC}"
else
  echo -e "${RED}FAIL${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}All tests passed!${NC}"
echo "Backend is ready for frontend integration."
```

**Run**:
```bash
chmod +x backend/quick_test.sh
./backend/quick_test.sh
```

---

## Manual Testing Checklist

**Print this and check off as you test**:

```
[ ] 1. Environment setup complete
[ ] 2. Database migrations applied
[ ] 3. Backend server starts successfully
[ ] 4. User signup works
[ ] 5. User signin works
[ ] 6. POST /api/chat creates conversation
[ ] 7. Agent creates task via MCP
[ ] 8. Task appears in database
[ ] 9. POST /api/chat continues conversation
[ ] 10. Agent lists tasks conversationally
[ ] 11. Agent completes task
[ ] 12. GET /api/conversations returns list
[ ] 13. GET /api/conversations/{id}/messages returns history
[ ] 14. Invalid conversation_id returns 400
[ ] 15. Unauthorized access returns 403
[ ] 16. Backend restart persists conversations
[ ] 17. MCP tools called successfully
[ ] 18. User data isolation enforced
```

**Signature**: _________________ **Date**: _________________
