# Tasks: Phase IV - Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-phase4-local-k8s/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested in specification - tasks focus on deployment implementation and validation

**Organization**: Tasks grouped by user story (US1-US4) to enable independent implementation and testing

**Critical Constraint**: Minikube cannot run due to SLAT limitation. Tasks support dual-track approach:
- **Track A**: Docker Compose (immediate deployment)
- **Track B**: Kubernetes with kind/Helm (K8s-ready)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4)
- Exact file paths included in descriptions

## Path Conventions

This is a web application deployment project with:
- **Backend**: `backend/` (existing Phase III code - NO CHANGES)
- **Frontend**: `frontend/` (existing Phase III code - NO CHANGES)
- **Deployment**: `docker/`, `helm/`, `k8s/`, `scripts/`, `docs/deployment/` (NEW)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize deployment infrastructure directories and documentation structure

- [x] T001 Create deployment directory structure: `docker/backend/`, `docker/frontend/`, `helm/backend/`, `helm/frontend/`, `k8s/backend/`, `k8s/frontend/`, `scripts/`, `docs/deployment/`
- [x] T002 [P] Create `.gitignore` entries for secrets: `.env`, `values-local.yaml`, `*-secrets.yaml`, `*.env.local`
- [x] T003 [P] Create `.env.example` template file at repository root with all required environment variables documented
- [x] T004 [P] Create `docs/deployment/prerequisites.md` documenting required tools (Docker Desktop, kubectl, Helm, kind)
- [x] T005 [P] Update main `README.md` with "Deployment" section linking to deployment guides

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Docker infrastructure that MUST be complete before ANY user story deployment

**⚠️ CRITICAL**: No user story deployment can begin until Docker images are buildable

### Backend Docker Infrastructure

- [x] T006 Create `docker/backend/Dockerfile` with multi-stage build (builder + runtime stages)
- [x] T007 [P] Create `docker/backend/.dockerignore` excluding `venv/`, `__pycache__/`, `*.pyc`, `.env`, `tests/`
- [x] T008 [P] Create `docker/backend/docker-entrypoint.sh` for container initialization (uvicorn startup)
- [x] T009 Test backend Docker image build: `docker build -f docker/backend/Dockerfile -t todo-backend:latest ./backend` (Note: Requires Docker Desktop to be running)

### Frontend Docker Infrastructure

- [x] T010 [P] Create `docker/frontend/Dockerfile` with multi-stage build (deps + builder + runtime stages)
- [x] T011 [P] Create `docker/frontend/.dockerignore` excluding `node_modules/`, `.next/`, `*.log`, `.env*`
- [x] T012 [P] Create `docker/frontend/docker-entrypoint.sh` for container initialization (Next.js server startup)
- [x] T013 [P] Test frontend Docker image build: `docker build -f docker/frontend/Dockerfile -t todo-frontend:latest ./frontend` (Note: Requires Docker Desktop to be running)

### Docker Compose (Track A Foundation)

- [x] T014 Create `docker-compose.yml` defining `backend` and `frontend` services with networks, health checks, and depends_on
- [x] T015 Create `docker-compose.override.yml` for local development overrides (optional hot-reload mounts)

**Checkpoint**: Foundation ready - Dockerfiles built successfully, both images created

---

## Phase 3: User Story 1 - Deploy Backend to Local Kubernetes (Priority: P0) 🎯 MVP

**Goal**: Deploy existing FastAPI backend in containerized environment with secrets management

**Independent Test**: Access backend health endpoint and verify API responds correctly

**Dual-Track Approach**:
- Track A: Deploy backend via Docker Compose
- Track B: Deploy backend via Helm chart

### Track A: Backend Docker Compose Deployment

- [x] T016 [US1] Verify `.env` file created from `.env.example` with actual secrets (OPENAI_API_KEY, DATABASE_URL, SECRET_KEY) - .env.example template verified; user must create .env with real secrets
- [x] T017 [US1] Start backend service: `docker-compose up backend -d` - Container started successfully
- [x] T018 [US1] Verify backend container running: `docker-compose ps` shows backend as "Up (healthy)"
- [x] T019 [US1] Test backend health endpoint: `curl http://localhost:8000/health` returns `{"status":"healthy","environment":"development"}`
- [x] T020 [US1] Test backend API docs accessible: `curl http://localhost:8000/docs` returns HTTP 200
- [x] T021 [US1] Verify backend logs show successful startup: Uvicorn running on http://0.0.0.0:8000

