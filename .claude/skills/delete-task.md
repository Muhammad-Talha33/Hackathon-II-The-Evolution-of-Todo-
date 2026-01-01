# Delete Task Skill

## Purpose
This skill removes a task from the in-memory list using its ID.

## Responsibilities
- Validate the task ID exists
- Remove the task from the list
- Return confirmation of deletion
- Handle errors if task ID is invalid

## When to Use
- Call this skill when the user selects "Delete Task" from the menu

## Instructions

When this skill is invoked:

1. **Validate Input**
   - Ensure task ID is provided
   - Verify the task ID is in a valid format (numeric)
   - Check if the task ID exists in the in-memory task list

2. **Retrieve Task Before Deletion**
   - Find the task in the task list by ID
   - Store task details for confirmation message
   - If task not found, return an error message

3. **Confirm Deletion (Optional)**
   - Optionally ask for confirmation: "Are you sure you want to delete task [ID]: [Title]?"
   - Wait for user confirmation (yes/no)
   - If user declines, cancel the deletion

4. **Remove Task**
   - Delete the task from the in-memory task list
   - Remove by ID to ensure correct task is deleted
   - Update the task list in memory

5. **Return Confirmation**
   - Display the deleted task details for confirmation
   - Show success message with task information

## Example Usage

**User Input:**
- Task ID: 2

**Expected Output:**
```
Task deleted successfully:

ID: 2
Title: Complete assignment
Description: Finish math homework
Status: complete

Task has been removed from your list.
```

**With Confirmation Prompt:**
```
Are you sure you want to delete this task?
ID: 2
Title: Complete assignment
Description: Finish math homework

Type 'yes' to confirm or 'no' to cancel: yes

Task deleted successfully. Task has been removed from your list.
```

## Error Handling

- **Task ID not provided**: "Error: Task ID is required for deletion"
- **Task ID not found**: "Error: Task with ID [X] not found"
- **Invalid ID format**: "Error: Invalid task ID format. Please provide a valid numeric ID."
- **Task list empty**: "Error: No tasks available to delete. Your task list is empty."
- **Deletion cancelled**: "Deletion cancelled. Task was not removed."

## Validation Rules

1. Task ID must be provided
2. Task ID must exist in the current task list
3. Task ID must be in valid format (numeric)
4. Task list must not be empty
5. Deletion is permanent and cannot be undone (for in-memory implementation)

## Edge Cases

- **Deleting last task**: Successfully delete and leave empty list
- **Deleting task by wrong ID**: Show clear error message with available task IDs
- **Rapid consecutive deletions**: Handle properly without index errors
- **Delete then add**: New tasks get next available ID, don't reuse deleted IDs

## Additional Features (Optional)

### Soft Delete
Instead of permanently removing, mark task as "deleted" with timestamp:
```
{
  id: 2,
  title: "Complete assignment",
  description: "Finish math homework",
  status: "complete",
  deleted: true,
  deletedAt: "2025-12-28T08:15:00Z"
}
```

### Undo Delete
Store last deleted task in memory to allow undo:
```
Last deleted task stored. Type 'undo delete' to restore.
```

## Safety Considerations

- **Confirmation**: Consider requiring confirmation for destructive operations
- **Logging**: Log deletion events for audit trail
- **Backup**: Optionally maintain deleted tasks in a separate list for recovery
