# Implementation Plan: Phase IV - Local Kubernetes Deployment

**Branch**: `004-phase4-local-k8s` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-phase4-local-k8s/spec.md`

## Summary

Deploy the existing Phase III Todo AI Chatbot (FastAPI backend + Next.js frontend) using Docker containerization and Kubernetes orchestration. **Critical Constraint**: Minikube cannot run on current hardware due to SLAT (Second Level Address Translation) limitation in CPU virtualization.

**Primary Strategy**: Implement dual-track approach:
1. **Track A (Immediate)**: Docker Compose for local container orchestration and testing
2. **Track B (K8s-Ready)**: Create production-grade Helm charts and Kubernetes manifests for future deployment when proper K8s cluster is available (Minikube on different hardware, kind, or cloud)

This approach delivers containerization benefits immediately while ensuring Kubernetes readiness for when the platform constraint is resolved.

## Technical Context

**Backend**:
- Language/Version: Python 3.11+
- Framework: FastAPI
- Dependencies: OpenAI Agents SDK, SQLModel, Neon PostgreSQL driver
- Runtime: Uvicorn ASGI server

**Frontend**:
- Language/Version: TypeScript/Node.js 18+
- Framework: Next.js 14
- Build: Production static export or SSR

**Container Platform**:
- **Immediate**: Docker Desktop + Docker Compose (SLAT limitation workaround)
- **Future K8s**: Minikube (requires SLAT-capable CPU) OR kind (Kubernetes in Docker - alternative)
- Image Registry: Local Docker registry or DockerHub

**Orchestration Stack**:
- Package Manager: Helm 3.x
- CLI: kubectl
- Secrets Management: Kubernetes Secrets (encoded in Helm charts) + Docker Compose environment files

**External Dependencies**:
- Storage: Neon PostgreSQL (cloud-hosted, Phase III existing)
- AI Service: OpenAI API (requires OPENAI_API_KEY)

**Project Type**: Web application (frontend + backend microservices)

**Performance Goals**:
- Image build time: <5 minutes per service
- Container startup: <60 seconds
- Application response: Match Phase III local dev performance

**Constraints**:
- **CRITICAL**: No Minikube support due to SLAT CPU limitation
- No changes to Phase III application code (UI, business logic, auth)
- Secrets must never be committed to version control
- Must support both Docker Compose (immediate) and Kubernetes (future) deployment paths

**Scale/Scope**:
- 2 containerized services (frontend, backend)
- 2 Helm charts with complete lifecycle management
- Local development/learning environment (not production-scale)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase I Constitution Applicability

The Phase I Todo Application Constitution defines principles for in-memory task management with console UI. Phase IV is a **deployment-only phase** that containerizes an existing web application (Phase III) without modifying its business logic.

**Constitution Compliance Analysis**:

| Principle | Applicability | Compliance Status |
|-----------|---------------|-------------------|
| **I. In-Memory Task Management** | NOT APPLICABLE | Phase III uses PostgreSQL; Phase IV deploys existing architecture unchanged |
| **II. Separation of Concerns** | APPLICABLE (adapted) | Dockerfiles and Helm charts maintain clear separation between infrastructure (deployment) and application code (Phase III) |
| **III. Input Validation** | APPLICABLE | Helm charts must validate values.yaml; deployment scripts must validate prerequisites |
| **IV. Deterministic Behavior** | APPLICABLE | Container builds and deployments must be reproducible and predictable |
| **V. Code Quality** | APPLICABLE | Dockerfiles, Helm templates, and documentation must follow best practices |

**Gates**:
- ✅ **No Business Logic Changes**: Phase IV must NOT modify Phase III application code
- ✅ **Clear Separation**: Deployment artifacts (Dockerfiles, Helm charts) isolated from application source
- ✅ **Input Validation**: Helm values and environment variables validated before deployment
- ✅ **Deterministic Builds**: Docker images build consistently from same source
- ✅ **Documentation**: Comprehensive setup, deployment, and troubleshooting guides

**Adapted Principles for Phase IV**:
1. **Deployment-Logic Separation**: Keep infrastructure code (Dockerfiles, K8s manifests) separate from application code
2. **Configuration Validation**: Validate all Helm values, environment variables, and secrets before deployment
3. **Reproducible Deployments**: Ensure container builds and Helm installations produce identical results
4. **Clear Error Messages**: Deployment failures must provide actionable troubleshooting steps
5. **Maintainable Infrastructure**: Use standard Kubernetes patterns, clear naming, and comprehensive comments

**GATE STATUS: PASS** - All applicable principles satisfied with deployment-specific adaptations.

## Project Structure

### Documentation (this feature)

```text
specs/004-phase4-local-k8s/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technology choices and alternatives
├── data-model.md        # Phase 1: Container and K8s resource entities
├── quickstart.md        # Phase 1: Quick deployment guide
├── contracts/           # Phase 1: Helm values schemas and examples
│   ├── backend-values.schema.yaml
│   ├── frontend-values.schema.yaml
│   └── secrets-template.yaml
├── checklists/
│   └── requirements.md  # Quality validation (completed)
└── tasks.md             # Phase 2: Implementation tasks (/sp.tasks command)
```

### Deployment Artifacts (repository root)

```text
# NEW: Docker and Kubernetes deployment infrastructure
docker/
├── backend/
│   ├── Dockerfile                 # Multi-stage FastAPI image
│   ├── .dockerignore             # Exclude venv, __pycache__, etc.
│   └── docker-entrypoint.sh      # Container startup script
└── frontend/
    ├── Dockerfile                 # Multi-stage Next.js image
    ├── .dockerignore             # Exclude node_modules, .next, etc.
    └── docker-entrypoint.sh      # Container startup script

