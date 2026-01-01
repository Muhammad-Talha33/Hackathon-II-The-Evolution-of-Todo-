# Implementation Plan: Phase 2 Full Stack Web Application

**Branch**: `001-phase2-full-stack-web` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase2-full-stack-web/spec.md`

## Summary

Build a full-stack web application with PostgreSQL persistence, FastAPI REST API backend, Next.js frontend, and JWT authentication. The system will replace Phase 1's in-memory task management with database-backed multi-user task management while keeping Phase 1 console app fully functional and untouched.

**Primary Requirements**:
- PostgreSQL database (via Neon) with SQLModel ORM for persistent task storage
- FastAPI backend with REST API endpoints for authentication and CRUD operations
- Next.js frontend with responsive UI, protected routes, and JWT token management
- User authentication with signup, signin, and token refresh using JWT
- Multi-user support with task ownership and authorization
- Phase 1 backward compatibility (src/ directory untouched)

**Technical Approach** (from research.md):
- **Database**: Neon serverless PostgreSQL + SQLModel (async ORM with Pydantic integration)
- **Backend**: FastAPI with async/await pattern, python-jose for JWT, passlib for password hashing
- **Frontend**: Next.js 14 App Router with TypeScript and Tailwind CSS
- **Auth**: Custom JWT implementation (15-min access tokens, 7-day refresh tokens)
- **Token Storage**: httpOnly cookies (preferred) with localStorage fallback
- **Project Structure**: Web application pattern (backend/, frontend/, existing src/)

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.3+ / Node.js 18+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, asyncpg, Next.js, React 18, Tailwind CSS
**Storage**: PostgreSQL 15+ (Neon cloud-hosted), async connection pooling
**Testing**: pytest + pytest-asyncio (backend), manual testing (frontend - Phase 2)
**Target Platform**: Web application (backend: uvicorn ASGI server, frontend: Next.js dev server / production build)
**Project Type**: Web (backend + frontend split architecture)
**Performance Goals**:
  - API response time: < 200ms p95 for CRUD operations
  - Task list load time: < 2 seconds for up to 1,000 tasks
  - Frontend page load: < 3 seconds (First Contentful Paint)
  - Concurrent users: Support 100+ concurrent users (scalable via async)
**Constraints**:
  - Access token expiration: 15 minutes (hard limit)
  - Refresh token expiration: 7 days (hard limit)
  - Task title max length: 500 characters (database constraint)
  - Phase 1 src/ directory: MUST remain completely untouched
  - No breaking changes to existing Phase 1 functionality
**Scale/Scope**:
  - Expected user base: 100-1,000 users initially
  - Tasks per user: Up to 10,000 tasks supported without degradation
  - Database: Neon free tier initially (can scale to paid tier)
  - Deployment: Single-region initially (can expand to multi-region)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 1 Constitution Compliance

**From `.specify/memory/constitution.md`**:

✅ **Core Principle I**: In-Memory Task Management (NON-NEGOTIABLE)
- **Status**: ✅ COMPLIANT for Phase 1
- **Verification**: Phase 1 code in `src/` remains untouched. Phase 2 creates separate `backend/` and `frontend/` directories. Phase 1 console app (`python src/main.py`) continues to use in-memory storage as originally designed.
- **No Violation**: Phase 2 is a separate implementation that does not modify Phase 1 behavior.

✅ **Core Principle II**: Separation of Concerns
- **Status**: ✅ COMPLIANT
- **Backend Architecture**:
  - **Router Layer**: FastAPI routers handle HTTP requests, routing, validation (`routers/`)
  - **Service/Business Logic Layer**: Database operations, authentication logic (`models/`, `dependencies/`)
  - **Data Layer**: SQLModel models define schema and ORM operations (`models/`)
- **Frontend Architecture**:
  - **UI Layer**: React components, pages (`components/`, `app/`)
  - **API Layer**: API client, fetch wrappers (`lib/api.ts`)
  - **State Management**: Local state, server components (no global store needed for Phase 2)
- **Clear Boundaries**: Frontend ↔ REST API ↔ Database with well-defined contracts

✅ **Core Principle III**: Input Validation and Error Handling (MANDATORY)
- **Status**: ✅ COMPLIANT
- **Implementation**:
  - **Backend**: Pydantic schemas validate all request bodies (automatic via FastAPI)
  - **Database**: CHECK constraints, FOREIGN KEY constraints, NOT NULL constraints
  - **Frontend**: Form validation, user-friendly error messages
  - **Error Responses**: Clear HTTP status codes (401, 404, 422, 500) with descriptive messages
  - **No Crashes**: Global exception handlers in FastAPI, try-catch in frontend

✅ **Core Principle IV**: Deterministic and Explainable Behavior
- **Status**: ✅ COMPLIANT
- **Implementation**:
  - **UUIDs**: Unique, deterministic per record (not sequential for security)
  - **Timestamps**: All operations timestamped (`created_at`, `updated_at`)
  - **Status Changes**: Explicit state transitions (incomplete ↔ complete)
  - **Logging**: All API requests logged with timestamp, endpoint, user_id, status
  - **Confirmation**: All mutations return updated resource or success confirmation

✅ **Core Principle V**: Code Quality and Maintainability
- **Status**: ✅ COMPLIANT
- **Implementation**:
  - **Python**: PEP 8 style, type hints (Python 3.13+), docstrings for public functions
  - **TypeScript**: Strict mode enabled, type safety enforced, ESLint configured
  - **Project Structure**: Clear directory organization (see Project Structure below)
  - **DRY**: Reusable components, shared utilities, API client abstraction
  - **Single Responsibility**: Each router handles one resource, each component one UI concern

### Constitution Check Summary

**Result**: ✅ **ALL GATES PASSED**

- Phase 1 principles remain intact (no modifications to `src/`)
- Phase 2 follows industry-standard architecture patterns
- Separation of concerns enforced at all layers
- Comprehensive validation and error handling
- Deterministic behavior with full auditability
- High code quality standards

**No violations requiring justification.**

---

## Project Structure

### Documentation (this feature)

```text
specs/001-phase2-full-stack-web/
├── spec.md              # Feature specification (created by /sp.specify)
├── plan.md              # This file (created by /sp.plan)
├── research.md          # Technical research and decisions (created by /sp.plan)
├── data-model.md        # Database schema and models (created by /sp.plan)
├── quickstart.md        # Setup guide (created by /sp.plan)
├── contracts/           # API contracts (created by /sp.plan)
│   └── api-spec.yaml    # OpenAPI 3.1 specification
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Implementation tasks (will be created by /sp.tasks)
```

### Source Code (repository root)

```text
# Phase 2: Web Application Structure
backend/
├── src/
│   ├── main.py              # FastAPI app initialization, CORS, middleware
│   ├── config.py            # Settings (Pydantic BaseSettings from .env)
│   ├── database.py          # Database connection, session management
│   ├── models/              # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py          # User model (id, email, password_hash, created_at)
│   │   └── task.py          # Task model (id, user_id, title, description, status, timestamps)
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py          # SignupRequest, SigninRequest, TokenResponse, UserResponse
│   │   └── task.py          # TaskCreate, TaskUpdate, TaskResponse
│   ├── routers/             # API endpoint routers
│   │   ├── __init__.py
│   │   ├── auth.py          # POST /auth/signup, /signin, /refresh
│   │   └── tasks.py         # GET/POST /tasks, GET/PUT/DELETE /tasks/{id}, PATCH /tasks/{id}/complete
│   ├── dependencies/        # Dependency injection functions
│   │   ├── __init__.py
│   │   └── auth.py          # get_current_user, get_current_active_user, verify_token
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── security.py      # hash_password, verify_password, create_access_token, create_refresh_token
│       └── errors.py        # Custom exception classes
├── tests/                   # Backend tests (pytest)
│   ├── __init__.py
│   ├── test_auth.py         # Authentication endpoint tests
│   └── test_tasks.py        # Task CRUD endpoint tests
├── alembic/                 # Database migrations
│   ├── versions/            # Migration files
│   └── env.py               # Alembic configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
└── .env                     # Actual environment variables (NOT committed)

