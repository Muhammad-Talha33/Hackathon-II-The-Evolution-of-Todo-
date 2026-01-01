# Feature Specification: Phase 2 Full Stack Web Application

**Feature Branch**: `001-phase2-full-stack-web`
**Created**: 2025-12-29
**Status**: Draft
**Input**: User description: "Building a Web Interface and Database layer, keeping Phase 1 as a reference. Includes PostgreSQL database using Neon & SQLModel, REST APIs in backend/ using FastAPI, modern responsive UI in frontend/ (Next.js), user authentication using Better Auth with JWT tokens, while ensuring Phase 1 code in src/ remains untouched and fully runnable."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Database Schema and Connection (Priority: P0)

As a developer, I want to set up a PostgreSQL database using Neon with SQLModel so that tasks can be persisted across sessions.

**Why this priority**: This is the foundational infrastructure requirement. Without persistent storage, the web application cannot function. This must be completed before any API or UI work can begin.

**Independent Test**: Can be fully tested by establishing database connection, creating the task table schema with all required fields (id, title, description, status, user_id, created_at, updated_at), and verifying CRUD operations work directly through SQLModel without APIs.

**Acceptance Scenarios**:

1. **Given** Neon PostgreSQL credentials are configured, **When** the application initializes, **Then** database connection is established successfully
2. **Given** database connection is active, **When** schema migration runs, **Then** task table is created with correct fields and constraints
3. **Given** task table exists, **When** a task is inserted via SQLModel, **Then** the task persists and can be queried with all fields intact
4. **Given** database connection fails, **When** application starts, **Then** clear error message is displayed indicating connection issue

---

### User Story 2 - Backend REST API Endpoints (Priority: P0)

As a developer, I want FastAPI REST endpoints for task operations so that the frontend can manage tasks through a standard API.

**Why this priority**: The API layer is the bridge between database and UI. Without functional APIs, the frontend cannot interact with persisted data. This replaces Phase 1 in-memory logic with database-backed operations.

**Independent Test**: Can be fully tested using API testing tools (Postman, curl) to verify all CRUD endpoints (GET /tasks, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}, PATCH /tasks/{id}/complete) return correct responses, handle errors properly, and persist data to database.

**Acceptance Scenarios**:

1. **Given** authenticated user, **When** POST /tasks with valid task data, **Then** task is created in database and returns 201 with task object
2. **Given** tasks exist in database, **When** GET /tasks, **Then** returns 200 with array of all user's tasks
3. **Given** task exists with ID 5, **When** PUT /tasks/5 with updated title, **Then** task is updated in database and returns 200 with updated task
4. **Given** task exists with ID 3, **When** DELETE /tasks/3, **Then** task is removed from database and returns 204
5. **Given** task exists with ID 2, **When** PATCH /tasks/2/complete, **Then** task status toggles and returns 200 with updated task
6. **Given** invalid task ID 999, **When** any operation on /tasks/999, **Then** returns 404 with error message
7. **Given** invalid request body, **When** POST or PUT request, **Then** returns 422 with validation errors

---

### User Story 3 - User Authentication System (Priority: P0)

As a user, I want to sign up and sign in using Better Auth so that my tasks are private and secure.

**Why this priority**: Authentication is critical for multi-user support and data privacy. Without it, all tasks would be shared or public. This must be implemented before the UI to ensure secure API access from the start.

**Independent Test**: Can be fully tested by creating user accounts via signup endpoint, obtaining JWT tokens via signin endpoint, verifying protected API endpoints reject unauthenticated requests, and confirming authenticated requests with valid JWT tokens succeed.

**Acceptance Scenarios**:

1. **Given** no existing account, **When** POST /auth/signup with email and password, **Then** user account is created and returns 201 with user object
2. **Given** valid credentials, **When** POST /auth/signin with email and password, **Then** returns 200 with JWT access token and refresh token
3. **Given** invalid credentials, **When** POST /auth/signin, **Then** returns 401 with error message "Invalid credentials"
4. **Given** duplicate email, **When** POST /auth/signup, **Then** returns 409 with error message "Email already registered"
5. **Given** no JWT token, **When** accessing protected endpoint /tasks, **Then** returns 401 with error message "Authentication required"
6. **Given** valid JWT token in Authorization header, **When** accessing /tasks, **Then** returns user's tasks successfully
7. **Given** expired JWT token, **When** accessing protected endpoint, **Then** returns 401 with error message "Token expired"
8. **Given** valid refresh token, **When** POST /auth/refresh, **Then** returns new JWT access token

