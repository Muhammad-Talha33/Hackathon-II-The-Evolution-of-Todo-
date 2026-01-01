"""Task request/response schemas."""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from src.models.task import TaskStatus


class TaskCreate(BaseModel):
    """Request schema for creating a task."""

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Get milk, eggs, bread",
            }
        }


class TaskUpdate(BaseModel):
    """Request schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and supplies",
                "description": "Get milk, eggs, bread, and cleaning products",
            }
        }


class TaskResponse(BaseModel):
    """Response schema for task data."""

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