frontend/
├── app/                     # Next.js App Router
│   ├── layout.tsx           # Root layout (global styles, fonts)
│   ├── page.tsx             # Home page (redirects to /tasks or /signin)
│   ├── globals.css          # Tailwind CSS imports
│   ├── signin/
│   │   └── page.tsx         # Sign in form
│   ├── signup/
│   │   └── page.tsx         # Sign up form
│   └── tasks/
│       ├── page.tsx         # Task list (protected route)
│       ├── new/
│       │   └── page.tsx     # Add new task form
│       └── [id]/
│           └── edit/
│               └── page.tsx # Edit task form
├── components/              # Reusable React components
│   ├── ui/                  # UI primitives (buttons, inputs, etc.)
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── Toast.tsx        # Toast notifications for errors/success
│   ├── TaskList.tsx         # Task list with checkboxes, edit/delete buttons
│   ├── TaskForm.tsx         # Reusable form for add/edit task
│   ├── AuthForm.tsx         # Reusable form for signin/signup
│   └── LoadingSpinner.tsx   # Loading state component
├── lib/                     # Utility libraries
│   ├── api.ts               # API client (fetch wrapper with auth header injection)
│   ├── auth.ts              # Auth helpers (getCookie, setCookie, clearTokens, refreshToken)
│   └── types.ts             # TypeScript types (Task, User, ApiError)
├── middleware.ts            # Protected route middleware (checks for access_token)
├── public/                  # Static assets
├── node_modules/            # NPM dependencies
├── package.json             # NPM dependencies and scripts
├── next.config.js           # Next.js configuration
├── tailwind.config.ts       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
├── .env.local.example       # Example environment variables
└── .env.local               # Actual environment variables (NOT committed)

