"""Task model for todo items."""
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKey, Boolean, String
from sqlalchemy.dialects.postgresql import ARRAY
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurrencePattern(str, Enum):
    """Task recurrence patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


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
    priority: str = Field(default=Priority.MEDIUM)
    tags: List[str] = Field(
        default=[],
        sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
    due_at: Optional[datetime] = Field(default=None)
    remind_at: Optional[datetime] = Field(default=None)
    reminder_sent: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="false")
    )
    recurrence_pattern: Optional[str] = Field(default=None)
    parent_task_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Get milk, eggs, bread",
                "status": "incomplete",
                "priority": "medium",
                "tags": ["shopping"],
            }
        }
