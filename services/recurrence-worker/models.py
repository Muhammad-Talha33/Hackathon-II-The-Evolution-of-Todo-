"""Task model for database access from the Recurrence Worker.

Mirrors the backend Task model to enable direct database writes.
"""
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKey, Boolean, String
from sqlalchemy.dialects.postgresql import ARRAY
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TaskStatus(str, Enum):
    """Task completion status."""
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class Task(SQLModel, table=True):
    """Task model matching the backend schema."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False))
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.INCOMPLETE)
    priority: str = Field(default="medium")
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
