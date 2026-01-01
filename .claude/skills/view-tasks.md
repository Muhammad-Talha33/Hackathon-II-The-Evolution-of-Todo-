# View Tasks Skill

## Purpose
This skill displays all tasks in the current in-memory list with their status indicators (complete/incomplete).

## Responsibilities
- Retrieve all tasks from the in-memory list
- Format tasks for display (ID, title, description, status)
- Return the formatted list to the console

## When to Use
- Call this skill when the user selects "View Tasks" from the menu

## Instructions

When this skill is invoked:

1. **Retrieve Tasks**
   - Access the in-memory task list
   - Get all tasks currently stored

2. **Check for Empty List**
   - If the task list is empty, display: "No tasks found. Your task list is empty."
   - Return early if no tasks exist

3. **Format Tasks for Display**
   - For each task, format the output with:
     - Task ID
     - Title
     - Description (if provided)
     - Status indicator (✓ for complete, ✗ for incomplete)

4. **Display All Tasks**
   - Present tasks in a clear, readable format
   - Show total count of tasks
   - Optionally group by status (completed vs incomplete)

## Example Output

**When tasks exist:**
```
=== Your Tasks ===

[1] ✗ Buy groceries
    Description: Get milk, eggs, and bread
    Status: incomplete

[2] ✓ Complete assignment
    Description: Finish math homework
    Status: complete

[3] ✗ Call dentist
    Status: incomplete

Total tasks: 3 (1 completed, 2 incomplete)
```

**When no tasks exist:**
```
No tasks found. Your task list is empty.
```

## Display Format Options

### Option 1: Detailed View (Default)
Shows all task information including ID, title, description, and status with visual indicators.

### Option 2: Compact View
```
Tasks:
1. ✗ Buy groceries
2. ✓ Complete assignment
3. ✗ Call dentist
```

### Option 3: Grouped by Status
```
=== Incomplete Tasks ===
1. Buy groceries - Get milk, eggs, and bread
3. Call dentist

=== Completed Tasks ===
2. Complete assignment - Finish math homework
```

## Error Handling
- If task list is not initialized: Display "Task list not initialized. Add a task to get started."
- If task list is null/undefined: Initialize empty list and display empty message
