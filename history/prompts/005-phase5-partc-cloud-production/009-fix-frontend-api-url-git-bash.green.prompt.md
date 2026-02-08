---
id: 009
title: Fix Frontend API URL Git Bash Path Corruption
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-5
feature: 005-phase5-partc-cloud-production
branch: 001-phase2-full-stack-web
user: Muhammad-Talha33
command: /sp.implement
labels: ["deployment", "docker", "frontend", "debugging", "git-bash"]
links:
  spec: specs/005-phase5-partc-cloud-production/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - docker/frontend/Dockerfile (rebuild with PowerShell)
tests:
  - curl http://139.59.194.7/api/health - PASS
  - curl http://139.59.194.7/api/auth/signin - PASS (returns Invalid credentials)
  - kubectl get pods -n todo-staging - frontend Running
  - User login test - PASS
---

## Prompt

User reported error when trying to login from frontend: "Not allowed to load local resource: file:///C:/Program%20Files/Git/api/auth/signin". This indicated the frontend was trying to use a corrupted file:// URL instead of an HTTP API call.

## Response snapshot

Diagnosed the root cause: When the Docker image was built using Git Bash on Windows, the `--build-arg NEXT_PUBLIC_API_URL=/api` path was auto-converted by Git Bash to a Windows path (`C:/Program Files/Git/api`). This corrupted path was baked into the Next.js frontend at build time.

**Fix applied:**
1. Rebuilt frontend Docker image using **PowerShell** instead of Git Bash to avoid path conversion
2. Passed correct `--build-arg NEXT_PUBLIC_API_URL=/api`
3. Pushed new image to ghcr.io/muhammad-talha33/todo-frontend:staging
4. Restarted frontend deployment with `kubectl rollout restart`

**Verification:**
- API health endpoint: `{"status":"healthy","environment":"production"}`
- Signin endpoint returns proper JSON response
- User confirmed: "its working"

## Outcome

- ✅ Impact: Frontend now correctly calls /api/* endpoints through ingress routing to backend
- 🧪 Tests: All API endpoints responding correctly, user login functional
- 📁 Files: Frontend Docker image rebuilt (no source code changes needed)
- 🔁 Next prompts: Consider adding TLS/SSL, configure production domain, add Confluent Cloud Kafka credentials
- 🧠 Reflection: Git Bash on Windows auto-converts paths starting with / to Windows paths. Always use PowerShell or CMD for Docker builds with path arguments on Windows.

## Evaluation notes (flywheel)

- Failure modes observed: Git Bash MSYS path conversion corrupted NEXT_PUBLIC_API_URL build arg
- Graders run and results (PASS/FAIL): Manual verification PASS - user confirmed login working
- Prompt variant (if applicable): N/A
- Next experiment: Document Windows build requirements - use PowerShell/CMD, not Git Bash for Docker builds with path arguments
