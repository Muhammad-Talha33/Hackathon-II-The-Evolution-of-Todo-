# Implementation Plan: Todo Console Application

**Branch**: `001-todo-console-app` | **Date**: 2025-12-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-console-app/spec.md`

## Summary

Phase I Todo In-Memory Python Console Application provides a menu-driven command-line interface for basic task management. Users can add, view, update, delete, and mark tasks complete. All task data is stored exclusively in memory (volatile, lost on exit). The implementation prioritizes simplicity, clean code (PEP 8, type hints, docstrings), deterministic behavior, and robust error handling. No external dependencies required - uses Python 3.13+ standard library only.

**Technical Approach**:
- **Architecture**: Separation of concerns with Main Menu (orchestration), Task Manager (business logic), and Utilities (helpers)
- **Data Storage**: In-memory Python list of task dictionaries
- **User Interface**: Interactive menu-driven CLI with numbered options (1-6)
- **Validation**: Comprehensive input validation preventing all crashes
- **Testing**: Manual testing workflow + optional unittest for CRUD operations

---

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (standard library only)
**Storage**: In-memory Python list (no persistence)
**Testing**: Manual testing + optional `unittest` for Task Manager module
**Target Platform**: Cross-platform (Windows, Linux, macOS) - any system with Python 3.13+ and terminal support
**Project Type**: Single console application
**Performance Goals**: Instant response (<1 second) for up to 100 tasks
**Constraints**: In-memory only (no files/databases), menu-driven only (no CLI arguments), single-user/single-threaded
**Scale/Scope**: Small utility app, ~5 modules, ~500-800 lines of code total

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Check (Phase 0)

**Principle I - In-Memory Task Management**: ✅ PASS
- Tasks stored in Python list during runtime
- No file or database persistence
- Aligns with NON-NEGOTIABLE constraint

**Principle II - Separation of Concerns**: ✅ PASS
- Agent Layer: `src/main.py` (menu display, user input, routing)
- Skills Layer: `src/task_manager.py` (CRUD operations)
- Data Layer: In-memory task list with Task model
- Each layer independently testable

**Principle III - Input Validation and Error Handling**: ✅ PASS
- Title validation: non-empty, no whitespace-only
- ID validation: positive integer, must exist
- Error messages include what went wrong + how to fix
- No crashes from user input

**Principle IV - Deterministic and Explainable Behavior**: ✅ PASS
- Sequential ID generation (1, 2, 3...)
- Explicit status changes with confirmation
- Consistent display formatting
- Same input → same output

**Principle V - Code Quality and Maintainability**: ✅ PASS
- PEP 8 style guidelines
- Type hints for all functions (Python 3.13+ syntax)
- Docstrings for all public functions
- SRP and DRY principles applied

**Technical Standards - Project Structure**: ✅ PASS
- Follows mandated structure: `/src`, `/tests`, `README.md`
- Task data model matches constitution schema
- Menu-driven interface (no CLI args)
- Python 3.13+ compatible

### Post-Design Check (Phase 1)

**Architecture Review**: ✅ PASS
- research.md: All decisions documented with rationale
- data-model.md: Task entity defined with validation rules
- contracts/task-manager-api.md: Function signatures and error handling specified
- quickstart.md: Implementation guide created

**All Constitution Gates**: ✅ PASSED

---

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-console-app/
├── spec.md                     # Feature specification (user stories, requirements)
├── plan.md                     # This file (/sp.plan command output)
├── research.md                 # Phase 0 output - technical decisions
├── data-model.md               # Phase 1 output - Task entity and validation
├── quickstart.md               # Phase 1 output - implementation guide
├── contracts/
│   └── task-manager-api.md     # Phase 1 output - function signatures
├── checklists/
│   └── requirements.md         # Specification quality validation
└── tasks.md                    # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
/
├── src/                        # All source code
│   ├── __init__.py             # Package marker
│   ├── main.py                 # Entry point and menu loop
│   ├── task_manager.py         # CRUD operations and in-memory list
│   ├── utils.py                # Display formatting and validation helpers
│   └── models/
│       ├── __init__.py         # Package marker
│       └── task.py             # Task data structure and creation
│
├── tests/                      # Optional test files
│   ├── __init__.py             # Package marker
│   └── test_task_manager.py   # Unit tests for Task Manager CRUD operations
│
├── README.md                   # User-facing setup and usage instructions
└── requirements.txt            # Dependencies (empty for Phase I)
```

**Structure Decision**: Selected **Single Project** structure (Option 1 from template). This is a standalone Python console application with no web frontend, backend, or mobile components. All code resides in `/src` with optional tests in `/tests`.

---

## Complexity Tracking

