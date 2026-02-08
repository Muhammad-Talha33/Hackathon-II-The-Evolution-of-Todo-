# Tasks: Phase V Part C - Cloud Production Deployment

**Input**: Design documents from `/specs/005-phase5-partc-cloud-production/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: No automated tests for infrastructure tasks. Validation via `kubectl dry-run` and manual verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US8)
- Include exact file paths in descriptions

## Path Conventions

- **Kubernetes manifests**: `k8s/base/`, `k8s/overlays/`
- **CI/CD workflows**: `.github/workflows/`
- **Observability**: `k8s/observability/`
- **Documentation**: `docs/`, `README.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and foundational files

- [x] T001 Create Kubernetes directory structure: `k8s/base/backend/`, `k8s/base/frontend/`, `k8s/base/workers/`, `k8s/base/dapr/`
- [x] T002 Create overlay directory structure: `k8s/overlays/staging/patches/`, `k8s/overlays/production/patches/`
- [x] T003 [P] Create observability directory structure: `k8s/observability/grafana-dashboards/`
- [x] T004 [P] Create GitHub workflows directory: `.github/workflows/`

**Checkpoint**: Directory structure ready for manifest creation

---

## Phase 2: Foundational (Base Manifests)

**Purpose**: Create base Kubernetes manifests shared across all environments

**⚠️ CRITICAL**: Environment overlays depend on base manifests being complete

### Core Base Resources

- [x] T005 Create base namespace manifest in `k8s/base/namespace.yaml` with todo-app namespace and environment labels
- [x] T006 [P] Create backend deployment manifest in `k8s/base/backend/deployment.yaml` with Dapr sidecar annotations, resource limits, liveness/readiness probes
- [x] T007 [P] Create backend service manifest in `k8s/base/backend/service.yaml` with ClusterIP on port 8000
- [x] T008 [P] Create backend configmap in `k8s/base/backend/configmap.yaml` with ENVIRONMENT, LOG_LEVEL, DAPR_HTTP_PORT
- [x] T009 [P] Create frontend deployment manifest in `k8s/base/frontend/deployment.yaml` with resource limits and probes (no Dapr sidecar)
- [x] T010 [P] Create frontend service manifest in `k8s/base/frontend/service.yaml` with ClusterIP on port 3000
- [x] T011 [P] Create frontend configmap in `k8s/base/frontend/configmap.yaml` with NEXT_PUBLIC_API_URL

### Worker Deployments

- [x] T012 [P] Create reminder worker deployment in `k8s/base/workers/reminder-worker-deployment.yaml` with Dapr sidecar annotations
- [x] T013 [P] Create reminder worker service in `k8s/base/workers/reminder-worker-service.yaml` with ClusterIP on port 8001
- [x] T014 [P] Create recurrence worker deployment in `k8s/base/workers/recurrence-worker-deployment.yaml` with Dapr sidecar and DB secret
- [x] T015 [P] Create recurrence worker service in `k8s/base/workers/recurrence-worker-service.yaml` with ClusterIP on port 8002

### Dapr Components

- [x] T016 [P] Create Dapr pubsub component in `k8s/base/dapr/pubsub.yaml` with cloud Kafka configuration and secretKeyRef
- [x] T017 [P] Create Dapr statestore component in `k8s/base/dapr/statestore.yaml` with Redis configuration
- [x] T018 [P] Create Dapr cron binding in `k8s/base/dapr/cron-binding.yaml` with @every 1m schedule
- [x] T019 [P] Create Dapr configuration in `k8s/base/dapr/configuration.yaml` with Zipkin tracing and metrics enabled

### Kustomization

- [x] T020 Create base kustomization.yaml in `k8s/base/kustomization.yaml` listing all resources with common labels

**Validation**:
```bash
kustomize build k8s/base
```

**Checkpoint**: Base manifests complete - overlays can now be created

---

## Phase 3: User Story 1 - Deploy Application to Kubernetes (Priority: P0) 🎯 MVP

**Goal**: Deploy complete Todo stack to managed Kubernetes cluster with healthy pods

**Independent Test**: Apply manifests to cluster, verify all pods Running, access frontend, create task

### Implementation for User Story 1

