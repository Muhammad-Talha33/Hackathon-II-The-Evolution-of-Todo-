"""
Utility functions for validation and formatting.

This module provides helper functions for input validation,
task display formatting, and status indicators.
"""

from typing import Any


def validate_title(title: str) -> bool:
    """
    Validate that a task title is non-empty.

    Args:
        title: The title string to validate

    Returns:
        True if title is valid (non-empty after stripping whitespace)

    Examples:
        >>> validate_title("Buy groceries")
        True
        >>> validate_title("   ")
        False
        >>> validate_title("")
        False
    """
    return bool(title and title.strip())


def validate_task_id(task_id: Any) -> bool:
    """
    Validate that a task ID is a positive integer.

    Args:
        task_id: The ID to validate (can be any type)

    Returns:
        True if task_id is a positive integer

    Examples:
        >>> validate_task_id(1)
        True
        >>> validate_task_id(0)
        False
        >>> validate_task_id(-1)
        False
        >>> validate_task_id("1")
        False
    """
    return isinstance(task_id, int) and task_id > 0


def format_status_indicator(status: str) -> str:
    """
    Convert task status to a visual indicator.

    Args:
        status: Task status ("complete" or "incomplete")

    Returns:
        "[X]" for complete tasks, "[ ]" for incomplete tasks

    Examples:
        >>> format_status_indicator("complete")
        '[X]'
        >>> format_status_indicator("incomplete")
        '[ ]'
    """
    return "[X]" if status == "complete" else "[ ]"


def format_task_display(task: dict[str, int | str]) -> str:
    """
    Format a task dictionary for display.

    Args:
        task: Task dictionary with id, title, description, and status

    Returns:
        Formatted string representation of the task

    Examples:
        >>> task = {"id": 1, "title": "Buy groceries", "description": "Get milk", "status": "incomplete"}
        >>> print(format_task_display(task))
        [1] [ ] Buy groceries
            Description: Get milk
    """
    status_icon = format_status_indicator(str(task["status"]))
    result = f"[{task['id']}] {status_icon} {task['title']}"

    if task["description"]:
        result += f"\n    Description: {task['description']}"

    return result


def get_int_input(prompt: str) -> int | None:
    """
    Get validated integer input from the user.

    Args:
        prompt: The prompt message to display

    Returns:
        Valid integer input, or None if input is invalid

    Examples:
        >>> # User enters "5"
        >>> get_int_input("Enter task ID: ")
        5
        >>> # User enters "abc"
        >>> get_int_input("Enter task ID: ")
        None
    """
    try:
        return int(input(prompt))
    except ValueError:
        return None
