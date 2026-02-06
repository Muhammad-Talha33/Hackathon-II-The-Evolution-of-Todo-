"""Task request/response schemas."""
import re
from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.models.task import TaskStatus


VALID_PRIORITIES = {"low", "medium", "high"}
VALID_RECURRENCE = {"daily", "weekly", "monthly"}
TAG_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\-]{0,49}$")


class TaskCreate(BaseModel):
    """Request schema for creating a task."""

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    priority: Optional[str] = "medium"
    tags: Optional[List[str]] = Field(default_factory=list)
    recurrence_pattern: Optional[str] = None

    @model_validator(mode="after")
    def validate_task_create(self):
        # Validate priority
        if self.priority and self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of: {', '.join(VALID_PRIORITIES)}")
        # Validate recurrence_pattern
        if self.recurrence_pattern and self.recurrence_pattern not in VALID_RECURRENCE:
            raise ValueError(f"recurrence_pattern must be one of: {', '.join(VALID_RECURRENCE)}")
        # Recurrence requires due_at
        if self.recurrence_pattern and self.due_at is None:
            raise ValueError("due_at is required when recurrence_pattern is set")
        # Validate and deduplicate tags
        if self.tags:
            for tag in self.tags:
                if not TAG_PATTERN.match(tag):
                    raise ValueError(
                        f"Tag '{tag}' is invalid. Tags must be 1-50 chars, "
                        "alphanumeric with hyphens, starting with alphanumeric."
                    )
            self.tags = list(dict.fromkeys(self.tags))  # deduplicate preserving order
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Get milk, eggs, bread",
                "priority": "medium",
                "tags": ["shopping"],
            }
        }


class TaskUpdate(BaseModel):
    """Request schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    recurrence_pattern: Optional[str] = None

    @model_validator(mode="after")
    def validate_task_update(self):
        # Validate priority if provided
        if self.priority is not None and self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of: {', '.join(VALID_PRIORITIES)}")
        # Validate recurrence_pattern if provided
        if self.recurrence_pattern is not None and self.recurrence_pattern not in VALID_RECURRENCE:
            raise ValueError(f"recurrence_pattern must be one of: {', '.join(VALID_RECURRENCE)}")
        # Validate tags if provided
        if self.tags is not None:
            for tag in self.tags:
                if not TAG_PATTERN.match(tag):
                    raise ValueError(
                        f"Tag '{tag}' is invalid. Tags must be 1-50 chars, "
                        "alphanumeric with hyphens, starting with alphanumeric."
                    )
            self.tags = list(dict.fromkeys(self.tags))  # deduplicate
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and supplies",
                "description": "Get milk, eggs, bread, and cleaning products",
                "priority": "high",
                "tags": ["shopping", "errands"],
            }
        }


class TaskResponse(BaseModel):
    """Response schema for task data."""

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: str
    tags: List[str]
    due_at: Optional[datetime]
    remind_at: Optional[datetime]
    reminder_sent: bool
    recurrence_pattern: Optional[str]
    parent_task_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