### Track B: Backend Helm Chart Creation

- [x] T022 [P] [US1] Initialize backend Helm chart: `helm create helm/backend` (generates chart skeleton) - Created manually with custom structure
- [x] T023 [P] [US1] Create `helm/backend/Chart.yaml` with name: todo-backend, version: 1.0.0, description
- [x] T024 [P] [US1] Create `helm/backend/values.yaml` based on `contracts/backend-values.schema.yaml`
- [x] T025 [P] [US1] Create `helm/backend/templates/deployment.yaml` for backend Deployment with health probes
- [x] T026 [P] [US1] Create `helm/backend/templates/service.yaml` for backend Service (ClusterIP type, port 8000)
- [x] T027 [P] [US1] Create `helm/backend/templates/secrets.yaml` templating secrets from values (stringData format)
- [x] T028 [P] [US1] Create `helm/backend/templates/configmap.yaml` for non-sensitive config (CORS_ORIGINS, ENVIRONMENT)
- [x] T029 [P] [US1] Create `helm/backend/templates/_helpers.tpl` with name, labels, and selector helpers
- [x] T030 [P] [US1] Create `helm/backend/templates/NOTES.txt` with post-install instructions for accessing backend
- [x] T031 [US1] Create `helm/backend/.helmignore` to exclude unnecessary files from chart package

### Track B: Backend Kubernetes Deployment (kind)

- [x] T032 [US1] Document kind cluster creation in `docs/deployment/kubernetes.md`: `kind create cluster --name todo-local`
- [x] T033 [US1] Load backend image into kind: `kind load docker-image todo-backend:latest --name todo-local` - Image loaded successfully
- [x] T034 [US1] Create `helm/backend/values-local.yaml` with actual secrets (gitignored, based on schema)
- [x] T035 [US1] Install backend Helm chart: `helm install todo-backend ./helm/backend -f helm/backend/values-local.yaml` - Deployed revision 1
- [x] T036 [US1] Verify backend deployment: `kubectl get deployments` shows todo-backend with 1/1 ready
- [x] T037 [US1] Verify backend pods running: `kubectl get pods -l app=todo-backend` shows Running status
- [x] T038 [US1] Verify backend service created: `kubectl get svc todo-backend` shows ClusterIP service on 8000/TCP
- [x] T039 [US1] Port-forward backend service: `kubectl port-forward svc/todo-backend 8000:8000` - health returns {"status":"healthy"}
- [x] T040 [US1] Verify secrets not exposed: `kubectl describe pod` shows secretRef/configMapRef but not values

**Checkpoint US1**: Backend deployed via both Docker Compose (Track A) and kind/Helm (Track B), health checks passing

---

## Phase 4: User Story 2 - Deploy Frontend to Local Kubernetes (Priority: P0)

**Goal**: Deploy Next.js frontend with backend connectivity

**Independent Test**: Access frontend URL and verify web interface loads (may show errors if backend unavailable)

**Dual-Track Approach**:
- Track A: Deploy frontend via Docker Compose
- Track B: Deploy frontend via Helm chart

### Track A: Frontend Docker Compose Deployment

- [x] T041 [US2] Update `docker-compose.yml` frontend service to set `NEXT_PUBLIC_API_URL=http://backend:8000` - Already set to http://localhost:8000 (correct for browser access)
- [x] T042 [US2] Start frontend service: `docker-compose up frontend -d` - Container started after backend healthy
- [x] T043 [US2] Verify frontend container running: `docker-compose ps` shows frontend as "Up (healthy)"
- [x] T044 [US2] Test frontend accessible: `curl http://localhost:3000` returns HTTP 200
- [x] T045 [US2] Verify frontend logs show successful startup: Next.js 16.1.1 Ready in 316ms
- [x] T046 [US2] Test full stack: Both services running healthy, frontend at http://localhost:3000, backend at http://localhost:8000

