---
id: 006
title: Passlib Bcrypt Error Fix
stage: red
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-phase2-full-stack-web
branch: 001-phase2-full-stack-web
user: Muhammad Talha
command: /sp.implement
labels: ["debugging", "passlib", "bcrypt", "password-hashing", "runtime-error"]
links:
  spec: specs/001-phase2-full-stack-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/utils/security.py
tests:
  - POST /auth/signup (user creation)
  - POST /auth/signin (authentication)
  - POST /tasks (task creation with JWT)
  - GET /tasks (task retrieval)
  - PATCH /tasks/{id}/complete (task completion toggle)
---

## Prompt

User reported 500 Internal Server Error when testing POST /auth/signup:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/signup' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "talha@gmail.com",
  "password": "talha123"
}'
```

Response:
```json
{
  "detail": "Internal server error"
}
```

## Response snapshot

**Root Cause**: Passlib + bcrypt compatibility issue. The error occurred during bcrypt backend initialization in passlib's `detect_wrap_bug()` function:

```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
```

This was triggered by passlib's internal testing during `CryptContext` initialization, not by the actual user password.

**Solution**: Replaced passlib wrapper with direct bcrypt usage in `backend/src/utils/security.py`:

**Before**:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**After**:
```python
import bcrypt

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
```

After restarting the server, all authentication and task endpoints work correctly.

## Outcome

- ✅ Impact: Backend authentication fully functional. Users can now sign up, sign in, and manage tasks with JWT-based authorization. All 5 core API flows tested and working: signup → signin → create task → list tasks → toggle completion.
- 🧪 Tests: Manual API testing via curl - all endpoints return 200/201 responses with correct data. Created user "talha@gmail.com", generated valid JWT tokens, created task "Test Task", retrieved task list, toggled completion status from "incomplete" to "complete".
- 📁 Files: 1 file modified (backend/src/utils/security.py) - removed passlib dependency, replaced with direct bcrypt calls
- 🔁 Next prompts: User should either (1) test remaining CRUD operations (update task, delete task) via Swagger UI, (2) initialize Next.js frontend (IMPLEMENTATION_GUIDE.md Steps 6-8), or (3) verify Phase 1 console app compatibility
- 🧠 Reflection: The passlib abstraction layer added unnecessary complexity and introduced a compatibility bug with newer bcrypt versions. Direct bcrypt usage is simpler, more reliable, and has no compatibility issues. This demonstrates the value of using minimal dependencies and avoiding unnecessary wrapper libraries when the underlying library API is straightforward.

## Evaluation notes (flywheel)

- Failure modes observed: Passlib's internal password length validation during initialization caused runtime crash even though user passwords were valid. The error message was misleading - it appeared to be about the user's password but was actually from passlib's internal testing. Server auto-reload with uvicorn --reload didn't pick up the fix initially, requiring manual server restart.
- Graders run and results (PASS/FAIL): PASS - Signup endpoint returns 201 with valid JWT tokens. PASS - Signin endpoint authenticates existing user successfully. PASS - Task creation requires valid JWT (401 without token). PASS - Task completion toggle works correctly. PASS - User data isolation verified (tasks belong to correct user_id).
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): For future Python projects requiring password hashing, default to direct bcrypt usage instead of passlib unless there's a specific need for passlib's algorithm migration features. Add a startup health check that validates password hashing is working correctly before accepting traffic - this would have caught the error immediately during deployment.
