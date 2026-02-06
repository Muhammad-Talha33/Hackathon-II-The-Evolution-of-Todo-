"""Reminder checking service."""
import logging
from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.events.bus import EventBus
from src.events.models import TaskReminderDueEvent
from src.models.task import Task, TaskStatus

logger = logging.getLogger(__name__)


async def check_and_emit_reminders(
    user_id: UUID,
    db: AsyncSession,
    event_bus: EventBus,
) -> List[Task]:
    """Check for due reminders and emit TaskReminderDue events.

    Finds tasks where remind_at <= now, reminder_sent is False,
    and status is not complete. For each, emits an event and marks
    reminder_sent = True.

    Args:
        user_id: The user whose tasks to check.
        db: Async database session.
        event_bus: Event bus for emitting TaskReminderDue.

    Returns:
        List of tasks whose reminders were triggered.
    """
    now = datetime.utcnow()

    result = await db.execute(
        select(Task).where(
            Task.user_id == user_id,
            Task.remind_at <= now,
            Task.reminder_sent == False,  # noqa: E712
            Task.status != TaskStatus.COMPLETE,
        )
    )
    tasks = list(result.scalars().all())

    for task in tasks:
        try:
            event_bus.emit(TaskReminderDueEvent(
                task_id=task.id,
                user_id=task.user_id,
                title=task.title,
                remind_at=task.remind_at,
                due_at=task.due_at,
            ))
        except Exception as e:
            logger.warning("Failed to emit TaskReminderDue for task %s: %s", task.id, e)

        task.reminder_sent = True

    if tasks:
        await db.commit()
        # Refresh all affected tasks
        for task in tasks:
            await db.refresh(task)

    return tasks
