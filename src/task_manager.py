"""
Task management module providing CRUD operations.

This module manages an in-memory list of tasks and provides functions
for adding, viewing, updating, deleting, and marking tasks as complete.
"""

from typing import TypeAlias
from models.task import Task, create_task

# In-memory task storage
_tasks: list[Task] = []


def _generate_next_id() -> int:
    """
    Generate the next sequential task ID.

    Returns:
        The next available task ID (1 if list is empty, otherwise max_id + 1)

    Examples:
        >>> _tasks.clear()
        >>> _generate_next_id()
        1
        >>> _tasks.append({"id": 1, "title": "Test", "description": "", "status": "incomplete"})
        >>> _generate_next_id()
        2
    """
    if not _tasks:
        return 1
    return max(task["id"] for task in _tasks) + 1


def _find_task_by_id(task_id: int) -> Task | None:
    """
    Find a task in the task list by its ID.

    Args:
        task_id: The ID of the task to find

    Returns:
        The task dictionary if found, None otherwise

    Examples:
        >>> _tasks.clear()
        >>> task = {"id": 1, "title": "Test", "description": "", "status": "incomplete"}
        >>> _tasks.append(task)
        >>> _find_task_by_id(1) == task
        True
        >>> _find_task_by_id(999)

    """
    for task in _tasks:
        if task["id"] == task_id:
            return task
    return None


def add_task(title: str, description: str = "") -> dict | str:
    """
    Add a new task to the task list.

    Args:
        title: Task title (required, non-empty)
        description: Optional task description

    Returns:
        Task dictionary if successful, error message string if failed

    Examples:
        >>> result = add_task("Buy groceries", "Get milk and eggs")
        >>> isinstance(result, dict)
        True
        >>> add_task("")
        'Error: Task title cannot be empty'
    """
    if not title or not title.strip():
        return "Error: Task title cannot be empty"

    try:
        task_id = _generate_next_id()
        task = create_task(task_id, title, description)
        _tasks.append(task)
        return task
    except ValueError as e:
        return f"Error: {str(e)}"


def view_tasks() -> list[Task]:
    """
    Retrieve all tasks from the task list.

    Returns:
        List of all task dictionaries (empty list if no tasks)

    Examples:
        >>> _tasks.clear()
        >>> view_tasks()
        []
        >>> add_task("Test task")
        >>> len(view_tasks())
        1
    """
    return _tasks.copy()


def update_task(task_id: int, title: str | None = None, description: str | None = None) -> dict | str:
    """
    Update a task's title and/or description.

    Args:
        task_id: ID of the task to update
        title: New title (optional, None means no change)
        description: New description (optional, None means no change)

    Returns:
        Updated task dictionary if successful, error message string if failed

    Examples:
        >>> task = add_task("Original title")
        >>> result = update_task(1, title="New title")
        >>> isinstance(result, dict)
        True
        >>> update_task(999, title="Test")
        'Error: Task with ID 999 not found'
    """
    task = _find_task_by_id(task_id)

    if task is None:
        return f"Error: Task with ID {task_id} not found"

    if title is not None:
        if not title or not title.strip():
            return "Error: Task title cannot be empty"
        task["title"] = title.strip()

    if description is not None:
        task["description"] = description.strip()

    return task


def delete_task(task_id: int) -> dict | str:
    """
    Delete a task from the task list.

    Args:
        task_id: ID of the task to delete

    Returns:
        Deleted task dictionary if successful, error message string if failed

    Examples:
        >>> task = add_task("Task to delete")
        >>> result = delete_task(task["id"])
        >>> isinstance(result, dict)
        True
        >>> delete_task(999)
        'Error: Task with ID 999 not found'
    """
    task = _find_task_by_id(task_id)

    if task is None:
        return f"Error: Task with ID {task_id} not found"

    _tasks.remove(task)
    return task


def mark_complete(task_id: int) -> dict | str:
    """
    Toggle a task's completion status.

    Args:
        task_id: ID of the task to mark complete/incomplete

    Returns:
        Updated task dictionary if successful, error message string if failed

    Examples:
        >>> task = add_task("Task to complete")
        >>> result = mark_complete(task["id"])
        >>> result["status"]
        'complete'
        >>> result = mark_complete(task["id"])  # Toggle back
        >>> result["status"]
        'incomplete'
    """
    task = _find_task_by_id(task_id)

    if task is None:
        return f"Error: Task with ID {task_id} not found"

    # Toggle status
    task["status"] = "complete" if task["status"] == "incomplete" else "incomplete"

    return task
