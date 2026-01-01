# Research: Todo Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-28
**Status**: Complete

## Purpose

This document consolidates technical research and decisions for the Phase I Todo In-Memory Python Console Application. All decisions align with the project constitution and user requirements.

---

## Phase 0: Technical Research & Decisions

### 1. Python Version & Environment

**Decision**: Python 3.13+

**Rationale**:
- Ensures compatibility with modern type hints (PEP 585, PEP 604)
- Supports latest PEP 8 style features
- Provides improved error messages and debugging capabilities
- Aligns with constitution requirement for "Python 3.13+ compatible"

**Alternatives Considered**:
- Python 3.10/3.11: Would work but miss newer type hint features
- Python 3.12: Suitable, but 3.13+ ensures future-proofing

**References**:
- Python 3.13 Documentation: https://docs.python.org/3.13/
- PEP 8 Style Guide: https://peps.python.org/pep-0008/

---

### 2. Package Manager

**Decision**: `uv` for virtual environment and dependency management

**Rationale**:
- Fast, modern Python package installer and resolver
- Simplifies virtual environment management
- Compatible with Python 3.13+
- Minimal dependencies for Phase I (only standard library needed)

**Alternatives Considered**:
- `pip` + `venv`: Standard but slower
- `poetry`: More complex than needed for simple Phase I app
- `conda`: Overkill for this project scope

**References**:
- uv documentation: https://github.com/astral-sh/uv

---

### 3. Data Storage

**Decision**: In-memory Python list

**Rationale**:
- Aligns with Constitution Principle I (In-Memory Task Management - NON-NEGOTIABLE)
- Simplest implementation: tasks stored in Python list during runtime
- No external dependencies required
- Tasks are volatile (lost on exit) as specified

**Alternatives Considered**:
- File-based storage (JSON/CSV): Violates Phase I constitution
- SQLite database: Violates Phase I constitution, introduces complexity
- Pickle serialization: Violates Phase I constitution

**Tradeoffs**:
- ✅ Simplicity, no persistence overhead
- ❌ Data lost when application terminates (accepted Phase I constraint)

**Implementation**:
```python
# In-memory task list (global or class attribute)
tasks: list[dict] = []
```

---

### 4. User Input Method

**Decision**: Menu-driven interactive CLI (no command-line arguments)

**Rationale**:
- Aligns with constitution requirement: "Menu-Driven Interface"
- User-friendly for end users unfamiliar with CLI arguments
- Supports all CRUD operations through numbered menu
- Allows for detailed prompts and error messages

**Alternatives Considered**:
- CLI arguments (e.g., `--add "task title"`): Violates Phase I constitution
- Mixed approach (menu + CLI args): Unnecessary complexity for Phase I

**Tradeoffs**:
- ✅ Intuitive for non-technical users
- ❌ No automation via shell scripts (acceptable for Phase I)

**Implementation Pattern**:
```
=== Todo Console App ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete
6. Exit
Enter choice (1-6):
```

---

### 5. Task ID Generation

**Decision**: Sequential integers starting from 1

**Rationale**:
- Simple, readable, predictable
- Easy for users to reference in commands ("Update task 3")
- Deterministic behavior (IDs increment sequentially)
- No external library required

**Alternatives Considered**:
- UUIDs: Overly complex, not user-friendly for console display
- Random integers: Non-deterministic, potential collisions

**Tradeoffs**:
- ✅ Simple, readable, deterministic
- ❌ IDs reset each session (acceptable for in-memory Phase I)

**Implementation**:
```python
next_id = 1
for task in tasks:
    next_id = max(next_id, task['id'] + 1)
```

---

### 6. Task Display Format

**Decision**: Text-based with Unicode status indicators (✓/✗)

**Rationale**:
- Readable in standard console/terminal
- Unicode characters widely supported (✓ = complete, ✗ = incomplete)
- Clear visual distinction between states
- No external formatting libraries needed

**Alternatives Considered**:
- ASCII only (e.g., [X] / [ ]): Less visually appealing
- Rich tables (using `rich` library): Adds dependency, unnecessary for Phase I
- ANSI colors: May not work in all terminals

**Tradeoffs**:
- ✅ Clear, universally supported
- ❌ Minimal formatting compared to GUI

**Display Example**:
```
=== Your Tasks ===

[1] ✗ Buy groceries
    Description: Get milk, eggs, and bread
    Status: incomplete

[2] ✓ Complete assignment
    Status: complete
```

---

### 7. Error Handling Strategy

**Decision**: Informative error messages with recovery guidance

**Rationale**:
- Aligns with Constitution Principle III (Input Validation and Error Handling - MANDATORY)
- Error messages must state: (1) what went wrong, (2) how to correct it
- Application must never crash due to user input
- Enhances user experience and reduces frustration

**Alternatives Considered**:
- Silent failures: Poor UX, violates constitution
- Exceptions without handling: App crashes, violates constitution
- Generic error messages: Doesn't help user recover