### Track B: Frontend Helm Chart Creation

- [x] T047 [P] [US2] Initialize frontend Helm chart: `helm create helm/frontend` - Created manually with custom structure
- [x] T048 [P] [US2] Create `helm/frontend/Chart.yaml` with name: todo-frontend, version: 1.0.0, description
- [x] T049 [P] [US2] Create `helm/frontend/values.yaml` based on `contracts/frontend-values.schema.yaml`
- [x] T050 [P] [US2] Create `helm/frontend/templates/deployment.yaml` for frontend Deployment with health probes
- [x] T051 [P] [US2] Create `helm/frontend/templates/service.yaml` for frontend Service (NodePort type: 30080)
- [x] T052 [P] [US2] Create `helm/frontend/templates/configmap.yaml` for NEXT_PUBLIC_API_URL config
- [x] T053 [P] [US2] Create `helm/frontend/templates/_helpers.tpl` with name, labels, and selector helpers
- [x] T054 [P] [US2] Create `helm/frontend/templates/NOTES.txt` with post-install access instructions
- [x] T055 [US2] Create `helm/frontend/.helmignore` to exclude unnecessary files

### Track B: Frontend Kubernetes Deployment (kind)

- [x] T056 [US2] Load frontend image into kind: `kind load docker-image todo-frontend:latest --name todo-local` - Image loaded successfully
- [x] T057 [US2] Create `helm/frontend/values-local.yaml` with config overrides (apiUrl: http://todo-backend:8000)
- [x] T058 [US2] Install frontend Helm chart: `helm install todo-frontend ./helm/frontend -f helm/frontend/values-local.yaml` - Deployed revision 1
- [x] T059 [US2] Verify frontend deployment: `kubectl get deployments` shows todo-frontend with 1/1 ready
- [x] T060 [US2] Verify frontend pods running: `kubectl get pods -l app=todo-frontend` shows Running status
- [x] T061 [US2] Verify frontend service created: `kubectl get svc todo-frontend` shows NodePort 3000:30080/TCP
- [x] T062 [US2] Configure kind port mapping in `kind-config.yaml` for NodePort 30080, recreate cluster if needed
- [x] T063 [US2] Test frontend accessible: http://localhost:30080 returns HTTP 200
- [x] T064 [US2] Test frontend-backend connectivity: Frontend pod can wget http://todo-backend:8000/health successfully

**Checkpoint US2**: Frontend deployed via both tracks, full stack functional end-to-end

---

## Phase 5: User Story 4 - Manage Helm Charts for Application Lifecycle (Priority: P0)

**Goal**: Validate Helm lifecycle operations (install, upgrade, uninstall)

**Independent Test**: Execute Helm upgrade and uninstall operations, verify state changes

**Note**: This story validates the Helm charts created in US1 and US2

### Helm Chart Lifecycle Testing

- [x] T065 [US4] Test backend Helm upgrade: `--set replicaCount=2` upgraded to revision 2 with 2 pods Running
- [x] T066 [US4] Verify backend scaled: `kubectl get pods -l app=todo-backend` showed 2 pods Running
- [x] T067 [US4] Test backend rollback: `helm rollback todo-backend 1` reverted to 1 replica successfully
- [x] T068 [US4] Test frontend Helm upgrade: Upgraded to revision 2 with `--set replicaCount=2`, then back to 1
- [x] T069 [US4] Test Helm chart values override: `--set replicaCount=1` override applied successfully
- [x] T070 [US4] Verify Helm releases: `helm list` shows both as "deployed" with correct chart versions
- [x] T071 [US4] Test Helm uninstall: `helm uninstall todo-backend todo-frontend` - both released
- [x] T072 [US4] Verify clean removal: `kubectl get all` showed only kubernetes service remaining
- [x] T073 [US4] Document Helm best practices in `docs/deployment/kubernetes.md` (upgrade, rollback, values override)

### Kubernetes Manifests (Alternative to Helm)

- [x] T074 [P] [US4] Create `k8s/backend/deployment.yaml` with hardcoded backend Deployment manifest
- [x] T075 [P] [US4] Create `k8s/backend/service.yaml` with backend Service manifest
- [x] T076 [P] [US4] Create `k8s/backend/secrets.yaml.example` as template (user fills base64 values)
- [x] T077 [P] [US4] Create `k8s/frontend/deployment.yaml` with frontend Deployment manifest
- [x] T078 [P] [US4] Create `k8s/frontend/service.yaml` with frontend Service manifest (NodePort)
- [x] T079 [P] [US4] Create `k8s/frontend/configmap.yaml` with frontend ConfigMap
- [x] T080 [US4] Document kubectl apply workflow in `docs/deployment/kubernetes.md` as Helm alternative

**Checkpoint US4**: Helm lifecycle validated, alternative kubectl manifests created

---

## Phase 6: User Story 3 - Use AI-Assisted DevOps Tools (Priority: P1)

**Goal**: Document AI tools for enhanced K8s operations (optional learning enhancement)

**Independent Test**: Run example kubectl-ai and kagent commands, verify they generate correct operations

**Note**: This is an optional enhancement - tools may not be installed

### AI Tools Documentation

- [x] T081 [P] [US3] Document kubectl-ai installation in `docs/deployment/ai-tools.md`: `pip install kubectl-ai`
- [x] T082 [P] [US3] Document kubectl-ai example: "deploy the todo frontend with 2 replicas" → expected kubectl command
- [x] T083 [P] [US3] Document kubectl-ai example: "scale the backend to handle more load" → expected scaling command
- [x] T084 [P] [US3] Document kubectl-ai example: "check why the pods are failing" → expected diagnostic steps
- [x] T085 [P] [US3] Document kagent installation and usage in `docs/deployment/ai-tools.md`
- [x] T086 [P] [US3] Document kagent example: "analyze the cluster health" → expected health report format
- [x] T087 [P] [US3] Document kagent example: "optimize resource allocation" → expected recommendations
- [x] T088 [US3] Add AI tools section to `docs/deployment/kubernetes.md` with fallback to manual commands

**Checkpoint US3**: AI tools documented with examples (implementation optional)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Automation, documentation, and deployment quality improvements

### Deployment Automation Scripts

- [x] T089 [P] Create `scripts/build-images.sh` to build both backend and frontend images with error handling
- [x] T090 [P] Create `scripts/build-images.ps1` (PowerShell version for Windows)
- [x] T091 [P] Create `scripts/deploy-compose.sh` to start Docker Compose with validation checks
- [x] T092 [P] Create `scripts/deploy-compose.ps1` (PowerShell version)
- [x] T093 [P] Create `scripts/deploy-k8s.sh` to deploy both Helm charts with kind cluster creation
- [x] T094 [P] Create `scripts/deploy-k8s.ps1` (PowerShell version)
- [x] T095 [P] Create `scripts/validate-env.sh` to check prerequisites (Docker, kubectl, Helm, kind) and secrets
- [x] T096 [P] Make all shell scripts executable: `chmod +x scripts/*.sh`

### Comprehensive Documentation

- [x] T097 [P] Create `docs/deployment/docker-compose.md` with complete Docker Compose guide (Track A)
- [x] T098 [P] Expand `docs/deployment/kubernetes.md` with complete kind/Helm guide (Track B)
- [x] T099 [P] Create `docs/deployment/troubleshooting.md` with common issues and solutions for both tracks
- [x] T100 [P] Create `docs/architecture/containerization.md` documenting deployment architecture decisions
- [x] T101 Update `README.md` "Deployment" section with quick links to both deployment tracks

### Security & Best Practices

- [x] T102 [P] Verify `.gitignore` covers all secret files: `.env`, `values-local.yaml`, `*-secrets.yaml`
- [x] T103 [P] Add security scanning to Dockerfiles: Include `HEALTHCHECK` and run as non-root user where possible
- [x] T104 [P] Document secrets rotation procedure in `docs/deployment/secrets-management.md`
- [x] T105 Validate that Phase III code is unchanged: `git status backend/ frontend/` shows no modifications

### End-to-End Validation

- [x] T106 Full Track A validation: `docker-compose down -v && docker-compose up -d` - both services healthy
- [x] T107 Full Track B validation: Fresh kind cluster created, both Helm charts deployed, all pods Running 1/1
- [x] T108 Verify Phase III functionality unchanged: Health endpoint, frontend UI, API docs all respond correctly
- [x] T109 Performance validation: Backend 6ms, Frontend 10ms response times; startup under 60s
- [x] T110 Document validation checklist in `docs/deployment/validation.md` for future deployments

**Final Checkpoint**: All user stories complete, both deployment tracks validated, documentation comprehensive

---

## Dependencies & Execution Order

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1 Backend) → Phase 4 (US2 Frontend) → Phase 5 (US4 Helm Lifecycle)
                                                                                           → Phase 6 (US3 AI Tools - Independent)
                                          → Phase 7 (Polish)
