"""MCP Server startup script."""
from src.mcp_server.server import get_mcp_server, set_session
from src.database import get_session as get_db_session


def run_mcp_server():
    """
    Run the MCP server.

    Note: In the actual implementation, the database session will be injected
    by the FastAPI application when handling chat requests, not by running
    this server independently. This is a stateless architecture where each
    request provides its own session context.
    """
    mcp = get_mcp_server()

    # For standalone testing, you would initialize a session here
    # In production, FastAPI will inject the session per request
    print("MCP Server initialized with 5 tools:")
    print("  - mcp_add_task: Create a new task")
    print("  - mcp_list_tasks: List tasks (with optional status filter)")
    print("  - mcp_complete_task: Mark a task as complete")
    print("  - mcp_delete_task: Delete a task")
    print("  - mcp_update_task: Update task title/description")
    print("\nMCP Server ready. Tools will be called by OpenAI Agent via FastAPI.")


if __name__ == "__main__":
    run_mcp_server()
