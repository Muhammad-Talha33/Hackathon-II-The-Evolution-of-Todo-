# Task Manager API Contract

**Feature**: 001-todo-console-app
**Date**: 2025-12-28
**Module**: src/task_manager.py

## Purpose

This document defines the internal API contract for the Task Manager module. Since this is a console application (not a web/REST API), the contract specifies Python function signatures, parameters, return values, and error handling.

---

## Module: Task Manager

**Responsibility**: Manage in-memory task list and provide CRUD operations

**Global State**:
```python
tasks: list[dict] = []  # In-memory task list
```

---

## API Functions

### 1. Add Task

**Function Signature**:
```python
def add_task(title: str, description: str = "") -> dict | str
```

**Description**: Creates a new task with unique ID and adds it to the task list.

**Parameters**:
- `title` (str, required): Task title (must be non-empty)
- `description` (str, optional): Additional task details (default: empty string)

**Returns**:
- `dict`: The created task with fields {id, title, description, status} if successful
- `str`: Error message if validation fails

**Success Response**:
```python
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Get milk, eggs, bread",
    "status": "incomplete"
}
```

**Error Responses**:
- `"Error: Task title cannot be empty"` - if title is empty or whitespace-only

**Side Effects**:
- Adds new task to global `tasks` list
- Generates sequential ID

**Example Usage**:
```python
task = add_task("Buy groceries", "Get milk, eggs, bread")
if isinstance(task, dict):
    print(f"Task added successfully: ID {task['id']}")
else:
    print(task)  # Error message
```

---

### 2. View Tasks

**Function Signature**:
```python
def view_tasks() -> list[dict]
```

**Description**: Returns all tasks in the task list.

**Parameters**: None

**Returns**:
- `list[dict]`: List of all tasks (empty list if no tasks)

**Success Response**:
```python
[
    {"id": 1, "title": "Buy groceries", "description": "...", "status": "incomplete"},
    {"id": 2, "title": "Complete assignment", "description": "...", "status": "complete"}
]
```

**Empty State Response**:
```python
[]  # Empty list
```

**Side Effects**: None (read-only operation)

**Example Usage**:
```python
all_tasks = view_tasks()
if not all_tasks:
    print("No tasks found. Your task list is empty.")
else:
    for task in all_tasks:
        print(f"[{task['id']}] {task['title']}")
```

---

### 3. Update Task

**Function Signature**:
```python
def update_task(task_id: int, title: str | None = None, description: str | None = None) -> dict | str
```

**Description**: Updates the title and/or description of an existing task.

**Parameters**:
- `task_id` (int, required): ID of the task to update
- `title` (str | None, optional): New title (None = no change)
- `description` (str | None, optional): New description (None = no change)

**Returns**:
- `dict`: The updated task if successful
- `str`: Error message if validation fails or task not found

**Success Response**:
```python
{
    "id": 1,
    "title": "Buy groceries and supplies",  # Updated
    "description": "Get milk, eggs, bread, cleaning supplies",  # Updated
    "status": "incomplete"  # Unchanged
}
```

**Error Responses**:
- `"Error: Task with ID {task_id} not found"` - if ID doesn't exist
- `"Error: Task title cannot be empty"` - if new title is empty/whitespace
- `"Error: Please provide at least a new title or description to update"` - if both parameters are None

**Side Effects**:
- Modifies task in global `tasks` list
- Does NOT modify task ID or status

**Example Usage**:
```python
result = update_task(1, title="Buy groceries and supplies")
if isinstance(result, dict):
    print(f"Task updated successfully")
else:
    print(result)  # Error message
```

---

### 4. Delete Task

**Function Signature**:
```python
def delete_task(task_id: int) -> dict | str
```

**Description**: Removes a task from the task list by ID.

**Parameters**:
- `task_id` (int, required): ID of the task to delete

**Returns**:
- `dict`: The deleted task (for confirmation) if successful
- `str`: Error message if task not found

**Success Response**:
```python
{
    "id": 3,
    "title": "Call dentist",
    "description": "",
    "status": "incomplete"
}
```

**Error Responses**:
- `"Error: Task with ID {task_id} not found"` - if ID doesn't exist
- `"Error: Task list is empty"` - if no tasks to delete

**Side Effects**:
- Removes task from global `tasks` list
- Task is permanently deleted (cannot be recovered in Phase I)

**Example Usage**:
```python
result = delete_task(3)
if isinstance(result, dict):
    print(f"Task deleted successfully: {result['title']}")
else:
    print(result)  # Error message
```

