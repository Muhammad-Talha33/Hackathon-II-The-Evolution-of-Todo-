# Feature Specification: Phase V Part C - Cloud Production Deployment

**Feature Branch**: `005-phase5-partc-cloud-production`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Prepare the system for real-world cloud deployment and production readiness. Focus on Kubernetes deployment, Dapr installation, Kafka/Redpanda cloud setup, CI/CD pipeline, secrets management, environment separation, and observability."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Application to Kubernetes Cluster (Priority: P0)

As a DevOps engineer, I want to deploy the complete Todo application stack to a managed Kubernetes cluster so that the application runs in a production-grade environment with high availability and scalability.

**Why this priority**: This is the foundational capability that enables all other cloud deployment features. Without a working Kubernetes deployment, nothing else can be built or tested.

**Independent Test**: Deploy the full stack to a Kubernetes cluster. Verify all pods are running healthy. Access the frontend and create a task. Verify events flow through Kafka and workers process them correctly.

**Acceptance Scenarios**:

1. **Given** I have a Kubernetes cluster running, **When** I apply the Kubernetes manifests, **Then** all deployments, services, and pods reach a healthy state within 5 minutes.
2. **Given** the application is deployed, **When** I access the frontend URL, **Then** I can sign up, sign in, and perform task CRUD operations exactly as in local development.
3. **Given** a task is created with a reminder, **When** the reminder time passes, **Then** the Reminder Worker logs the reminder delivery (event flows through cloud Kafka).
4. **Given** a recurring task is completed, **When** the Recurrence Worker processes the event, **Then** a new task instance is created (exactly as in Phase B).
5. **Given** I scale the backend deployment to 3 replicas, **When** I perform multiple task operations, **Then** all replicas handle requests correctly with shared state.

---

### User Story 2 - Configure Dapr on Kubernetes (Priority: P0)

As a DevOps engineer, I want Dapr installed and configured on the Kubernetes cluster so that pub/sub, state management, and bindings work exactly as they do locally with docker-compose.

**Why this priority**: Dapr is the abstraction layer for event-driven architecture. Without Dapr working on Kubernetes, the application's event system won't function.

**Independent Test**: Install Dapr on the cluster. Deploy the application. Publish an event and verify it reaches Kafka and workers consume it.

**Acceptance Scenarios**:

1. **Given** I install Dapr on the cluster using `dapr init -k`, **When** the installation completes, **Then** Dapr system pods (`dapr-operator`, `dapr-sidecar-injector`, `dapr-placement`) are running in the `dapr-system` namespace.
2. **Given** Dapr is installed, **When** I apply Dapr component configurations (pubsub, statestore), **Then** the components are visible via `kubectl get components.dapr.io`.
3. **Given** the backend pod has the Dapr sidecar annotation, **When** the pod starts, **Then** a Dapr sidecar container is automatically injected alongside the application container.
4. **Given** the Dapr pubsub component points to cloud Kafka, **When** an event is published from the backend, **Then** the event appears in the Kafka topic within 2 seconds.
5. **Given** the cron binding is configured, **When** the scheduled time triggers, **Then** the reminder check endpoint is called and events are processed.

---

### User Story 3 - Set Up Cloud Kafka/Redpanda (Priority: P1)

As a DevOps engineer, I want to use a cloud-managed Kafka or Redpanda service so that the message broker is reliable, scalable, and requires minimal operational overhead.

**Why this priority**: A managed message broker removes operational burden and provides better reliability than self-hosted. This is critical for production but can be tested after basic Kubernetes works.

**Independent Test**: Provision a cloud Kafka cluster (Confluent Cloud, Aiven, or Redpanda Cloud). Configure Dapr to connect to it. Verify events flow between application and Kafka.

**Acceptance Scenarios**:

1. **Given** I have credentials for a cloud Kafka service, **When** I configure the Dapr pubsub component with those credentials, **Then** the component successfully connects to the cloud broker.
2. **Given** the pubsub component uses cloud Kafka, **When** a task is created, **Then** the `TaskCreated` event appears in the cloud Kafka topic.
3. **Given** the workers are configured to use cloud Kafka, **When** they start, **Then** they successfully subscribe and receive events.
4. **Given** the cloud Kafka service has SASL authentication enabled, **When** I store credentials in Kubernetes secrets, **Then** Dapr retrieves credentials securely and connects successfully.
5. **Given** the local docker-compose continues using local Redpanda, **When** I run locally, **Then** local development still works without cloud dependencies.

