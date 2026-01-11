"""MCP tools for task management operations."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlmodel import Session, select
from src.models import Task, TaskStatus


def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    session: Session = None
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: UUID of the task owner
        title: Task title/name
        description: Optional task description
        session: Database session

    Returns:
        Dictionary containing the created task details
    """
    if not session:
        raise ValueError("Database session is required")

    if not title or not title.strip():
        raise ValueError("Task title cannot be empty")

    # Create new task
    task = Task(
        user_id=UUID(user_id),
        title=title.strip(),
        description=description.strip() if description else None,
        status=TaskStatus.INCOMPLETE
    )

    session.add(task)
    session.commit()
    session.refresh(task)

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
        "tasks": [
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
        "task": {
            "id": str(task.id),
            "title": task.title,
            "status": task.status.value,
            "updated_at": task.updated_at.isoformat()
        }
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
    session: Session = None
) -> Dict[str, Any]:
    """
    Update a task's title and/or description.

    Args:
        user_id: UUID of the task owner (for authorization)
        task_id: UUID of the task to update
        title: New task title (optional)
        description: New task description (optional)
        session: Database session

    Returns:
        Dictionary containing the updated task details
    """
    if not session:
        raise ValueError("Database session is required")

    if not title and description is None:
        raise ValueError("At least one of title or description must be provided")

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

    session.add(task)
    session.commit()
    session.refresh(task)

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
