#!/bin/sh
# =============================================================================
# Frontend Docker Entrypoint Script
# =============================================================================
# Purpose: Container initialization before starting Next.js server
# Used by: docker/frontend/Dockerfile (optional - can be added to CMD)

set -e  # Exit on error

echo "🚀 Starting Todo AI Chatbot Frontend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# =============================================================================
# Environment Variables Validation
# =============================================================================
echo "📋 Checking environment configuration..."

# Check if NEXT_PUBLIC_API_URL is set
if [ -z "$NEXT_PUBLIC_API_URL" ]; then
    echo "⚠️  WARNING: NEXT_PUBLIC_API_URL not set"
    echo "   Using default: http://backend:8000"
    export NEXT_PUBLIC_API_URL="http://backend:8000"
else
    echo "✅ API URL: $NEXT_PUBLIC_API_URL"
fi

# Check NODE_ENV
if [ -z "$NODE_ENV" ]; then
    echo "⚠️  WARNING: NODE_ENV not set, defaulting to production"
    export NODE_ENV="production"
else
    echo "✅ Environment: $NODE_ENV"
fi

echo ""

# =============================================================================
# Display Configuration
# =============================================================================
echo "⚙️  Configuration:"
echo "   - Environment: ${NODE_ENV}"
echo "   - API URL: ${NEXT_PUBLIC_API_URL}"
echo "   - Host: ${HOSTNAME:-0.0.0.0}"
echo "   - Port: ${PORT:-3000}"
echo ""

# =============================================================================
# Start Next.js Server
# =============================================================================
echo "🌟 Starting Next.js server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Execute CMD from Dockerfile (node server.js)
exec "$@"