# NEW: Docker Compose (SLAT workaround - Track A)
docker-compose.yml                 # Local orchestration (immediate use)
docker-compose.override.yml        # Local development overrides
.env.example                       # Template for secrets (NOT .env itself)

# NEW: Helm Charts (K8s-ready - Track B)
helm/
├── backend/
│   ├── Chart.yaml                 # Chart metadata
│   ├── values.yaml                # Default configuration
│   ├── values-local.yaml          # Local/Minikube overrides
│   ├── templates/
│   │   ├── deployment.yaml        # Backend Deployment
│   │   ├── service.yaml           # Backend Service (ClusterIP + NodePort)
│   │   ├── secrets.yaml           # Secrets from values (base64)
│   │   ├── configmap.yaml         # Non-sensitive config
│   │   ├── _helpers.tpl           # Template helpers
│   │   └── NOTES.txt              # Post-install instructions
│   └── .helmignore
└── frontend/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-local.yaml
    ├── templates/
    │   ├── deployment.yaml
    │   ├── service.yaml           # Frontend Service (LoadBalancer/NodePort)
    │   ├── configmap.yaml
    │   ├── _helpers.tpl
    │   └── NOTES.txt
    └── .helmignore

# NEW: Kubernetes Manifests (alternative to Helm)
k8s/
├── backend/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── secrets.yaml.example       # Template (user fills with base64 values)
└── frontend/
    ├── deployment.yaml
    ├── service.yaml
    └── configmap.yaml

# NEW: Deployment scripts and documentation
scripts/
├── build-images.sh                # Build Docker images for both services
├── build-images.ps1               # PowerShell version for Windows
├── deploy-compose.sh              # Deploy via Docker Compose (Track A)
├── deploy-compose.ps1
├── deploy-k8s.sh                  # Deploy via Helm/kubectl (Track B)
├── deploy-k8s.ps1
└── validate-env.sh                # Check prerequisites and secrets

# UPDATED: Documentation
README.md                          # Add "Deployment" section
docs/
├── deployment/
│   ├── docker-compose.md          # Track A: Immediate Docker Compose guide
│   ├── kubernetes.md              # Track B: Kubernetes/Helm guide (future)
│   ├── troubleshooting.md         # Common issues and solutions
│   └── prerequisites.md           # Required tools and setup
└── architecture/
    └── containerization.md        # Deployment architecture decisions

# EXISTING: Phase III application code (UNCHANGED)
backend/
├── src/                           # FastAPI application (no changes)
├── tests/                         # Backend tests (no changes)
├── requirements.txt               # Python dependencies (no changes)
└── alembic/                       # Database migrations (no changes)