---

### User Story 4 - Next.js Web Interface (Priority: P1)

As a user, I want a modern, responsive web UI so that I can manage tasks through a browser instead of command line.

**Why this priority**: While critical for user experience, the UI depends on functional APIs and authentication. It's P1 (not P0) because the APIs can be tested independently first, and the UI can be developed iteratively.

**Independent Test**: Can be fully tested by navigating through all pages (signup, signin, task list, add task, edit task), verifying responsive design on mobile and desktop, confirming all CRUD operations work through the UI, and validating error handling displays user-friendly messages.

**Acceptance Scenarios**:

1. **Given** unauthenticated user, **When** visiting /tasks, **Then** redirected to /signin page
2. **Given** signin page, **When** entering valid credentials and submitting, **Then** redirected to /tasks with task list displayed
3. **Given** authenticated on /tasks, **When** clicking "Add Task" and submitting form, **Then** new task appears in list without page reload
4. **Given** task in list, **When** clicking edit icon and updating title, **Then** task updates in list without page reload
5. **Given** task in list, **When** clicking delete icon and confirming, **Then** task is removed from list without page reload
6. **Given** incomplete task, **When** clicking checkbox, **Then** task is marked complete with visual indicator (checkmark)
7. **Given** mobile viewport, **When** viewing task list, **Then** UI is fully responsive and usable on small screens
8. **Given** API error, **When** operation fails, **Then** user-friendly error message is displayed (not raw API error)
9. **Given** authenticated user, **When** clicking "Sign Out", **Then** JWT token is cleared and user is redirected to /signin

---

### User Story 5 - Phase 1 Legacy Compatibility (Priority: P0)

As a developer, I want Phase 1 console application to remain fully functional so that we maintain backward compatibility and can demonstrate the evolution from Phase 1 to Phase 2.

**Why this priority**: This is a critical constraint to ensure existing work is preserved and runnable. It validates that the new Phase 2 implementation doesn't interfere with Phase 1.

**Independent Test**: Can be fully tested by running `python src/main.py` and verifying all five Phase 1 operations (Add Task, View Tasks, Update Task, Delete Task, Mark Complete) work exactly as specified in Phase 1 spec, with in-memory storage and menu-driven interface.

**Acceptance Scenarios**:

1. **Given** Phase 2 backend and database are set up, **When** running `python src/main.py`, **Then** Phase 1 console app launches with original menu
2. **Given** Phase 1 app running, **When** performing all CRUD operations, **Then** all operations work as specified in Phase 1 spec using in-memory storage
3. **Given** Phase 1 app running, **When** exiting application, **Then** tasks are lost (in-memory behavior preserved)
4. **Given** Phase 2 files exist in backend/ and frontend/, **When** checking src/ directory, **Then** no Phase 1 files are modified or deleted

---

### Edge Cases

- What happens when database connection is lost during API request? System returns 503 Service Unavailable with message "Database temporarily unavailable, please try again"
- What happens when user's JWT token expires during active session? Frontend detects 401 response, attempts token refresh, and re-authenticates user or prompts signin
- What happens when two users modify the same task simultaneously? Last write wins (optimistic concurrency), user sees updated data on next refresh
- What happens when user provides extremely long task title (>10,000 chars)? API validates and rejects with 422 error "Title exceeds maximum length of 500 characters"
- What happens when Neon database reaches connection limit? System queues requests and returns 503 if timeout exceeded
- How does system handle SQL injection attempts in task data? SQLModel parameterized queries prevent injection; system sanitizes and validates all inputs
- What happens when user forgets password? Password reset is out of scope for Phase 2; users must create a new account or contact support
- What happens when user tries to access another user's task by guessing ID? API validates task ownership; returns 404 (not 403) to prevent task ID enumeration
- How are JWT tokens stored in frontend? Tokens stored in httpOnly cookies (preferred) or localStorage with XSS protections
- What happens when user's session expires while editing a task? Changes are lost; user is prompted to sign in again (no auto-save in Phase 2)

## Requirements *(mandatory)*

### Functional Requirements

