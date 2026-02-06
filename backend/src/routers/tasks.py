"""Task CRUD router with all task management endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, case, or_, cast
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.types import Text
from sqlalchemy.sql.expression import nullslast, nullsfirst
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.database import get_db
from src.models.user import User
from src.models.task import Task, TaskStatus
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from src.dependencies.auth import get_current_user
from src.events.bus import EventBus, get_event_bus
from src.events.models import (
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
)
from src.services.recurrence import generate_next_recurring_task
from src.services.reminders import check_and_emit_reminders

logger = logging.getLogger(__name__)

router = APIRouter()


def _strip_tz(dt: datetime | None) -> datetime | None:
    """Strip timezone info from a datetime for TIMESTAMP WITHOUT TIME ZONE columns."""
    if dt is None:
        return None
    return dt.replace(tzinfo=None)


# --- check-reminders MUST be before /{task_id} routes ---

@router.post("/check-reminders", response_model=List[TaskResponse])
async def check_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Check for due reminders and emit events.

    Returns list of tasks whose reminders were just triggered.
    """
    tasks = await check_and_emit_reminders(current_user.id, db, event_bus)
    return tasks


# --- Standard CRUD endpoints ---

@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all tasks for the current user with optional filter, sort, and search.

    Query params:
        status: Filter by 'incomplete', 'complete', or 'overdue'
        priority: Filter by 'low', 'medium', or 'high'
        tag: Filter tasks containing this tag
        q: Search title and description (case-insensitive)
        sort_by: Sort field - 'created_at' (default), 'due_date', 'priority'
        order: Sort order - 'asc' or 'desc' (default)
    """
    # Base query: user-scoped
    query = select(Task).where(Task.user_id == current_user.id)

    # --- Filtering ---
    if status_filter == "incomplete":
        query = query.where(Task.status == TaskStatus.INCOMPLETE)
    elif status_filter == "complete":
        query = query.where(Task.status == TaskStatus.COMPLETE)
    elif status_filter == "overdue":
        now = datetime.utcnow()
        query = query.where(
            Task.status == TaskStatus.INCOMPLETE,
            Task.due_at < now,
            Task.due_at.isnot(None),
        )

    if priority:
        query = query.where(Task.priority == priority)

    if tag:
        # PostgreSQL: check if tag is contained in the ARRAY column
        # Cast to text[] to match the database column type (text[] vs varchar[])
        query = query.where(Task.tags.contains(cast([tag], PG_ARRAY(Text))))

    # --- Search ---
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
            )
        )

    # --- Sorting ---
    if sort_by == "due_date":
        sort_col = Task.due_at
        if order == "asc":
            query = query.order_by(nullslast(sort_col.asc()))
        else:
            query = query.order_by(nullsfirst(sort_col.desc()))
    elif sort_by == "priority":
        priority_order = case(
            (Task.priority == "high", 1),
            (Task.priority == "medium", 2),
            else_=3,
        )
        if order == "asc":
            query = query.order_by(priority_order.asc())
        else:
            query = query.order_by(priority_order.desc())
    else:
        # Default: created_at
        if order == "asc":
            query = query.order_by(Task.created_at.asc())
        else:
            query = query.order_by(Task.created_at.desc())

    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Create a new task for the current user.
    """
    new_task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        status=TaskStatus.INCOMPLETE,
        priority=task_data.priority or "medium",
        tags=task_data.tags or [],
        due_at=_strip_tz(task_data.due_at),
        remind_at=_strip_tz(task_data.remind_at),
        recurrence_pattern=task_data.recurrence_pattern,
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # Emit event (best-effort)
    try:
        event_bus.emit(TaskCreatedEvent(
            task_id=new_task.id,
            user_id=new_task.user_id,
            title=new_task.title,
            priority=new_task.priority,
            tags=list(new_task.tags) if new_task.tags else [],
            due_at=new_task.due_at,
            recurrence_pattern=new_task.recurrence_pattern,
            created_at=new_task.created_at,
        ))
    except Exception as e:
        logger.warning("Failed to emit TaskCreated event: %s", e)

    return new_task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single task by ID.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Update a task by ID.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Track which fields change for the event
    updated_fields = []

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title
        updated_fields.append("title")
    if task_data.description is not None:
        task.description = task_data.description
        updated_fields.append("description")
    if task_data.due_at is not None:
        task.due_at = _strip_tz(task_data.due_at)
        updated_fields.append("due_at")
    if task_data.remind_at is not None:
        task.remind_at = _strip_tz(task_data.remind_at)
        updated_fields.append("remind_at")
    if task_data.priority is not None:
        task.priority = task_data.priority
        updated_fields.append("priority")
    if task_data.tags is not None:
        task.tags = task_data.tags
        updated_fields.append("tags")
    if task_data.recurrence_pattern is not None:
        task.recurrence_pattern = task_data.recurrence_pattern
        updated_fields.append("recurrence_pattern")

    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    # Emit event (best-effort)
    if updated_fields:
        try:
            event_bus.emit(TaskUpdatedEvent(
                task_id=task.id,
                user_id=task.user_id,
                updated_fields=updated_fields,
                updated_at=task.updated_at,
            ))
        except Exception as e:
            logger.warning("Failed to emit TaskUpdated event: %s", e)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Delete a task by ID.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Capture details before deletion
    task_title = task.title
    task_user_id = task.user_id

    await db.delete(task)
    await db.commit()

    # Emit event (best-effort)
    try:
        event_bus.emit(TaskDeletedEvent(
            task_id=task_id,
            user_id=task_user_id,
            title=task_title,
        ))
    except Exception as e:
        logger.warning("Failed to emit TaskDeleted event: %s", e)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Toggle task completion status (incomplete <-> complete).
    If completing a recurring task, generates the next instance.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Toggle status
    if task.status == TaskStatus.INCOMPLETE:
        task.status = TaskStatus.COMPLETE
        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        # Emit TaskCompleted event (best-effort)
        try:
            was_overdue = (
                task.due_at is not None and task.due_at < datetime.utcnow()
            )
            event_bus.emit(TaskCompletedEvent(
                task_id=task.id,
                user_id=task.user_id,
                title=task.title,
                completed_at=task.updated_at,
                had_recurrence=task.recurrence_pattern is not None,
                was_overdue=was_overdue,
            ))
        except Exception as e:
            logger.warning("Failed to emit TaskCompleted event: %s", e)

        # Generate next recurring task (best-effort)
        try:
            await generate_next_recurring_task(task, db, event_bus)
        except Exception as e:
            logger.warning("Failed to generate recurring task: %s", e)

    else:
        task.status = TaskStatus.INCOMPLETE
        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        # Emit TaskUpdated event for status change (best-effort)
        try:
            event_bus.emit(TaskUpdatedEvent(
                task_id=task.id,
                user_id=task.user_id,
                updated_fields=["status"],
                updated_at=task.updated_at,
            ))
        except Exception as e:
            logger.warning("Failed to emit TaskUpdated event: %s", e)

    return task