---

### 5. Mark Complete

**Function Signature**:
```python
def mark_complete(task_id: int) -> dict | str
```

**Description**: Toggles task completion status between "incomplete" and "complete".

**Parameters**:
- `task_id` (int, required): ID of the task to toggle

**Returns**:
- `dict`: The updated task with new status if successful
- `str`: Error message if task not found

**Success Response** (incomplete → complete):
```python
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Get milk, eggs, bread",
    "status": "complete"  # Toggled from "incomplete"
}
```

**Success Response** (complete → incomplete):
```python
{
    "id": 2,
    "title": "Complete assignment",
    "description": "Finish math homework",
    "status": "incomplete"  # Toggled from "complete"
}
```

**Error Responses**:
- `"Error: Task with ID {task_id} not found"` - if ID doesn't exist
- `"Error: Task list is empty"` - if no tasks available

**Side Effects**:
- Modifies task status in global `tasks` list
- Does NOT modify task ID, title, or description

**Example Usage**:
```python
result = mark_complete(1)
if isinstance(result, dict):
    status_icon = "✓" if result['status'] == "complete" else "✗"
    print(f"Task marked as {result['status']} {status_icon}")
else:
    print(result)  # Error message
```

---

## Helper Functions

### Generate Next ID

**Function Signature**:
```python
def _generate_next_id() -> int
```

**Description**: Internal helper to generate the next sequential task ID.

**Parameters**: None (accesses global `tasks` list)

**Returns**:
- `int`: Next available ID (1 if list empty, max_id + 1 otherwise)

**Example**:
```python
next_id = _generate_next_id()  # Returns 1 if tasks = []
# After adding tasks [1, 2, 3], returns 4
```

---

### Find Task by ID

**Function Signature**:
```python
def _find_task_by_id(task_id: int) -> dict | None
```

**Description**: Internal helper to find a task by its ID.

**Parameters**:
- `task_id` (int): ID to search for

**Returns**:
- `dict`: The task if found
- `None`: If task not found

**Example**:
```python
task = _find_task_by_id(1)
if task:
    print(f"Found: {task['title']}")
else:
    print("Task not found")
```

---

## Error Handling Contract

**Error Message Format**:
- All error messages start with `"Error: "`
- Error messages are descriptive and actionable
- Examples:
  - `"Error: Task title cannot be empty"`
  - `"Error: Task with ID 999 not found"`
  - `"Error: Please provide at least a new title or description to update"`

**Return Type Pattern**:
- Success: Return `dict` (the task object)
- Failure: Return `str` (error message)
- Caller can check type: `isinstance(result, dict)` for success

**No Exceptions**:
- Functions do not raise exceptions
- All errors returned as strings
- Prevents application crashes from user input

---

## Validation Contract

### Input Validation Rules

1. **Task Title**:
   - Must not be None
   - Must not be empty string
   - Must not be only whitespace
   - Strip leading/trailing whitespace before storage

2. **Task ID**:
   - Must be a positive integer
   - Must exist in current task list (for update/delete/mark)

3. **Task Description**:
   - Optional (can be empty string)
   - Strip leading/trailing whitespace before storage

### Validation Timing

- **Pre-validation**: Before any task list modification
- **Early return**: Return error immediately on validation failure
- **No partial updates**: Either full success or complete rollback

---

## State Management Contract

### In-Memory State

```python
# Global task list (module-level variable)
tasks: list[dict] = []
```

**Guarantees**:
- All operations modify this single source of truth
- Task IDs are unique within this list
- List persists for application lifetime
- List is reset (empty) when application restarts

### Concurrency

**Not Required**: Single-threaded console application
- No locking needed
- No race conditions possible
- One operation at a time (menu-driven)

---

## Summary

| Function | Purpose | Parameters | Returns | Side Effects |
|----------|---------|------------|---------|--------------|
| `add_task` | Create new task | title, description | dict \| str | Adds to list |
| `view_tasks` | List all tasks | None | list[dict] | None (read-only) |
| `update_task` | Modify task | task_id, title?, description? | dict \| str | Modifies in list |
| `delete_task` | Remove task | task_id | dict \| str | Removes from list |
| `mark_complete` | Toggle status | task_id | dict \| str | Modifies status |

**Contract Guarantees**:
- No exceptions raised (errors returned as strings)
- Clear error messages with actionable guidance
- Deterministic behavior (same input → same output)
- Single source of truth (global `tasks` list)

---

**Status**: API contract complete and ready for implementation