---

### User Story 4 - Implement Secure Secrets Management (Priority: P1)

As a DevOps engineer, I want application secrets (database credentials, API keys, Kafka auth) stored securely and never committed to source control so that the application meets security best practices.

**Why this priority**: Security is non-negotiable for production. Secrets management must be in place before any real credentials are used.

**Independent Test**: Store secrets in Kubernetes Secrets. Verify the application reads secrets correctly. Confirm no secrets appear in manifests or logs.

**Acceptance Scenarios**:

1. **Given** I create Kubernetes Secrets for database and Kafka credentials, **When** pods start, **Then** secrets are mounted as environment variables and the application connects successfully.
2. **Given** manifests reference secrets via `secretKeyRef`, **When** I view the manifests in source control, **Then** no actual credential values are visible.
3. **Given** the Dapr secrets component is configured, **When** Dapr components reference secrets, **Then** Dapr retrieves secrets from Kubernetes and passes them to components.
4. **Given** I need to rotate a secret, **When** I update the Kubernetes Secret and restart affected pods, **Then** the new secret value is used without code changes.
5. **Given** secrets are stored in Kubernetes, **When** I audit the cluster, **Then** secrets are encrypted at rest (cluster default) and access is controlled via RBAC.

---

### User Story 5 - Configure Environment Separation (Priority: P1)

As a DevOps engineer, I want separate configurations for development, staging, and production environments so that I can test changes safely before production deployment.

**Why this priority**: Environment separation prevents accidental production impacts and allows for proper testing workflows.

**Independent Test**: Deploy to staging environment with staging-specific configuration. Verify staging uses staging database and Kafka. Verify production uses separate resources.

**Acceptance Scenarios**:

1. **Given** I have Kubernetes namespaces for `dev`, `staging`, and `prod`, **When** I deploy to each namespace, **Then** each environment uses its own set of resources (databases, Kafka topics).
2. **Given** staging has different configuration values, **When** I deploy with staging values, **Then** the application connects to staging database and staging Kafka.
3. **Given** I use Kustomize or Helm values for environment-specific config, **When** I build manifests for each environment, **Then** the correct environment values are applied.
4. **Given** production has stricter resource limits, **When** I deploy to production, **Then** pods have production-appropriate CPU/memory limits and replica counts.
5. **Given** each environment has its own secrets, **When** I deploy, **Then** environment-specific secrets are used (no cross-environment secret sharing).

---

### User Story 6 - Set Up CI/CD Pipeline (Priority: P2)

As a DevOps engineer, I want an automated CI/CD pipeline so that code changes are automatically tested, built, and deployed with minimal manual intervention.

**Why this priority**: Automation is essential for production but can be set up after manual deployment works correctly.

**Independent Test**: Push a code change. Verify the pipeline runs tests, builds images, pushes to registry, and deploys to staging automatically.

**Acceptance Scenarios**:

1. **Given** I push code to the main branch, **When** the CI pipeline triggers, **Then** tests run and a Docker image is built.
2. **Given** tests pass and image is built, **When** the image is pushed to a container registry, **Then** the image is tagged with commit SHA and `latest`.
3. **Given** images are in the registry, **When** the CD pipeline deploys to staging, **Then** staging pods use the new image.
4. **Given** staging deployment succeeds, **When** I approve production deployment, **Then** production pods are updated with rolling deployment strategy.
5. **Given** a deployment fails, **When** health checks fail, **Then** the rollout is automatically rolled back to the previous version.

---

### User Story 7 - Implement Observability Stack (Priority: P2)

As a DevOps engineer, I want centralized logging, metrics, and distributed tracing so that I can monitor application health and debug issues in production.

**Why this priority**: Observability is critical for production operations but the application can run without it initially.

**Independent Test**: Deploy the application with observability enabled. Verify logs appear in the logging system. Check metrics are scraped. Trace a request through all services.

**Acceptance Scenarios**:

1. **Given** the application has structured logging configured, **When** I query the logging system, **Then** I can see logs from all services with correlation IDs.
2. **Given** Prometheus metrics are exposed, **When** I view the Grafana dashboard, **Then** I can see request rates, latencies, and error rates for all services.
3. **Given** Dapr observability is enabled, **When** a task operation involves multiple services, **Then** I can trace the request from API to Dapr to Kafka to Worker.
4. **Given** alerts are configured, **When** error rate exceeds threshold, **Then** an alert is triggered and I am notified.
5. **Given** I need to debug a slow request, **When** I look at distributed traces, **Then** I can identify which service/component caused the latency.

---

### User Story 8 - Create Production Readiness Checklist (Priority: P2)

As a DevOps engineer, I want a comprehensive production readiness checklist so that I can verify all aspects of production deployment are covered before going live.

**Why this priority**: The checklist ensures nothing is missed but is documentation, not infrastructure.

**Independent Test**: Review the checklist. Verify each item can be validated. Confirm all items are checked before production launch.

**Acceptance Scenarios**:

1. **Given** the checklist exists, **When** I review it, **Then** it covers security, reliability, observability, and operational concerns.
2. **Given** I complete the checklist, **When** all items are checked, **Then** the application is ready for production traffic.
3. **Given** a new team member joins, **When** they use the checklist, **Then** they can independently validate production readiness.
4. **Given** we make infrastructure changes, **When** we re-run the checklist, **Then** we catch any regressions or missing configurations.

---

### Edge Cases

- What happens when Kubernetes cluster nodes fail?
  - Pods are rescheduled to healthy nodes. Application remains available if replica count > 1.

- What happens when cloud Kafka becomes unavailable?
  - Same graceful degradation as local: API operations succeed, events are logged as failed. Manual replay may be needed.

- What happens when a deployment fails mid-rollout?
  - Kubernetes rolling deployment ensures old pods remain until new pods are healthy. Failed rollout is automatically rolled back.

- What happens when secrets are rotated?
  - Pods must be restarted to pick up new secret values. Zero-downtime rotation requires rolling restart.

- What happens when container registry is unavailable?
  - Existing pods continue running with cached images. New deployments fail until registry is available.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Kubernetes Deployment

- **FR-001**: The system MUST deploy to a managed Kubernetes cluster (DigitalOcean Kubernetes or Google Kubernetes Engine).
- **FR-002**: Kubernetes manifests MUST be provided for all services: Backend, Frontend, Reminder Worker, Recurrence Worker.
- **FR-003**: Each service MUST have a Deployment, Service, and ConfigMap resource defined.
- **FR-004**: Pods MUST have liveness and readiness probes configured.
- **FR-005**: Services MUST use appropriate service types (ClusterIP for internal, LoadBalancer/Ingress for external).
- **FR-006**: Resource requests and limits MUST be defined for all containers.

#### Dapr on Kubernetes

- **FR-007**: Dapr MUST be installed on the Kubernetes cluster using the official Helm chart or `dapr init -k`.
- **FR-008**: Dapr components (pubsub, statestore, secrets) MUST be deployed as Kubernetes custom resources.
- **FR-009**: Application pods MUST have Dapr sidecar injection annotations (`dapr.io/enabled: "true"`, `dapr.io/app-id`, `dapr.io/app-port`).
- **FR-010**: Dapr components MUST reference Kubernetes secrets for sensitive configuration.

#### Cloud Kafka/Redpanda

- **FR-011**: The system MUST support connection to cloud-managed Kafka (Confluent Cloud, Aiven, or Redpanda Cloud).
- **FR-012**: Kafka connection MUST use SASL/SSL authentication with credentials stored in Kubernetes secrets.
- **FR-013**: Kafka topics MUST be pre-created or auto-created by the Dapr pubsub component.
- **FR-014**: Local docker-compose MUST continue using local Redpanda (no cloud dependency for local dev).

#### Container Registry

- **FR-015**: Docker images MUST be pushed to a container registry (Docker Hub, GitHub Container Registry, or cloud-specific registry).
- **FR-016**: Images MUST be tagged with semantic versions and/or commit SHAs.
- **FR-017**: Kubernetes manifests MUST reference registry images with specific tags (not `latest` in production).

#### Secrets Management

- **FR-018**: All secrets MUST be stored in Kubernetes Secrets and never in plain text manifests.
- **FR-019**: Secrets MUST include: database connection string, Kafka credentials, JWT secret, API keys.
- **FR-020**: Manifests MUST reference secrets using `envFrom` or `secretKeyRef`.
- **FR-021**: A secrets template/documentation MUST exist showing which secrets are required.