- [x] T021 [US1] Create staging namespace in `k8s/overlays/staging/namespace.yaml` with todo-staging name
- [x] T022 [US1] Create staging kustomization in `k8s/overlays/staging/kustomization.yaml` referencing base and patches
- [x] T023 [P] [US1] Create staging replica count patch in `k8s/overlays/staging/patches/replica-count.yaml` (backend:1, frontend:1, workers:1)
- [x] T024 [P] [US1] Create staging resource limits patch in `k8s/overlays/staging/patches/resource-limits.yaml` with conservative limits
- [x] T025 [US1] Create staging secrets template in `k8s/overlays/staging/secrets.yaml.template` with documented placeholders
- [x] T026 [US1] Create production namespace in `k8s/overlays/production/namespace.yaml` with todo-production name
- [x] T027 [US1] Create production kustomization in `k8s/overlays/production/kustomization.yaml` referencing base and patches
- [x] T028 [P] [US1] Create production replica count patch in `k8s/overlays/production/patches/replica-count.yaml` (backend:3, frontend:2, workers:2)
- [x] T029 [P] [US1] Create production resource limits patch in `k8s/overlays/production/patches/resource-limits.yaml` with elevated limits
- [x] T030 [US1] Create production ingress in `k8s/overlays/production/ingress.yaml` with NGINX class and path routing
- [x] T031 [US1] Create production secrets template in `k8s/overlays/production/secrets.yaml.template`

**Validation**:
```bash
kustomize build k8s/overlays/staging | kubectl apply --dry-run=client -f -
kustomize build k8s/overlays/production | kubectl apply --dry-run=client -f -
```

**Checkpoint**: Kubernetes deployment manifests ready - US1 testable by deploying to cluster

---

## Phase 4: User Story 2 - Configure Dapr on Kubernetes (Priority: P0)

**Goal**: Dapr installed and configured, sidecar injection working, components applied

**Independent Test**: Run `dapr init -k`, verify system pods, apply components, check sidecar injection on app pods

### Implementation for User Story 2

- [x] T032 [US2] Document Dapr installation steps in `k8s/README.md` (dapr init -k --enable-ha --enable-mtls)
- [x] T033 [US2] Verify Dapr annotations in `k8s/base/backend/deployment.yaml` include dapr.io/enabled, app-id, app-port
- [x] T034 [US2] Verify Dapr annotations in `k8s/base/workers/reminder-worker-deployment.yaml`
- [x] T035 [US2] Verify Dapr annotations in `k8s/base/workers/recurrence-worker-deployment.yaml`
- [x] T036 [US2] Update Dapr configuration in `k8s/base/dapr/configuration.yaml` to reference Zipkin in observability namespace

**Checkpoint**: Dapr configuration complete - sidecars will inject on pod creation

---

## Phase 5: User Story 3 - Cloud Kafka/Redpanda (Priority: P1)

**Goal**: Connect to cloud-managed Kafka with SASL/SSL authentication

**Independent Test**: Configure Confluent Cloud credentials, apply pubsub component, verify events flow

### Implementation for User Story 3

- [x] T037 [US3] Update pubsub component in `k8s/base/dapr/pubsub.yaml` with SASL authentication metadata
- [x] T038 [US3] Add kafka-credentials secret reference to `k8s/overlays/staging/secrets.yaml.template`
- [x] T039 [US3] Add kafka-credentials secret reference to `k8s/overlays/production/secrets.yaml.template`
- [x] T040 [US3] Document Confluent Cloud setup in `docs/deployment-guide.md` (cluster creation, API keys, topics)
- [x] T041 [US3] Verify local docker-compose.dapr.yml unchanged (local Redpanda preserved)

**Checkpoint**: Cloud Kafka integration complete - events will flow through cloud broker

---

## Phase 6: User Story 4 - Secure Secrets Management (Priority: P1)

**Goal**: All secrets stored in Kubernetes Secrets, never in manifests

**Independent Test**: Create secrets via kubectl, verify pods start and connect to services

### Implementation for User Story 4

- [x] T042 [US4] Create Dapr secrets component in `k8s/base/dapr/secrets.yaml` for Kubernetes secret store
- [x] T043 [US4] Add Dapr secrets component to `k8s/base/kustomization.yaml`
- [x] T044 [US4] Document db-credentials secret creation in `k8s/overlays/staging/secrets.yaml.template`
- [x] T045 [US4] Document app-secrets secret creation in `k8s/overlays/staging/secrets.yaml.template`
- [x] T046 [US4] Document secret rotation procedure in `docs/deployment-guide.md`
- [x] T047 [US4] Verify all deployments reference secrets via secretKeyRef in environment variables

**Checkpoint**: Secrets management complete - no credentials in source control

---

## Phase 7: User Story 5 - Environment Separation (Priority: P1)

**Goal**: Separate staging and production with different configurations

**Independent Test**: Deploy to staging with staging config, deploy to production with production config

### Implementation for User Story 5

- [x] T048 [US5] Verify namespace isolation in overlays (todo-staging vs todo-production)
- [x] T049 [US5] Add environment-specific ConfigMap patches if needed in `k8s/overlays/staging/patches/`
- [x] T050 [US5] Add environment-specific ConfigMap patches if needed in `k8s/overlays/production/patches/`
- [x] T051 [US5] Document environment deployment commands in `k8s/README.md`
- [x] T052 [US5] Verify Kustomize namespace transformation in kustomization.yaml files

