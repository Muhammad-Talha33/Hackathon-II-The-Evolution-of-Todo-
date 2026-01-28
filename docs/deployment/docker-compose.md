# Docker Compose Deployment Guide (Track A)

## Phase IV - Local Container Deployment

**Last Updated**: 2026-01-18

This guide covers deploying the Todo AI Chatbot using Docker Compose for immediate local development and testing.

---

## Overview

Docker Compose provides a simple, immediate deployment path that works without Kubernetes. This is the recommended approach for:

- Local development and testing
- Quick demonstrations
- Environments without Kubernetes support
- Systems with SLAT limitations (cannot run Minikube)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                    (todo-network)                        │
│                                                         │
│  ┌─────────────────┐       ┌─────────────────┐         │
│  │                 │       │                 │         │
│  │    Backend      │◄──────│    Frontend     │         │
│  │   (FastAPI)     │       │   (Next.js)     │         │
│  │   Port: 8000    │       │   Port: 3000    │         │
│  │                 │       │                 │         │
│  └────────┬────────┘       └────────┬────────┘         │
│           │                         │                   │
└───────────┼─────────────────────────┼───────────────────┘
            │                         │
    localhost:8000            localhost:3000
            │                         │
            ▼                         ▼
    ┌───────────────┐        ┌───────────────┐
    │  API Docs     │        │  Web Browser  │
    │  /docs        │        │  Chatbot UI   │
    └───────────────┘        └───────────────┘
```

---

## Prerequisites

### Required

- ✅ Docker Desktop installed and running
- ✅ Docker Compose v2.x (included with Docker Desktop)
- ✅ `.env` file with valid secrets

### Check Prerequisites

```bash
# Windows PowerShell
.\scripts\validate-env.ps1

# Linux/macOS
./scripts/validate-env.sh
```

---

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project
cd path/to/todo-chatbot

# Copy environment template
cp .env.example .env

# Edit .env with your secrets
# Required: DATABASE_URL, SECRET_KEY, OPENAI_API_KEY
```

### 2. Build Images

```bash
# Windows PowerShell
.\scripts\build-images.ps1

# Linux/macOS
./scripts/build-images.sh

# Or manually
docker-compose build
```

### 3. Start Services

```bash
# Windows PowerShell
.\scripts\deploy-compose.ps1 Up

# Linux/macOS
./scripts/deploy-compose.sh up

# Or manually
docker-compose up -d
```

### 4. Verify Deployment

```bash
# Check service status
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# View logs
docker-compose logs -f
```

### 5. Access Application

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Web UI (Chatbot) |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |

---

## Configuration

### Environment Variables

Create `.env` file in the project root:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require

# Security
SECRET_KEY=your-jwt-secret-key

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (Docker Compose)
CORS_ORIGINS=http://localhost:3000,http://frontend:3000

# Environment
ENVIRONMENT=development

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker Compose Override

For local development with hot-reload, use `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  backend:
    volumes:
      - ./backend/src:/app/src:ro
    environment:
      - ENVIRONMENT=development

  frontend:
    volumes:
      - ./frontend/app:/app/app:ro
      - ./frontend/components:/app/components:ro
    environment:
      - NODE_ENV=development
```

---

## Commands Reference

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend
docker-compose up -d frontend

# Start with rebuild
docker-compose up -d --build
```

### Stop Services

```bash
# Stop all services (keep volumes)
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last N lines
docker-compose logs --tail=100 backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Shell Access

```bash
# Backend container
docker-compose exec backend sh

# Frontend container
docker-compose exec frontend sh
```

### Rebuild Images

```bash
# Rebuild all
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Rebuild specific service
docker-compose build backend
```

---

## Health Checks

### Backend Health

```bash
# Health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy","environment":"development"}

# API docs
curl -I http://localhost:8000/docs
# Expected: HTTP/1.1 200 OK
```

### Frontend Health

```bash
# Main page
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK
```

### Docker Health Status

```bash
# View container health
docker-compose ps

# Detailed health info
docker inspect --format='{{json .State.Health}}' todo-backend
docker inspect --format='{{json .State.Health}}' todo-frontend
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Common issues:
# - Missing .env file
# - Invalid environment variables
# - Port already in use
```

### Port Already in Use

```bash
# Find process using port
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Linux/macOS
lsof -i :8000
lsof -i :3000

# Kill process or change ports in docker-compose.yml
```

### Build Failures

```bash
# Clean Docker cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -f docker/backend/Dockerfile ./backend --progress=plain
```

### Database Connection Issues

```bash
# Verify DATABASE_URL in .env
# Check Neon dashboard for connection limits
# Ensure SSL mode is correct (ssl=require for Neon)
```

### Frontend Can't Connect to Backend

```bash
# Verify NEXT_PUBLIC_API_URL is set correctly
# Should be http://localhost:8000 for browser access
# Check CORS_ORIGINS includes frontend URL
```

---

## Resource Management

### View Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Cleanup

```bash
# Remove stopped containers
docker-compose down

# Remove unused images
docker image prune

# Full cleanup (WARNING: removes all unused data)
docker system prune -a
```

---

## Development Workflow

### Making Code Changes

1. **Backend Changes**: Restart backend container
   ```bash
   docker-compose restart backend
   ```

2. **Frontend Changes**: With volume mounts, changes are reflected automatically (hot-reload)

3. **Dependency Changes**: Rebuild images
   ```bash
   docker-compose build backend  # for Python deps
   docker-compose build frontend  # for Node deps
   ```

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test
```

---

## Next Steps

- **Kubernetes Deployment**: See [kubernetes.md](./kubernetes.md) for K8s/Helm deployment
- **Troubleshooting**: See [troubleshooting.md](./troubleshooting.md) for common issues
- **Prerequisites**: See [prerequisites.md](./prerequisites.md) for tool installation

---

**Questions?** Check [troubleshooting.md](./troubleshooting.md) or open an issue.