#### Environment Separation

- **FR-022**: The system MUST support deployment to separate namespaces or clusters for dev/staging/prod.
- **FR-023**: Environment-specific configuration MUST use Kustomize overlays or Helm values files.
- **FR-024**: Each environment MUST have isolated resources (database, Kafka topics, secrets).

#### CI/CD Pipeline

- **FR-025**: A CI/CD pipeline definition MUST be provided (GitHub Actions, GitLab CI, or similar).
- **FR-026**: The pipeline MUST include stages: lint, test, build, push, deploy.
- **FR-027**: Deployments MUST use rolling update strategy with health check gates.
- **FR-028**: The pipeline MUST support manual approval for production deployments.

#### Observability

- **FR-029**: Applications MUST emit structured JSON logs with correlation IDs.
- **FR-030**: Applications MUST expose Prometheus metrics at `/metrics` endpoint.
- **FR-031**: Dapr observability MUST be configured for distributed tracing (Zipkin or Jaeger).
- **FR-032**: Basic Grafana dashboards MUST be provided for service monitoring.

#### Helm/Manifests Structure

- **FR-033**: Kubernetes manifests MUST be organized in a `k8s/` or `deploy/` directory.
- **FR-034**: Manifests MUST use either Kustomize structure OR Helm chart structure (not both).
- **FR-035**: Base/common configurations MUST be separated from environment-specific overlays.

---

### Key Entities *(mandatory)*

#### Kubernetes Resources

- **Namespace**: Isolation boundary for environments (dev, staging, prod)
- **Deployment**: Manages pod replicas for each service
- **Service**: Network endpoint for accessing pods
- **ConfigMap**: Non-sensitive configuration data
- **Secret**: Sensitive configuration (credentials, keys)
- **Ingress**: External HTTP(S) routing to services
- **HorizontalPodAutoscaler**: Automatic scaling based on metrics

#### Dapr Resources

- **Component**: Dapr building blocks (pubsub, statestore, secrets, bindings)
- **Configuration**: Dapr runtime settings (tracing, metrics)

#### CI/CD Entities

- **Pipeline**: Automated workflow for build and deploy
- **Registry**: Container image storage
- **Environment**: Deployment target (staging, production)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All application pods reach Running status within 5 minutes of manifest application.
- **SC-002**: Frontend is accessible via public URL with HTTPS (TLS termination at ingress or load balancer).
- **SC-003**: End-to-end task operations (create, read, update, delete, complete) work identically to local development.
- **SC-004**: Events flow through cloud Kafka to workers: Reminder Worker logs, Recurrence Worker creates tasks.
- **SC-005**: Application remains functional when scaled to 3 backend replicas (stateless horizontal scaling).
- **SC-006**: Zero secrets are visible in source-controlled manifests or CI/CD logs.
- **SC-007**: CI/CD pipeline completes successfully from code push to staging deployment.
- **SC-008**: Logs from all services are queryable in a centralized logging system.
- **SC-009**: Metrics are visible in monitoring dashboards with request rate, latency, and error rate.
- **SC-010**: Distributed traces show end-to-end request flow across services.
- **SC-011**: Rolling deployment successfully replaces pods with zero downtime.
- **SC-012**: Production readiness checklist is 100% complete before launch.
- **SC-013**: Local docker-compose (`docker-compose.dapr.yml`) continues to work unchanged.

---

## Scope & Boundaries *(mandatory)*

### In Scope

- Kubernetes manifests or Helm charts for all services
- Dapr installation and configuration on Kubernetes
- Cloud Kafka/Redpanda connection configuration
- Container registry setup and image tagging strategy
- Kubernetes secrets management for all credentials
- Environment separation via namespaces and overlays
- CI/CD pipeline definition (GitHub Actions preferred)
- Basic observability (logging, metrics, tracing)
- Production readiness checklist
- Documentation for deployment procedures

### Out of Scope

- Multi-region deployment or disaster recovery
- Advanced security (network policies, pod security policies, service mesh)
- Cost optimization or autoscaling tuning
- Database migration automation (schema changes)
- Blue-green or canary deployment strategies
- Advanced alerting rules and on-call rotation
- Load testing and performance benchmarking
- CDN configuration for frontend assets
- Domain name and DNS configuration
- SSL certificate management automation
- Backup and restore procedures
- Compliance auditing (SOC2, HIPAA, etc.)
- Changes to business logic, domain events, or API contracts
- Frontend UX changes
- New features beyond Phase B

