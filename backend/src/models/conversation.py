"""Conversation model for chat sessions."""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Conversation(SQLModel, table=True):
    """Conversation model representing a chat session between user and AI agent."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2026-01-03T10:00:00Z",
                "updated_at": "2026-01-03T10:05:00Z",
            }
        }
