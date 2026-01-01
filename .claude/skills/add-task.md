# Add Task Skill

## Purpose
This skill adds a new task to the in-memory task list. Each task must have a unique ID, a title, an optional description, and a default status of incomplete.

## Responsibilities
- Validate the input (title must not be empty, description optional)
- Generate a unique ID for the task
- Append the task to the current in-memory task list
- Return the newly added task details

## When to Use
- Call this skill when the user selects "Add Task" from the menu

## Instructions

When this skill is invoked:

1. **Validate Input**
   - Ensure the task title is provided and not empty
   - If title is missing or empty, return an error message
   - Description is optional and can be empty

2. **Generate Unique ID**
   - Generate a unique identifier for the task (e.g., incremental integer or UUID)
   - Ensure the ID does not conflict with existing task IDs

3. **Create Task Object**
   - Create a task object with the following structure:
     ```
     {
       id: <unique_id>,
       title: <task_title>,
       description: <task_description> (optional, can be empty string),
       status: "incomplete"
     }
     ```

4. **Add to Task List**
   - Append the new task to the in-memory task list
   - Maintain the task list in memory for the current session

5. **Return Confirmation**
   - Return the newly created task details to confirm successful addition
   - Display: "Task added successfully: [Task ID] - [Task Title]"

## Example Usage

**User Input:**
- Title: "Buy groceries"
- Description: "Get milk, eggs, and bread"

**Expected Output:**
```
Task added successfully:
ID: 1
Title: Buy groceries
Description: Get milk, eggs, and bread
Status: incomplete
```

## Error Handling
- If title is empty: "Error: Task title cannot be empty"
- If task list is not initialized: Initialize an empty list first
