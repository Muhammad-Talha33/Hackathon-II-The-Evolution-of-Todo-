"""Message model for chat messages."""
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKey
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message model representing a single message in a conversation."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(sa_column=Column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True))
    role: MessageRole = Field(index=True)
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "user",
                "content": "Add buy groceries to my tasks",
                "created_at": "2026-01-03T10:00:00Z",
            }
        }
