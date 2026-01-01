"""Task model for todo items."""
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKey
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    """Task completion status."""
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class Task(SQLModel, table=True):
    """Task model representing a todo item."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False))
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.INCOMPLETE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Get milk, eggs, bread",
                "status": "incomplete",
            }
        }
