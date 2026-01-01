# Data Model: Phase 2 Full Stack Web Application

**Date**: 2025-12-29
**Feature**: 001-phase2-full-stack-web
**Database**: PostgreSQL (via Neon)
**ORM**: SQLModel

## Entity Relationship Diagram

```
┌─────────────────┐          ┌─────────────────┐
│      User       │          │      Task       │
├─────────────────┤          ├─────────────────┤
│ id (UUID) PK    │──────────│ id (UUID) PK    │
│ email (str)     │   1:N    │ user_id (UUID)  │
│ password_hash   │          │ title (str)     │
│ created_at      │          │ description     │
└─────────────────┘          │ status (enum)   │
                             │ created_at      │
                             │ updated_at      │
                             └─────────────────┘
```

## Entities

### 1. User

**Purpose**: Represents an authenticated application user

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address for authentication |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password (never store plaintext) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Validation Rules** (from FR-021, FR-022):
- Email must match standard email regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Email must be unique across all users
- Password must be minimum 8 characters (validated before hashing)
- Password must be hashed using bcrypt with cost factor 12

**Relationships**:
- **Has Many**: Tasks (one user can have multiple tasks)
- **Cascade Delete**: When user is deleted, all associated tasks are deleted

**Indexes**:
- Primary key index on `id` (automatic)
- Unique index on `email` (for fast lookup during signin)

**SQLModel Implementation**:
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 2. Task

**Purpose**: Represents a todo item owned by a specific user

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique identifier |
| `user_id` | UUID | FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE, NOT NULL | Owner of the task |
| `title` | VARCHAR(500) | NOT NULL | Task description (max 500 chars per FR-003) |
| `description` | TEXT | NULL | Optional additional details (unlimited) |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'incomplete', CHECK (status IN ('incomplete', 'complete')) | Completion state |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp (auto-updated) |

**Validation Rules** (from FR-003, spec edge cases):
- Title must not be empty or whitespace-only
- Title maximum length: 500 characters
- Status must be exactly 'incomplete' or 'complete' (enforced by CHECK constraint)
- User_id must reference an existing user
- New tasks default to 'incomplete' status

**Relationships**:
- **Belongs To**: User (each task has exactly one owner)
- **Cascade Behavior**: When user is deleted, all their tasks are automatically deleted

**Indexes**:
- Primary key index on `id` (automatic)
- Foreign key index on `user_id` (for efficient user task queries)
- Composite index on `(user_id, created_at DESC)` for sorted task lists

**SQLModel Implementation**:
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.INCOMPLETE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## State Transitions

### Task Status Lifecycle

```
┌─────────────┐
│   Created   │
│  (incomplete)│
└──────┬──────┘
       │
       │ User marks complete (PATCH /tasks/{id}/complete)
       ▼
┌─────────────┐
│  Complete   │
└──────┬──────┘
       │
       │ User toggles back (PATCH /tasks/{id}/complete)
       ▼
┌─────────────┐
│  Incomplete │
└─────────────┘
```

**State Transition Rules**:
1. New tasks always start in `incomplete` state
2. `PATCH /tasks/{id}/complete` toggles status:
   - If current status is `incomplete` → change to `complete`
   - If current status is `complete` → change to `incomplete`
3. No other status values are allowed (enforced by database CHECK constraint)

---

## Database Migrations

### Initial Schema (Alembic Migration)

```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'incomplete'
        CHECK (status IN ('incomplete', 'complete')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_task_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Data Constraints Summary

### User Constraints
- ✅ Email must be unique
- ✅ Email must match valid format (application-level validation)
- ✅ Password must be minimum 8 characters (application-level validation)
- ✅ Password must be bcrypt hashed (cost factor 12)
- ✅ All fields required except defaults

### Task Constraints
- ✅ Title required, max 500 characters
- ✅ Description optional, unlimited length
- ✅ Status must be 'incomplete' or 'complete' (database CHECK constraint)
- ✅ User_id must reference existing user (foreign key constraint)
- ✅ Cascade delete: deleting user deletes all their tasks
- ✅ Updated_at automatically updated on any task modification

---

## Pydantic Schemas (API Layer)

These schemas define the API request/response shapes (separate from database models):

### Auth Schemas

```python
# Request schemas
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class SigninRequest(BaseModel):
    email: EmailStr
    password: str

# Response schemas
class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

### Task Schemas

```python
# Request schemas
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None

# Response schemas
class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows SQLModel -> Pydantic conversion
```

---

## Security Considerations

### Password Storage
- **Never** store passwords in plaintext
- Use `passlib` with `bcrypt` algorithm
- Cost factor: 12 (balance between security and performance)
- Salt is automatically generated per password

### Authorization
- Tasks are filtered by `user_id` from JWT token
- Users can only access their own tasks (enforced in API layer)
- Attempting to access another user's task returns 404 (not 403) to prevent task ID enumeration

### Data Validation
- Input validation at multiple layers:
  1. **Database**: CHECK constraints, FOREIGN KEY constraints
  2. **ORM**: SQLModel field constraints
  3. **API**: Pydantic schema validation
  4. **Frontend**: Form validation (UX, not security)

---

## Sample Data (for Testing)

```python
# Sample User
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "password_hash": "$2b$12$KIXxKj...",  # bcrypt hash of "password123"
    "created_at": "2025-12-29T10:00:00Z"
}

# Sample Tasks
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Get milk, eggs, bread",
    "status": "incomplete",
    "created_at": "2025-12-29T10:30:00Z",
    "updated_at": "2025-12-29T10:30:00Z"
}

{
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Finish project report",
    "description": "Complete sections 3-5",
    "status": "complete",
    "created_at": "2025-12-28T15:00:00Z",
    "updated_at": "2025-12-29T09:00:00Z"
}
```

---

## Notes

- All timestamps stored in UTC
- UUIDs generated using `uuid4()` (random, not sequential)
- Enum values stored as strings in database for readability
- `updated_at` automatically updated via database trigger on UPDATE
- Foreign key relationships enforce referential integrity
- Cascade delete ensures no orphaned tasks when user is deleted
