# Todo Console Application

A simple Python console application for managing tasks in memory.

## Features

- Add tasks with titles and descriptions
- View all tasks with status indicators
- Mark tasks as complete/incomplete
- Update task details
- Delete tasks
- Interactive menu-driven interface

## Requirements

- Python 3.13+
- No external dependencies required for Phase I

## Setup

1. Clone this repository
2. Navigate to the project directory
3. Run the application:
   ```bash
   python src/main.py
   ```

## Usage

The application presents an interactive menu with the following options:

1. **Add Task** - Create a new task with title and optional description
2. **View Tasks** - Display all tasks with their status (✓ complete, ✗ incomplete)
3. **Mark Complete** - Toggle task completion status
4. **Update Task** - Modify task title and/or description
5. **Delete Task** - Remove a task from the list
6. **Exit** - Close the application

### Example Session

```
Welcome to Todo Console Application! 🎯

========================================
TODO CONSOLE APPLICATION
========================================
1. Add Task
2. View Tasks
3. Mark Complete
4. Update Task
5. Delete Task
6. Exit
========================================
Enter your choice (1-6): 1

--- Add New Task ---
Enter task title: Buy groceries
Enter task description (optional): Get milk, eggs, and bread
✓ Task added successfully! [ID: 1]

Enter your choice (1-6): 2

--- Task List ---
[1] ✗ Buy groceries
    Description: Get milk, eggs, and bread

Enter your choice (1-6): 3

--- Mark Task Complete ---
Enter task ID to mark complete: 1
✓ Task 1 marked as complete

Enter your choice (1-6): 6

========================================
Thank you for using Todo Console App!
Goodbye! 👋
========================================
```

## Project Structure

```
src/
├── __init__.py
├── main.py              # Entry point and menu loop
├── task_manager.py      # Task CRUD operations
├── utils.py             # Validation and formatting utilities
└── models/
    ├── __init__.py
    └── task.py          # Task data structure
tests/
└── __init__.py
```

## Development

This project follows:
- PEP 8 style guidelines
- Type hints for all function signatures
- Comprehensive docstrings
- Separation of concerns architecture

For implementation details, see the design documents in `specs/001-todo-console-app/`.

## License

This is a learning project for demonstrating Spec-Driven Development principles.
