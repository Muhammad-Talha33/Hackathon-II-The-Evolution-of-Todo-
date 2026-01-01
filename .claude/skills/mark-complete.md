# Mark Complete Skill

## Purpose
This skill toggles a task's completion status (complete/incomplete) based on its ID.

## Responsibilities
- Validate the task ID exists
- Toggle the completion status
- Return the updated task details
- Handle errors if task ID is invalid

## When to Use
- Call this skill when the user selects "Mark Task Complete" from the menu

## Instructions

When this skill is invoked:

1. **Validate Input**
   - Ensure task ID is provided
   - Verify the task ID is in a valid format (numeric)
   - Check if the task ID exists in the in-memory task list

2. **Retrieve Existing Task**
   - Find the task in the task list by ID
   - Store the current status for reference
   - If task not found, return an error message

3. **Toggle Completion Status**
   - If current status is "incomplete", change to "complete"
   - If current status is "complete", change to "incomplete"
   - Update the task status in the in-memory list

4. **Save Changes**
   - Update the task in the task list with the new status
   - Maintain all other task properties (ID, title, description)

5. **Return Confirmation**
   - Display the updated task with new status
   - Show clear indication of status change

## Example Usage

**Marking Incomplete Task as Complete:**
```
User Input: Task ID: 1

Output:
Task status updated successfully:

ID: 1
Title: Buy groceries
Description: Get milk, eggs, and bread
Status: complete ✓ (changed from incomplete)
```

**Marking Complete Task as Incomplete:**
```
User Input: Task ID: 2

Output:
Task status updated successfully:

ID: 2
Title: Complete assignment
Description: Finish math homework
Status: incomplete ✗ (changed from complete)
```

## Error Handling

- **Task ID not provided**: "Error: Task ID is required to mark completion status"
- **Task ID not found**: "Error: Task with ID [X] not found"
- **Invalid ID format**: "Error: Invalid task ID format. Please provide a valid numeric ID."
- **Task list empty**: "Error: No tasks available. Add a task first."

## Validation Rules

1. Task ID must be provided
2. Task ID must exist in the current task list
3. Task ID must be in valid format (numeric)
4. Status can only be "complete" or "incomplete"
5. Title and description remain unchanged

## Status Display

Use visual indicators for clarity:
- **Complete**: ✓ or "complete"
- **Incomplete**: ✗ or "incomplete"

## Alternative Implementation Options

### Option 1: Separate Actions (More Explicit)
Instead of toggle, have two separate operations:
- "Mark as Complete" - only sets to complete
- "Mark as Incomplete" - only sets to incomplete

### Option 2: Toggle with Confirmation
```
Current status: incomplete
Change to complete? (yes/no): yes
Task marked as complete ✓
```

### Option 3: Batch Operations
Allow marking multiple tasks at once:
```
User Input: Task IDs: 1, 3, 5

Output:
Tasks updated successfully:
- Task 1: marked as complete ✓
- Task 3: marked as complete ✓
- Task 5: marked as complete ✓
```

## Edge Cases

- **Already complete**: Toggle to incomplete (don't treat as error)
- **Already incomplete**: Toggle to complete (don't treat as error)
- **Rapid status changes**: Allow, no restriction on toggling frequency

## Optional Enhancements

### Add Timestamp
Track when task was completed:
```
{
  id: 1,
  title: "Buy groceries",
  description: "Get milk, eggs, and bread",
  status: "complete",
  completedAt: "2025-12-28T08:20:00Z"
}
```

### Add Completion Message
```
Task completed successfully! 🎉
ID: 1
Title: Buy groceries
Completed at: 2025-12-28 08:20:00
```

### Statistics Update
After marking complete, optionally show:
```
Task marked as complete ✓
Progress: 3 of 5 tasks completed (60%)
```
