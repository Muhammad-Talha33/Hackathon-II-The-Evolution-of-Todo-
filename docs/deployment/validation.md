# Deployment Validation Checklist

**Purpose**: Verify deployment is complete and functional for both Track A (Docker Compose) and Track B (Kubernetes/Helm)

---

## Pre-Deployment Checks

- [ ] Docker Desktop is installed and running (`docker info`)
- [ ] `.env` file created from `.env.example` with actual secrets
- [ ] Docker images built successfully:
  - [ ] `docker build -f docker/backend/Dockerfile -t todo-backend:latest ./backend`
  - [ ] `docker build -f docker/frontend/Dockerfile -t todo-frontend:latest ./frontend`

---

## Track A: Docker Compose Validation

### Backend Service

- [ ] Start backend: `docker-compose up backend -d`
- [ ] Container running: `docker-compose ps` shows backend as "Up"
- [ ] Health check passes: `curl http://localhost:8000/health` returns `{"status": "healthy"}`
- [ ] API docs accessible: `curl http://localhost:8000/docs` returns HTML
- [ ] Logs clean: `docker-compose logs backend` shows successful startup

### Frontend Service

- [ ] Start frontend: `docker-compose up frontend -d`
- [ ] Container running: `docker-compose ps` shows frontend as "Up"
- [ ] Frontend accessible: `curl http://localhost:3000` returns HTML
- [ ] Logs clean: `docker-compose logs frontend` shows successful startup

### Full Stack

- [ ] Both services running: `docker-compose ps` shows both as "Up"
- [ ] Frontend loads in browser: http://localhost:3000
- [ ] Chatbot UI functional: Can send messages and receive AI responses
- [ ] Backend API reachable from frontend: No CORS or connection errors in browser console

### Cleanup

- [ ] Clean shutdown: `docker-compose down -v`
- [ ] No orphan containers: `docker ps -a` shows no todo containers

---

## Track B: Kubernetes (kind + Helm) Validation

### Prerequisites

- [ ] kubectl installed: `kubectl version --client`
- [ ] Helm installed: `helm version`
- [ ] kind installed: `kind version`

### Cluster Setup

- [ ] kind cluster created: `kind create cluster --name todo-local --config kind-config.yaml`
- [ ] Cluster running: `kubectl cluster-info --context kind-todo-local`
- [ ] Node ready: `kubectl get nodes` shows Ready status

### Image Loading

- [ ] Backend image loaded: `kind load docker-image todo-backend:latest --name todo-local`
- [ ] Frontend image loaded: `kind load docker-image todo-frontend:latest --name todo-local`

### Backend Deployment

- [ ] Helm install: `helm install todo-backend ./helm/backend -f helm/backend/values-local.yaml`
- [ ] Deployment ready: `kubectl get deployments` shows todo-backend 1/1
- [ ] Pod running: `kubectl get pods -l app=todo-backend` shows Running
- [ ] Service created: `kubectl get svc todo-backend` shows ClusterIP
- [ ] Health check: `kubectl port-forward svc/todo-backend 8000:8000` then `curl http://localhost:8000/health`
- [ ] Secrets secure: `kubectl describe pod` shows secretRef but not values

### Frontend Deployment

- [ ] Helm install: `helm install todo-frontend ./helm/frontend -f helm/frontend/values-local.yaml`
- [ ] Deployment ready: `kubectl get deployments` shows todo-frontend 1/1
- [ ] Pod running: `kubectl get pods -l app=todo-frontend` shows Running
- [ ] Service created: `kubectl get svc todo-frontend` shows NodePort
- [ ] Frontend accessible: http://localhost:30080 loads UI
- [ ] Backend connectivity: Chatbot can communicate with backend API

### Helm Lifecycle

- [ ] Upgrade works: `helm upgrade todo-backend ./helm/backend --set replicaCount=2`
- [ ] Scaling verified: `kubectl get pods -l app=todo-backend` shows 2 pods
- [ ] Rollback works: `helm rollback todo-backend`
- [ ] Release list: `helm list` shows both releases as "deployed"
- [ ] Uninstall clean: `helm uninstall todo-backend todo-frontend`
- [ ] Resources removed: `kubectl get all` shows no todo resources

### Cleanup

- [ ] Delete cluster: `kind delete cluster --name todo-local`

---

## Phase III Functionality Preservation

- [ ] `git status backend/ frontend/` shows no modifications
- [ ] Todo creation works identically to Phase III
- [ ] Task completion/toggle works
- [ ] AI chatbot responds to queries
- [ ] All existing features function as expected

---

## Performance Validation

- [ ] Backend image build time: < 5 minutes
- [ ] Frontend image build time: < 5 minutes
- [ ] Container startup time: < 60 seconds
- [ ] Application response times match Phase III local dev performance

---

## Validation Summary

| Check | Track A | Track B |
|-------|---------|---------|
| Services start | | |
| Health checks pass | | |
| Frontend loads | | |
| Backend API works | | |
| Full stack functional | | |
| Clean shutdown | | |
| Phase III unchanged | | |
| Performance meets spec | | |

**Date validated**: ________________
**Validated by**: ________________
**Notes**: ________________
