# Quickstart Guide: Todo Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-28
**Audience**: Developers implementing the Phase I Todo Console App

## Purpose

This guide provides a quick reference for setting up, implementing, and testing the Todo Console Application based on the technical plan and specifications.

---

## Prerequisites

- **Python**: Version 3.13 or higher
- **Package Manager**: `uv` (recommended) or `pip`
- **Git**: For version control
- **Terminal/Console**: Windows PowerShell, Command Prompt, or Unix terminal

---

## Project Setup

### 1. Create Project Structure

```bash
# Create directories
mkdir -p src/models
mkdir -p src/skills
mkdir -p tests

# Create empty Python files
touch src/__init__.py
touch src/main.py
touch src/task_manager.py
touch src/models/__init__.py
touch src/models/task.py
touch src/utils.py
touch tests/__init__.py
touch tests/test_task_manager.py
touch README.md
```

**Expected Structure**:
```
/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point, menu loop
│   ├── task_manager.py      # CRUD operations
│   ├── utils.py             # Display & validation helpers
│   └── models/
│       ├── __init__.py
│       └── task.py          # Task data structure
├── tests/
│   ├── __init__.py
│   └── test_task_manager.py # Unit tests (optional)
├── README.md                # Usage instructions
└── requirements.txt         # Dependencies (empty for Phase I)
```

### 2. Initialize Virtual Environment

**Using uv** (recommended):
```bash
# Install uv if not already installed
pip install uv

# Create virtual environment
uv venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.\.venv\Scripts\activate.bat

# Activate (Linux/Mac)
source .venv/bin/activate
```

**Using venv** (alternative):
```bash
# Create virtual environment
python -m venv .venv

# Activate (same commands as above)
```

### 3. Verify Python Version

```bash
python --version
# Should show: Python 3.13.x or higher
```

---

## Implementation Order

Follow this sequence for implementation:

### Phase 0: Project Setup
✅ Create directory structure
✅ Initialize virtual environment
✅ Create empty files

### Phase 1: Task Model
**File**: `src/models/task.py`

**What to implement**:
- Task dictionary structure (or dataclass if preferred)
- Task type alias: `Task = dict[str, int | str]`

**Example**:
```python
# src/models/task.py
"""Task data model."""

Task = dict[str, int | str]

def create_task(task_id: int, title: str, description: str = "") -> Task:
    """Create a new task dictionary."""
    return {
        "id": task_id,
        "title": title.strip(),
        "description": description.strip(),
        "status": "incomplete"
    }
```

### Phase 2: Task Manager CRUD
**File**: `src/task_manager.py`

**What to implement**:
1. Global task list: `tasks: list[Task] = []`
2. `add_task(title, description)` → dict | str
3. `view_tasks()` → list[dict]
4. `update_task(task_id, title, description)` → dict | str
5. `delete_task(task_id)` → dict | str
6. `mark_complete(task_id)` → dict | str
7. Helper: `_generate_next_id()` → int
8. Helper: `_find_task_by_id(task_id)` → dict | None

**Reference**: See `contracts/task-manager-api.md` for function signatures

### Phase 3: Main Menu Loop
**File**: `src/main.py`

**What to implement**:
1. Display menu (options 1-6)
2. Get user input (menu choice)
3. Route to appropriate Task Manager function
4. Display results/errors
5. Loop until user selects "Exit"

**Menu Structure**:
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

### Phase 4: Utilities
**File**: `src/utils.py`

**What to implement**:
1. `validate_title(title)` → str | None
2. `validate_task_id(task_id, tasks)` → str | None
3. `format_task_display(task)` → str (with ✓/✗ indicators)
4. `get_int_input(prompt)` → int | None (safe integer input)

### Phase 5: Testing (Optional)
**File**: `tests/test_task_manager.py`

**What to test**:
- Add task with valid/invalid title
- View empty/populated task list
- Update task with valid/invalid ID
- Delete task with valid/invalid ID
- Mark complete toggle functionality
- Edge cases: empty list, whitespace titles, non-existent IDs

### Phase 6: Documentation
**File**: `README.md`

**What to include**:
- Project description
- Requirements (Python 3.13+)
- Setup instructions
- How to run: `python src/main.py`
- Feature list (Add, View, Update, Delete, Mark Complete)
- Known limitations (in-memory only, no persistence)

---

## Quick Reference: Implementation Checklist

**Task Manager Module** (`src/task_manager.py`):
- [ ] Import Task type from models
- [ ] Create global `tasks` list
- [ ] Implement `add_task()` function
- [ ] Implement `view_tasks()` function
- [ ] Implement `update_task()` function
- [ ] Implement `delete_task()` function
- [ ] Implement `mark_complete()` function
- [ ] Implement `_generate_next_id()` helper
- [ ] Implement `_find_task_by_id()` helper
- [ ] Add type hints to all functions
- [ ] Add docstrings to all public functions