> **No Constitution violations** - all gates passed. This section intentionally left empty.

---

## Architecture & Design

### High-Level Module Design

#### 1. Main Application Module (`src/main.py`)

**Responsibility**: Application entry point, menu display, user input, routing

**Key Functions**:
- `display_menu()` → None: Display menu options 1-6
- `get_menu_choice()` → int: Get and validate user menu selection
- `handle_add_task()` → None: Prompt for title/description, call task_manager.add_task()
- `handle_view_tasks()` → None: Call task_manager.view_tasks(), display formatted output
- `handle_update_task()` → None: Prompt for ID/title/description, call task_manager.update_task()
- `handle_delete_task()` → None: Prompt for ID, call task_manager.delete_task()
- `handle_mark_complete()` → None: Prompt for ID, call task_manager.mark_complete()
- `main_loop()` → None: Main menu loop until user selects Exit
- `main()` → None: Entry point with `if __name__ == "__main__"`

**Dependencies**:
- `task_manager` module for CRUD operations
- `utils` module for input validation and display formatting

#### 2. Task Manager Module (`src/task_manager.py`)

**Responsibility**: Maintain in-memory task list, implement CRUD operations, validate inputs

**Global State**:
```python
tasks: list[dict] = []  # In-memory task list
```

**Public API Functions**:
- `add_task(title: str, description: str = "") -> dict | str`
- `view_tasks() -> list[dict]`
- `update_task(task_id: int, title: str | None = None, description: str | None = None) -> dict | str`
- `delete_task(task_id: int) -> dict | str`
- `mark_complete(task_id: int) -> dict | str`

**Private Helper Functions**:
- `_generate_next_id() -> int`: Generate next sequential ID
- `_find_task_by_id(task_id: int) -> dict | None`: Find task by ID

**Full API contract**: See `contracts/task-manager-api.md`

#### 3. Models Module (`src/models/task.py`)

**Responsibility**: Task data structure definition

**Exports**:
```python
Task = dict[str, int | str]  # Type alias

def create_task(task_id: int, title: str, description: str = "") -> Task:
    """Create a new task dictionary with default status 'incomplete'."""
    return {
        "id": task_id,
        "title": title.strip(),
        "description": description.strip(),
        "status": "incomplete"
    }
```

#### 4. Utilities Module (`src/utils.py`)

**Responsibility**: Input validation, display formatting, error messages

**Key Functions**:
- `validate_title(title: str | None) -> str | None`: Returns error message if invalid
- `validate_task_id(task_id: int, tasks: list[Task]) -> str | None`: Returns error message if invalid
- `format_task_display(task: Task) -> str`: Format task for display with ✓/✗ indicators
- `format_status_indicator(status: str) -> str`: Convert "complete"/"incomplete" to ✓/✗
- `get_int_input(prompt: str) -> int | None`: Safely get integer input from user

---

## Data Flow

### User Journey: Add Task

```
User → Main Menu → Select "1. Add Task"
   ↓
Main.handle_add_task()
   ↓ Prompt title
User inputs: "Buy groceries"
   ↓ Prompt description
User inputs: "Get milk, eggs, bread"
   ↓
task_manager.add_task(title, description)
   ↓ Validate title (non-empty)
   ↓ Generate next ID (e.g., 3)
   ↓ Create task dict
   ↓ Append to tasks list
   ↓ Return task dict
   ↓
Main displays: "Task added successfully: ID 3"
   ↓
Return to menu
```

### User Journey: View Tasks

```
User → Main Menu → Select "2. View Tasks"
   ↓
Main.handle_view_tasks()
   ↓
task_manager.view_tasks()
   ↓ Return copy of tasks list
   ↓
Main formats each task:
   [1] ✗ Buy groceries
       Description: Get milk, eggs, bread
       Status: incomplete
   ↓
Display to user
   ↓
Return to menu
```

### Error Handling Flow

```
User → Selects "5. Mark Complete"
   ↓
Main prompts: "Enter task ID:"
   ↓
User inputs: "999" (non-existent)
   ↓
task_manager.mark_complete(999)
   ↓ _find_task_by_id(999) → None
   ↓ Return error: "Error: Task with ID 999 not found"
   ↓
Main displays error message
   ↓
Return to menu (no crash)
```

---

## Implementation Decisions

### Decision 1: Data Storage

| Option | Tradeoff |
|--------|----------|
| ✅ **In-memory list** | ✅ Simplest, no dependencies<br>❌ Data lost on exit (acceptable Phase I constraint) |
| File-based (JSON/CSV) | ❌ Violates Phase I constitution |
| Database (SQLite) | ❌ Violates Phase I constitution, adds complexity |

**Choice**: In-memory Python list (aligns with Constitution Principle I - NON-NEGOTIABLE)

