# Todo AI Chatbot

An AI-powered todo management application with intelligent chatbot interface, built with FastAPI backend and Next.js frontend.

## Features

- Add tasks with titles and descriptions
- View all tasks with status indicators
- Mark tasks as complete/incomplete
- Update task details
- Delete tasks
- Interactive menu-driven interface

## Requirements

- Python 3.13+
- No external dependencies required for Phase I

## Setup

1. Clone this repository
2. Navigate to the project directory
3. Run the application:
   ```bash
   python src/main.py
   ```

## Usage

The application presents an interactive menu with the following options:

1. **Add Task** - Create a new task with title and optional description
2. **View Tasks** - Display all tasks with their status (✓ complete, ✗ incomplete)
3. **Mark Complete** - Toggle task completion status
4. **Update Task** - Modify task title and/or description
5. **Delete Task** - Remove a task from the list
6. **Exit** - Close the application

### Example Session

```
Welcome to Todo Console Application! 🎯

========================================
TODO CONSOLE APPLICATION
========================================
1. Add Task
2. View Tasks
3. Mark Complete
4. Update Task
5. Delete Task
6. Exit
========================================
Enter your choice (1-6): 1

--- Add New Task ---
Enter task title: Buy groceries
Enter task description (optional): Get milk, eggs, and bread
✓ Task added successfully! [ID: 1]

Enter your choice (1-6): 2

--- Task List ---
[1] ✗ Buy groceries
    Description: Get milk, eggs, and bread

Enter your choice (1-6): 3

--- Mark Task Complete ---
Enter task ID to mark complete: 1
✓ Task 1 marked as complete

Enter your choice (1-6): 6

========================================
Thank you for using Todo Console App!
Goodbye! 👋
========================================
```

## Project Structure

```
src/
├── __init__.py
├── main.py              # Entry point and menu loop
├── task_manager.py      # Task CRUD operations
├── utils.py             # Validation and formatting utilities
└── models/
    ├── __init__.py
    └── task.py          # Task data structure
tests/
└── __init__.py
```

## Development

This project follows:
- PEP 8 style guidelines
- Type hints for all function signatures
- Comprehensive docstrings
- Separation of concerns architecture

For implementation details, see the design documents in `specs/001-todo-console-app/`.

## Deployment (Phase IV)

This project supports **dual-track deployment strategy**:

### Track A: Docker Compose (Immediate Deployment)

Deploy the full application stack locally using Docker Compose:

**Prerequisites**: Docker Desktop

**Quick Start**:
```bash
# 1. Create secrets file
cp .env.example .env
# Edit .env with your actual secrets (OPENAI_API_KEY, DATABASE_URL, etc.)

# 2. Build and start services
docker-compose up -d

# 3. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Documentation**: See `docs/deployment/docker-compose.md` for complete guide

---

### Track B: Kubernetes (Learning & Production-Ready)

Deploy to local Kubernetes cluster using kind and Helm:

**Prerequisites**: Docker Desktop, kubectl, Helm, kind

**Quick Start**:
```bash
# 1. Create kind cluster
kind create cluster --name todo-local

# 2. Build and load images
docker build -f docker/backend/Dockerfile -t todo-backend:latest ./backend
docker build -f docker/frontend/Dockerfile -t todo-frontend:latest ./frontend
kind load docker-image todo-backend:latest todo-frontend:latest --name todo-local

# 3. Create secrets
kubectl create secret generic todo-backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-your-key' \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=SECRET_KEY='your-secret'

# 4. Deploy with Helm
helm install todo-backend ./helm/backend
helm install todo-frontend ./helm/frontend

# 5. Access application
# Via port-forward: kubectl port-forward svc/todo-frontend 3000:3000
# Via NodePort: http://localhost:30080 (requires kind port mapping)
```

**Documentation**: See `docs/deployment/kubernetes.md` for complete guide

---

### Track C: Event-Driven Stack with Dapr + Kafka (Phase V Part B)

Run the full event-driven architecture locally with Dapr sidecars and Redpanda (Kafka-compatible):

**Prerequisites**: Docker Desktop

**Quick Start**:
```bash
# 1. Create secrets file (if not done)
cp .env.example .env
# Edit .env with your actual secrets

