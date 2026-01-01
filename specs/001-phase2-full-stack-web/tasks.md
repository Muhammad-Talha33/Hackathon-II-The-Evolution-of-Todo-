# Implementation Tasks: Phase 2 Full Stack Web Application

**Branch**: `001-phase2-full-stack-web` | **Date**: 2025-12-29
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Task Summary

**Total Tasks**: 73
**User Stories**: 5 (4 x P0, 1 x P1)
**Parallelizable Tasks**: 28
**Estimated Completion**: 3 stages (Backend → Frontend → Integration)

## Implementation Strategy

**MVP Scope**: User Story 1 (Database Schema and Connection) + User Story 2 (Backend REST API Endpoints) + User Story 3 (User Authentication System)

This provides a fully functional backend API that can be tested independently before frontend development.

**Incremental Delivery**:
1. **Stage 1** (Backend): Complete US1 + US2 + US3 → Testable API with authentication
2. **Stage 2** (Frontend): Complete US4 → Full web UI with task management
3. **Stage 3** (Integration): Complete US5 + Polish → Production-ready application

**Independent Testing**: Each user story can be tested independently using the acceptance scenarios defined in spec.md.

---

## Phase 1: Setup & Environment (8 tasks)

**Goal**: Initialize project structure, set up development environment, configure external services

**Prerequisites**: None

**Tasks**:

