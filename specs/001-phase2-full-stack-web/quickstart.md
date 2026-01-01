# Quickstart Guide: Phase 2 Full Stack Web Application

**Date**: 2025-12-29
**Feature**: 001-phase2-full-stack-web
**Estimated Setup Time**: 30-45 minutes

## Prerequisites

Before starting, ensure you have:

- **Python 3.13+** installed (`python --version`)
- **Node.js 18+** installed (`node --version`)
- **npm** or **yarn** package manager
- **Git** for version control
- **Code editor** (VS Code, PyCharm, etc.)
- **Neon account** (free tier): https://neon.tech

## Project Overview

This guide will help you set up:
1. **Backend**: FastAPI REST API (Python) at `http://localhost:8000`
2. **Frontend**: Next.js web application (TypeScript) at `http://localhost:3000`
3. **Database**: PostgreSQL via Neon (cloud-hosted)

**Important**: This setup creates NEW directories (`backend/`, `frontend/`). The existing Phase 1 code in `src/` remains untouched.

---

## Step 1: Database Setup (Neon PostgreSQL)

### 1.1 Create Neon Project

1. Go to https://neon.tech and sign up (free tier)
2. Create new project:
   - **Project name**: `phase2-todo-app`
   - **Region**: Choose closest to you
   - **PostgreSQL version**: 15 or higher
3. Copy the connection string (looks like):
   ```
   postgresql://user:pass@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### 1.2 Modify Connection String for SQLModel

Change the protocol from `postgresql://` to `postgresql+asyncpg://`:

```
postgresql+asyncpg://user:pass@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

Save this for later (you'll add it to `.env` file).

---

## Step 2: Backend Setup (FastAPI)

### 2.1 Create Backend Directory Structure

```bash
# From project root
mkdir -p backend/src/models backend/src/schemas backend/src/routers backend/src/dependencies backend/src/utils backend/tests
cd backend
```

### 2.2 Create Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 2.3 Create requirements.txt

Create `backend/requirements.txt`:

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
asyncpg==0.29.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
alembic==1.13.1
```

### 2.4 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.5 Create Environment File

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Security
SECRET_KEY=your-super-secret-key-min-32-characters-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Important**: Replace `DATABASE_URL` with your actual Neon connection string from Step 1.2.

**Generate SECRET_KEY** (Python):
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.6 Create Initial Files

This is just to verify setup works. Detailed implementation will be in tasks.md.

**backend/src/main.py** (minimal FastAPI app):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Phase 2 Todo API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Phase 2 Todo API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
```

### 2.7 Run Backend Server

```bash
# Make sure you're in backend/ directory with venv activated
uvicorn src.main:app --reload --port 8000
```

Visit http://localhost:8000 - you should see:
```json
{"message": "Phase 2 Todo API is running"}
```

Visit http://localhost:8000/docs - you should see Swagger UI (auto-generated API docs).

**Press Ctrl+C to stop the server** (we'll run it again later).

---

## Step 3: Frontend Setup (Next.js)

### 3.1 Create Next.js Application

```bash
# From project root (NOT inside backend/)
cd ..  # If you're still in backend/

npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

