#!/bin/bash
# =============================================================================
# Validate Environment - Todo AI Chatbot
# =============================================================================
# Usage: ./scripts/validate-env.sh
# Checks all prerequisites and configuration before deployment
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

ERRORS=0
WARNINGS=0

log_pass() { echo -e "  ${GREEN}✓${NC} $1"; }
log_fail() { echo -e "  ${RED}✗${NC} $1"; ((ERRORS++)); }
log_warn() { echo -e "  ${YELLOW}!${NC} $1"; ((WARNINGS++)); }

check_command() {
    if command -v "$1" &> /dev/null; then
        log_pass "$1 is installed"
        return 0
    else
        log_fail "$1 is not installed"
        return 1
    fi
}

check_docker_running() {
    if docker info > /dev/null 2>&1; then
        log_pass "Docker daemon is running"
        return 0
    else
        log_fail "Docker daemon is not running"
        return 1
    fi
}

check_file_exists() {
    if [ -f "$1" ]; then
        log_pass "File exists: $2"
        return 0
    else
        log_fail "File missing: $2"
        return 1
    fi
}

check_env_var() {
    local file="$1"
    local var="$2"

    if grep -q "^${var}=" "$file" 2>/dev/null; then
        local value=$(grep "^${var}=" "$file" | cut -d'=' -f2-)
        if [ -n "$value" ] && [ "$value" != "your-" ] && [ "$value" != "sk-your-" ]; then
            log_pass "Environment variable set: $var"
            return 0
        else
            log_fail "Environment variable empty or placeholder: $var"
            return 1
        fi
    else
        log_fail "Environment variable missing: $var"
        return 1
    fi
}

echo "=============================================="
echo "  Todo AI Chatbot - Environment Validation"
echo "=============================================="
echo ""

# Check required tools
echo "Checking Required Tools:"
check_command docker
check_command docker-compose || check_command "docker compose"
echo ""

# Check optional tools
echo "Checking Optional Tools (for Kubernetes):"
check_command kubectl || log_warn "kubectl not installed (required for K8s)"
check_command helm || log_warn "helm not installed (required for K8s)"
check_command kind || log_warn "kind not installed (required for local K8s)"
echo ""

# Check Docker daemon
echo "Checking Docker:"
check_docker_running
echo ""

# Check project files
echo "Checking Project Files:"
check_file_exists "$PROJECT_ROOT/docker-compose.yml" "docker-compose.yml"
check_file_exists "$PROJECT_ROOT/docker/backend/Dockerfile" "Backend Dockerfile"
check_file_exists "$PROJECT_ROOT/docker/frontend/Dockerfile" "Frontend Dockerfile"
check_file_exists "$PROJECT_ROOT/helm/backend/Chart.yaml" "Backend Helm chart"
check_file_exists "$PROJECT_ROOT/helm/frontend/Chart.yaml" "Frontend Helm chart"
echo ""

# Check environment file
echo "Checking Environment Configuration:"
ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    log_pass ".env file exists"

    # Check required variables
    check_env_var "$ENV_FILE" "DATABASE_URL"
    check_env_var "$ENV_FILE" "SECRET_KEY"
    check_env_var "$ENV_FILE" "OPENAI_API_KEY"
else
    log_fail ".env file not found"
    echo "  Run: cp .env.example .env && edit .env"
fi
echo ""

# Check Docker images
echo "Checking Docker Images:"
if docker images | grep -q "todo-backend"; then
    log_pass "todo-backend image exists"
else
    log_warn "todo-backend image not built (run: ./scripts/build-images.sh)"
fi

if docker images | grep -q "todo-frontend"; then
    log_pass "todo-frontend image exists"
else
    log_warn "todo-frontend image not built (run: ./scripts/build-images.sh)"
fi
echo ""

# Summary
echo "=============================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    echo "Ready for deployment."
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}$WARNINGS warning(s) found${NC}"
    echo "Deployment may work with limitations."
else
    echo -e "${RED}$ERRORS error(s) found${NC}"
    echo "Please fix the issues before deploying."
    exit 1
fi
echo "=============================================="