- [X] T001 Create backend/ directory structure (src/, models/, schemas/, routers/, dependencies/, utils/, tests/)
- [X] T002 Create frontend/ directory structure using `npx create-next-app@latest`
- [X] T003 Create backend/.env.example file with DATABASE_URL, SECRET_KEY, CORS_ORIGINS, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
- [X] T004 Create frontend/.env.local.example file with NEXT_PUBLIC_API_URL
- [X] T005 Create backend/requirements.txt with FastAPI, SQLModel, asyncpg, python-jose, passlib, uvicorn, pydantic-settings
- [X] T006 Set up Neon PostgreSQL project at neon.tech and copy connection string
- [X] T007 Create backend/.env file from .env.example with actual Neon connection string (postgresql+asyncpg://...)
- [X] T008 Update .gitignore to exclude backend/.env, backend/venv/, frontend/.env.local, frontend/node_modules/, frontend/.next/

**Acceptance**: Directory structure matches plan.md, .env files created with correct placeholders, .gitignore prevents committing secrets

---

## Phase 2: Foundational Infrastructure (7 tasks)

**Goal**: Set up core backend infrastructure (database connection, configuration, base FastAPI app)

**Prerequisites**: Phase 1 complete

**Tasks**:

- [X] T009 Install backend dependencies: `cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt`
- [X] T010 Create backend/src/config.py with Pydantic BaseSettings loading from .env (DATABASE_URL, SECRET_KEY, CORS_ORIGINS, token expiration)
- [X] T011 Create backend/src/database.py with async SQLAlchemy engine, AsyncSession factory, get_db dependency
- [X] T012 Create backend/src/main.py with FastAPI app initialization, CORS middleware, health check endpoint
- [X] T013 Test backend server starts: `uvicorn src.main:app --reload --port 8000` and verify http://localhost:8000/health returns 200
- [X] T014 Install frontend dependencies: `cd frontend && npm install && npm install js-cookie @types/js-cookie`
- [X] T015 Create frontend/.env.local from .env.local.example with NEXT_PUBLIC_API_URL=http://localhost:8000

**Acceptance**: Backend server runs at :8000, frontend dev server ready, database connection configured, CORS enabled

---

## Phase 3: User Story 1 - Database Schema and Connection (P0) (8 tasks)

**Story Goal**: Set up PostgreSQL database using Neon with SQLModel so tasks can be persisted across sessions

**Why P0**: Foundational infrastructure - all other features depend on database persistence

**Independent Test**: Verify database connection, schema creation, and direct CRUD operations through SQLModel (no API needed yet)

**Tasks**:

- [X] T016 [P] [US1] Create backend/src/models/__init__.py (empty init file)
- [X] T017 [P] [US1] Create backend/src/models/user.py with User SQLModel (id: UUID, email: str unique, password_hash: str, created_at: datetime)
- [X] T018 [P] [US1] Create backend/src/models/task.py with Task SQLModel (id: UUID, user_id: UUID FK, title: str max 500, description: Optional[str], status: TaskStatus enum, created_at, updated_at)
- [X] T019 [US1] Initialize Alembic in backend/: `alembic init alembic` and configure alembic.ini with DATABASE_URL
- [X] T020 [US1] Configure alembic/env.py to import SQLModel metadata and use async engine from database.py
- [X] T021 [US1] Generate initial migration: `alembic revision --autogenerate -m "Initial schema - users and tasks tables"`
- [X] T022 [US1] Apply migration to Neon database: `alembic upgrade head`
- [X] T023 [US1] Write Python script to test direct database CRUD (create user, create task, query tasks, verify persistence) and run successfully

**Acceptance Scenarios** (from spec.md):
1. ✅ Given Neon PostgreSQL credentials configured, When application initializes, Then database connection established successfully
2. ✅ Given database connection active, When schema migration runs, Then task table created with correct fields and constraints
3. ✅ Given task table exists, When task inserted via SQLModel, Then task persists and can be queried with all fields intact
4. ✅ Given database connection fails, When application starts, Then clear error message displayed indicating connection issue

**Parallel Opportunities**: T016, T017, T018 can be implemented in parallel (different files, no dependencies)

---

## Phase 4: User Story 2 - Backend REST API Endpoints (P0) (15 tasks)

**Story Goal**: Develop FastAPI REST endpoints for task operations so frontend can manage tasks through standard API

**Why P0**: Core backend functionality - replaces Phase 1 in-memory logic with database-backed operations

**Independent Test**: Test all CRUD endpoints using Postman/curl/Swagger UI (http://localhost:8000/docs) with authenticated requests

**Tasks**:

### Schemas (Request/Response Models)

- [X] T024 [P] [US2] Create backend/src/schemas/__init__.py (empty init file)
- [X] T025 [P] [US2] Create backend/src/schemas/task.py with TaskCreate, TaskUpdate, TaskResponse Pydantic models matching data-model.md
- [X] T026 [US2] Add from_attributes = True to TaskResponse Config for SQLModel → Pydantic conversion

### Task Router & Endpoints

- [X] T027 [P] [US2] Create backend/src/routers/__init__.py (empty init file)
- [X] T028 [US2] Create backend/src/routers/tasks.py with APIRouter and dependency injection for database session and current user
- [X] T029 [US2] Implement GET /tasks endpoint - query tasks filtered by current user_id, return List[TaskResponse]
- [X] T030 [US2] Implement POST /tasks endpoint - validate TaskCreate, create task with user_id from token, return 201 with TaskResponse
- [X] T031 [US2] Implement GET /tasks/{task_id} endpoint - query by ID, verify ownership (user_id match), return 404 if not found/not owned
- [X] T032 [US2] Implement PUT /tasks/{task_id} endpoint - validate TaskUpdate, verify ownership, update task, return TaskResponse
- [X] T033 [US2] Implement DELETE /tasks/{task_id} endpoint - verify ownership, delete task, return 204 No Content
- [X] T034 [US2] Implement PATCH /tasks/{task_id}/complete endpoint - verify ownership, toggle status (incomplete ↔ complete), return TaskResponse
- [X] T035 [US2] Add tasks router to main.py: `app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])`
- [X] T036 [US2] Add global exception handler in main.py for HTTPException and general exceptions with proper error formatting
- [X] T037 [US2] Add request logging middleware in main.py to log all API requests with timestamp, endpoint, user_id (if authenticated), response status
- [X] T038 [US2] Test all task endpoints via Swagger UI at http://localhost:8000/docs - verify responses match contracts/api-spec.yaml

**Acceptance Scenarios** (from spec.md):
1. ✅ Given authenticated user, When POST /tasks with valid task data, Then task created in database and returns 201 with task object
2. ✅ Given tasks exist in database, When GET /tasks, Then returns 200 with array of all user's tasks
3. ✅ Given task exists with ID 5, When PUT /tasks/5 with updated title, Then task updated in database and returns 200 with updated task
4. ✅ Given task exists with ID 3, When DELETE /tasks/3, Then task removed from database and returns 204
5. ✅ Given task exists with ID 2, When PATCH /tasks/2/complete, Then task status toggles and returns 200 with updated task
6. ✅ Given invalid task ID 999, When any operation on /tasks/999, Then returns 404 with error message
7. ✅ Given invalid request body, When POST or PUT request, Then returns 422 with validation errors

**Parallel Opportunities**: T024, T025, T027 can be implemented in parallel (schemas and router init files)

**Dependencies**: Requires Phase 3 (database models) complete before T028-T038

---

## Phase 5: User Story 3 - User Authentication System (P0) (14 tasks)

**Story Goal**: Implement user signup and signin using JWT tokens so tasks are private and secure

**Why P0**: Critical for multi-user support and data privacy - must be implemented before UI to ensure secure API access

**Independent Test**: Test signup/signin endpoints, verify JWT token generation, test protected endpoints reject unauthenticated requests

**Tasks**:

### Security Utilities

- [X] T039 [P] [US3] Create backend/src/utils/__init__.py (empty init file)
- [X] T040 [P] [US3] Create backend/src/utils/security.py with hash_password (using bcrypt directly), verify_password, create_access_token (15 min exp), create_refresh_token (7 day exp) using python-jose
- [X] T041 [P] [US3] Create backend/src/utils/errors.py with custom exception classes: AuthenticationError, AuthorizationError, NotFoundError

### Auth Schemas

- [X] T042 [P] [US3] Create backend/src/schemas/auth.py with SignupRequest (email: EmailStr, password: str min 8), SigninRequest, TokenResponse, UserResponse Pydantic models

### Auth Dependencies

- [X] T043 [P] [US3] Create backend/src/dependencies/__init__.py (empty init file)
- [X] T044 [US3] Create backend/src/dependencies/auth.py with get_current_user dependency (extracts JWT from Authorization header, validates token, returns user_id)
- [X] T045 [US3] Add OAuth2PasswordBearer scheme to dependencies/auth.py for Swagger UI authorization

### Auth Router & Endpoints

- [X] T046 [US3] Create backend/src/routers/auth.py with APIRouter
- [X] T047 [US3] Implement POST /auth/signup endpoint - validate email uniqueness, hash password, create user in database, generate tokens, return 201 with TokenResponse
- [X] T048 [US3] Add error handling to signup endpoint - return 409 if email already registered, 422 for validation errors
- [X] T049 [US3] Implement POST /auth/signin endpoint - verify email exists, verify password using verify_password, generate tokens, return 200 with TokenResponse
- [X] T050 [US3] Add error handling to signin endpoint - return 401 for invalid credentials (don't reveal if email or password wrong)
- [X] T051 [US3] Implement POST /auth/refresh endpoint - validate refresh token, generate new access token, return TokenResponse
- [X] T052 [US3] Add auth router to main.py: `app.include_router(auth.router, prefix="/auth", tags=["Authentication"])`

**Acceptance Scenarios** (from spec.md):
1. ✅ Given no existing account, When POST /auth/signup with email and password, Then user account created and returns 201 with user object
2. ✅ Given valid credentials, When POST /auth/signin with email and password, Then returns 200 with JWT access token and refresh token
3. ✅ Given invalid credentials, When POST /auth/signin, Then returns 401 with error message "Invalid credentials"
4. ✅ Given duplicate email, When POST /auth/signup, Then returns 409 with error message "Email already registered"
5. ✅ Given no JWT token, When accessing protected endpoint /tasks, Then returns 401 with error message "Authentication required"
6. ✅ Given valid JWT token in Authorization header, When accessing /tasks, Then returns user's tasks successfully
7. ✅ Given expired JWT token, When accessing protected endpoint, Then returns 401 with error message "Token expired"
8. ✅ Given valid refresh token, When POST /auth/refresh, Then returns new JWT access token

**Parallel Opportunities**: T039, T040, T041, T042, T043 can be implemented in parallel (independent utility files and schemas)

**Integration**: After T052, update tasks router (Phase 4) to use get_current_user dependency on all endpoints

---

## Phase 6: User Story 4 - Next.js Web Interface (P1) (16 tasks)

**Story Goal**: Build modern, responsive web UI so users can manage tasks through browser instead of command line

**Why P1**: Critical for user experience but depends on functional APIs (P0 stories must be complete first)

**Independent Test**: Navigate through all pages, verify responsive design, test all CRUD operations through UI, validate error handling

**Tasks**:

### Frontend Infrastructure

- [X] T053 [P] [US4] Create frontend/lib/types.ts with TypeScript interfaces: User, Task, TaskStatus, ApiError, TokenResponse
- [X] T054 [P] [US4] Create frontend/lib/auth.ts with token management helpers: setCookie, getCookie, clearTokens, refreshAccessToken using js-cookie
- [X] T055 [US4] Create frontend/lib/api.ts with API client wrapper - fetch with auth header injection, automatic token refresh on 401, error handling
- [X] T056 [US4] Update frontend/lib/api.ts with task API functions: getTasks(), createTask(), updateTask(), deleteTask(), toggleTaskComplete()
- [X] T057 [US4] Update frontend/lib/api.ts with auth API functions: signup(), signin(), refresh()

### UI Components

- [X] T058 [P] [US4] Create frontend/components/ui/Button.tsx (reusable button component with Tailwind variants: primary, secondary, danger)
- [X] T059 [P] [US4] Create frontend/components/ui/Input.tsx (reusable input component with label, error state, validation)
- [X] T060 [P] [US4] Create frontend/components/ui/Toast.tsx (toast notification component for success/error messages)
- [X] T061 [US4] Create frontend/components/AuthForm.tsx (reusable form for signin/signup with email, password fields, submit handling)
- [X] T062 [US4] Create frontend/components/TaskList.tsx (task list component with checkboxes, edit/delete buttons, empty state)
- [X] T063 [US4] Create frontend/components/TaskForm.tsx (reusable form for add/edit task with title, description fields, validation)

### Pages

- [X] T064 [US4] Create frontend/app/signin/page.tsx - signin form using AuthForm, call signin API, store tokens in cookies, redirect to /tasks
- [X] T065 [US4] Create frontend/app/signup/page.tsx - signup form using AuthForm, call signup API, store tokens, redirect to /tasks
- [X] T066 [US4] Create frontend/app/tasks/page.tsx - fetch and display task list using TaskList component, handle loading/error states
- [X] T067 [US4] Create frontend/app/tasks/new/page.tsx - add task form using TaskForm, call createTask API, redirect to /tasks on success
- [X] T068 [US4] Create frontend/app/tasks/[id]/edit/page.tsx - edit task form using TaskForm pre-filled with task data, call updateTask API

### Protected Routes & Middleware

- [X] T069 [US4] Create frontend/middleware.ts - check for access_token cookie, redirect unauthenticated users to /signin for /tasks/* routes

**Acceptance Scenarios** (from spec.md):
1. ✅ Given unauthenticated user, When visiting /tasks, Then redirected to /signin page
2. ✅ Given signin page, When entering valid credentials and submitting, Then redirected to /tasks with task list displayed
3. ✅ Given authenticated on /tasks, When clicking "Add Task" and submitting form, Then new task appears in list without page reload
4. ✅ Given task in list, When clicking edit icon and updating title, Then task updates in list without page reload
5. ✅ Given task in list, When clicking delete icon and confirming, Then task removed from list without page reload
6. ✅ Given incomplete task, When clicking checkbox, Then task marked complete with visual indicator (checkmark)
7. ✅ Given mobile viewport, When viewing task list, Then UI fully responsive and usable on small screens
8. ✅ Given API error, When operation fails, Then user-friendly error message displayed (not raw API error)
9. ✅ Given authenticated user, When clicking "Sign Out", Then JWT token cleared and user redirected to /signin

**Parallel Opportunities**: T053, T054, T058, T059, T060 can be implemented in parallel (independent type definitions and UI components)

**Dependencies**: Requires Phase 5 (authentication) complete for token management; requires Phase 4 (task API) complete for CRUD operations

---

## Phase 7: User Story 5 - Phase 1 Legacy Compatibility (P0) (3 tasks)

**Story Goal**: Verify Phase 1 console application remains fully functional so we maintain backward compatibility

**Why P0**: Critical constraint to ensure existing work is preserved and demonstrates evolution from Phase 1 to Phase 2

**Independent Test**: Run `python src/main.py` and verify all five Phase 1 operations work with in-memory storage

**Tasks**:

- [ ] T070 [US5] Run Phase 1 console app: `python src/main.py` and verify menu appears with all 6 options
- [ ] T071 [US5] Test all Phase 1 CRUD operations (Add Task, View Tasks, Update Task, Delete Task, Mark Complete, Exit) and verify they work correctly with in-memory storage
- [ ] T072 [US5] Verify Phase 1 tasks are lost on exit (in-memory behavior preserved) and check `git status src/` shows no modifications to Phase 1 files

**Acceptance Scenarios** (from spec.md):
1. ✅ Given Phase 2 backend and database set up, When running `python src/main.py`, Then Phase 1 console app launches with original menu
2. ✅ Given Phase 1 app running, When performing all CRUD operations, Then all operations work as specified in Phase 1 spec using in-memory storage
3. ✅ Given Phase 1 app running, When exiting application, Then tasks are lost (in-memory behavior preserved)
4. ✅ Given Phase 2 files exist in backend/ and frontend/, When checking src/ directory, Then no Phase 1 files modified or deleted

**Dependencies**: Can be tested at any point after Phase 2 (Foundational) is complete

---

## Phase 8: Integration, Testing & Polish (2 tasks)

**Goal**: Final integration verification, performance testing, security validation, documentation

**Prerequisites**: All user story phases (3-7) complete

**Tasks**:

- [ ] T073 End-to-end integration test - complete user journey: signup → signin → add tasks → mark complete → edit → delete → signout, verify all flows work without errors, test token expiration and refresh, verify authorization (users can't access others' tasks), test error scenarios from spec.md edge cases
- [ ] T074 Final verification - update README.md with quickstart instructions from quickstart.md, verify .gitignore prevents committing secrets, run Phase 1 console app to confirm no interference, verify all 12 success criteria from spec.md

**Acceptance**: All end-to-end flows work, Phase 1 still functional, all success criteria met, documentation updated

---

## Dependency Graph

### Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
    ├─→ Phase 3: US1 (Database) ──────────────┐
    │                                          ↓
    ├─→ Phase 5: US3 (Authentication) ────→ Phase 4: US2 (Backend API)
    │                                          ↓
    └─→ Phase 7: US5 (Phase 1 Check)     Phase 6: US4 (Frontend)
                                               ↓
                                          Phase 8 (Integration)
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (US1) → Phase 5 (US3) → Phase 4 (US2) → Phase 6 (US4) → Phase 8

**Parallel Opportunities**:
- Phase 3 (US1) and Phase 5 (US3) security utilities can be developed in parallel
- Phase 7 (US5) Phase 1 verification can be done anytime after Phase 2
- Within Phase 4 (US2): Schema creation tasks can be parallelized
- Within Phase 6 (US4): UI component creation can be highly parallelized

### Task Dependencies by Phase

**Phase 3 (US1 - Database)**:
- T016-T018 (models) → independent, can parallelize
- T019-T022 (Alembic) → sequential, depend on T016-T018
- T023 (test) → depends on T022

**Phase 4 (US2 - Backend API)**:
- T024-T027 (schemas/init) → independent, can parallelize
- T028-T038 (router/endpoints) → sequential, depend on T024-T027 and Phase 3 complete

**Phase 5 (US3 - Authentication)**:
- T039-T043 (utils/schemas/deps init) → independent, can parallelize
- T044-T045 (auth dependencies) → depend on T039-T041
- T046-T052 (auth router) → depend on T044-T045

**Phase 6 (US4 - Frontend)**:
- T053-T060 (types/utils/UI components) → mostly independent, can parallelize
- T061-T063 (complex components) → depend on T053-T060
- T064-T068 (pages) → depend on T061-T063
- T069 (middleware) → depends on T054

**Phase 7 (US5 - Phase 1 Check)**:
- T070-T072 → sequential verification tasks

---

## Parallel Execution Examples

### Backend Development (Phases 3-5)

**Iteration 1** (Parallel):
```bash
# Terminal 1: Database models
- T016, T017, T018 (User and Task models)

# Terminal 2: Auth utilities
- T039, T040, T041 (security utils, errors)

# Terminal 3: Schemas
- T024, T025 (task schemas)
- T042 (auth schemas)
```

**Iteration 2** (Sequential):
```bash
# Complete Alembic setup and migrations
- T019, T020, T021, T022, T023
```

**Iteration 3** (Parallel):
```bash
# Terminal 1: Task endpoints
- T028-T034 (task router and all endpoints)

# Terminal 2: Auth endpoints
- T044-T051 (auth dependencies and endpoints)
```

**Iteration 4** (Integration):
```bash
# Integrate routers and test
- T035, T036, T037, T038 (add routers to main, test)
- T052 (add auth router to main)
```

### Frontend Development (Phase 6)

**Iteration 1** (Parallel - High Parallelization):
```bash
# Terminal 1: Types and API layer
- T053 (types), T054 (auth helpers)

# Terminal 2: UI components set 1
- T058 (Button), T059 (Input)

# Terminal 3: UI components set 2
- T060 (Toast)
```

**Iteration 2** (Parallel):
```bash
# Terminal 1: API client
- T055, T056, T057 (API client with all functions)

# Terminal 2: Complex components
- T061 (AuthForm), T062 (TaskList), T063 (TaskForm)
```

**Iteration 3** (Can be parallelized):
```bash
# Terminal 1: Auth pages
- T064 (signin), T065 (signup)

# Terminal 2: Task pages
- T066 (task list), T067 (new task), T068 (edit task)

# Terminal 3: Middleware
- T069 (protected routes middleware)
```

---

## Testing Strategy

**Backend Testing** (via Swagger UI):
1. Start backend: `uvicorn src.main:app --reload --port 8000`
2. Open http://localhost:8000/docs
3. Test auth flow:
   - POST /auth/signup with test user
   - POST /auth/signin to get tokens
   - Use "Authorize" button to add Bearer token
4. Test task CRUD:
   - POST /tasks to create tasks
   - GET /tasks to list tasks
   - PUT /tasks/{id} to update
   - PATCH /tasks/{id}/complete to toggle
   - DELETE /tasks/{id} to remove
5. Verify authorization:
   - Create second user
   - Verify user A cannot access user B's tasks (404 response)

**Frontend Testing** (manual browser testing):
1. Start frontend: `npm run dev` (runs on :3000)
2. Test authentication flow:
   - Navigate to http://localhost:3000/tasks (should redirect to /signin)
   - Sign up new user → should redirect to /tasks
   - Sign out → should clear tokens and redirect to /signin
   - Sign in with existing user → should work
3. Test task management:
   - Add new task → appears in list
   - Edit task → updates inline
   - Mark complete → checkbox toggles
   - Delete task → removes from list
4. Test responsive design:
   - Open Chrome DevTools (F12)
   - Toggle device toolbar (Ctrl+Shift+M)
   - Test mobile (320px), tablet (768px), desktop (1024px+)
5. Test error handling:
   - Stop backend server
   - Try to add task → should show user-friendly error
   - Invalid credentials on signin → should show error

**Phase 1 Compatibility Testing**:
1. Run `python src/main.py`
2. Test all menu options (1-6)
3. Verify tasks are in-memory only (lost on exit)
4. Run `git status src/` → should show no changes

---

## Success Criteria Verification

After completing all tasks, verify these success criteria from spec.md:

- [ ] **SC-001**: Users can sign up and sign in to their account in under 1 minute
- [ ] **SC-002**: Users can create a new task and see it in their list in under 5 seconds
- [ ] **SC-003**: Task list loads and displays within 2 seconds for up to 1,000 tasks
- [ ] **SC-004**: All CRUD operations persist to database and survive application restarts
- [ ] **SC-005**: Web UI is fully responsive and usable on screens as small as 320px width (mobile)
- [ ] **SC-006**: 100% of API endpoints return appropriate status codes and error messages for invalid requests
- [ ] **SC-007**: Users cannot access another user's tasks (100% authorization coverage)
- [ ] **SC-008**: Phase 1 console application runs successfully without any modifications to src/ code
- [ ] **SC-009**: Authentication tokens expire appropriately (access: 15 min, refresh: 7 days) and are refreshable
- [ ] **SC-010**: Database schema supports minimum 10,000 tasks per user without performance degradation
- [ ] **SC-011**: API handles database connection failures gracefully with appropriate error responses (no crashes)
- [ ] **SC-012**: 95% of users can complete primary workflows (signup, add task, mark complete, view tasks) on first attempt without help

---

## MVP Definition

**Minimum Viable Product** = Phase 1 + Phase 2 + Phase 3 (US1) + Phase 5 (US3) + Phase 4 (US2)

This provides:
- ✅ Database persistence with User and Task models
- ✅ User authentication (signup, signin, JWT tokens)
- ✅ Complete task CRUD API (testable via Swagger UI)
- ✅ Multi-user support with authorization

**Not included in MVP** (can be added incrementally):
- Web UI (Phase 6 - US4)
- Full end-to-end testing (Phase 8)

**MVP can be tested independently** using API testing tools before frontend development begins.

---

## Next Steps

1. **Start with Phase 1**: Set up project structure and environment
2. **Complete Phase 2**: Initialize backend and frontend frameworks
3. **Implement MVP** (Phases 3, 5, 4): Database + Auth + API
4. **Test MVP**: Use Swagger UI to verify all backend functionality
5. **Build Frontend** (Phase 6): Add web UI
6. **Verify Compatibility** (Phase 7): Ensure Phase 1 still works
7. **Final Integration** (Phase 8): End-to-end testing and polish
8. **Run `/sp.git.commit_pr`**: Commit changes and create pull request

---

## Format Validation

✅ **All 73 tasks follow the required checklist format**:
- Checkbox: `- [ ]`
- Task ID: `T001` through `T074`
- [P] marker: Present on 28 parallelizable tasks
- [Story] label: Present on all user story phase tasks (US1-US5)
- Description: Includes clear action and file path where applicable

✅ **Task organization validates**:
- Organized by user story phases (matching spec.md priorities)
- Each phase has clear goal and independent test criteria
- Dependencies documented in dependency graph
- Parallel opportunities identified and documented
