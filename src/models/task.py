"""
Task model and creation utilities.

This module defines the Task type alias and provides a factory function
for creating new task dictionaries with validated data.
"""

from typing import TypeAlias

# Task type definition
Task: TypeAlias = dict[str, int | str]


def create_task(task_id: int, title: str, description: str = "") -> Task:
    """
    Create a new task dictionary with validated fields.

    Args:
        task_id: Unique identifier for the task (positive integer)
        title: Task title (non-empty string)
        description: Optional task description (defaults to empty string)

    Returns:
        A dictionary representing a task with the following structure:
        {
            "id": int,
            "title": str,
            "description": str,
            "status": str  # Always "incomplete" for new tasks
        }

    Raises:
        ValueError: If task_id is not positive or title is empty

    Examples:
        >>> task = create_task(1, "Buy groceries", "Get milk and eggs")
        >>> task["id"]
        1
        >>> task["status"]
        'incomplete'
    """
    if task_id <= 0:
        raise ValueError("Task ID must be a positive integer")

    if not title or not title.strip():
        raise ValueError("Task title cannot be empty")

    return {
        "id": task_id,
        "title": title.strip(),
        "description": description.strip(),
        "status": "incomplete"
    }
