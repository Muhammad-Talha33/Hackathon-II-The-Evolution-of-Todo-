"""Conversations router for retrieving chat history."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from typing import List
from uuid import UUID

from src.database import get_db
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.dependencies.auth import get_current_user
from src.schemas.chat import ConversationSummary, ConversationMessagesResponse, MessageSchema

router = APIRouter()


@router.get("/conversations", response_model=List[ConversationSummary], status_code=status.HTTP_200_OK)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all conversations for the authenticated user.

    Returns conversations ordered by most recently updated first.

    Args:
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        List of ConversationSummary objects with id, timestamps, and message count

    Raises:
        HTTPException 401: If user not authenticated
    """
    # Query conversations for the current user
    statement = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    result = await db.execute(statement)
    conversations = result.scalars().all()

    # Build response with message counts
    conversation_summaries = []
    for conv in conversations:
        # Count messages in this conversation
        count_statement = select(func.count(Message.id)).where(
            Message.conversation_id == conv.id
        )
        count_result = await db.execute(count_statement)
        message_count = count_result.scalar()

        conversation_summaries.append(
            ConversationSummary(
                id=str(conv.id),
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count
            )
        )

    return conversation_summaries


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=ConversationMessagesResponse,
    status_code=status.HTTP_200_OK
)
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve all messages for a specific conversation.

    Messages are returned in chronological order (oldest first).

    Args:
        conversation_id: UUID of the conversation
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        ConversationMessagesResponse with conversation_id and list of messages

    Raises:
        HTTPException 400: If conversation_id format is invalid
        HTTPException 404: If conversation not found
        HTTPException 403: If conversation doesn't belong to user
        HTTPException 401: If user not authenticated
    """
    # Validate conversation_id format
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation_id format: {conversation_id}"
        )

    # Fetch conversation and verify ownership
    conv_statement = select(Conversation).where(
        Conversation.id == conv_uuid
    )
    conv_result = await db.execute(conv_statement)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this conversation"
        )

    # Fetch messages in chronological order
    messages_statement = (
        select(Message)
        .where(Message.conversation_id == conv_uuid)
        .order_by(Message.created_at.asc())
    )
    messages_result = await db.execute(messages_statement)
    messages = messages_result.scalars().all()

    # Convert to MessageSchema
    message_schemas = [
        MessageSchema(
            id=str(msg.id),
            role=msg.role.value,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]

    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        messages=message_schemas
    )
