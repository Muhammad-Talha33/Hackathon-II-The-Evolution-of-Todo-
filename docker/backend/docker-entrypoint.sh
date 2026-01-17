#!/bin/bash
# =============================================================================
# Backend Docker Entrypoint Script
# =============================================================================
# Purpose: Container initialization and health checks before starting server
# Used by: docker/backend/Dockerfile

set -e  # Exit on error

echo "🚀 Starting Todo AI Chatbot Backend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# =============================================================================
# Environment Variables Validation
# =============================================================================
echo "📋 Checking required environment variables..."

required_vars=(
    "OPENAI_API_KEY"
    "DATABASE_URL"
    "SECRET_KEY"
)

missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
        echo "❌ Missing: $var"
    else
        echo "✅ Found: $var"
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ ERROR: Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "💡 Tip: Ensure these are set in:"
    echo "   - Docker Compose: .env file"
    echo "   - Kubernetes: Secrets and ConfigMaps"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi

echo "✅ All required environment variables are set"
echo ""

# =============================================================================
# Optional: Database Connection Test
# =============================================================================
# Uncomment if you want to wait for database availability before starting
# echo "🔌 Testing database connection..."
# python -c "
# import asyncio
# import asyncpg
# import os
# import sys
#
# async def test_connection():
#     try:
#         conn = await asyncpg.connect(os.environ['DATABASE_URL'], timeout=10)
#         await conn.close()
#         print('✅ Database connection successful')
#         return True
#     except Exception as e:
#         print(f'❌ Database connection failed: {e}')
#         return False
#
# if not asyncio.run(test_connection()):
#     sys.exit(1)
# "
# echo ""

# =============================================================================
# Optional: Run Database Migrations
# =============================================================================
# Uncomment if you want to auto-run Alembic migrations on container start
# echo "🔄 Running database migrations..."
# alembic upgrade head
# echo "✅ Migrations complete"
# echo ""

# =============================================================================
# Display Configuration
# =============================================================================
echo "⚙️  Configuration:"
echo "   - Environment: ${ENVIRONMENT:-production}"
echo "   - Host: 0.0.0.0"
echo "   - Port: 8000"
echo "   - Workers: 1 (default)"
echo ""

# =============================================================================
# Start Uvicorn Server
# =============================================================================
echo "🌟 Starting Uvicorn server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Execute CMD from Dockerfile (uvicorn command)
exec "$@"
