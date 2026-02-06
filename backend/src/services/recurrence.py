"""Recurrence logic for recurring tasks."""
import calendar
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.events.bus import EventBus
from src.events.models import RecurringTaskGeneratedEvent
from src.models.task import Task, TaskStatus

logger = logging.getLogger(__name__)


def _strip_tz(dt: datetime | None) -> datetime | None:
    """Strip timezone info for TIMESTAMP WITHOUT TIME ZONE columns."""
    if dt is None:
        return None
    return dt.replace(tzinfo=None)


def compute_next_due_date(current_due: datetime, pattern: str) -> datetime:
    """Compute the next due date based on recurrence pattern.

    Args:
        current_due: The current due date.
        pattern: One of 'daily', 'weekly', 'monthly'.

    Returns:
        The next due date.
    """
    if pattern == "daily":
        return current_due + timedelta(days=1)
    elif pattern == "weekly":
        return current_due + timedelta(days=7)
    elif pattern == "monthly":
        # Add one calendar month, clamping to last day of target month
        year = current_due.year
        month = current_due.month + 1
        if month > 12:
            month = 1
            year += 1
        # Get last day of target month
        last_day = calendar.monthrange(year, month)[1]
        day = min(current_due.day, last_day)
        return current_due.replace(year=year, month=month, day=day)
    else:
        raise ValueError(f"Unknown recurrence pattern: {pattern}")


async def generate_next_recurring_task(
    completed_task: Task,
    db: AsyncSession,
    event_bus: EventBus,
) -> Optional[Task]:
    """Generate the next instance of a recurring task after completion.

    If the completed task has a recurrence_pattern, creates a new task
    with the next due date. The new task copies title, description,
    priority, tags, and recurrence_pattern from the completed task.

    Args:
        completed_task: The task that was just completed.
        db: Async database session.
        event_bus: Event bus for emitting RecurringTaskGenerated.

    Returns:
        The newly created task, or None if not recurring or on failure.
    """
    if not completed_task.recurrence_pattern:
        return None

    try:
        # Strip timezone info — DB uses TIMESTAMP WITHOUT TIME ZONE
        current_due = _strip_tz(completed_task.due_at)
        next_due = compute_next_due_date(current_due, completed_task.recurrence_pattern)

        # Preserve remind_at offset if it existed
        next_remind_at = None
        current_remind = _strip_tz(completed_task.remind_at)
        if current_remind and current_due:
            offset = current_remind - current_due
            next_remind_at = next_due + offset

        new_task = Task(
            user_id=completed_task.user_id,
            title=completed_task.title,
            description=completed_task.description,
            status=TaskStatus.INCOMPLETE,
            priority=completed_task.priority,
            tags=list(completed_task.tags) if completed_task.tags else [],
            due_at=next_due,
            remind_at=next_remind_at,
            reminder_sent=False,
            recurrence_pattern=completed_task.recurrence_pattern,
            parent_task_id=completed_task.id,
        )

        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)

        try:
            event_bus.emit(RecurringTaskGeneratedEvent(
                new_task_id=new_task.id,
                parent_task_id=completed_task.id,
                user_id=completed_task.user_id,
                title=new_task.title,
                next_due_at=next_due,
                recurrence_pattern=completed_task.recurrence_pattern,
            ))
        except Exception as e:
            logger.warning("Failed to emit RecurringTaskGenerated event: %s", e)

        return new_task

    except Exception as e:
        logger.error("Failed to generate recurring task: %s", e)
        try:
            await db.rollback()
        except Exception:
            pass
        return None