When prompted:
- ✅ TypeScript: **Yes**
- ✅ ESLint: **Yes**
- ✅ Tailwind CSS: **Yes**
- ✅ App Router: **Yes**
- ❌ `src/` directory: **No**
- ✅ Import alias: **Yes** (@/*)

### 3.2 Navigate to Frontend

```bash
cd frontend
```

### 3.3 Create Environment File

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3.4 Install Additional Dependencies

```bash
npm install js-cookie
npm install --save-dev @types/js-cookie
```

### 3.5 Verify Next.js Setup

```bash
npm run dev
```

Visit http://localhost:3000 - you should see Next.js default page.

**Press Ctrl+C to stop the server**.

---

## Step 4: Test Integration

### 4.1 Start Backend (Terminal 1)

```bash
# From project root
cd backend
venv\Scripts\activate  # Windows
# OR: source venv/bin/activate  # macOS/Linux

uvicorn src.main:app --reload --port 8000
```

Leave this running.

### 4.2 Start Frontend (Terminal 2)

```bash
# From project root (new terminal)
cd frontend
npm run dev
```

Leave this running.

### 4.3 Test CORS Integration

Open browser console (F12) on http://localhost:3000 and run:

```javascript
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
```

You should see: `{status: "healthy"}` with no CORS errors.

---

## Step 5: Verify Phase 1 Still Works

**Important**: Verify Phase 1 console app is NOT affected by Phase 2 setup.

### 5.1 Run Phase 1 Console App

```bash
# From project root (new terminal or stop frontend temporarily)
python src/main.py
```

You should see the Phase 1 menu:
```
=== Todo Application ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete
6. Exit

Enter your choice:
```

Test a few operations to confirm it works.

**This confirms Phase 1 and Phase 2 are completely separate.**

---

## Step 6: Project Structure Verification

After setup, your project should look like this:

```
project-root/
├── backend/
│   ├── src/
│   │   ├── main.py              ✅ Created
│   │   ├── models/              ✅ Created (empty for now)
│   │   ├── schemas/             ✅ Created (empty for now)
│   │   ├── routers/             ✅ Created (empty for now)
│   │   ├── dependencies/        ✅ Created (empty for now)
│   │   └── utils/               ✅ Created (empty for now)
│   ├── tests/                   ✅ Created (empty for now)
│   ├── venv/                    ✅ Python virtual environment
│   ├── requirements.txt         ✅ Created
│   └── .env                     ✅ Created (NOT committed to git)
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           ✅ Next.js default
│   │   ├── page.tsx             ✅ Next.js default
│   │   └── globals.css          ✅ Tailwind CSS
│   ├── public/                  ✅ Static assets
│   ├── node_modules/            ✅ NPM packages
│   ├── package.json             ✅ Created
│   ├── next.config.js           ✅ Created
│   ├── tailwind.config.ts       ✅ Created
│   ├── tsconfig.json            ✅ TypeScript config
│   └── .env.local               ✅ Created (NOT committed to git)
├── src/                         ✅ Phase 1 (UNTOUCHED)
│   ├── main.py
│   ├── skills/
│   └── models/
├── specs/
│   └── 001-phase2-full-stack-web/
│       ├── spec.md              ✅ Feature specification
│       ├── plan.md              ✅ Implementation plan
│       ├── research.md          ✅ Technical research
│       ├── data-model.md        ✅ Database models
│       ├── quickstart.md        ✅ This file
│       └── contracts/
│           └── api-spec.yaml    ✅ OpenAPI specification
└── .gitignore                   ⚠️ Update (see below)
```

---

## Step 7: Update .gitignore

Add these entries to `.gitignore` (create if doesn't exist):

```gitignore
# Python
backend/venv/
backend/.env
backend/__pycache__/
backend/**/__pycache__/
backend/*.pyc
backend/.pytest_cache/

# Node.js
frontend/node_modules/
frontend/.next/
frontend/.env.local
frontend/out/

# IDE
.vscode/
.idea/
*.swp
*.swo
```

---

## Step 8: Next Steps

Setup complete! You now have:
- ✅ Backend skeleton running at http://localhost:8000
- ✅ Frontend skeleton running at http://localhost:3000
- ✅ Database connection to Neon PostgreSQL
- ✅ CORS configured between frontend and backend
- ✅ Phase 1 console app still functional

### What's Next?

1. **Run `/sp.tasks`** to generate `tasks.md` with step-by-step implementation tasks
2. **Implement database models** (User, Task) in `backend/src/models/`
3. **Implement authentication** (signup, signin, JWT) in `backend/src/routers/auth.py`
4. **Implement task CRUD** endpoints in `backend/src/routers/tasks.py`
5. **Build frontend pages** (signin, signup, task list, add/edit tasks)
6. **Connect frontend to backend** with API client
7. **Test end-to-end flows**

---

## Common Issues & Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (macOS/Linux)

**Issue**: `sqlalchemy.exc.OperationalError: connection failed`
**Solution**: Check `DATABASE_URL` in `backend/.env` is correct and Neon database is active

**Issue**: Port 8000 already in use
**Solution**: Use different port: `uvicorn src.main:app --reload --port 8001`

### Frontend Issues

**Issue**: `Error: listen EADDRINUSE: address already in use :::3000`
**Solution**: Stop other Next.js instances or use: `npm run dev -- -p 3001`

**Issue**: CORS errors in browser console
**Solution**: Verify backend CORS middleware allows `http://localhost:3000`

### Database Issues

**Issue**: `asyncpg.exceptions.InvalidPasswordError`
**Solution**: Verify Neon connection string credentials are correct

**Issue**: Connection string starts with `postgresql://` instead of `postgresql+asyncpg://`
**Solution**: Update `.env` to use `postgresql+asyncpg://` protocol

---

## Development Workflow

### Daily Development

```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate  # or source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Git, testing, etc.
```

### Testing API Endpoints

- **Swagger UI**: http://localhost:8000/docs (interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (API documentation)
- **Postman/curl**: Import `specs/001-phase2-full-stack-web/contracts/api-spec.yaml`

### Verifying Phase 1

```bash
python src/main.py
```

Should launch Phase 1 console app with no errors.

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Neon Docs**: https://neon.tech/docs

---

## Success Criteria

✅ Backend runs without errors at http://localhost:8000
✅ Frontend runs without errors at http://localhost:3000
✅ Swagger UI loads at http://localhost:8000/docs
✅ CORS requests from frontend to backend succeed
✅ Phase 1 console app (`python src/main.py`) still works
✅ `.gitignore` prevents committing `.env` and `venv/`

**You're now ready to implement the full feature!** Run `/sp.tasks` to generate detailed implementation tasks.
