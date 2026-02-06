"""MCP Server initialization for Task Management tools."""
import logging
from typing import Optional, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID
from datetime import datetime
from agents import function_tool, RunContextWrapper

from src.models.task import Task, TaskStatus

logger = logging.getLogger(__name__)

# Global session placeholder - will be injected at runtime
_db_session: Optional[AsyncSession] = None


def set_session(session: AsyncSession):
    """Set the database session for the MCP server."""
    global _db_session
    _db_session = session


def get_session() -> AsyncSession:
    """Get the current database session."""
    if _db_session is None:
        raise RuntimeError("Database session not initialized. Call set_session() first.")
    return _db_session


def _task_to_dict(task: Task) -> dict:
    """Serialize a Task to a response dictionary including all fields."""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority,
        "tags": list(task.tags) if task.tags else [],
        "due_at": task.due_at.isoformat() if task.due_at else None,
        "remind_at": task.remind_at.isoformat() if task.remind_at else None,
        "recurrence_pattern": task.recurrence_pattern,
        "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


# Tool 1: Add Task
@function_tool
async def mcp_add_task(
    ctx: RunContextWrapper[Any],
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_at: Optional[str] = None,
    remind_at: Optional[str] = None,
    tags: Optional[List[str]] = None,
    recurrence_pattern: Optional[str] = None,
) -> dict:
    """
    Create a new task for the user.

    Args:
        ctx: Run context with user_id
        title: Task title/name (required, non-empty)
        description: Optional task description
        priority: Optional priority level ('low', 'medium', 'high'). Defaults to 'medium'.
        due_at: Optional due date as ISO 8601 string
        remind_at: Optional reminder date/time as ISO 8601 string
        tags: Optional list of tag strings
        recurrence_pattern: Optional recurrence pattern ('daily', 'weekly', 'monthly')

    Returns:
        Dictionary with success status and created task details
    """
    session = get_session()
    user_id = ctx.context["user_id"]

    if not title or not title.strip():
        raise ValueError("Task title cannot be empty")

    # Parse due_at if provided
    parsed_due_at = None
    if due_at:
        try:
            parsed_due_at = datetime.fromisoformat(due_at.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            raise ValueError(f"Invalid due_at format: {due_at}")

    # Parse remind_at if provided
    parsed_remind_at = None
    if remind_at:
        try:
            parsed_remind_at = datetime.fromisoformat(remind_at.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            raise ValueError(f"Invalid remind_at format: {remind_at}")

    task = Task(
        user_id=UUID(user_id),
        title=title.strip(),
        description=description.strip() if description else None,
        status=TaskStatus.INCOMPLETE,
        priority=priority or "medium",
        tags=tags or [],
        due_at=parsed_due_at,
        remind_at=parsed_remind_at,
        recurrence_pattern=recurrence_pattern,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {
        "success": True,
        "task": _task_to_dict(task),
    }


# Tool 2: List Tasks
@function_tool
async def mcp_list_tasks(
    ctx: RunContextWrapper[Any],
    status: Optional[str] = None
) -> dict:
    """
    List all tasks for the user, optionally filtered by status.

    Args:
        ctx: Run context with user_id
        status: Optional filter - 'incomplete' or 'complete'

    Returns:
        Dictionary with task count and list of tasks
    """
    session = get_session()
    user_id = ctx.context["user_id"]

    # Build query
    statement = select(Task).where(Task.user_id == UUID(user_id))

    # Apply status filter if provided
    if status:
        if status.lower() == "incomplete":
            statement = statement.where(Task.status == TaskStatus.INCOMPLETE)
        elif status.lower() == "complete":
            statement = statement.where(Task.status == TaskStatus.COMPLETE)
        else:
            raise ValueError(f"Invalid status filter: {status}. Must be 'incomplete' or 'complete'")

    # Execute query
    result = await session.execute(statement)
    tasks = result.scalars().all()

    return {
        "success": True,
        "count": len(tasks),
        "tasks": [_task_to_dict(task) for task in tasks],
    }


# Tool 3: Complete Task
@function_tool
async def mcp_complete_task(
    ctx: RunContextWrapper[Any],
    task_id: str
) -> dict:
    """
    Mark a task as complete.

    Args:
        ctx: Run context with user_id
        task_id: UUID of the task to complete

    Returns:
        Dictionary with success status and updated task details
    """
    session = get_session()
    user_id = ctx.context["user_id"]

    # Find task with ownership verification
    statement = select(Task).where(
        Task.id == UUID(task_id),
        Task.user_id == UUID(user_id)
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise ValueError(f"Task {task_id} not found or does not belong to user")

    # Update status
    task.status = TaskStatus.COMPLETE
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {
        "success": True,
        "task": _task_to_dict(task),
    }


# Tool 4: Delete Task
@function_tool
async def mcp_delete_task(
    ctx: RunContextWrapper[Any],
    task_id: str
) -> dict:
    """
    Delete a task permanently.

    Args:
        ctx: Run context with user_id
        task_id: UUID of the task to delete

    Returns:
        Dictionary with success status and confirmation message
    """
    session = get_session()
    user_id = ctx.context["user_id"]

    # Find task with ownership verification
    statement = select(Task).where(
        Task.id == UUID(task_id),
        Task.user_id == UUID(user_id)
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise ValueError(f"Task {task_id} not found or does not belong to user")

    # Store title for confirmation message
    task_title = task.title

    # Delete task
    await session.delete(task)
    await session.commit()

    return {
        "success": True,
        "message": f"Task '{task_title}' deleted successfully",
        "task_id": task_id
    }


# Tool 5: Update Task
@function_tool
async def mcp_update_task(
    ctx: RunContextWrapper[Any],
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_at: Optional[str] = None,
    remind_at: Optional[str] = None,
    tags: Optional[List[str]] = None,
    recurrence_pattern: Optional[str] = None,
) -> dict:
    """
    Update a task's fields.

    Args:
        ctx: Run context with user_id
        task_id: UUID of the task to update
        title: New task title (optional)
        description: New task description (optional, can be empty string to clear)
        priority: New priority level (optional, 'low'/'medium'/'high')
        due_at: New due date as ISO 8601 string (optional)
        remind_at: New reminder date/time as ISO 8601 string (optional)
        tags: New tags list (optional)
        recurrence_pattern: New recurrence pattern (optional, 'daily'/'weekly'/'monthly')

    Returns:
        Dictionary with success status and updated task details
    """
    session = get_session()
    user_id = ctx.context["user_id"]

    # Validate at least one field is provided
    if all(v is None for v in [title, description, priority, due_at, remind_at, tags, recurrence_pattern]):
        raise ValueError("Must provide at least one field to update")

    # Find task with ownership verification
    statement = select(Task).where(
        Task.id == UUID(task_id),
        Task.user_id == UUID(user_id)
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise ValueError(f"Task {task_id} not found or does not belong to user")

    # Update fields
    if title is not None:
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        task.title = title.strip()

    if description is not None:
        task.description = description.strip() if description else None

    if priority is not None:
        task.priority = priority

    if due_at is not None:
        try:
            task.due_at = datetime.fromisoformat(due_at.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            raise ValueError(f"Invalid due_at format: {due_at}")

    if remind_at is not None:
        try:
            task.remind_at = datetime.fromisoformat(remind_at.replace("Z", "+00:00")).replace(tzinfo=None)
            task.reminder_sent = False  # Reset reminder_sent when updating remind_at
        except ValueError:
            raise ValueError(f"Invalid remind_at format: {remind_at}")

    if tags is not None:
        task.tags = tags

    if recurrence_pattern is not None:
        task.recurrence_pattern = recurrence_pattern

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {
        "success": True,
        "task": _task_to_dict(task),
    }