**Checkpoint**: Environment separation complete - staging and production isolated

---

## Phase 8: User Story 6 - CI/CD Pipeline (Priority: P2)

**Goal**: Automated build, test, and deploy via GitHub Actions

**Independent Test**: Push to main, verify CI runs, images pushed, staging deployed

### Implementation for User Story 6

- [x] T053 [US6] Create CI workflow in `.github/workflows/ci.yaml` with lint, test, build, push jobs
- [x] T054 [US6] Add Docker build steps for backend, frontend, workers in CI workflow
- [x] T055 [US6] Add GHCR push steps with SHA tagging in CI workflow
- [x] T056 [US6] Create CD staging workflow in `.github/workflows/cd-staging.yaml` triggered on CI success
- [x] T057 [US6] Add Kustomize deploy steps to CD staging workflow
- [x] T058 [US6] Create CD production workflow in `.github/workflows/cd-production.yaml` with manual trigger
- [x] T059 [US6] Add environment protection requirement for production in CD workflow
- [x] T060 [US6] Create deployment script in `scripts/deploy-k8s.sh` for manual deployments
- [x] T061 [US6] Document required repository secrets (KUBE_CONFIG, GHCR_TOKEN) in `docs/deployment-guide.md`

**Checkpoint**: CI/CD pipeline complete - automated deployment on push to main

---

## Phase 9: User Story 7 - Observability Stack (Priority: P2)

**Goal**: Prometheus, Grafana, Zipkin deployed for monitoring and tracing

**Independent Test**: Deploy observability stack, verify metrics scraped, traces visible

### Implementation for User Story 7

- [x] T062 [US7] Create observability namespace manifest in `k8s/observability/namespace.yaml`
- [x] T063 [P] [US7] Create Prometheus Helm values in `k8s/observability/prometheus-values.yaml` with scrape configs
- [x] T064 [P] [US7] Create Grafana Helm values in `k8s/observability/grafana-values.yaml` with Prometheus datasource
- [x] T065 [P] [US7] Create Todo App Grafana dashboard in `k8s/observability/grafana-dashboards/todo-app.json`
- [x] T066 [P] [US7] Create Zipkin deployment in `k8s/observability/zipkin.yaml` with service
- [x] T067 [US7] Create observability kustomization in `k8s/observability/kustomization.yaml`
- [x] T068 [US7] Document observability deployment in `k8s/README.md`

**Checkpoint**: Observability stack complete - metrics and traces visible in dashboards

---

## Phase 10: User Story 8 - Production Readiness Checklist (Priority: P2)

**Goal**: Comprehensive checklist for validating production deployment

**Independent Test**: Review checklist, verify all items validatable

### Implementation for User Story 8

- [x] T069 [US8] Create production readiness checklist in `docs/production-readiness-checklist.md` with security, reliability, observability sections
- [x] T070 [US8] Add pre-deployment checks to checklist (secrets, images, cluster access)
- [x] T071 [US8] Add post-deployment verification steps to checklist
- [x] T072 [US8] Add rollback procedures to checklist

**Checkpoint**: Production readiness checklist complete

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final validation

- [x] T073 [P] Create comprehensive deployment guide in `docs/deployment-guide.md`
- [x] T074 [P] Create k8s README in `k8s/README.md` with directory structure and Kustomize usage
- [x] T075 Update main README.md with cloud deployment section and quick command reference
- [x] T076 Validate all Kustomize overlays build without errors
- [x] T077 Verify local docker-compose.dapr.yml still works unchanged
- [x] T078 Run quickstart.md validation steps

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    │
    ▼
Phase 2: Foundational (Base Manifests) ← BLOCKS ALL USER STORIES
    │
    ├─────────────────────────────────────────────────────────┐
    │                                                         │
    ▼                                                         ▼
Phase 3: US1 - K8s Deploy (P0) ─────────────────► Phase 4: US2 - Dapr (P0)
    │                                                         │
    ├────────────────┬────────────────────────────────────────┤
    │                │                                        │
    ▼                ▼                                        ▼
Phase 5: US3     Phase 6: US4                           Phase 7: US5
Cloud Kafka      Secrets                                Env Separation
(P1)             (P1)                                   (P1)
    │                │                                        │
    └────────────────┴────────────────────────────────────────┘
                     │
    ┌────────────────┴────────────────────────────┐
    │                                             │
    ▼                                             ▼
