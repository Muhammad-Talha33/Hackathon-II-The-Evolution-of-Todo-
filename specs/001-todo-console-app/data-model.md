# Data Model: Todo Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-28
**Status**: Complete

## Purpose

This document defines the data structures and validation rules for the Todo Console Application. All models align with the feature specification and constitution requirements.

---

## Entities

### Task

Represents a single todo item in the application.

**Description**: A task is the core entity of the todo application, containing all information about a single item that needs to be done.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | int | Yes | Auto-generated | Unique sequential identifier (1, 2, 3, ...) |
| `title` | str | Yes | None | Task title/description of what needs to be done |
| `description` | str | No | "" (empty string) | Optional additional details about the task |
| `status` | str | Yes | "incomplete" | Completion state: "incomplete" or "complete" |

**Relationships**: None (single entity model for Phase I)

**Constraints**:
- `id`: Must be unique across all tasks, must be positive integer
- `title`: Must not be empty string, must not be only whitespace
- `description`: Can be empty string or any text
- `status`: Must be exactly "incomplete" or "complete" (case-sensitive)

---

## Data Structure

### In-Memory Representation

Tasks are stored as a Python list of dictionaries:

```python
# Type alias for clarity
Task = dict[str, int | str]

# In-memory task list (global or class attribute)
tasks: list[Task] = []
```

### Task Dictionary Format

```python
{
    "id": 1,                    # int: unique sequential ID
    "title": "Buy groceries",   # str: non-empty title
    "description": "Get milk, eggs, bread",  # str: optional details
    "status": "incomplete"      # str: "incomplete" or "complete"
}
```

### Alternative: Dataclass (Optional Enhancement)