---

## Assumptions *(mandatory)*

- A managed Kubernetes cluster is available (DigitalOcean or GKE).
- Cloud Kafka credentials can be obtained (Confluent Cloud free tier, Aiven, or Redpanda Cloud).
- A container registry is available (Docker Hub, GHCR, or cloud registry).
- GitHub Actions is available for CI/CD (or equivalent CI/CD platform).
- The existing Neon PostgreSQL database is accessible from cloud Kubernetes.
- Dapr 1.13+ Helm chart is compatible with the target Kubernetes version.
- Basic Kubernetes knowledge is assumed for deployment and operations.
- Budget constraints allow for managed services (K8s cluster, Kafka, registry).
- Environment-specific databases are created manually (not automated in this phase).

---

## Dependencies *(mandatory)*

### Internal Dependencies

- **Phase V Part A**: All task features (reminders, recurrence, due dates, priorities).
- **Phase V Part B**: Event-driven architecture (Dapr, Kafka, workers).
- **Existing Backend**: FastAPI app, event publishing, Dapr integration.
- **Existing Frontend**: Next.js app, no changes required.
- **docker-compose.dapr.yml**: Reference for local development parity.

### External Dependencies

- **Kubernetes Cluster**: DigitalOcean Kubernetes (DOKS) or Google Kubernetes Engine (GKE).
- **Dapr Helm Chart**: v1.13+ for Kubernetes installation.
- **Cloud Kafka**: Confluent Cloud, Aiven Kafka, or Redpanda Cloud.
- **Container Registry**: Docker Hub, GitHub Container Registry, or cloud-specific.
- **GitHub Actions**: CI/CD pipeline execution.
- **Prometheus/Grafana**: Metrics collection and visualization.
- **Zipkin/Jaeger**: Distributed tracing.

---

## Non-Functional Requirements *(mandatory)*

### Performance

- Application response times MUST be comparable to local development (under 500ms for API calls).
- Pod startup time MUST be under 60 seconds.
- Event processing latency (publish to worker processing) MUST be under 10 seconds.

### Reliability

- Application MUST remain available during rolling deployments (zero downtime).
- Application MUST recover automatically from single pod failures (ReplicaSet management).
- Workers MUST reconnect to Kafka after transient network issues.

### Security

- All secrets MUST be stored in Kubernetes Secrets (not ConfigMaps or manifests).
- External traffic MUST use HTTPS (TLS termination at ingress).
- Container images MUST be pulled from authenticated registry (not public `latest` tags).
- Pod-to-pod communication MUST stay within cluster network.

### Scalability

- Backend MUST support horizontal scaling to at least 5 replicas.
- Workers MUST support multiple replicas (Kafka consumer groups).
- No component MUST require vertical scaling for normal operation.

### Observability

- All services MUST emit structured logs (JSON format).
- All services MUST expose Prometheus metrics.
- Dapr MUST be configured for distributed tracing export.

### Backward Compatibility

- Local docker-compose development MUST remain unchanged and functional.
- API contracts MUST be identical to Phase B.
- No changes to business logic or domain events.

---

## Architecture Overview *(mandatory)*

### Kubernetes Cluster Diagram