frontend/
├── app/                           # Next.js pages (no changes)
├── components/                    # React components (no changes)
├── lib/                           # Utilities (no changes)
├── package.json                   # Node dependencies (no changes)
└── next.config.ts                 # Next.js config (no changes)
```

**Structure Decision**:

This deployment follows a **dual-track strategy** to address the SLAT limitation:

1. **Track A (Immediate - Docker Compose)**: Provides local container orchestration without Kubernetes, allowing immediate testing and development
2. **Track B (K8s-Ready - Helm Charts)**: Creates production-ready Kubernetes manifests for future deployment when SLAT-capable hardware or alternative K8s runtime (kind) becomes available

All deployment artifacts are isolated in new directories (`docker/`, `helm/`, `k8s/`, `scripts/`, `docs/deployment/`) to maintain clear separation from Phase III application code, ensuring the "no code changes" constraint is satisfied.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**NO VIOLATIONS** - All constitution principles satisfied with deployment-specific adaptations. The dual-track strategy (Docker Compose + Helm) adds necessary complexity to address the SLAT hardware limitation while maintaining K8s-readiness for future deployment.

## Phase 0: Research (Completed ✅)

All technology decisions and alternatives researched. See [research.md](./research.md) for detailed findings.

**Key Decisions**:
1. **Primary K8s Alternative**: kind (Kubernetes in Docker) - bypasses SLAT requirement
2. **Immediate Fallback**: Docker Compose for local orchestration
3. **Image Strategy**: Multi-stage Dockerfiles for optimal size and security
4. **Secrets Management**: K8s Secrets + Helm templating / .env files for Docker Compose
5. **Service Exposure**: NodePort for development, LoadBalancer pattern documented for production
6. **AI Tools**: Optional enhancements with manual fallbacks

**Risks Mitigated**:
- SLAT limitation: kind provides real Kubernetes API without hypervisor
- Accidental secret commits: .gitignore + template files (.env.example)
- Image build failures: Multi-stage builds with error handling
- Phase III code changes: Clear directory separation

---

## Phase 1: Design & Contracts (Completed ✅)

### Artifacts Created

1. **[data-model.md](./data-model.md)**: Complete entity catalog
   - 12 deployment entities defined (containers, K8s resources, Helm charts)
   - Entity relationships documented
   - Validation rules specified

2. **[contracts/](./contracts/)**: Helm values schemas and secret templates
   - `backend-values.schema.yaml`: Backend Helm chart configuration
   - `frontend-values.schema.yaml`: Frontend Helm chart configuration
   - `secrets-template.yaml`: Comprehensive secrets management guide

3. **[quickstart.md](./quickstart.md)**: Step-by-step deployment guide
   - Track A: Docker Compose (immediate deployment)
   - Track B: Kubernetes with kind (SLAT workaround)
   - Troubleshooting guide
   - Validation checklist

### Design Principles Applied

- **Deployment-Logic Separation**: All deployment artifacts in isolated directories
- **Dual-Track Strategy**: Docker Compose for immediate use + K8s readiness
- **Security First**: Comprehensive secrets management, .gitignore protection
- **Developer Experience**: Clear documentation, quick start guides, troubleshooting

---

## Phase 2: Task Breakdown (Next: /sp.tasks)

The implementation will be broken into prioritized, testable tasks following this structure:

### Proposed Task Groups

1. **Docker Infrastructure** (P0 - Foundation)
   - Create Dockerfiles for backend and frontend
   - Create .dockerignore files
   - Create docker-entrypoint.sh scripts
   - Build and test images locally

2. **Docker Compose Deployment** (P0 - Track A)
   - Create docker-compose.yml
   - Create .env.example template
   - Test local deployment
   - Document Docker Compose workflow

3. **Helm Charts - Backend** (P0 - Track B)
   - Initialize backend Helm chart
   - Create Deployment template
   - Create Service template
   - Create Secrets template
   - Create ConfigMap template
   - Test chart installation

4. **Helm Charts - Frontend** (P0 - Track B)
   - Initialize frontend Helm chart
   - Create Deployment template
   - Create Service template
   - Create ConfigMap template
   - Test chart installation

5. **Kubernetes Manifests** (P1 - Alternative to Helm)
   - Create raw K8s YAML files as alternative
   - Document kubectl apply workflow

6. **Deployment Scripts** (P1 - Automation)
   - Create build-images script (Bash + PowerShell)
   - Create deploy-compose script
   - Create deploy-k8s script
   - Create validate-env script

7. **Documentation** (P0 - User Guidance)
   - Update main README.md with deployment section
   - Create docs/deployment/docker-compose.md
   - Create docs/deployment/kubernetes.md
   - Create docs/deployment/troubleshooting.md
   - Create docs/deployment/prerequisites.md

8. **AI Tools Integration** (P2 - Optional Enhancement)
   - Document kubectl-ai usage examples
   - Document kagent usage examples
   - Create example workflows

9. **Testing & Validation** (P0 - Quality Assurance)
   - Test Docker Compose deployment end-to-end
   - Test kind cluster deployment end-to-end
   - Verify Phase III functionality unchanged
   - Document validation checklist

**Task Generation**: Run `/sp.tasks` to create detailed, testable implementation tasks in `tasks.md`

---

## Summary

### What We Built (Planning Phase)

| Artifact | Purpose | Status |
|----------|---------|--------|
| `plan.md` | Implementation strategy and architecture | ✅ Complete |
| `research.md` | Technology decisions and alternatives | ✅ Complete |
| `data-model.md` | Deployment entities and relationships | ✅ Complete |
| `contracts/` | Helm schemas and secrets templates | ✅ Complete |
| `quickstart.md` | Deployment guide (dual-track) | ✅ Complete |

### Key Architectural Decisions

1. **Dual-Track Strategy**: 
   - Track A (Docker Compose): Immediate deployment capability
   - Track B (Kubernetes): Future-ready with kind as Minikube alternative

2. **SLAT Workaround**:
   - Primary: kind (Kubernetes in Docker containers, not VMs)
   - Fallback: Docker Compose for full functionality without K8s

3. **Separation of Concerns**:
   - All deployment artifacts isolated in new directories
   - Zero modifications to Phase III application code
   - Clear .gitignore protection for secrets

4. **Developer Experience**:
   - Comprehensive documentation (quickstart, troubleshooting, schemas)
   - Multiple deployment options (Compose, Helm, kubectl)
   - Optional AI tool integration

### Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to create detailed implementation tasks
2. **Implementation**: Execute tasks in priority order (P0 → P1 → P2)
3. **Testing**: Validate both deployment tracks (Compose + kind)
4. **Documentation**: Ensure all guides are accurate and complete

### Success Criteria Check

| Criterion | Planning Support | Implementation Required |
|-----------|-----------------|-------------------------|
| Build images in <5 min | Multi-stage Dockerfiles designed | Build and time actual builds |
| Deploy via Helm in <3 min | Helm charts structured | Create charts and test deployment |
| App accessible in <30 sec | Service exposure designed | Test actual startup time |
| Phase III features unchanged | No code modification planned | Validate in testing |
| kubectl-ai executes 3+ ops | Examples documented | Test actual tool usage |
| 30-minute first deployment | Quickstart guide created | Validate with fresh user |

---

## Constitution Re-Check (Post-Design)

**Initial Status**: PASS (all principles satisfied with deployment adaptations)

**Post-Design Review**:

| Adapted Principle | Design Compliance | Evidence |
|-------------------|-------------------|----------|
| **Deployment-Logic Separation** | ✅ PASS | All artifacts in `docker/`, `helm/`, `k8s/`, `scripts/` directories |
| **Configuration Validation** | ✅ PASS | Helm values schemas defined, .env template provided |
| **Reproducible Deployments** | ✅ PASS | Declarative configs (Compose YAML, Helm charts), version-controlled |
| **Clear Error Messages** | ✅ PASS | Troubleshooting guide, health checks, deployment NOTES.txt |
| **Maintainable Infrastructure** | ✅ PASS | Standard K8s patterns, comprehensive comments in schemas |

**Final Status**: ✅ PASS - Design maintains all constitutional principles

---

**Plan Complete** | **Branch**: `004-phase4-local-k8s` | **Ready for**: `/sp.tasks`
