#!/bin/bash
# =============================================================================
# Build Docker Images - Todo AI Chatbot
# =============================================================================
# Usage: ./scripts/build-images.sh
# Options:
#   --backend-only   Build only backend image
#   --frontend-only  Build only frontend image
#   --no-cache       Build without Docker cache
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_IMAGE="todo-backend:latest"
FRONTEND_IMAGE="todo-frontend:latest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse arguments
BUILD_BACKEND=true
BUILD_FRONTEND=true
NO_CACHE=""

for arg in "$@"; do
    case $arg in
        --backend-only)
            BUILD_FRONTEND=false
            shift
            ;;
        --frontend-only)
            BUILD_BACKEND=false
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        *)
            ;;
    esac
done

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    log_info "Docker is running"
}

build_backend() {
    log_info "Building backend image: $BACKEND_IMAGE"
    cd "$PROJECT_ROOT"

    START_TIME=$(date +%s)

    if docker build $NO_CACHE -f docker/backend/Dockerfile -t "$BACKEND_IMAGE" ./backend; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        log_info "Backend image built successfully in ${DURATION}s"
    else
        log_error "Backend image build failed"
        exit 1
    fi
}

build_frontend() {
    log_info "Building frontend image: $FRONTEND_IMAGE"
    cd "$PROJECT_ROOT"

    START_TIME=$(date +%s)

    if docker build $NO_CACHE -f docker/frontend/Dockerfile -t "$FRONTEND_IMAGE" ./frontend; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        log_info "Frontend image built successfully in ${DURATION}s"
    else
        log_error "Frontend image build failed"
        exit 1
    fi
}

show_images() {
    log_info "Built images:"
    docker images | grep -E "todo-(backend|frontend)" || true
}

# Main execution
echo "=============================================="
echo "  Todo AI Chatbot - Docker Image Builder"
echo "=============================================="

check_docker

if [ "$BUILD_BACKEND" = true ]; then
    build_backend
fi

if [ "$BUILD_FRONTEND" = true ]; then
    build_frontend
fi

echo ""
show_images

echo ""
log_info "Build complete!"
echo ""
echo "Next steps:"
echo "  - Docker Compose: docker-compose up -d"
echo "  - Kubernetes:     kind load docker-image $BACKEND_IMAGE --name todo-local"
echo "                    kind load docker-image $FRONTEND_IMAGE --name todo-local"
