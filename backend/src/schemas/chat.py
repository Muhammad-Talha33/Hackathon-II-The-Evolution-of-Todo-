"""Pydantic schemas for chat API requests and responses."""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ChatRequest(BaseModel):
    """Request schema for POST /api/chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's message to the chat agent"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID to continue existing conversation"
    )

    @validator('message')
    def validate_message(cls, v):
        """Ensure message is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add buy groceries to my tasks",
                "conversation_id": None
            }
        }


class ChatResponse(BaseModel):
    """Response schema for POST /api/chat endpoint."""

    conversation_id: str = Field(
        ...,
        description="ID of the conversation (created or continued)"
    )
    message: str = Field(
        ...,
        description="Agent's response message"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the response was created"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "I've added 'buy groceries' to your tasks!",
                "created_at": "2026-01-03T10:00:00Z"
            }
        }


class MessageSchema(BaseModel):
    """Schema for a single message in conversation history."""

    id: str
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "user",
                "content": "Show me my tasks",
                "created_at": "2026-01-03T10:00:00Z"
            }
        }


class ConversationSummary(BaseModel):
    """Summary schema for GET /api/conversations endpoint."""

    id: str
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2026-01-03T10:00:00Z",
                "updated_at": "2026-01-03T10:05:00Z",
                "message_count": 6
            }
        }


class ConversationMessagesResponse(BaseModel):
    """Response schema for GET /api/conversations/{id}/messages endpoint."""

    conversation_id: str
    messages: List[MessageSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "messages": [
                    {
                        "id": "msg1",
                        "role": "user",
                        "content": "Add buy groceries",
                        "created_at": "2026-01-03T10:00:00Z"
                    },
                    {
                        "id": "msg2",
                        "role": "assistant",
                        "content": "I've added 'buy groceries' to your tasks!",
                        "created_at": "2026-01-03T10:00:01Z"
                    }
                ]
            }
        }
