# Research: Phase 2 Full Stack Web Application

**Date**: 2025-12-29
**Feature**: 001-phase2-full-stack-web
**Purpose**: Research technical decisions for implementing full-stack web application with FastAPI backend, Next.js frontend, PostgreSQL database, and Better Auth

## Research Areas

### 1. Database: Neon PostgreSQL + SQLModel

**Decision**: Use Neon serverless PostgreSQL with SQLModel ORM

**Rationale**:
- **Neon**: Serverless PostgreSQL with automatic scaling, branching, and generous free tier
- **SQLModel**: Combines SQLAlchemy (proven ORM) with Pydantic (validation), perfect for FastAPI integration
- **Type Safety**: Full type hints throughout database layer (Python 3.13+)
- **Migration**: Alembic integration for schema versioning

**Alternatives Considered**:
- **Raw SQLAlchemy**: More verbose, no automatic Pydantic model generation
- **Tortoise ORM**: Async-first but less mature, smaller community
- **Prisma**: Excellent DX but requires Node.js tooling in Python project

**Best Practices**:
- Use UUIDs for primary keys (better for distributed systems, prevents enumeration)
- Implement `created_at` and `updated_at` timestamps on all models
- Use connection pooling (asyncpg driver recommended)
- Enable cascade deletes for user->tasks relationship
- Use database-level constraints (UNIQUE, NOT NULL, CHECK) not just application-level

**Implementation Notes**:
- Connection string format: `postgresql+asyncpg://user:pass@host/db`
- Async engine required for FastAPI async endpoints
- Use `SQLModel.metadata.create_all()` for development; Alembic for production migrations

---

### 2. Backend: FastAPI Framework

**Decision**: FastAPI with async/await pattern

**Rationale**:
- **Performance**: Async support with uvicorn ASGI server (high concurrency)
- **Type Safety**: Automatic request/response validation via Pydantic
- **Auto Docs**: OpenAPI (Swagger) and ReDoc generated automatically
- **Dependency Injection**: Clean architecture for auth, database sessions
- **Python 3.13+**: Modern syntax (match statements, type hints)

**Alternatives Considered**:
- **Django REST**: More batteries-included but heavier, sync-only by default
- **Flask**: Lightweight but requires more manual setup for validation/docs

**Best Practices**:
- **Project Structure**:
  ```
  backend/
  ├── src/
  │   ├── main.py           # FastAPI app initialization
  │   ├── config.py         # Settings (from .env)
  │   ├── database.py       # Database connection
  │   ├── models/           # SQLModel database models
  │   │   ├── user.py
  │   │   └── task.py
  │   ├── schemas/          # Pydantic request/response schemas
  │   │   ├── auth.py
  │   │   └── task.py
  │   ├── routers/          # API endpoints
  │   │   ├── auth.py
  │   │   └── tasks.py
  │   ├── dependencies/     # Dependency injection
  │   │   └── auth.py       # get_current_user, etc.
  │   └── utils/            # Helpers
  │       ├── security.py   # Password hashing, JWT
  │       └── errors.py     # Custom exceptions
  ├── tests/
  ├── requirements.txt
  └── .env.example
  ```
- Use APIRouter for endpoint organization
- Implement global exception handlers
- Use BackgroundTasks for async operations (email, logging)
- Separate database models (SQLModel) from API schemas (Pydantic)

**Dependencies**:
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
asyncpg==0.29.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

---

### 3. Authentication: Better Auth + JWT

**Decision**: Implement custom JWT authentication (Better Auth is Node.js library, not Python)

**Correction**: Better Auth is a TypeScript/JavaScript library. For Python FastAPI, we'll implement JWT authentication using industry-standard libraries.

**Rationale**:
- **python-jose**: JWT encoding/decoding (JOSE standard)
- **passlib**: Secure password hashing (bcrypt algorithm)
- **FastAPI Security**: OAuth2PasswordBearer for token handling
- **Industry Standard**: RFC 7519 (JWT), RFC 6749 (OAuth2)

**Alternatives Considered**:
- **FastAPI Users**: Full-featured but opinionated, may be overkill
- **Authlib**: More comprehensive but heavier
- **Custom from scratch**: More control but reinvents wheel

**Best Practices**:
- **Password Hashing**: bcrypt with cost factor 12
- **JWT Structure**:
  - Access Token: 15-minute expiration, contains `user_id`, `exp`, `iat`
  - Refresh Token: 7-day expiration, stored in database for revocation
- **Token Storage** (Frontend):
  - **Preferred**: httpOnly cookies (XSS protection)
  - **Fallback**: localStorage with short expiration
- **Secret Management**: Use environment variables, rotate secrets
- **Security Headers**: CORS, CSP, X-Frame-Options

**Implementation Pattern**:
```python
# JWT payload
{
  "sub": "user_id_uuid",
  "exp": 1234567890,  # Unix timestamp
  "iat": 1234567890,
  "type": "access"    # or "refresh"
}
```

**Endpoints**:
- `POST /auth/signup`: Create user, return tokens
- `POST /auth/signin`: Verify credentials, return tokens
- `POST /auth/refresh`: Exchange refresh token for new access token
- `POST /auth/signout`: (Optional) Revoke refresh token

---

### 4. Frontend: Next.js 14+ with TypeScript

**Decision**: Next.js 14 with App Router, TypeScript, and Tailwind CSS

**Rationale**:
- **App Router**: Server components, improved routing, built-in layouts
- **TypeScript**: Type safety for API calls and state management
- **Tailwind CSS**: Utility-first CSS, responsive design, small bundle
- **React 18**: Concurrent features, Suspense, server components
- **Performance**: Automatic code splitting, image optimization, caching