**Main Module** (`src/main.py`):
- [ ] Import task_manager functions
- [ ] Create `display_menu()` function
- [ ] Create `main_loop()` function
- [ ] Handle menu choice 1 (Add Task)
- [ ] Handle menu choice 2 (View Tasks)
- [ ] Handle menu choice 3 (Update Task)
- [ ] Handle menu choice 4 (Delete Task)
- [ ] Handle menu choice 5 (Mark Complete)
- [ ] Handle menu choice 6 (Exit)
- [ ] Add error handling for invalid choices
- [ ] Add `if __name__ == "__main__"` block

**Utilities Module** (`src/utils.py`):
- [ ] Implement input validation functions
- [ ] Implement display formatting functions
- [ ] Add status indicator formatting (✓/✗)
- [ ] Add type hints and docstrings

---

## Running the Application

### Development Run

```bash
# From project root
python src/main.py
```

### Expected Behavior

1. **Start**: Display menu
2. **Add Task**: Prompt for title and description
3. **View Tasks**: Show all tasks with IDs, titles, status indicators
4. **Update Task**: Prompt for ID, new title/description
5. **Delete Task**: Prompt for ID, confirm deletion
6. **Mark Complete**: Prompt for ID, toggle status
7. **Exit**: Display goodbye message, terminate

---

## Testing

### Manual Testing Workflow

1. **Add Tasks**:
   - Add task "Buy groceries" with description
   - Add task "Complete assignment" without description
   - Try adding task with empty title (should fail)

2. **View Tasks**:
   - View all tasks (should show 2 tasks)
   - Verify IDs are 1 and 2
   - Verify status indicators (✗ for both)

3. **Mark Complete**:
   - Mark task 1 complete (status → ✓)
   - View tasks (task 1 should show ✓)
   - Mark task 1 incomplete (status → ✗)

4. **Update Task**:
   - Update task 2 title to "Complete math assignment"
   - Update task 2 description to "Problems 1-20"
   - Try updating non-existent task 999 (should fail)

5. **Delete Task**:
   - Delete task 1
   - View tasks (should show only task 2)
   - Try deleting task 1 again (should fail)

6. **Exit**:
   - Select Exit option
   - Verify app terminates cleanly

### Unit Testing (Optional)

```bash
# Run unit tests (if implemented)
python -m unittest discover tests

# Or using pytest (if installed)
pytest tests/
```

---

## Validation Checklist

Before marking complete, verify:

**Functionality**:
- [ ] All 5 CRUD operations work correctly
- [ ] Menu displays and loops properly
- [ ] Exit option terminates cleanly
- [ ] Tasks display with correct status indicators (✓/✗)

**Error Handling**:
- [ ] Empty title is rejected with clear error message
- [ ] Invalid task ID shows error message
- [ ] Invalid menu choice shows error and re-prompts
- [ ] Application never crashes from user input

**Code Quality**:
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Code follows PEP 8 style guidelines
- [ ] No code duplication (DRY principle)
- [ ] Each function has single responsibility

**Constitution Compliance**:
- [ ] In-memory storage only (no files/database)
- [ ] Menu-driven interface (no CLI arguments)
- [ ] Separation of concerns (main, task_manager, utils separate)
- [ ] Input validation prevents crashes
- [ ] Deterministic behavior (same input → same output)

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'src'`
**Solution**: Run from project root: `python src/main.py`, not `python main.py`

**Issue**: Unicode characters (✓/✗) not displaying correctly
**Solution**: Ensure terminal supports UTF-8 encoding

**Issue**: Virtual environment not activating
**Solution**: Use correct activation script for your OS/shell

**Issue**: Python version too old
**Solution**: Install Python 3.13+ from python.org

---

## Next Steps

After implementation:

1. **Test thoroughly**: Run through manual testing workflow
2. **Code review**: Check against constitution principles
3. **Documentation**: Complete README.md with usage instructions
4. **Optional**: Add unit tests for Task Manager functions
5. **Ready**: Proceed to `/sp.tasks` to generate implementation task list

---

## Resources

- **Spec**: `specs/001-todo-console-app/spec.md`
- **Data Model**: `specs/001-todo-console-app/data-model.md`
- **API Contract**: `specs/001-todo-console-app/contracts/task-manager-api.md`
- **Research**: `specs/001-todo-console-app/research.md`
- **Constitution**: `.specify/memory/constitution.md`
- **Python 3.13 Docs**: https://docs.python.org/3.13/
- **PEP 8**: https://peps.python.org/pep-0008/

---

**Status**: Quickstart guide complete - ready for implementation!