# Phase 1: Console Application (UNTOUCHED)
src/
├── main.py                  # Phase 1 entry point (menu-driven console)
├── skills/                  # Phase 1 task management skills
│   ├── add_task.py
│   ├── view_tasks.py
│   ├── update_task.py
│   ├── delete_task.py
│   └── mark_complete.py
└── models/                  # Phase 1 in-memory task model
    └── task.py

# Tests for Phase 1 (if applicable)
tests/
└── test_phase1.py           # Phase 1 tests (if created)

# Project Configuration
.gitignore                   # Ignore venv/, node_modules/, .env files
README.md                    # Project overview, setup instructions
requirements.txt             # Root-level Python requirements (if any)
```

**Structure Decision**:

This project uses **Option 2: Web application** structure with separate `backend/` and `frontend/` directories.

**Rationale**:
1. **Clear Separation**: Backend and frontend are distinct applications with different runtimes (Python vs Node.js)
2. **Independent Deployment**: Backend and frontend can be deployed separately to different hosts
3. **Phase 1 Preservation**: Existing `src/` directory for Phase 1 console app remains completely untouched
4. **Standard Practice**: Industry-standard monorepo structure for full-stack projects
5. **Future Scalability**: Easy to add additional services (e.g., `worker/`, `api-v2/`) if needed

**Key Directories**:
- `backend/src/`: All Python source code for FastAPI application
- `frontend/app/`: Next.js pages using App Router (server components, file-based routing)
- `frontend/components/`: Reusable React components
- `frontend/lib/`: Shared utilities (API client, auth helpers, types)
- `src/`: Phase 1 console application (MUST NOT BE MODIFIED)

---

## Implementation Stages

### Stage 1: Backend Setup

**Goal**: Set up FastAPI backend with database connection, authentication, and task CRUD APIs

**Tasks**:
1. **Environment Setup**:
   - Create `backend/` directory structure
   - Set up Python virtual environment
   - Install dependencies (`requirements.txt`)
   - Configure environment variables (`.env`)
   - Set up Neon PostgreSQL database

2. **Database Layer**:
   - Implement `database.py` (async SQLAlchemy engine, session management)
   - Implement `models/user.py` (User SQLModel)
   - Implement `models/task.py` (Task SQLModel)
   - Create Alembic migration for initial schema
   - Verify database connection and schema creation

3. **Authentication Implementation**:
   - Implement `utils/security.py` (password hashing, JWT token creation/verification)
   - Implement `schemas/auth.py` (request/response models)
   - Implement `routers/auth.py` (signup, signin, refresh endpoints)
   - Implement `dependencies/auth.py` (get_current_user dependency)
   - Test authentication flow end-to-end

4. **Task CRUD Implementation**:
   - Implement `schemas/task.py` (request/response models)
   - Implement `routers/tasks.py` (all task endpoints)
   - Implement authorization (filter by user_id)
   - Implement toggle completion endpoint
   - Test all CRUD operations with authenticated user

5. **API Integration**:
   - Configure CORS for frontend origin
   - Add global exception handlers
   - Add request logging
   - Test API via Swagger UI (/docs)
   - Verify all endpoints match OpenAPI spec

**Acceptance Criteria**:
- ✅ Backend server runs at http://localhost:8000
- ✅ Swagger UI accessible at http://localhost:8000/docs
- ✅ All auth endpoints working (signup, signin, refresh)
- ✅ All task endpoints working (GET, POST, PUT, DELETE, PATCH)
- ✅ JWT tokens generated and validated correctly
- ✅ Tasks filtered by user_id (no cross-user access)
- ✅ Database schema matches data-model.md
- ✅ All responses match contracts/api-spec.yaml

---

### Stage 2: Frontend Setup

**Goal**: Set up Next.js frontend with authentication UI, task management UI, and API integration

**Tasks**:
1. **Environment Setup**:
   - Create Next.js app in `frontend/` with TypeScript and Tailwind
   - Install additional dependencies (js-cookie, etc.)
   - Configure environment variables (`.env.local`)
   - Set up Tailwind CSS configuration
   - Create base UI components

2. **Authentication Pages**:
   - Implement `/signin` page with form and validation
   - Implement `/signup` page with form and validation
   - Implement auth API client functions (signup, signin, refresh)
   - Implement token storage (cookies with js-cookie)
   - Test signin/signup flows with backend

3. **Task Management Pages**:
   - Implement `/tasks` page (task list with checkboxes, edit/delete buttons)
   - Implement `/tasks/new` page (add task form)
   - Implement `/tasks/[id]/edit` page (edit task form)
   - Implement task API client functions (CRUD operations)
   - Implement optimistic UI updates

4. **Protected Routes**:
   - Implement `middleware.ts` (check for access_token cookie)
   - Redirect unauthenticated users to `/signin`
   - Implement automatic token refresh on 401 responses
   - Implement sign-out functionality
   - Test protected route access

5. **UI Polish**:
   - Implement responsive design (mobile, tablet, desktop)
   - Implement loading states for async operations
   - Implement error toast notifications
   - Implement empty states (no tasks)
   - Test on different screen sizes

**Acceptance Criteria**:
- ✅ Frontend runs at http://localhost:3000
- ✅ Signup page creates new users via backend API
- ✅ Signin page authenticates users and stores JWT tokens
- ✅ Unauthenticated users redirected to /signin
- ✅ Task list displays all user's tasks
- ✅ Add/edit/delete task operations work correctly
- ✅ Checkbox toggles task completion status
- ✅ UI is responsive on mobile (320px+), tablet, desktop
- ✅ Error messages display user-friendly text
- ✅ Token refresh works automatically on 401

---

### Stage 3: Integration & Testing

**Goal**: Verify end-to-end integration between frontend and backend, ensure Phase 1 compatibility

**Tasks**:
1. **End-to-End Flow Testing**:
   - Test complete user journey: signup → signin → add tasks → mark complete → edit → delete → signout
   - Verify token expiration and refresh flow
   - Verify authorization (users can't access others' tasks)
   - Test error scenarios (invalid credentials, network errors, etc.)
   - Test edge cases from spec.md

2. **Phase 1 Compatibility Verification**:
   - Run Phase 1 console app (`python src/main.py`)
   - Verify all Phase 1 CRUD operations work correctly
   - Verify in-memory storage behavior (tasks lost on exit)
   - Confirm no Phase 1 files were modified
   - Document Phase 1 and Phase 2 coexistence

3. **Performance Testing**:
   - Test task list with 1,000+ tasks (should load in < 2 seconds)
   - Test concurrent users (simulate 10+ users)
   - Verify API response times (< 200ms p95)
   - Check database connection pooling

4. **Security Validation**:
   - Verify password hashing (check database - no plaintext)
   - Verify JWT token expiration enforced
   - Verify CORS configuration (only allows frontend origin)
   - Test SQL injection attempts (should be prevented by SQLModel)
   - Verify task authorization (404 for other users' tasks)

5. **Documentation & Cleanup**:
   - Update .gitignore (backend/.env, frontend/.env.local, venv/, node_modules/)
   - Update README.md with quickstart instructions
   - Verify all generated files match plan
   - Clean up any temporary files or test data

**Acceptance Criteria**:
- ✅ Complete user journey works end-to-end without errors
- ✅ Phase 1 console app runs successfully (`python src/main.py`)
- ✅ No Phase 1 files modified (verify with `git status src/`)
- ✅ All 12 success criteria from spec.md verified
- ✅ All security validations passed
- ✅ Performance goals met (load time, API response time)
- ✅ .gitignore prevents committing secrets
- ✅ README.md includes setup instructions

---

## Complexity Tracking

No constitution violations or added complexity requiring justification.

**Justification for Web Application Structure**:
- This is the standard industry approach for full-stack applications
- Backend and frontend are distinct applications with separate runtimes
- Allows independent scaling and deployment
- Does not violate Phase 1 constraints (src/ untouched)
- Aligns with user requirements (FastAPI + Next.js specified)

---

## Dependencies

### Backend Dependencies (backend/requirements.txt)

```txt
# Core Framework
fastapi==0.109.0           # REST API framework
uvicorn[standard]==0.27.0  # ASGI server

