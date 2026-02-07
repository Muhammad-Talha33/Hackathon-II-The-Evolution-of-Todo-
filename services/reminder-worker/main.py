"""Reminder Worker - Consumes TaskReminderDue events via Dapr pub/sub.

Subscribes to the 'tasks' topic and processes TaskReminderDue events.
Logs reminder delivery as a stub for future notification integration.
"""
import logging
import os
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("reminder-worker")

app = FastAPI(
    title="Reminder Worker",
    description="Dapr event consumer for task reminders",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Dapr Subscription Registration
# ---------------------------------------------------------------------------

@app.get("/dapr/subscribe")
async def subscribe() -> List[Dict[str, Any]]:
    """Return Dapr subscription configuration.

    Tells the Dapr sidecar which topics this worker subscribes to
    and which route handles delivered events.
    """
    return [
        {
            "pubsubname": "taskpubsub",
            "topic": "tasks",
            "route": "/events/task-reminder-due",
        }
    ]


# ---------------------------------------------------------------------------
# Event Handler
# ---------------------------------------------------------------------------

@app.post("/events/task-reminder-due")
async def handle_task_reminder_due(request: Request) -> JSONResponse:
    """Handle incoming events from the 'tasks' topic.

    Filters for TaskReminderDue events and logs delivery.
    All other event types are acknowledged and dropped silently.
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.error("[ReminderWorker] Failed to parse event body: %s", e)
        return JSONResponse(content={"status": "DROP"}, status_code=200)

    # Extract event data - Dapr may wrap in CloudEvents envelope
    event_data = body.get("data", body) if isinstance(body, dict) else body

    if not isinstance(event_data, dict):
        logger.warning("[ReminderWorker] Invalid event data format")
        return JSONResponse(content={"status": "DROP"}, status_code=200)

    event_type = event_data.get("event_type", "")

    # Filter: only process TaskReminderDue events
    if event_type != "TaskReminderDue":
        # Silently acknowledge non-matching events
        return JSONResponse(content={"status": "SUCCESS"}, status_code=200)

    # Extract reminder details
    task_id = event_data.get("task_id", "unknown")
    title = event_data.get("title", "unknown")
    user_id = event_data.get("user_id", "unknown")
    remind_at = event_data.get("remind_at", "unknown")
    due_at = event_data.get("due_at", "N/A")

    # Log the reminder delivery (stub for future notification)
    logger.info(
        "[ReminderWorker] Delivered reminder for task %s: %s "
        "(user=%s, remind_at=%s, due_at=%s)",
        task_id,
        title,
        user_id,
        remind_at,
        due_at,
    )

    return JSONResponse(content={"status": "SUCCESS"}, status_code=200)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "reminder-worker"}


# ---------------------------------------------------------------------------
# Startup / Shutdown
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup() -> None:
    """Log startup."""
    port = os.environ.get("APP_PORT", "8001")
    logger.info("[ReminderWorker] Starting on port %s", port)
    logger.info("[ReminderWorker] Subscribed to topic: tasks (TaskReminderDue)")


@app.on_event("shutdown")
async def shutdown() -> None:
    """Log shutdown."""
    logger.info("[ReminderWorker] Shutting down")