For improved type safety, could use Python dataclass:

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    """Represents a todo task."""
    id: int
    title: str
    description: str = ""
    status: str = "incomplete"

    def __post_init__(self):
        """Validate task data after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if self.status not in ("incomplete", "complete"):
            raise ValueError("Status must be 'incomplete' or 'complete'")
```

**Decision**: Use dictionary format for Phase I (simpler, no class overhead). Dataclass can be considered for Phase II.

---

## Validation Rules

### Title Validation

**Rules**:
1. Must not be None
2. Must not be empty string ("")
3. Must not be only whitespace ("   ")
4. Leading/trailing whitespace should be stripped before storage

**Valid Examples**:
- "Buy groceries" ✓
- "Complete assignment  " → "Complete assignment" (trimmed) ✓
- "  Call dentist" → "Call dentist" (trimmed) ✓

**Invalid Examples**:
- "" ✗ (empty string)
- "   " ✗ (only whitespace)
- None ✗ (null value)

**Validation Function**:
```python
def validate_title(title: str | None) -> str | None:
    """
    Validate task title.

    Returns:
        None if valid, error message if invalid
    """
    if title is None:
        return "Error: Task title is required"
    if not title.strip():
        return "Error: Task title cannot be empty"
    return None
```

### ID Validation

**Rules**:
1. Must be a positive integer (>= 1)
2. Must be unique across all existing tasks
3. Must exist in task list for update/delete/mark complete operations

**Valid Examples**:
- 1, 2, 3, 100 ✓

**Invalid Examples**:
- 0 ✗ (not positive)
- -1 ✗ (negative)
- "abc" ✗ (not integer)
- 999 (if not in task list) ✗

**Validation Function**:
```python
def validate_task_id(task_id: int, tasks: list[Task]) -> str | None:
    """
    Validate task ID exists.

    Returns:
        None if valid, error message if invalid
    """
    if not isinstance(task_id, int) or task_id < 1:
        return "Error: Invalid task ID. Must be a positive integer"

    if not any(task['id'] == task_id for task in tasks):
        return f"Error: Task with ID {task_id} not found"

    return None
```

### Description Validation

**Rules**:
1. Optional field (can be empty)
2. No length limits for Phase I
3. Leading/trailing whitespace should be stripped

**Valid Examples**:
- "" (empty) ✓
- "Any text here" ✓
- Very long descriptions ✓

### Status Validation

**Rules**:
1. Must be exactly "incomplete" or "complete" (case-sensitive)
2. Default value is "incomplete" for new tasks

**Valid Values**:
- "incomplete" ✓
- "complete" ✓

**Invalid Values**:
- "Incomplete" ✗ (wrong case)
- "done" ✗ (wrong value)
- "pending" ✗ (not allowed)

**Validation Function**:
```python
def validate_status(status: str) -> str | None:
    """
    Validate task status.

    Returns:
        None if valid, error message if invalid
    """
    if status not in ("incomplete", "complete"):
        return "Error: Status must be 'incomplete' or 'complete'"
    return None
```

---

## State Transitions

### Task Lifecycle

```
                 +----------------+
                 | Task Created   |
                 | status: "incomplete" |
                 +--------+-------+
                          |
                          v
            +-------------+-------------+
            |                           |
            v                           v
    +-------+--------+         +--------+-------+
    | Incomplete     |<------->| Complete       |
    | status: "incomplete" |   | status: "complete" |
    +----------------+         +----------------+
            |                           |
            +-------------+-------------+
                          |
                          v
                 +--------+-------+
                 | Task Deleted   |
                 | (removed from  |
                 | task list)     |
                 +----------------+
```

**State Transitions**:
1. **Created** → `status = "incomplete"` (default)
2. **Mark Complete** → `status = "incomplete"` → `status = "complete"`
3. **Mark Incomplete** → `status = "complete"` → `status = "incomplete"`
4. **Delete** → Task removed from list (no longer accessible)

**Operations by State**:
- **Add**: Creates new task with status "incomplete"
- **View**: Displays all tasks regardless of status
- **Update**: Modifies title/description, status unchanged
- **Mark Complete**: Toggles status between "incomplete" ↔ "complete"
- **Delete**: Removes task entirely (any status)

---

## ID Generation Strategy

### Sequential ID Assignment

**Algorithm**:
1. Find the maximum ID currently in the task list
2. New ID = max ID + 1
3. If task list is empty, start with ID = 1

**Implementation**:
```python
def generate_next_id(tasks: list[Task]) -> int:
    """
    Generate the next sequential task ID.

    Args:
        tasks: Current list of tasks

    Returns:
        Next available ID (1 if list empty, max_id + 1 otherwise)
    """
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1
```

**Properties**:
- Deterministic: Same task list → same next ID
- Sequential: IDs increment by 1
- Gap-tolerant: If task 2 is deleted, next new task gets ID 4 (after existing tasks 1, 3)
- Reset each session: IDs start from 1 when app restarts

---

## Data Invariants

**System Invariants** (must always be true):

1. **Unique IDs**: No two tasks can have the same ID
2. **Valid Titles**: All tasks must have non-empty titles
3. **Valid Statuses**: All tasks must have status "incomplete" or "complete"
4. **Sequential IDs**: Task IDs are assigned sequentially (gaps allowed after deletion)

**Validation on Operations**:
- **Add**: Validate title before adding
- **Update**: Validate new title if provided
- **Mark Complete**: Validate ID exists
- **Delete**: Validate ID exists

---

## Example Task List

```python
tasks = [
    {
        "id": 1,
        "title": "Buy groceries",
        "description": "Get milk, eggs, and bread",
        "status": "incomplete"
    },
    {
        "id": 2,
        "title": "Complete assignment",
        "description": "Finish math homework",
        "status": "complete"
    },
    {
        "id": 3,
        "title": "Call dentist",
        "description": "",
        "status": "incomplete"
    }
]
```

---

## Notes

- **Phase I Constraint**: All data stored in-memory; lost when application terminates
- **No Persistence**: No file or database storage in Phase I
- **Scalability**: Optimized for <100 tasks (acceptable for in-memory Phase I)
- **Thread Safety**: Not required (single-user, single-threaded console app)

---

## Summary

| Entity | Fields | Validation | State Transitions |
|--------|--------|------------|-------------------|
| Task | id, title, description, status | Non-empty title, valid ID, valid status | Created → Incomplete ↔ Complete → Deleted |

**Status**: Data model complete and ready for implementation