### Decision 2: User Input Method

| Option | Tradeoff |
|--------|----------|
| ✅ **Menu-driven CLI** | ✅ User-friendly, no automation needed<br>❌ Cannot script operations |
| CLI arguments | ❌ Violates Phase I constitution |
| Mixed (menu + args) | ❌ Unnecessary complexity |

**Choice**: Menu-driven interactive CLI (aligns with constitution requirement)

### Decision 3: Task IDs

| Option | Tradeoff |
|--------|----------|
| ✅ **Sequential integers** | ✅ Simple, readable, deterministic<br>❌ IDs reset each session (acceptable) |
| UUIDs | ❌ Not user-friendly for console input |
| Random integers | ❌ Non-deterministic, potential collisions |

**Choice**: Sequential integers starting from 1

### Decision 4: Display Format

| Option | Tradeoff |
|--------|----------|
| ✅ **Text with ✓/✗** | ✅ Clear, universally supported<br>❌ Minimal formatting vs GUI |
| ASCII [X]/[ ] | ❌ Less visually appealing |
| Rich tables | ❌ Adds dependency |
| ANSI colors | ❌ May not work in all terminals |

**Choice**: Text-based with Unicode status indicators

### Decision 5: Error Handling

| Option | Tradeoff |
|--------|----------|
| ✅ **Informative messages** | ✅ Better UX, guides user<br>❌ Slightly more code |
| Silent failures | ❌ Poor UX, violates constitution |
| Exceptions | ❌ Can crash app, violates constitution |

**Choice**: Informative error messages with recovery guidance (aligns with Constitution Principle III)

**Full decision rationale**: See `research.md`

---

## Testing & Validation Strategy

### Manual Testing Workflow

**Prerequisites**: Application built and running

**Test Scenarios**:

1. **Add Task - Valid Input**
   - Action: Select "Add Task", enter title "Buy groceries", description "Get milk"
   - Expected: Task added with unique ID, status "incomplete", confirmation displayed
   - Pass Criteria: Task appears in View Tasks with correct details

2. **Add Task - Empty Title**
   - Action: Select "Add Task", enter empty title ""
   - Expected: Error message "Error: Task title cannot be empty"
   - Pass Criteria: No task added, error displayed, return to menu

3. **View Tasks - Empty List**
   - Action: Select "View Tasks" when no tasks exist
   - Expected: Message "No tasks found. Your task list is empty."
   - Pass Criteria: Clear empty state message

4. **View Tasks - Populated List**
   - Action: Add 3 tasks, then select "View Tasks"
   - Expected: All 3 tasks displayed with ID, title, description, status (✗)
   - Pass Criteria: All fields correct, status indicators visible

5. **Mark Complete - Toggle Status**
   - Action: Add task, mark as complete, view tasks
   - Expected: Status changes from ✗ to ✓
   - Pass Criteria: Status indicator updates correctly

6. **Mark Complete - Invalid ID**
   - Action: Select "Mark Complete", enter ID 999 (non-existent)
   - Expected: Error message "Error: Task with ID 999 not found"
   - Pass Criteria: Error displayed, no crash

7. **Update Task - Valid**
   - Action: Add task "Buy groceries", update to "Buy groceries and supplies"
   - Expected: Title updated, description preserved (if not changed)
   - Pass Criteria: Changes reflected in View Tasks

8. **Update Task - Empty Title**
   - Action: Try to update task with empty title
   - Expected: Error message "Error: Task title cannot be empty"
   - Pass Criteria: Task unchanged, error displayed

9. **Delete Task - Valid ID**
   - Action: Add task, delete it by ID, view tasks
   - Expected: Task removed from list, confirmation displayed
   - Pass Criteria: Task no longer appears in list

10. **Delete Task - Invalid ID**
    - Action: Select "Delete Task", enter ID 999
    - Expected: Error message "Error: Task with ID 999 not found"
    - Pass Criteria: Error displayed, no tasks affected

11. **Exit Application**
    - Action: Select "Exit"
    - Expected: Goodbye message, clean termination
    - Pass Criteria: App exits without errors

### Edge Cases

- Whitespace-only titles → Rejected with error
- Non-numeric task ID input → Handled gracefully
- Invalid menu choice (e.g., 7) → Error, re-prompt
- Very long titles/descriptions → Accepted and displayed

### Optional Unit Testing

**File**: `tests/test_task_manager.py`

