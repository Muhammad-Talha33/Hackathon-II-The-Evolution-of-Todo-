"""
Todo Console Application - Main Entry Point

This module provides the interactive menu-driven interface for the
todo application, handling user input and orchestrating task operations.
"""

from task_manager import add_task, view_tasks, update_task, delete_task, mark_complete
from utils import format_task_display, get_int_input


def display_menu() -> None:
    """
    Display the main menu options to the user.

    Prints a formatted menu with numbered options for all available
    task management operations.
    """
    print("\n" + "=" * 40)
    print("TODO CONSOLE APPLICATION")
    print("=" * 40)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Complete")
    print("4. Update Task")
    print("5. Delete Task")
    print("6. Exit")
    print("=" * 40)


def get_menu_choice() -> int:
    """
    Get and validate the user's menu choice.

    Returns:
        Integer representing the menu choice (1-6)
        Returns 0 if input is invalid

    Examples:
        >>> # User enters "1"
        >>> get_menu_choice()
        1
        >>> # User enters "abc"
        >>> get_menu_choice()
        0
    """
    choice = get_int_input("Enter your choice (1-6): ")

    if choice is None or choice < 1 or choice > 6:
        print("Error: Invalid choice. Please enter a number between 1 and 6.")
        return 0

    return choice


def handle_add_task() -> None:
    """
    Handle the 'Add Task' menu option.

    Prompts the user for task title and description, then adds
    the task to the task list. Displays success or error message.
    """
    print("\n--- Add New Task ---")
    title = input("Enter task title: ").strip()

    if not title:
        print("Error: Task title cannot be empty")
        return

    description = input("Enter task description (optional): ").strip()

    result = add_task(title, description)

    if isinstance(result, str):
        # Error message returned
        print(result)
    else:
        # Task created successfully
        print(f"[SUCCESS] Task added successfully! [ID: {result['id']}]")


def handle_view_tasks() -> None:
    """
    Handle the 'View Tasks' menu option.

    Retrieves and displays all tasks in a formatted list.
    Shows a message if no tasks exist.
    """
    print("\n--- Task List ---")
    tasks = view_tasks()

    if not tasks:
        print("No tasks found. Add a task to get started!")
        return

    for task in tasks:
        print(format_task_display(task))
        print()  # Blank line between tasks


def handle_mark_complete() -> None:
    """
    Handle the 'Mark Complete' menu option.

    Prompts the user for a task ID and toggles its completion status.
    Displays the updated task or error message.
    """
    print("\n--- Mark Task Complete ---")

    task_id = get_int_input("Enter task ID to mark complete: ")

    if task_id is None:
        print("Error: Invalid task ID. Please enter a number.")
        return

    result = mark_complete(task_id)

    if isinstance(result, str):
        # Error message returned
        print(result)
    else:
        # Task updated successfully
        status_text = "complete" if result["status"] == "complete" else "incomplete"
        print(f"[SUCCESS] Task {task_id} marked as {status_text}")


def handle_update_task() -> None:
    """
    Handle the 'Update Task' menu option.

    Prompts the user for task ID and new values for title and/or description.
    Supports partial updates (title only, description only, or both).
    """
    print("\n--- Update Task ---")

    task_id = get_int_input("Enter task ID to update: ")

    if task_id is None:
        print("Error: Invalid task ID. Please enter a number.")
        return

    print("Leave blank to keep current value")
    new_title = input("Enter new title (or press Enter to skip): ").strip()
    new_description = input("Enter new description (or press Enter to skip): ").strip()

    # Convert empty strings to None for optional parameters
    title_param = new_title if new_title else None
    description_param = new_description if new_description else None

    if title_param is None and description_param is None:
        print("No changes made (both fields were empty)")
        return

    result = update_task(task_id, title_param, description_param)

    if isinstance(result, str):
        # Error message returned
        print(result)
    else:
        # Task updated successfully
        print(f"[SUCCESS] Task {task_id} updated successfully")


def handle_delete_task() -> None:
    """
    Handle the 'Delete Task' menu option.

    Prompts the user for a task ID and deletes the task after confirmation.
    Displays success or error message.
    """
    print("\n--- Delete Task ---")

    task_id = get_int_input("Enter task ID to delete: ")

    if task_id is None:
        print("Error: Invalid task ID. Please enter a number.")
        return

    # Show confirmation
    confirm = input(f"Are you sure you want to delete task {task_id}? (y/n): ").strip().lower()

    if confirm != 'y':
        print("Delete cancelled")
        return

    result = delete_task(task_id)

    if isinstance(result, str):
        # Error message returned
        print(result)
    else:
        # Task deleted successfully
        print(f"[SUCCESS] Task {task_id} deleted successfully")


def handle_exit() -> None:
    """
    Handle the 'Exit' menu option.

    Displays a goodbye message and prepares for clean application termination.
    """
    print("\n" + "=" * 40)
    print("Thank you for using Todo Console App!")
    print("Goodbye!")
    print("=" * 40 + "\n")


def main_loop() -> None:
    """
    Run the main application loop.

    Continuously displays the menu, gets user input, and routes to
    the appropriate handler function until the user chooses to exit.
    """
    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 0:
            # Invalid input, loop continues
            continue
        elif choice == 1:
            handle_add_task()
        elif choice == 2:
            handle_view_tasks()
        elif choice == 3:
            handle_mark_complete()
        elif choice == 4:
            handle_update_task()
        elif choice == 5:
            handle_delete_task()
        elif choice == 6:
            handle_exit()
            break  # Exit the loop


def main() -> None:
    """
    Application entry point.

    Initializes and starts the main application loop.
    """
    print("\nWelcome to Todo Console Application!")
    main_loop()


if __name__ == "__main__":
    main()