**Alternatives Considered**:
- **Vite + React**: Faster dev server but manual routing, no SSR
- **Pages Router (Next.js 12)**: Older pattern, less performant
- **Remix**: Great DX but smaller ecosystem

**Best Practices**:
- **Project Structure**:
  ```
  frontend/
  ├── src/
  │   ├── app/
  │   │   ├── layout.tsx        # Root layout
  │   │   ├── page.tsx          # Home (redirect to /tasks)
  │   │   ├── signin/
  │   │   │   └── page.tsx
  │   │   ├── signup/
  │   │   │   └── page.tsx
  │   │   └── tasks/
  │   │       ├── page.tsx      # Task list
  │   │       ├── new/
  │   │       │   └── page.tsx  # Add task
  │   │       └── [id]/
  │   │           └── edit/
  │   │               └── page.tsx
  │   ├── components/
  │   │   ├── ui/               # Reusable UI components
  │   │   ├── TaskList.tsx
  │   │   ├── TaskForm.tsx
  │   │   └── AuthForm.tsx
  │   ├── lib/
  │   │   ├── api.ts            # API client (fetch wrapper)
  │   │   ├── auth.ts           # Auth helpers
  │   │   └── types.ts          # TypeScript types
  │   └── middleware.ts         # Protected routes
  ├── public/
  ├── tailwind.config.ts
  ├── next.config.js
  ├── package.json
  └── tsconfig.json
  ```

**Dependencies**:
```json
{
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.3"
  },
  "devDependencies": {
    "tailwindcss": "3.4.1",
    "autoprefixer": "10.4.17",
    "postcss": "8.4.33",
    "@types/react": "18.2.48",
    "@types/node": "20.11.5"
  }
}
```

**Responsive Design** (Tailwind Breakpoints):
- Mobile: 320px+ (default)
- Tablet: `md:` 768px+
- Desktop: `lg:` 1024px+

---

### 5. Frontend Auth Integration

**Decision**: Token-based authentication with middleware protection

**Approach**:
1. **Token Storage**:
   - Use `js-cookie` library for cookie management
   - Store tokens in httpOnly cookies via API Set-Cookie headers
   - Fallback: localStorage with `getItem`/`setItem`

2. **Middleware Pattern**:
```typescript
// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value

  if (!token && request.nextUrl.pathname.startsWith('/tasks')) {
    return NextResponse.redirect(new URL('/signin', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/tasks/:path*']
}
```

3. **API Client Pattern**:
```typescript
// src/lib/api.ts
async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = getCookie('access_token')

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers,
    },
  })

  if (response.status === 401) {
    // Try refresh token
    const refreshed = await refreshAccessToken()
    if (!refreshed) {
      // Redirect to signin
      window.location.href = '/signin'
    }
    // Retry original request
    return apiCall(endpoint, options)
  }

  return response
}
```

**Best Practices**:
- Implement automatic token refresh on 401 responses
- Clear tokens on signout
- Use optimistic UI updates (update UI immediately, rollback on failure)
- Handle loading states with Suspense or local state
- Display user-friendly error messages (toast notifications)

---

### 6. CORS Configuration

**Decision**: Configure CORS in FastAPI for Next.js origin

**Implementation**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production**:
- Replace with actual frontend domain
- Use environment variable: `CORS_ORIGINS=https://app.example.com`

---

### 7. Environment Configuration

**Backend (.env)**:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/db
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 8. Development Workflow

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev  # Runs on port 3000
```

**Database**:
- Create Neon project at https://neon.tech
- Copy connection string to backend/.env
- Run migrations: `alembic upgrade head`

---

### 9. Testing Strategy

**Backend**:
- Use `pytest` with `pytest-asyncio` for async tests
- Use `httpx.AsyncClient` for API endpoint testing
- Use in-memory SQLite for test database
- Test coverage: authentication, CRUD operations, authorization

**Frontend**:
- Use Jest + React Testing Library (optional for Phase 2)
- Manual testing: browser-based testing of all flows
- Focus on user journeys from spec acceptance scenarios

---

### 10. Deployment Considerations (Future)

**Backend Options**:
- Railway.app (easy Python deployment)
- Render.com (free tier available)
- Fly.io (global edge deployment)
- AWS ECS / Google Cloud Run (scalable containers)

**Frontend Options**:
- Vercel (Next.js creators, optimal performance)
- Netlify (good CDN, easy setup)
- Cloudflare Pages (fast edge network)

**Database**:
- Neon (already chosen, serverless PostgreSQL)

---

## Summary of Technical Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Database | Neon PostgreSQL + SQLModel | Serverless, type-safe ORM, Pydantic integration |
| Backend Framework | FastAPI | Async, auto-docs, type safety, modern Python |
| Auth | Custom JWT (python-jose + passlib) | Industry standard, flexible, no external deps |
| Frontend Framework | Next.js 14 (App Router) | SSR, routing, performance, React 18 |
| Styling | Tailwind CSS | Utility-first, responsive, small bundle |
| Language | Python 3.13+ / TypeScript 5.3+ | Modern type systems, excellent tooling |
| Token Storage | httpOnly cookies (fallback: localStorage) | XSS protection, secure defaults |

## Unknowns Resolved

All technical decisions have been researched and documented. No "NEEDS CLARIFICATION" items remain.

**Note**: Better Auth is a TypeScript library and not compatible with Python FastAPI. We'll implement standard JWT authentication using python-jose and passlib instead, which provides the same security features and is the industry-standard approach for FastAPI applications.
