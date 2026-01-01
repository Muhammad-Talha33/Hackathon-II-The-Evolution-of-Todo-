---
id: 006
title: Bugfix - Import Errors and Unicode Issues
stage: green
date: 2025-12-28
surface: agent
model: claude-sonnet-4-5
feature: 001-todo-console-app
branch: 001-todo-console-app
user: user
command: /sp.implement
labels: ["bugfix", "imports", "unicode", "windows-compatibility", "encoding"]
links:
  spec: specs/001-todo-console-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/main.py
  - src/task_manager.py
  - src/utils.py
tests:
  - Manual testing: Application runs successfully from src/ directory
  - Manual testing: Add task, view tasks, exit workflow completed
  - Windows console compatibility verified
---

## Prompt

User reported error when running the application from src/ directory:
```
src>python main.py
Traceback (most recent call last):
  File "C:\Users\Samreen Computer\Desktop\New folder (6)\src\main.py", line 8, in <module>
    from src.task_manager import add_task, view_tasks, update_task, delete_task, mark_complete
ModuleNotFoundError: No module named 'src
```

## Response snapshot

Fixed two critical issues preventing the application from running on Windows:

### Issue 1: Module Import Errors

**Problem**: When running `python main.py` from the `src/` directory, Python couldn't find the `src` module because the script was already inside the `src/` package. Absolute imports like `from src.task_manager import ...` failed with `ModuleNotFoundError`.

**Root Cause**: The application used absolute imports (`from src.X import Y`) which require running from the parent directory. When executed from within `src/`, Python looks for a `src` package relative to the current directory.

**Solution**: Changed all imports to relative imports:
- `src/main.py`: Changed `from src.task_manager` → `from task_manager`
- `src/main.py`: Changed `from src.utils` → `from utils`
- `src/task_manager.py`: Changed `from src.models.task` → `from models.task`

**Files Modified**:
- `src/main.py:8-9` - Import statements
- `src/task_manager.py:9` - Import statement

### Issue 2: Unicode Encoding Errors (Windows Console)

**Problem**: Windows console (cp1252 encoding) cannot display Unicode emoji and special characters, causing `UnicodeEncodeError`:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f3af' in position 39
```

**Root Cause**: Application used Unicode characters:
- Emojis: 🎯 (dart/target) and 👋 (waving hand)
- Check marks: ✓ (check) and ✗ (x mark)

Windows Command Prompt uses cp1252 encoding by default, which doesn't support these characters.

**Solution**: Replaced all Unicode characters with ASCII-safe alternatives:
- `🎯` → Removed from welcome message
- `👋` → Removed from goodbye message
- `✓` → `[SUCCESS]` prefix for success messages
- Status indicators: `✓` → `[X]`, `✗` → `[ ]`

**Files Modified**:
- `src/main.py:79` - Success message for add task
- `src/main.py:124` - Success message for mark complete
- `src/main.py:161` - Success message for update task
- `src/main.py:193` - Success message for delete task
- `src/main.py:204` - Goodbye message (removed emoji)
- `src/main.py:243` - Welcome message (removed emoji)
- `src/utils.py:71` - Status indicator function
- `src/utils.py:63-69` - Updated docstring examples

### Verification

**Test Execution**:
```bash
cd "C:\Users\Samreen Computer\Desktop\New folder (6)\src"
python main.py
```

**Test Flow**:
1. Add task: "Buy groceries" with description "Get milk and eggs"
2. View tasks: Display task list with [ ] status indicator
3. Exit: Clean termination

**Test Result**: ✅ ALL PASSED
```
Welcome to Todo Console Application!
[...menu displayed...]
[SUCCESS] Task added successfully! [ID: 1]
[1] [ ] Buy groceries
    Description: Get milk and eggs
Thank you for using Todo Console App!
Goodbye!
```

## Outcome

- ✅ Impact: Application now runs correctly from src/ directory on Windows systems
- 🧪 Tests: Manual testing passed - add task, view tasks, exit workflow completed successfully
- 📁 Files: Modified 3 files (main.py, task_manager.py, utils.py) to fix imports and Unicode issues
- 🔁 Next prompts: Application is ready for interactive use. Consider adding .bat launcher script for easier execution on Windows.
- 🧠 Reflection: Two Windows compatibility issues resolved. Import errors fixed by switching to relative imports (allows running from src/ directory). Unicode errors fixed by replacing special characters with ASCII-safe alternatives ([SUCCESS], [X], [ ]). Application is now fully compatible with Windows Command Prompt (cp1252 encoding).

## Evaluation notes (flywheel)

- Failure modes observed: Windows console encoding limitations (cp1252 vs UTF-8), Python module resolution when running scripts from package directories
- Graders run and results (PASS/FAIL): Manual Testing - PASS (application runs, workflow completes), Import Resolution - PASS (no ModuleNotFoundError), Unicode Safety - PASS (no UnicodeEncodeError)
- Prompt variant (if applicable): Standard bugfix workflow - identify, diagnose, fix, verify
- Next experiment (smallest change to try): Consider UTF-8 mode for Python (PYTHONUTF8=1) as alternative solution, or create launcher script that handles encoding configuration