```
+--------------------------------------------------------------------------------+
|                          Kubernetes Cluster                                    |
|  +------------------------------------------------------------------------+    |
|  |                         dapr-system namespace                          |    |
|  |   +--------------+  +---------------------+  +-------------------+     |    |
|  |   | dapr-operator|  |dapr-sidecar-injector|  |   dapr-placement  |     |    |
|  |   +--------------+  +---------------------+  +-------------------+     |    |
|  +------------------------------------------------------------------------+    |
|                                                                                |
|  +------------------------------------------------------------------------+    |
|  |                     todo-app namespace (staging/prod)                  |    |
|  |                                                                        |    |
|  |   +----------------------------------------------------------------+   |    |
|  |   |                         Ingress                                |   |    |
|  |   |                    (HTTPS termination)                         |   |    |
|  |   +----------------------------------------------------------------+   |    |
|  |                    |                        |                          |    |
|  |                    v                        v                          |    |
|  |   +------------------------+  +------------------------+              |    |
|  |   |    Frontend Service    |  |    Backend Service     |              |    |
|  |   |    (ClusterIP/LB)      |  |    (ClusterIP)         |              |    |
|  |   +-----------+------------+  +-----------+------------+              |    |
|  |               |                           |                           |    |
|  |               v                           v                           |    |
|  |   +------------------------+  +------------------------------------+  |    |
|  |   |   Frontend Deployment  |  |      Backend Deployment           |  |    |
|  |   |   +----------------+   |  |   +-----------+ +------------+    |  |    |
|  |   |   |  Next.js Pod   |   |  |   | FastAPI   | |Dapr Sidecar|    |  |    |
|  |   |   |  (replicas: 2) |   |  |   | Pod       | | (injected) |    |  |    |
|  |   |   +----------------+   |  |   |(replicas:3)| +------------+    |  |    |
|  |   +------------------------+  |   +-----------+                    |  |    |
|  |                               +------------------------------------+  |    |
|  |                                                                       |    |
|  |   +----------------------------+  +----------------------------+      |    |
|  |   | Reminder Worker Deployment |  | Recurrence Worker Deployment|     |    |
|  |   |  +----------+ +---------+  |  |  +----------+ +---------+  |      |    |
|  |   |  | Worker   | |  Dapr   |  |  |  | Worker   | |  Dapr   |  |      |    |
|  |   |  | Pod      | | Sidecar |  |  |  | Pod      | | Sidecar |  |      |    |
|  |   |  +----------+ +---------+  |  |  +----------+ +---------+  |      |    |
|  |   +----------------------------+  +----------------------------+      |    |
|  |                                                                       |    |
|  |   +---------------------------------------------------------------+   |    |
|  |   |                    Dapr Components                            |   |    |
|  |   |   +-------------+  +--------------+  +------------------+     |   |    |
|  |   |   |   pubsub    |  |  statestore  |  |   cron-binding   |     |   |    |
|  |   |   |(cloud Kafka)|  |   (Redis)    |  |   (reminders)    |     |   |    |
|  |   |   +-------------+  +--------------+  +------------------+     |   |    |
|  |   +---------------------------------------------------------------+   |    |
|  |                                                                       |    |
|  |   +---------------------------------------------------------------+   |    |
|  |   |                       Secrets                                 |   |    |
|  |   |  db-credentials | kafka-credentials | app-secrets            |   |    |
|  |   +---------------------------------------------------------------+   |    |
|  +------------------------------------------------------------------------+    |
|                                                                                |
|  +------------------------------------------------------------------------+    |
|  |                      observability namespace                           |    |
|  |   +--------------+  +--------------+  +--------------+                 |    |
|  |   |  Prometheus  |  |   Grafana    |  | Zipkin/Jaeger|                 |    |
|  |   +--------------+  +--------------+  +--------------+                 |    |
|  +------------------------------------------------------------------------+    |
+--------------------------------------------------------------------------------+
                    |                              |
                    v                              v
         +--------------------+       +------------------------+
         |   Cloud Kafka      |       |   Neon PostgreSQL      |
         | (Confluent/Aiven/  |       |   (External DB)        |
         |  Redpanda Cloud)   |       |                        |
         +--------------------+       +------------------------+
```

### Directory Structure

```
k8s/
|-- base/                           # Base manifests (shared across environments)
|   |-- namespace.yaml
|   |-- backend/
|   |   |-- deployment.yaml
|   |   |-- service.yaml
|   |   +-- configmap.yaml
|   |-- frontend/
|   |   |-- deployment.yaml
|   |   +-- service.yaml
|   |-- workers/
|   |   |-- reminder-worker-deployment.yaml
|   |   +-- recurrence-worker-deployment.yaml
|   |-- dapr/
|   |   |-- pubsub.yaml
|   |   |-- statestore.yaml
|   |   +-- cron-binding.yaml
|   +-- kustomization.yaml
|-- overlays/
|   |-- staging/
|   |   |-- kustomization.yaml
|   |   |-- namespace.yaml
|   |   |-- secrets.yaml.template    # Template, not actual secrets
|   |   +-- patches/
|   |       |-- replica-count.yaml
|   |       +-- resource-limits.yaml
|   +-- production/
|       |-- kustomization.yaml
|       |-- namespace.yaml
|       |-- secrets.yaml.template
|       |-- ingress.yaml
|       +-- patches/
|           |-- replica-count.yaml
|           +-- resource-limits.yaml
|-- observability/
|   |-- prometheus/
|   |   +-- values.yaml
|   |-- grafana/
|   |   |-- values.yaml
|   |   +-- dashboards/
|   |       +-- todo-app.json
|   +-- zipkin.yaml
+-- README.md                        # Deployment documentation

.github/
+-- workflows/
    |-- ci.yaml                      # Lint, test, build
    |-- cd-staging.yaml              # Deploy to staging
    +-- cd-production.yaml           # Deploy to production (manual trigger)
```

