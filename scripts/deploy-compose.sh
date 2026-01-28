#!/bin/bash
# =============================================================================
# Deploy via Docker Compose - Todo AI Chatbot
# =============================================================================
# Usage: ./scripts/deploy-compose.sh [up|down|restart|logs|status]
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    # Check Docker
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi

    # Check .env file
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_error ".env file not found. Copy .env.example to .env and fill in secrets."
        exit 1
    fi

    # Check Docker Compose file
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "docker-compose.yml not found"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

deploy_up() {
    log_info "Starting Docker Compose services..."
    cd "$PROJECT_ROOT"

    docker-compose up -d

    log_info "Waiting for services to be healthy..."
    sleep 10

    show_status
}

deploy_down() {
    log_info "Stopping Docker Compose services..."
    cd "$PROJECT_ROOT"

    docker-compose down

    log_info "Services stopped"
}

deploy_restart() {
    log_info "Restarting Docker Compose services..."
    deploy_down
    deploy_up
}

show_logs() {
    log_info "Showing logs (Ctrl+C to exit)..."
    cd "$PROJECT_ROOT"

    docker-compose logs -f
}

show_status() {
    log_info "Service Status:"
    cd "$PROJECT_ROOT"

    docker-compose ps

    echo ""
    log_info "Health Checks:"

    # Check backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "  Backend:  ${GREEN}HEALTHY${NC} (http://localhost:8000)"
    else
        echo -e "  Backend:  ${RED}NOT READY${NC}"
    fi

    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "  Frontend: ${GREEN}HEALTHY${NC} (http://localhost:3000)"
    else
        echo -e "  Frontend: ${RED}NOT READY${NC}"
    fi
}

show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  up       Start all services"
    echo "  down     Stop all services"
    echo "  restart  Restart all services"
    echo "  logs     Show service logs"
    echo "  status   Show service status"
    echo ""
    echo "Examples:"
    echo "  $0 up      # Start the application"
    echo "  $0 logs    # View logs"
    echo "  $0 down    # Stop the application"
}

# Main
case "${1:-up}" in
    up)
        check_prerequisites
        deploy_up
        ;;
    down)
        deploy_down
        ;;
    restart)
        check_prerequisites
        deploy_restart
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