**Tradeoffs**:
- ✅ Professional UX, prevents crashes, guides users
- ❌ Slightly more code complexity (acceptable)

**Error Message Examples**:
- "Error: Task title cannot be empty. Please provide a title for your task."
- "Error: Task with ID 999 not found. Use 'View Tasks' to see available task IDs."
- "Error: Invalid input. Please enter a number (1-6)."

---

### 8. Input Validation

**Decision**: Comprehensive validation with early returns

**Rationale**:
- Validate all inputs before processing (titles, IDs, menu choices)
- Title validation: not empty, not whitespace-only
- ID validation: integer, exists in task list
- Menu validation: within valid range (1-6)

**Validation Rules**:
1. **Task Title**:
   - Must not be empty string
   - Must not be only whitespace
   - Strip leading/trailing whitespace before storage

2. **Task ID**:
   - Must be a valid integer
   - Must exist in current task list
   - Return clear error if not found

3. **Menu Choice**:
   - Must be integer 1-6
   - Re-prompt on invalid input, don't crash

**Implementation Pattern**:
```python
def validate_title(title: str) -> str | None:
    """Returns error message if invalid, None if valid"""
    if not title or not title.strip():
        return "Error: Task title cannot be empty"
    return None
```

---

### 9. Testing Approach

**Decision**: Manual testing + optional unittest for Task Manager operations

**Rationale**:
- Manual testing sufficient for menu navigation and user interaction
- Optional `unittest` for Task Manager CRUD logic (add, view, update, delete, mark complete)
- Edge case testing: empty list, invalid IDs, whitespace titles
- Constitution emphasizes clean code but doesn't mandate automated tests

**Test Coverage**:
- **Manual**: Menu flow, user prompts, error message display
- **Automated (optional)**: Task Manager methods, validation logic, edge cases

**Test Cases** (from user input):
- Add Task → Task added with unique ID, default "incomplete" status
- View Tasks → Correct display with ID, title, description, status
- Update Task → Changes applied; empty title rejected
- Delete Task → Task removed; invalid ID shows error
- Mark Complete → Status toggles; invalid ID shows error
- Exit → Graceful termination

---

### 10. Code Quality Standards

**Decision**: PEP 8 + Type Hints + Docstrings + SRP + DRY

**Rationale**:
- Aligns with Constitution Principle V (Code Quality and Maintainability)
- PEP 8 for consistent style
- Type hints for all function parameters and returns
- Docstrings for all public functions and classes
- Single Responsibility Principle - each function does one thing
- DRY - eliminate code duplication

**Standards**:
1. **PEP 8**: Line length <100 chars, snake_case naming, proper spacing
2. **Type Hints**: Use modern Python 3.13+ syntax (list[dict], str | None)
3. **Docstrings**: Google-style or NumPy-style for all public APIs
4. **SRP**: Each function has one clear purpose
5. **DRY**: Extract common logic into utility functions

**Example**:
```python
def add_task(title: str, description: str = "") -> dict | str:
    """
    Add a new task to the in-memory task list.

    Args:
        title: Required task title (non-empty)
        description: Optional task description

    Returns:
        dict: The created task if successful
        str: Error message if validation fails
    """
    ...
```

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Python Version | 3.13+ | Modern features, type hints, PEP 8 compatibility |
| Package Manager | uv | Fast, modern, minimal dependencies |
| Data Storage | In-memory Python list | Constitution requirement, simplicity |
| User Input | Menu-driven CLI (no args) | Constitution requirement, user-friendly |
| Task IDs | Sequential integers (1, 2, 3...) | Simple, readable, deterministic |
| Display Format | Text with ✓/✗ indicators | Clear, universally supported |
| Error Handling | Informative messages + guidance | Constitution requirement, better UX |
| Input Validation | Comprehensive, early validation | Prevent crashes, ensure data integrity |
| Testing | Manual + optional unittest | Sufficient for Phase I scope |
| Code Quality | PEP 8 + type hints + docstrings | Constitution requirement |

---

## Architecture Confirmed

Based on research, the architecture follows:

**Main Module** (`src/main.py`):
- Entry point
- Menu loop
- User input handling
- Calls Task Manager functions

**Task Manager** (`src/task_manager.py`):
- In-memory task list (global or class)
- CRUD operations (add, view, update, delete, mark complete)
- Input validation
- ID generation

**Models** (`src/models/task.py`):
- Task data structure (dict or dataclass)
- Fields: id (int), title (str), description (str), status (str)

**Utilities** (`src/utils.py`):
- Display formatting (✓/✗ status indicators)
- Error message generation
- Input sanitization

**Tests** (`tests/test_task_manager.py` - optional):
- Unit tests for Task Manager operations
- Edge case tests

---

## Next Steps

✅ **Research Complete**: All technical decisions documented
➡️ **Next**: Phase 1 - Create data-model.md, contracts/, quickstart.md

**Status**: Ready for Phase 1 design artifacts