Phase 8: US6 - CI/CD (P2)           Phase 9: US7 - Observability (P2)
    │                                             │
    └─────────────────────────────────────────────┘
                     │
                     ▼
            Phase 10: US8 - Checklist (P2)
                     │
                     ▼
            Phase 11: Polish
```

### User Story Dependencies

- **US1 (P0)**: Deploy to K8s - Depends on Phase 2 only
- **US2 (P0)**: Dapr Config - Depends on Phase 2, can parallel with US1
- **US3 (P1)**: Cloud Kafka - Depends on US1, US2 (Dapr must be configured)
- **US4 (P1)**: Secrets - Depends on US1 (deployments exist)
- **US5 (P1)**: Env Separation - Depends on US1 (overlays exist)
- **US6 (P2)**: CI/CD - Depends on US1-US5 (deployment works manually)
- **US7 (P2)**: Observability - Depends on US2 (Dapr config for tracing)
- **US8 (P2)**: Checklist - Depends on US1-US7 (all components documented)

### Parallel Opportunities

**Within Phase 2 (Base Manifests)**:
```bash
# All service manifests can be created in parallel:
T006, T007, T008  # Backend
T009, T010, T011  # Frontend
T012, T013, T014, T015  # Workers
T016, T017, T018, T019  # Dapr components
```

**Within User Stories**:
```bash
# US1: Staging and production patches in parallel
T023, T024  # Staging patches
T028, T029  # Production patches

# US7: Observability components in parallel
T063, T064, T065, T066  # Prometheus, Grafana, Dashboard, Zipkin
```

---

## Parallel Example: Phase 2 Base Manifests

```bash
# Launch all backend resources together:
Task: "Create backend deployment in k8s/base/backend/deployment.yaml"
Task: "Create backend service in k8s/base/backend/service.yaml"
Task: "Create backend configmap in k8s/base/backend/configmap.yaml"

# Launch all frontend resources together:
Task: "Create frontend deployment in k8s/base/frontend/deployment.yaml"
Task: "Create frontend service in k8s/base/frontend/service.yaml"
Task: "Create frontend configmap in k8s/base/frontend/configmap.yaml"

# Launch all Dapr components together:
Task: "Create Dapr pubsub in k8s/base/dapr/pubsub.yaml"
Task: "Create Dapr statestore in k8s/base/dapr/statestore.yaml"
Task: "Create Dapr cron binding in k8s/base/dapr/cron-binding.yaml"
Task: "Create Dapr configuration in k8s/base/dapr/configuration.yaml"
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup (directory structure)
2. Complete Phase 2: Foundational (base manifests)
3. Complete Phase 3: US1 - Kubernetes deployment
4. Complete Phase 4: US2 - Dapr configuration
5. **STOP and VALIDATE**: Deploy to staging, verify pods healthy
6. Demo/deploy if ready (basic cloud deployment working)

### Incremental Delivery

1. Setup + Foundational → Base manifests ready
2. Add US1 + US2 → K8s + Dapr working → Deploy/Demo (MVP!)
3. Add US3 → Cloud Kafka integration
4. Add US4 → Secrets management
5. Add US5 → Environment separation
6. Add US6 → CI/CD automation
7. Add US7 → Observability stack
8. Add US8 → Production readiness checklist

### Full Deployment Sequence

```bash
# 1. Setup cluster (manual)
doctl kubernetes cluster create todo-cluster --region nyc1 --node-pool "name=default;size=s-2vcpu-4gb;count=2"

# 2. Install Dapr
dapr init -k --enable-ha --enable-mtls

# 3. Create secrets (manual, never automated with real values)
kubectl create secret generic db-credentials --from-literal=DATABASE_URL="..." -n todo-staging
kubectl create secret generic kafka-credentials --from-literal=brokers="..." --from-literal=username="..." --from-literal=password="..." -n todo-staging
kubectl create secret generic app-secrets --from-literal=JWT_SECRET="..." -n todo-staging

# 4. Deploy to staging
kubectl apply -k k8s/overlays/staging

# 5. Verify deployment
kubectl get pods -n todo-staging
kubectl logs deployment/backend -n todo-staging

# 6. Deploy observability
helm install prometheus prometheus-community/prometheus -n observability -f k8s/observability/prometheus-values.yaml
helm install grafana grafana/grafana -n observability -f k8s/observability/grafana-values.yaml
kubectl apply -f k8s/observability/zipkin.yaml -n observability
```

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label (US1-US8) maps task to specific user story
- Each user story is independently completable and testable
- Validate Kustomize builds after completing each phase
- Commit after each logical group of tasks
- Local docker-compose must remain unchanged
- Never commit actual secrets - use .template suffix for examples
- Total tasks: 78
- MVP scope: T001-T036 (Setup + Foundational + US1 + US2 = 36 tasks)