# Database
sqlmodel==0.0.14           # ORM with Pydantic integration
asyncpg==0.29.0            # Async PostgreSQL driver
alembic==1.13.1            # Database migrations

# Settings & Config
pydantic-settings==2.1.0   # Environment variable management

# Authentication & Security
python-jose[cryptography]==3.3.0  # JWT encoding/decoding
passlib[bcrypt]==1.7.4     # Password hashing
python-multipart==0.0.6    # Form data parsing
```

### Frontend Dependencies (frontend/package.json)

```json
{
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.3",
    "js-cookie": "3.0.5"
  },
  "devDependencies": {
    "tailwindcss": "3.4.1",
    "autoprefixer": "10.4.17",
    "postcss": "8.4.33",
    "@types/react": "18.2.48",
    "@types/node": "20.11.5",
    "@types/js-cookie": "3.0.6"
  }
}
```

### External Services

- **Neon PostgreSQL**: Cloud-hosted serverless PostgreSQL database

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| JWT token security | Low | High | Use strong secret keys (32+ chars), short expiration, httpOnly cookies |
| Database connection failures | Medium | High | Implement connection pooling, retry logic, graceful error handling |
| CORS misconfiguration | Low | Medium | Test cross-origin requests early, use environment-based origins |
| Phase 1 compatibility broken | Low | Critical | Never modify src/, verify Phase 1 works after each stage |
| Token refresh race conditions | Medium | Medium | Implement refresh lock, use refresh token rotation |
| Slow task list with many tasks | Low | Medium | Implement pagination, indexing on user_id + created_at |

### Implementation Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Better Auth library incompatibility | High | Low | Already mitigated in research.md - using python-jose instead |
| Complex middleware setup | Low | Low | Follow Next.js documentation, test protected routes early |
| Environment variable management | Medium | Low | Use .env.example files, document all required variables |
| Database migration issues | Low | Medium | Test migrations on dev database first, have rollback plan |

---

## Next Steps

After completing this implementation plan:

1. **Run `/sp.tasks`** to generate detailed `tasks.md` with step-by-step implementation tasks
2. **Follow quickstart.md** to set up development environment
3. **Implement Stage 1** (Backend Setup)
4. **Implement Stage 2** (Frontend Setup)
5. **Implement Stage 3** (Integration & Testing)
6. **Run `/sp.git.commit_pr`** to commit changes and create pull request

---

## References

- **Feature Specification**: [spec.md](./spec.md)
- **Technical Research**: [research.md](./research.md)
- **Database Schema**: [data-model.md](./data-model.md)
- **API Contract**: [contracts/api-spec.yaml](./contracts/api-spec.yaml)
- **Setup Guide**: [quickstart.md](./quickstart.md)
- **Phase 1 Constitution**: [../../.specify/memory/constitution.md](../../.specify/memory/constitution.md)

---

**Plan Status**: ✅ **COMPLETE AND READY FOR TASK GENERATION**

All research completed, all design artifacts generated, constitution gates passed. Ready to proceed with `/sp.tasks` to generate implementation tasks.
