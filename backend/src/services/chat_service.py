"""Chat service for stateless orchestration of chat interactions.

This service is fully stateless - it does NOT maintain any session storage.
Every request:
1. Fetches conversation history from database
2. Creates fresh agent with MCP tools
3. Calls agent with history context
4. Persists messages to database
"""
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from agents import Agent, Runner
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.schemas.chat import ChatResponse
from src.agents.todo_agent import get_agent_with_tools
from src.mcp_server.server import (
    set_session,
    mcp_add_task,
    mcp_list_tasks,
    mcp_complete_task,
    mcp_delete_task,
    mcp_update_task
)


async def get_or_create_conversation(
    user_id: UUID,
    conversation_id: Optional[str],
    db: AsyncSession
) -> Conversation:
    """
    Fetch existing conversation or create a new one.

    Args:
        user_id: Current user's UUID
        conversation_id: Optional conversation ID to continue
        db: Database session

    Returns:
        Conversation object (existing or newly created)

    Raises:
        ValueError: If conversation_id provided but not found or belongs to different user
    """
    if conversation_id:
        # Fetch existing conversation
        try:
            conv_uuid = UUID(conversation_id)
        except ValueError:
            raise ValueError(f"Invalid conversation_id format: {conversation_id}")

        statement = select(Conversation).where(
            Conversation.id == conv_uuid,
            Conversation.user_id == user_id
        )
        result = await db.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise ValueError(
                f"Conversation {conversation_id} not found or does not belong to user"
            )

        # Update timestamp
        conversation.updated_at = datetime.utcnow()
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return conversation

    # Create new conversation
    new_conversation = Conversation(
        id=uuid4(),
        user_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)

    return new_conversation


async def load_conversation_history(
    conversation_id: UUID,
    db: AsyncSession,
    limit: int = 50
) -> List[Dict[str, str]]:
    """
    Load conversation history from database for agent context.

    Fetches the last N messages to provide context to the agent.
    This enables stateless architecture - context is reconstructed from DB every request.

    Args:
        conversation_id: UUID of the conversation
        db: Database session
        limit: Maximum number of messages to load (default 50)

    Returns:
        List of message dicts with 'role' and 'content' keys for agent context
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(statement)
    messages = result.scalars().all()

    # Reverse to get chronological order (oldest first)
    messages = list(reversed(messages))

    # Convert to agent context format
    history = [
        {
            "role": msg.role.value,
            "content": msg.content
        }
        for msg in messages
    ]

    return history


async def save_message(
    conversation_id: UUID,
    role: str,
    content: str,
    db: AsyncSession
) -> Message:
    """
    Persist a single message to the database.

    Args:
        conversation_id: UUID of the conversation
        role: Message role ('user' or 'assistant')
        content: Message text content
        db: Database session

    Returns:
        Created Message object

    Raises:
        ValueError: If role is invalid
    """
    if role not in ["user", "assistant"]:
        raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")

    message = Message(
        id=uuid4(),
        conversation_id=conversation_id,
        role=MessageRole(role),
        content=content,
        created_at=datetime.utcnow()
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message


async def process_chat_message(
    user_id: UUID,
    message: str,
    conversation_id: Optional[str],
    db: AsyncSession
) -> ChatResponse:
    """
    Main stateless orchestration function for chat interactions.

    This function implements the stateless architecture:
    1. Get/create conversation from database
    2. Load conversation history from database (NO session storage)
    3. Create fresh agent instance with MCP tools
    4. Run agent with message and history context
    5. Save user message and agent response to database
    6. Return ChatResponse

    Args:
        user_id: Current user's UUID
        message: User's message text
        conversation_id: Optional conversation ID to continue
        db: Database session

    Returns:
        ChatResponse with conversation_id, agent message, and timestamp

    Raises:
        ValueError: If conversation not found or MCP/agent errors occur
        RuntimeError: If agent execution fails
    """
    # Step 1: Get or create conversation
    conversation = await get_or_create_conversation(user_id, conversation_id, db)

    # Step 2: Load conversation history from database (stateless!)
    history = await load_conversation_history(conversation.id, db)

    # Step 3: Create fresh agent with MCP tools
    # Inject database session into MCP server
    set_session(db)

    # Get MCP tools (imported directly from server module)
    tools = [
        mcp_add_task,
        mcp_list_tasks,
        mcp_complete_task,
        mcp_delete_task,
        mcp_update_task
    ]

    # Debug: check tool types
    print(f"DEBUG: Tool types: {[type(t).__name__ for t in tools]}")
    print(f"DEBUG: First tool has name: {hasattr(tools[0], 'name')}")
    if hasattr(tools[0], 'name'):
        print(f"DEBUG: First tool name: {tools[0].name}")

    # Create fresh agent (stateless - no built-in session storage)
    try:
        agent = get_agent_with_tools(tools)
        print(f"DEBUG: Agent created successfully")
    except Exception as e:
        print(f"DEBUG: Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Step 4: Run agent with message and history context
    try:
        # Run agent with user message (async version)
        # The user_id is passed via context for MCP tools to use
        print(f"DEBUG: About to run agent with message: {message}")
        print(f"DEBUG: Agent type: {type(agent)}")
        print(f"DEBUG: Agent tools: {[t.name for t in agent.tools]}")

        result = await Runner.run(
            starting_agent=agent,
            input=message,
            context={"user_id": str(user_id)}
        )

        print(f"DEBUG: Agent run completed")
        print(f"DEBUG: RunResult type: {type(result)}")
        print(f"DEBUG: RunResult attributes: {dir(result)}")

        # Extract agent's response from result
        # RunResult has 'final_output' attribute for the agent's response
        if hasattr(result, 'final_output'):
            agent_message = str(result.final_output) if result.final_output else "I'm sorry, I couldn't process that."
        elif hasattr(result, 'output'):
            agent_message = str(result.output) if result.output else "I'm sorry, I couldn't process that."
        else:
            # Fallback: try to get any text response
            agent_message = str(result)

    except Exception as e:
        print(f"DEBUG: Exception during agent run: {e}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Agent execution failed: {str(e)}")

    # Step 5: Save user message and agent response
    await save_message(conversation.id, "user", message, db)
    await save_message(conversation.id, "assistant", agent_message, db)

    # Step 6: Return ChatResponse
    return ChatResponse(
        conversation_id=str(conversation.id),
        message=agent_message,
        created_at=datetime.utcnow()
    )