**Database Layer:**
- **FR-001**: System MUST use PostgreSQL hosted on Neon as the persistence layer
- **FR-002**: System MUST use SQLModel for database schema definition and ORM operations
- **FR-003**: System MUST define Task model with fields: id (UUID primary key), user_id (UUID foreign key), title (string, required, max 500 chars), description (text, optional), status (enum: incomplete/complete), created_at (timestamp), updated_at (timestamp)
- **FR-004**: System MUST define User model with fields: id (UUID primary key), email (string, unique, required), password_hash (string, required), created_at (timestamp)
- **FR-005**: System MUST establish foreign key relationship: Task.user_id references User.id with cascade delete
- **FR-006**: System MUST handle database connection pooling and graceful connection failures

**Backend API Layer:**
- **FR-007**: System MUST implement REST API using FastAPI framework
- **FR-008**: System MUST expose endpoints: POST /auth/signup, POST /auth/signin, POST /auth/refresh
- **FR-009**: System MUST expose endpoints: GET /tasks, POST /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id}, PATCH /tasks/{id}/complete
- **FR-010**: System MUST validate all request bodies using Pydantic models
- **FR-011**: System MUST return appropriate HTTP status codes: 200 (success), 201 (created), 204 (deleted), 400 (bad request), 401 (unauthorized), 404 (not found), 422 (validation error), 500 (server error), 503 (service unavailable)
- **FR-012**: System MUST filter tasks by authenticated user (user can only access their own tasks)
- **FR-013**: System MUST implement CORS configuration allowing frontend origin
- **FR-014**: System MUST log all API requests with timestamp, endpoint, user_id, and response status

**Authentication Layer:**
- **FR-015**: System MUST use Better Auth library for authentication implementation
- **FR-016**: System MUST hash passwords using bcrypt or Argon2 before storing in database
- **FR-017**: System MUST generate JWT access tokens with 15-minute expiration
- **FR-018**: System MUST generate JWT refresh tokens with 7-day expiration
- **FR-019**: System MUST validate JWT tokens on all protected endpoints (all /tasks endpoints)
- **FR-020**: System MUST include user_id in JWT payload for authorization
- **FR-021**: System MUST validate email format during signup (standard email regex)
- **FR-022**: System MUST enforce minimum password length of 8 characters during signup
- **FR-023**: System MUST return 401 for invalid credentials without revealing whether email or password was incorrect

**Frontend Layer:**
- **FR-024**: System MUST implement UI using Next.js framework with React
- **FR-025**: System MUST implement responsive design supporting mobile (320px+), tablet (768px+), and desktop (1024px+) viewports
- **FR-026**: System MUST implement pages: /signin, /signup, /tasks (task list), /tasks/new (add task), /tasks/[id]/edit (edit task)
- **FR-027**: System MUST implement protected route middleware redirecting unauthenticated users to /signin
- **FR-028**: System MUST display loading states during API requests
- **FR-029**: System MUST display user-friendly error messages for all failed operations
- **FR-030**: System MUST store JWT tokens securely and include in Authorization header for API requests
- **FR-031**: System MUST implement task list with visual status indicators (checkbox for complete/incomplete)
- **FR-032**: System MUST implement optimistic UI updates (update UI immediately, rollback on API failure)
- **FR-033**: System MUST implement sign-out functionality clearing JWT tokens and redirecting to /signin

**Phase 1 Compatibility:**
- **FR-034**: System MUST maintain all Phase 1 source code in src/ directory without modifications
- **FR-035**: System MUST ensure `python src/main.py` launches Phase 1 console app with original functionality
- **FR-036**: System MUST keep Phase 1 in-memory storage behavior independent of Phase 2 database
- **FR-037**: Phase 2 backend MUST reside in backend/ directory (separate from src/)
- **FR-038**: Phase 2 frontend MUST reside in frontend/ directory (separate from src/)

### Key Entities

- **User**: Represents an authenticated application user
  - **ID**: Unique UUID identifier
  - **Email**: Unique email address for authentication (validated format)
  - **Password Hash**: Securely hashed password (never store plaintext)
  - **Created At**: Timestamp of account creation
  - Relationships: Has many Tasks

