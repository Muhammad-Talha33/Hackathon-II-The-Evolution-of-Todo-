# =============================================================================
# Recurrence Worker - FastAPI Service with DB Access
# =============================================================================
FROM python:3.11-slim

LABEL description="Recurrence Worker for Dapr event consumption"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY *.py .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8002

ENV PYTHONUNBUFFERED=1
ENV APP_PORT=8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
