"""Chat router for AI-powered task management conversations."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.user import User
from src.dependencies.auth import get_current_user
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import process_chat_message

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a chat message and return the agent's response.

    This endpoint is fully stateless:
    - Fetches conversation history from database
    - Creates fresh agent with MCP tools
    - Runs agent with context
    - Persists messages to database

    Args:
        request: ChatRequest with message and optional conversation_id
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        ChatResponse with conversation_id, agent message, and timestamp

    Raises:
        HTTPException 400: If conversation not found or invalid
        HTTPException 500: If agent execution fails
        HTTPException 401: If user not authenticated
    """
    try:
        response = await process_chat_message(
            user_id=current_user.id,
            message=request.message,
            conversation_id=request.conversation_id,
            db=db
        )
        return response

    except ValueError as e:
        # Conversation not found or validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except RuntimeError as e:
        # Agent execution failure
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )

    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