### Component Responsibilities

| Component           | Responsibility                                                      |
| ------------------- | ------------------------------------------------------------------- |
| Ingress             | TLS termination, route external traffic to services                 |
| Frontend Deployment | Serve Next.js app, replicas for availability                        |
| Backend Deployment  | Run FastAPI app with Dapr sidecar, horizontal scaling               |
| Worker Deployments  | Consume events from Kafka, process async tasks                      |
| Dapr Components     | Configure pubsub, state, bindings for Kubernetes                    |
| Secrets             | Store sensitive configuration securely                              |
| ConfigMaps          | Store non-sensitive environment configuration                       |
| Prometheus          | Collect and store metrics from all services                         |
| Grafana             | Visualize metrics, provide dashboards                               |
| Zipkin              | Collect and display distributed traces                              |

---

## File Impact Summary

### Files to Create

```
k8s/base/namespace.yaml
k8s/base/backend/deployment.yaml
k8s/base/backend/service.yaml
k8s/base/backend/configmap.yaml
k8s/base/frontend/deployment.yaml
k8s/base/frontend/service.yaml
k8s/base/workers/reminder-worker-deployment.yaml
k8s/base/workers/recurrence-worker-deployment.yaml
k8s/base/dapr/pubsub.yaml
k8s/base/dapr/statestore.yaml
k8s/base/dapr/cron-binding.yaml
k8s/base/kustomization.yaml
k8s/overlays/staging/kustomization.yaml
k8s/overlays/staging/namespace.yaml
k8s/overlays/staging/secrets.yaml.template
k8s/overlays/staging/patches/replica-count.yaml
k8s/overlays/staging/patches/resource-limits.yaml
k8s/overlays/production/kustomization.yaml
k8s/overlays/production/namespace.yaml
k8s/overlays/production/secrets.yaml.template
k8s/overlays/production/ingress.yaml
k8s/overlays/production/patches/replica-count.yaml
k8s/overlays/production/patches/resource-limits.yaml
k8s/observability/prometheus/values.yaml
k8s/observability/grafana/values.yaml
k8s/observability/grafana/dashboards/todo-app.json
k8s/observability/zipkin.yaml
k8s/README.md
.github/workflows/ci.yaml
.github/workflows/cd-staging.yaml
.github/workflows/cd-production.yaml
docs/production-readiness-checklist.md
docs/deployment-guide.md
```

### Files to Modify

```
README.md                            # Add cloud deployment section
```

### Files Unchanged (Critical Preservation)

```
docker-compose.dapr.yml              # Local dev unchanged
backend/**/*                         # No code changes
frontend/**/*                        # No code changes
services/reminder-worker/**/*        # No code changes
services/recurrence-worker/**/*      # No code changes
dapr/components/**/*                 # Local Dapr components unchanged
```

---

## Open Questions

- **Q1**: Which managed Kubernetes provider should be used?
  - **Answer**: DigitalOcean Kubernetes (DOKS) is recommended for cost-effectiveness and simplicity. GKE is an alternative for teams already using GCP.

- **Q2**: Which cloud Kafka provider should be used?
  - **Answer**: Confluent Cloud (free tier for development), Aiven, or Redpanda Cloud. All are Kafka-compatible and work with Dapr.

- **Q3**: Should we use Kustomize or Helm for Kubernetes manifests?
  - **Answer**: Kustomize is recommended. It's built into kubectl, simpler for this project size, and doesn't require additional tooling.

- **Q4**: Which container registry should be used?
  - **Answer**: GitHub Container Registry (GHCR) integrates well with GitHub Actions. Docker Hub or cloud-specific registries are alternatives.

- **Q5**: Should observability stack be deployed to the same cluster or external?
  - **Answer**: Same cluster in a separate namespace for simplicity. Managed solutions (Datadog, New Relic) are out of scope for this phase.
