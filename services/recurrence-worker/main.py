"""Recurrence Worker - Consumes RecurringTaskGenerated events via Dapr pub/sub.

Subscribes to the 'tasks' topic and processes RecurringTaskGenerated events.
Creates the next task instance in the database with idempotency checks.
"""
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from database import AsyncSessionLocal
from models import Task, TaskStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("recurrence-worker")

app = FastAPI(
    title="Recurrence Worker",
    description="Dapr event consumer for recurring task generation",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Dapr Subscription Registration
# ---------------------------------------------------------------------------

@app.get("/dapr/subscribe")
async def subscribe() -> List[Dict[str, Any]]:
    """Return Dapr subscription configuration."""
    return [
        {
            "pubsubname": "taskpubsub",
            "topic": "tasks",
            "route": "/events/recurring-task-generated",
        }
    ]


# ---------------------------------------------------------------------------
# Event Handler
# ---------------------------------------------------------------------------

@app.post("/events/recurring-task-generated")
async def handle_recurring_task_generated(request: Request) -> JSONResponse:
    """Handle incoming events from the 'tasks' topic.

    Filters for RecurringTaskGenerated events and creates the next
    task instance in the database. Implements idempotency by checking
    for existing tasks with the same parent_task_id and due_at.
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.error("[RecurrenceWorker] Failed to parse event body: %s", e)
        return JSONResponse(content={"status": "DROP"}, status_code=200)

    # Extract event data - Dapr may wrap in CloudEvents envelope
    event_data = body.get("data", body) if isinstance(body, dict) else body

    if not isinstance(event_data, dict):
        logger.warning("[RecurrenceWorker] Invalid event data format")
        return JSONResponse(content={"status": "DROP"}, status_code=200)

    event_type = event_data.get("event_type", "")

    # Filter: only process RecurringTaskGenerated events
    if event_type != "RecurringTaskGenerated":
        return JSONResponse(content={"status": "SUCCESS"}, status_code=200)

    # Extract event fields
    try:
        parent_task_id = UUID(event_data["parent_task_id"])
        user_id = UUID(event_data["user_id"])
        title = event_data["title"]
        next_due_at_str = event_data["next_due_at"]
        recurrence_pattern = event_data["recurrence_pattern"]
    except (KeyError, ValueError) as e:
        logger.error(
            "[RecurrenceWorker] Invalid event payload: %s | data=%s", e, event_data
        )
        return JSONResponse(content={"status": "DROP"}, status_code=200)

    # Parse next_due_at
    try:
        if isinstance(next_due_at_str, str):
            next_due_at = datetime.fromisoformat(
                next_due_at_str.replace("Z", "+00:00")
            ).replace(tzinfo=None)
        else:
            next_due_at = next_due_at_str
    except (ValueError, AttributeError) as e:
        logger.error("[RecurrenceWorker] Invalid next_due_at: %s", e)
        return JSONResponse(content={"status": "DROP"}, status_code=200)

    # Process in database
    try:
        async with AsyncSessionLocal() as session:
            # Idempotency check: skip if task already exists
            existing = await session.execute(
                select(Task).where(
                    Task.parent_task_id == parent_task_id,
                    Task.due_at == next_due_at,
                )
            )
            if existing.scalar_one_or_none() is not None:
                logger.info(
                    "[RecurrenceWorker] Task already exists for parent=%s due_at=%s - skipping",
                    parent_task_id,
                    next_due_at,
                )
                return JSONResponse(content={"status": "SUCCESS"}, status_code=200)

            # Look up parent task for additional fields
            parent_result = await session.execute(
                select(Task).where(Task.id == parent_task_id)
            )
            parent_task: Optional[Task] = parent_result.scalar_one_or_none()

            # Build new task from event + parent fields
            description = parent_task.description if parent_task else None
            priority = parent_task.priority if parent_task else "medium"
            tags = list(parent_task.tags) if parent_task and parent_task.tags else []

            # Compute remind_at offset if parent had one
            remind_at = None
            if parent_task and parent_task.remind_at and parent_task.due_at:
                offset = parent_task.remind_at - parent_task.due_at
                remind_at = next_due_at + offset

            new_task = Task(
                id=uuid4(),
                user_id=user_id,
                title=title,
                description=description,
                status=TaskStatus.INCOMPLETE,
                priority=priority,
                tags=tags,
                due_at=next_due_at,
                remind_at=remind_at,
                reminder_sent=False,
                recurrence_pattern=recurrence_pattern,
                parent_task_id=parent_task_id,
            )

            session.add(new_task)
            await session.commit()

            logger.info(
                "[RecurrenceWorker] Created next task %s for parent=%s "
                "(title=%s, due_at=%s, pattern=%s)",
                new_task.id,
                parent_task_id,
                title,
                next_due_at,
                recurrence_pattern,
            )

            return JSONResponse(content={"status": "SUCCESS"}, status_code=200)

    except Exception as e:
        logger.error(
            "[RecurrenceWorker] Database error creating task: %s", e, exc_info=True
        )
        return JSONResponse(content={"status": "RETRY"}, status_code=200)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "recurrence-worker"}


# ---------------------------------------------------------------------------
# Startup / Shutdown
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup() -> None:
    """Log startup."""
    port = os.environ.get("APP_PORT", "8002")
    db_url = os.environ.get("DATABASE_URL", "not-set")
    # Mask the password in the connection string for logging
    masked = db_url.split("@")[1] if "@" in db_url else "configured"
    logger.info("[RecurrenceWorker] Starting on port %s", port)
    logger.info("[RecurrenceWorker] Database: %s", masked)
    logger.info(
        "[RecurrenceWorker] Subscribed to topic: tasks (RecurringTaskGenerated)"
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    """Log shutdown."""
    logger.info("[RecurrenceWorker] Shutting down")
