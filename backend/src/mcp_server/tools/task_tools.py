"""MCP tools for task management operations."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from src.models import Task, TaskStatus


def _task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert a Task to a response dictionary including all fields."""
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


def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_at: Optional[str] = None,
    remind_at: Optional[str] = None,
    tags: Optional[List[str]] = None,
    recurrence_pattern: Optional[str] = None,
    session: Session = None
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: UUID of the task owner
        title: Task title/name
        description: Optional task description
        priority: Optional priority (low/medium/high)
        due_at: Optional due date (ISO 8601 string)
        remind_at: Optional reminder date/time (ISO 8601 string)
        tags: Optional list of tag strings
        recurrence_pattern: Optional recurrence pattern (daily/weekly/monthly)
        session: Database session

    Returns:
        Dictionary containing the created task details
    """
    if not session:
        raise ValueError("Database session is required")

    if not title or not title.strip():
        raise ValueError("Task title cannot be empty")

    # Parse due_at if provided
    parsed_due_at = None
    if due_at:
        try:
            parsed_due_at = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Invalid due_at format: {due_at}")

    # Parse remind_at if provided
    parsed_remind_at = None
    if remind_at:
        try:
            parsed_remind_at = datetime.fromisoformat(remind_at.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Invalid remind_at format: {remind_at}")

    # Create new task
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
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return {
        "success": True,
        "task": _task_to_dict(task),
    }


def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    session: Session = None
) -> Dict[str, Any]:
    """
    List all tasks for the user, optionally filtered by status.

    Args:
        user_id: UUID of the task owner
        status: Optional filter by status ('incomplete' or 'complete')
        session: Database session

    Returns:
        Dictionary containing list of tasks
    """
    if not session:
        raise ValueError("Database session is required")

    # Build query
    statement = select(Task).where(Task.user_id == UUID(user_id))

    # Add status filter if provided
    if status:
        status_enum = TaskStatus.COMPLETE if status.lower() == "complete" else TaskStatus.INCOMPLETE
        statement = statement.where(Task.status == status_enum)

    # Order by created date (newest first)
    statement = statement.order_by(Task.created_at.desc())

    # Execute query
    tasks = session.exec(statement).all()

    return {
        "success": True,
        "count": len(tasks),
        "tasks": [_task_to_dict(task) for task in tasks],
    }


def complete_task(
    user_id: str,
    task_id: str,
    session: Session = None
) -> Dict[str, Any]:
    """
    Mark a task as complete.

    Args:
        user_id: UUID of the task owner (for authorization)
        task_id: UUID of the task to complete
        session: Database session

    Returns:
        Dictionary containing the updated task details
    """
    if not session:
        raise ValueError("Database session is required")

    # Find task
    task = session.get(Task, UUID(task_id))

    if not task:
        raise ValueError(f"Task with ID {task_id} not found")

    # Verify ownership
    if str(task.user_id) != user_id:
        raise ValueError("You can only complete your own tasks")

    # Update status
    task.status = TaskStatus.COMPLETE
    session.add(task)
    session.commit()
    session.refresh(task)

    return {
        "success": True,
        "task": _task_to_dict(task),
    }


def delete_task(
    user_id: str,
    task_id: str,
    session: Session = None
) -> Dict[str, Any]:
    """
    Delete a task.

    Args:
        user_id: UUID of the task owner (for authorization)
        task_id: UUID of the task to delete
        session: Database session

    Returns:
        Dictionary confirming deletion
    """
    if not session:
        raise ValueError("Database session is required")

    # Find task
    task = session.get(Task, UUID(task_id))

    if not task:
        raise ValueError(f"Task with ID {task_id} not found")

    # Verify ownership
    if str(task.user_id) != user_id:
        raise ValueError("You can only delete your own tasks")

    # Delete task
    task_title = task.title
    session.delete(task)
    session.commit()

    return {
        "success": True,
        "message": f"Task '{task_title}' has been deleted",
        "task_id": task_id
    }


def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_at: Optional[str] = None,
    remind_at: Optional[str] = None,
    tags: Optional[List[str]] = None,
    recurrence_pattern: Optional[str] = None,
    session: Session = None
) -> Dict[str, Any]:
    """
    Update a task's fields.

    Args:
        user_id: UUID of the task owner (for authorization)
        task_id: UUID of the task to update
        title: New task title (optional)
        description: New task description (optional)
        priority: New priority (optional, low/medium/high)
        due_at: New due date (optional, ISO 8601 string)
        remind_at: New reminder date (optional, ISO 8601 string)
        tags: New tags list (optional)
        recurrence_pattern: New recurrence pattern (optional, daily/weekly/monthly)
        session: Database session

    Returns:
        Dictionary containing the updated task details
    """
    if not session:
        raise ValueError("Database session is required")

    if (not title and description is None and priority is None
            and due_at is None and remind_at is None
            and tags is None and recurrence_pattern is None):
        raise ValueError("At least one field must be provided for update")

    # Find task
    task = session.get(Task, UUID(task_id))

    if not task:
        raise ValueError(f"Task with ID {task_id} not found")

    # Verify ownership
    if str(task.user_id) != user_id:
        raise ValueError("You can only update your own tasks")

    # Update fields
    if title and title.strip():
        task.title = title.strip()
    if description is not None:
        task.description = description.strip() if description else None
    if priority is not None:
        task.priority = priority
    if due_at is not None:
        try:
            task.due_at = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Invalid due_at format: {due_at}")
    if remind_at is not None:
        try:
            task.remind_at = datetime.fromisoformat(remind_at.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Invalid remind_at format: {remind_at}")
    if tags is not None:
        task.tags = tags
    if recurrence_pattern is not None:
        task.recurrence_pattern = recurrence_pattern

    session.add(task)
    session.commit()
    session.refresh(task)

    return {
        "success": True,
        "task": _task_to_dict(task),
    }