**Test Coverage**:
```python
import unittest
from src.task_manager import add_task, view_tasks, update_task, delete_task, mark_complete

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        # Reset tasks list before each test
        ...

    def test_add_task_valid(self):
        # Test adding task with valid title
        ...

    def test_add_task_empty_title(self):
        # Test adding task with empty title returns error
        ...

    def test_view_tasks_empty(self):
        # Test viewing empty task list
        ...

    def test_mark_complete_toggle(self):
        # Test toggling task status
        ...

    def test_delete_task_invalid_id(self):
        # Test deleting non-existent task
        ...
```

**Run Tests**:
```bash
python -m unittest discover tests
```

---

## Quality Validation

### Code Quality Checklist

**PEP 8 Compliance**:
- [ ] Line length <100 characters
- [ ] snake_case naming for functions/variables
- [ ] Proper spacing (2 blank lines between top-level definitions)
- [ ] Import order: standard library, third-party, local

**Type Hints** (Python 3.13+):
- [ ] All function parameters have type hints
- [ ] All function return values have type hints
- [ ] Use modern syntax: `list[dict]`, `str | None` (not `List[dict]`, `Optional[str]`)

**Docstrings**:
- [ ] All public functions have docstrings
- [ ] Docstring format: Google-style or NumPy-style
- [ ] Includes: brief description, Args, Returns, Raises (if applicable)

**Single Responsibility Principle**:
- [ ] Each function does one thing
- [ ] Functions are <30 lines (guideline, not strict)
- [ ] Clear, descriptive function names

**DRY (Don't Repeat Yourself)**:
- [ ] No code duplication
- [ ] Common validation logic in utils module
- [ ] Reusable display formatting functions

### Deterministic Behavior Validation

- [ ] Same inputs always produce same outputs
- [ ] ID generation is sequential and predictable
- [ ] No random elements in task creation/display
- [ ] Error messages are consistent for same error type

### User Experience Validation

- [ ] Menu is clear and intuitive
- [ ] Error messages state what went wrong + how to fix
- [ ] No crashes from any user input
- [ ] Operations complete in <1 second (for ≤100 tasks)

### Constitution Compliance

- [ ] In-memory storage only (no files/databases)
- [ ] Menu-driven interface (no CLI arguments)
- [ ] Separation of concerns (main, task_manager, utils separate)
- [ ] Input validation prevents all crashes
- [ ] All code follows Python 3.13+ standards

---

## Implementation Phases

| Phase | Deliverables | Estimated Lines of Code |
|-------|--------------|-------------------------|
| **Phase 0** | Project structure, `README.md` | ~50 (docs) |
| **Phase 1** | `src/models/task.py` | ~30 |
| **Phase 2** | `src/task_manager.py` (CRUD operations) | ~200 |
| **Phase 3** | `src/main.py` (menu loop) | ~150 |
| **Phase 4** | `src/utils.py` (validation, formatting) | ~100 |
| **Phase 5** | `tests/test_task_manager.py` (optional) | ~150 |
| **Phase 6** | Quality checks, documentation | ~0 (review) |

**Total Estimated LOC**: ~500-800 lines

### Phase Sequence

1. **Phase 0**: Setup (`/src`, `/tests`, `README.md`, virtual environment)
2. **Phase 1**: Task Model (data structure definition)
3. **Phase 2**: Task Manager (CRUD operations, validation)
4. **Phase 3**: Main Module (menu loop, user interaction)
5. **Phase 4**: Utilities (input validation, display formatting)
6. **Phase 5**: Testing (unit tests, manual workflow)
7. **Phase 6**: Quality Validation (PEP 8, type hints, docstrings)

**Implementation Order**: Sequential (each phase builds on previous)

**Reference Guide**: See `quickstart.md` for detailed implementation checklist

---

## Deliverables

**Required**:
- `/src` directory with source code (main.py, task_manager.py, utils.py, models/task.py)
- `README.md` with setup and usage instructions

**Optional**:
- `/tests` directory with unit tests
- `requirements.txt` (empty for Phase I, but good practice)

**Documentation Artifacts** (already created):
- ✅ `research.md` - Technical decisions and rationale
- ✅ `data-model.md` - Task entity and validation rules
- ✅ `contracts/task-manager-api.md` - Function signatures
- ✅ `quickstart.md` - Implementation guide

---

## Next Steps

✅ **Planning Complete**: All design artifacts created

**Ready for**:
➡️ `/sp.tasks` - Generate actionable task list from this plan
➡️ `/sp.implement` - Execute tasks and build the application

**Implementation Resources**:
- **Quickstart Guide**: `specs/001-todo-console-app/quickstart.md`
- **API Contract**: `specs/001-todo-console-app/contracts/task-manager-api.md`
- **Data Model**: `specs/001-todo-console-app/data-model.md`
- **Research Decisions**: `specs/001-todo-console-app/research.md`

---

**Status**: Implementation plan complete and validated against constitution ✅
