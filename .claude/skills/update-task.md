# Update Task Skill

## Purpose
This skill updates the title and/or description of an existing task based on its ID.

## Responsibilities
- Validate the task ID exists
- Update the title and/or description as provided
- Return the updated task details
- Handle errors if task ID is invalid

## When to Use
- Call this skill when the user selects "Update Task" from the menu

## Instructions

When this skill is invoked:

1. **Validate Input**
   - Ensure task ID is provided
   - Check if the task ID exists in the in-memory task list
   - If task ID is invalid or not found, return an error message

2. **Retrieve Existing Task**
   - Find the task in the task list by ID
   - Store the current task details for reference

3. **Update Task Fields**
   - Update the title if a new title is provided
   - Update the description if a new description is provided
   - If both are provided, update both fields
   - At least one field (title or description) must be provided for update
   - Preserve the task ID and status (don't modify these)

4. **Validate Updates**
   - If updating title, ensure the new title is not empty
   - Description can be empty or null (optional field)

5. **Save Changes**
   - Update the task in the in-memory list
   - Maintain all other task properties (ID, status)

6. **Return Confirmation**
   - Display the updated task details
   - Show what changed (before/after comparison if helpful)

## Example Usage

**User Input:**
- Task ID: 1
- New Title: "Buy groceries and supplies"
- New Description: "Get milk, eggs, bread, and cleaning supplies"

**Expected Output:**
```
Task updated successfully:

ID: 1
Title: Buy groceries and supplies (updated)
Description: Get milk, eggs, bread, and cleaning supplies (updated)
Status: incomplete
```

**Partial Update Example:**
```
User Input:
- Task ID: 2
- New Title: "Complete math assignment"
- Description: (not provided, keep existing)

Output:
Task updated successfully:
ID: 2
Title: Complete math assignment (updated)
Description: Finish problems 1-20 (unchanged)
Status: complete
```

## Error Handling

- **Task ID not provided**: "Error: Task ID is required for update"
- **Task ID not found**: "Error: Task with ID [X] not found"
- **No updates provided**: "Error: Please provide at least a new title or description to update"
- **Empty title**: "Error: Task title cannot be empty"
- **Task list empty**: "Error: No tasks available to update. Add a task first."
- **Invalid ID format**: "Error: Invalid task ID format. Please provide a valid numeric ID."

## Validation Rules

1. Task ID must exist in the current task list
2. At least one field (title or description) must be provided for update
3. If updating title, the new title must not be empty
4. Description updates are optional and can be set to empty
5. Task status is NOT updated by this skill (use Mark Complete skill instead)
6. Task ID cannot be changed

## Edge Cases

- **Updating to same values**: Allow, but optionally notify "No changes detected"
- **Clearing description**: Allow setting description to empty string
- **Unicode/special characters**: Support in both title and description