- **Task**: Represents a todo item owned by a specific user
  - **ID**: Unique UUID identifier
  - **User ID**: Foreign key referencing owning User
  - **Title**: Required description of task (max 500 characters)
  - **Description**: Optional additional details (unlimited text)
  - **Status**: Completion state (incomplete or complete)
  - **Created At**: Timestamp of task creation
  - **Updated At**: Timestamp of last modification
  - Relationships: Belongs to one User

- **JWT Token**: Authentication credential
  - **Access Token**: Short-lived token (15 min) for API authentication
  - **Refresh Token**: Long-lived token (7 days) for obtaining new access tokens
  - **Payload**: Contains user_id, issued_at, expires_at

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can sign up and sign in to their account in under 1 minute
- **SC-002**: Users can create a new task and see it in their list in under 5 seconds
- **SC-003**: Task list loads and displays within 2 seconds for up to 1,000 tasks
- **SC-004**: All CRUD operations (Create, Read, Update, Delete) persist to database and survive application restarts
- **SC-005**: Web UI is fully responsive and usable on screens as small as 320px width (mobile)
- **SC-006**: 100% of API endpoints return appropriate status codes and error messages for invalid requests
- **SC-007**: Users cannot access another user's tasks (100% authorization coverage)
- **SC-008**: Phase 1 console application runs successfully without any modifications to src/ code
- **SC-009**: Authentication tokens expire appropriately (access: 15 min, refresh: 7 days) and are refreshable
- **SC-010**: Database schema supports minimum 10,000 tasks per user without performance degradation
- **SC-011**: API handles database connection failures gracefully with appropriate error responses (no crashes)
- **SC-012**: 95% of users can complete primary workflows (signup, add task, mark complete, view tasks) on first attempt without help

### Out of Scope

The following are explicitly NOT included in Phase 2:

- Task categories, tags, or labels
- Task priorities or due dates
- Task assignment to other users or sharing
- Real-time collaboration or WebSocket updates
- Task search or advanced filtering
- Bulk operations (delete all, mark all complete)
- Task history or audit trail
- User profile management or settings
- Email notifications or reminders
- Third-party OAuth providers (Google, GitHub)
- Password reset via email (requires email service)
- Two-factor authentication (2FA)
- Task attachments or file uploads
- Dark mode or theme customization
- Internationalization (i18n) - English only
- Mobile native apps (iOS/Android)
- Task export (PDF, CSV)
- Analytics or usage tracking
- Rate limiting or API throttling
- Automated testing (unit, integration, e2e)

## Assumptions

1. **Infrastructure**: Neon PostgreSQL free tier provides sufficient database capacity for development and testing
2. **Deployment**: Application will be deployed separately (backend and frontend can be on different hosts)
3. **User Base**: Initially supporting single-region deployment (no multi-region requirements)
4. **Authentication**: Better Auth library is compatible with FastAPI and Next.js ecosystems
5. **Session Management**: Users accept 15-minute access token expiration (re-authentication via refresh token)
6. **Data Volume**: Average user will have under 1,000 tasks (database schema optimized for this scale)
7. **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge) with JavaScript enabled
8. **Network**: Users have stable internet connection (no offline mode)
9. **Security**: HTTPS will be used in production (development may use HTTP)
10. **Performance**: Standard web application response times acceptable (< 3 seconds for all operations)
11. **Email Uniqueness**: Each user has one account per email address (no email change functionality)
12. **Password Policy**: 8-character minimum is sufficient for initial release (no complexity requirements)
13. **Data Retention**: No automatic data deletion (tasks and accounts persist indefinitely)
14. **Concurrent Users**: System will support up to 100 concurrent users initially (can scale horizontally)
15. **Development Environment**: Developers have Node.js, Python, and database tools installed locally

## Dependencies

**External Services:**
- Neon PostgreSQL (cloud-hosted database)
- Better Auth library (authentication framework)

**Technology Stack:**
- Backend: Python 3.13+, FastAPI, SQLModel, Pydantic
- Frontend: Node.js 18+, Next.js 14+, React 18+
- Database: PostgreSQL 15+ (via Neon)
- Authentication: JWT tokens via Better Auth

**Development Tools:**
- Package managers: pip (Python), npm/yarn (Node.js)
- Environment configuration: .env files for secrets
- API testing: Postman, curl, or similar (for independent API testing)

**Phase 1 Dependency:**
- Phase 1 console app in src/ must remain runnable (no breaking changes)
