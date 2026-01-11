"""MCP Server initialization for Task Management tools."""
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID
from datetime import datetime
from agents import function_tool, RunContextWrapper

from src.models.task import Task, TaskStatus

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


# Tool 1: Add Task
@function_tool
async def mcp_add_task(
    ctx: RunContextWrapper[Any],
    title: str,
    description: Optional[str] = None
) -> dict:
    """
    Create a new task for the user.

    Args:
        ctx: Run context with user_id
        title: Task title/name (required, non-empty)
        description: Optional task description

    Returns:
        Dictionary with success status and created task details
    """
    session = get_session()
    user_id = ctx.context["user_id"]

    if not title or not title.strip():
        raise ValueError("Task title cannot be empty")

    task = Task(
        user_id=UUID(user_id),
        title=title.strip(),
        description=description.strip() if description else None,
        status=TaskStatus.INCOMPLETE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {
        "success": True,
        "task": {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "created_at": task.created_at.isoformat()
        }
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

    # Serialize tasks
    task_list = [
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }
        for task in tasks
    ]

    return {
        "success": True,
        "count": len(task_list),
        "tasks": task_list
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
        "task": {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "updated_at": task.updated_at.isoformat()
        }
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
    description: Optional[str] = None
) -> dict:
    """
    Update a task's title and/or description.

    Args:
        ctx: Run context with user_id
        task_id: UUID of the task to update
        title: New task title (optional)
        description: New task description (optional, can be empty string to clear)

    Returns:
        Dictionary with success status and updated task details
    """
    session = get_session()
    user_id = ctx.context["user_id"]

    # Validate at least one field is provided
    if title is None and description is None:
        raise ValueError("Must provide at least one field to update (title or description)")

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
        # Empty string clears description
        task.description = description.strip() if description else None

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {
        "success": True,
        "task": {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "updated_at": task.updated_at.isoformat()
        }
    }