# 2. Start the event-driven stack
docker-compose -f docker-compose.dapr.yml up -d

# 3. Access services
# Frontend:          http://localhost:3000
# Backend API:       http://localhost:8000
# Redpanda Console:  http://localhost:8080
# API Docs:          http://localhost:8000/docs
```

**Architecture**:
```
Frontend → Backend API → Dapr Sidecar → Redpanda (Kafka)
                                              │
                           ┌──────────────────┼──────────────────┐
                           ▼                  ▼                  ▼
                    Reminder Worker    Recurrence Worker    (Future Services)
                    (logs delivery)   (creates next task)
```

**Services**:

| Service | Port | Purpose |
|---------|------|---------|
| Backend + Dapr sidecar | 8000 | API + event publishing |
| Frontend | 3000 | Next.js UI |
| Redpanda | 19092, 8080 | Kafka broker + Console |
| Reminder Worker + sidecar | 8001 | Consume TaskReminderDue events |
| Recurrence Worker + sidecar | 8002 | Consume RecurringTaskGenerated events |
| Redis | 6379 | Dapr state store (optional) |

**Verify Event Flow**:
1. Create a task via the API or frontend
2. Open Redpanda Console at http://localhost:8080
3. Navigate to Topics → `tasks` → Messages
4. Verify `TaskCreated` event appears with correct payload

**Troubleshooting**:
```bash
# Check all container status
docker-compose -f docker-compose.dapr.yml ps

# View backend Dapr sidecar logs
docker logs todo-backend-dapr

# View worker logs
docker logs reminder-worker
docker logs recurrence-worker

# Restart Dapr sidecars after component changes
docker-compose -f docker-compose.dapr.yml restart todo-backend-dapr reminder-worker-dapr recurrence-worker-dapr

# Full teardown
docker-compose -f docker-compose.dapr.yml down -v
```

**Key Files**:
- `docker-compose.dapr.yml` - Full Dapr stack compose file
- `dapr/components/` - Dapr component configurations (pubsub, statestore, secrets, cron)
- `services/reminder-worker/` - Reminder event consumer
- `services/recurrence-worker/` - Recurring task generator
- `backend/src/events/bus.py` - EventBus (publishes via Dapr)
- `backend/src/events/dapr_client.py` - Dapr HTTP pub/sub client

---

### Deployment Resources

| Guide | Description |
|-------|-------------|
| [Prerequisites](docs/deployment/prerequisites.md) | Required tools and installation |
| [Docker Compose Guide](docs/deployment/docker-compose.md) | Complete Track A deployment guide |
| [Kubernetes Guide](docs/deployment/kubernetes.md) | Complete Track B (kind + Helm) guide |
| [Troubleshooting](docs/deployment/troubleshooting.md) | Common issues and solutions |
| [Secrets Management](docs/deployment/secrets-management.md) | Secret rotation and security |
| [Validation Checklist](docs/deployment/validation.md) | Deployment verification checklist |
| [AI Tools](docs/deployment/ai-tools.md) | kubectl-ai and kagent usage |
| [Architecture](docs/architecture/containerization.md) | Container architecture decisions |
| [Quick Start](specs/004-phase4-local-k8s/quickstart.md) | Step-by-step deployment |

### Automation Scripts

| Script | Description |
|--------|-------------|
| `scripts/build-images.sh` / `.ps1` | Build Docker images for both services |
| `scripts/deploy-compose.sh` / `.ps1` | Deploy via Docker Compose (Track A) |
| `scripts/deploy-k8s.sh` / `.ps1` | Deploy via kind + Helm (Track B) |
| `scripts/validate-env.sh` | Check prerequisites and environment |

---

## License

This is a learning project for demonstrating Spec-Driven Development principles.
