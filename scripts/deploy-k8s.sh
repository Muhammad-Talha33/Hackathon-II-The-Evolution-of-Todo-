#!/bin/bash
# =============================================================================
# Deploy to Kubernetes via Helm - Todo AI Chatbot
# =============================================================================
# Usage: ./scripts/deploy-k8s.sh [up|down|status]
# Options:
#   --cluster-name NAME   Kind cluster name (default: todo-local)
#   --create-cluster      Create kind cluster if not exists
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLUSTER_NAME="todo-local"
CREATE_CLUSTER=false

# Parse arguments
COMMAND=""
for arg in "$@"; do
    case $arg in
        --cluster-name=*)
            CLUSTER_NAME="${arg#*=}"
            shift
            ;;
        --create-cluster)
            CREATE_CLUSTER=true
            shift
            ;;
        up|down|status)
            COMMAND="$arg"
            ;;
        *)
            ;;
    esac
done

COMMAND="${COMMAND:-up}"

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    # Check Docker
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Install it first."
        exit 1
    fi

    # Check helm
    if ! command -v helm &> /dev/null; then
        log_error "Helm not found. Install it first."
        exit 1
    fi

    # Check kind
    if ! command -v kind &> /dev/null; then
        log_error "kind not found. Install it first."
        exit 1
    fi

    log_info "Prerequisites check passed"
}

create_cluster() {
    if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
        log_info "Cluster '$CLUSTER_NAME' already exists"
        return
    fi

    log_info "Creating kind cluster: $CLUSTER_NAME"

    # Create cluster with port mapping for NodePort
    cat > /tmp/kind-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 30080
        protocol: TCP
      - containerPort: 30000
        hostPort: 30000
        protocol: TCP
EOF

    kind create cluster --name "$CLUSTER_NAME" --config /tmp/kind-config.yaml
    rm /tmp/kind-config.yaml

    log_info "Cluster created successfully"
}

load_images() {
    log_info "Loading Docker images into kind cluster..."

    # Check if images exist
    if ! docker images | grep -q "todo-backend"; then
        log_error "todo-backend:latest not found. Run build-images.sh first."
        exit 1
    fi

    if ! docker images | grep -q "todo-frontend"; then
        log_error "todo-frontend:latest not found. Run build-images.sh first."
        exit 1
    fi

    kind load docker-image todo-backend:latest --name "$CLUSTER_NAME"
    kind load docker-image todo-frontend:latest --name "$CLUSTER_NAME"

    log_info "Images loaded successfully"
}

deploy_backend() {
    log_info "Deploying backend..."
    cd "$PROJECT_ROOT"

    # Check for values-local.yaml
    if [ -f "helm/backend/values-local.yaml" ]; then
        helm upgrade --install todo-backend ./helm/backend -f helm/backend/values-local.yaml
    else
        log_warn "values-local.yaml not found. Using default values."
        helm upgrade --install todo-backend ./helm/backend
    fi
}

deploy_frontend() {
    log_info "Deploying frontend..."
    cd "$PROJECT_ROOT"

    if [ -f "helm/frontend/values-local.yaml" ]; then
        helm upgrade --install todo-frontend ./helm/frontend -f helm/frontend/values-local.yaml
    else
        helm upgrade --install todo-frontend ./helm/frontend
    fi
}

deploy_up() {
    if [ "$CREATE_CLUSTER" = true ]; then
        create_cluster
    fi

    # Set kubectl context
    kubectl config use-context "kind-$CLUSTER_NAME" 2>/dev/null || true

    load_images
    deploy_backend
    deploy_frontend

    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=120s deployment/todo-backend || true
    kubectl wait --for=condition=available --timeout=120s deployment/todo-frontend || true

    show_status
}

deploy_down() {
    log_info "Uninstalling Helm releases..."

    helm uninstall todo-frontend 2>/dev/null || log_warn "todo-frontend not found"
    helm uninstall todo-backend 2>/dev/null || log_warn "todo-backend not found"

    log_info "Releases uninstalled"
}

show_status() {
    log_info "Deployment Status:"
    echo ""

    echo "Helm Releases:"
    helm list

    echo ""
    echo "Deployments:"
    kubectl get deployments

    echo ""
    echo "Pods:"
    kubectl get pods

    echo ""
    echo "Services:"
    kubectl get services

    echo ""
    log_info "Access:"
    echo "  Backend:  kubectl port-forward svc/todo-backend 8000:8000"
    echo "  Frontend: http://localhost:30080 (if NodePort configured)"
    echo "            kubectl port-forward svc/todo-frontend 3000:3000"
}

show_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  up       Deploy to Kubernetes"
    echo "  down     Remove deployment"
    echo "  status   Show deployment status"
    echo ""
    echo "Options:"
    echo "  --cluster-name=NAME   Kind cluster name (default: todo-local)"
    echo "  --create-cluster      Create kind cluster if not exists"
    echo ""
    echo "Examples:"
    echo "  $0 up --create-cluster    # Create cluster and deploy"
    echo "  $0 down                   # Remove deployment"
    echo "  $0 status                 # Show status"
}

# Main
check_prerequisites

case "$COMMAND" in
    up)
        deploy_up
        ;;
    down)
        deploy_down
        ;;
    status)
        show_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