```

**Dependency Rules**:
- **US1** (Backend): Must complete before US2 (frontend needs backend API)
- **US2** (Frontend): Depends on US1 backend being deployed
- **US4** (Helm Lifecycle): Validates charts from US1 and US2
- **US3** (AI Tools): Independent, can be done anytime after Phase 2
- **Polish**: Can proceed once core user stories (US1, US2) are complete

### Parallel Execution Opportunities

**Phase 2 (Foundational)**: Tasks T007-T013 can run in parallel (different services)
**Phase 3 (US1 Backend Track B)**: Tasks T022-T031 can run in parallel (different Helm templates)
**Phase 4 (US2 Frontend Track B)**: Tasks T047-T055 can run in parallel (different Helm templates)
**Phase 5 (US4 K8s Manifests)**: Tasks T074-T079 can run in parallel (different manifest files)
**Phase 6 (US3 AI Tools)**: Tasks T081-T087 can run in parallel (different documentation files)
**Phase 7 (Polish)**: Tasks T089-T104 can run in parallel (independent scripts and docs)

### MVP Scope (Minimum Viable Product)

**MVP = Phase 1 + Phase 2 + Phase 3 (US1)**

Delivers: Backend containerized and deployable via Docker Compose, immediately usable for API testing.

**Next Increment**: Add Phase 4 (US2) for full-stack deployment.

---

## Implementation Strategy

### Recommended Approach

1. **Start with MVP**: Complete Phases 1-3 (Setup → Foundational → US1 Backend)
   - Validates Docker infrastructure works
   - Delivers working backend API immediately via Docker Compose

2. **Add Frontend**: Complete Phase 4 (US2 Frontend)
   - Full application now deployable via Docker Compose (Track A complete)

3. **Kubernetes Readiness**: Validate Track B tasks in US1 and US2
   - Helm charts ready for future kind/Minikube deployment

4. **Polish**: Complete Phases 5-7 (Helm lifecycle, AI tools, automation)
   - Production-ready deployment with comprehensive documentation

### Track-Specific Execution

**Track A Only** (Docker Compose - Immediate):
- Execute: T001-T021, T041-T046
- Result: Full application running via `docker-compose up`
- Time: ~2-3 hours

**Track B Only** (Kubernetes - Learning):
- Execute: T001-T015 (foundation), then T022-T040 (backend K8s), T047-T064 (frontend K8s)
- Result: Full application in kind cluster via Helm
- Time: ~4-6 hours (includes kind setup)

**Both Tracks** (Complete):
- Execute all tasks T001-T110
- Result: Dual-track deployment, full documentation, automation scripts
- Time: ~8-10 hours

---

## Task Summary

**Total Tasks**: 110
**Breakdown by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 10 tasks
- Phase 3 (US1 Backend): 25 tasks
- Phase 4 (US2 Frontend): 24 tasks
- Phase 5 (US4 Helm Lifecycle): 16 tasks
- Phase 6 (US3 AI Tools): 8 tasks
- Phase 7 (Polish): 22 tasks

**Parallelizable Tasks**: 62 tasks marked with [P] (56% can run in parallel)

**MVP Scope**: 40 tasks (Phases 1-3)
**Track A Completion**: 26 tasks (Docker Compose deployment)
**Track B Completion**: 84 tasks (Full Kubernetes with Helm)

---

**Next Step**: Begin with Phase 1 (Setup) to create deployment directory structure and foundational configurations.
