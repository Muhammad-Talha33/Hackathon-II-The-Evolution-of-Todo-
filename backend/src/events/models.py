"""Domain event definitions for the task management system.

These events represent the conceptual domain events emitted by the application.
In Phase V Part A, they are recorded in-process via EventBus for logging/testing.
In Phase V Part B, EventBus.emit() will be replaced with Dapr/Kafka publishing.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class TaskCreatedEvent:
    """Emitted after a new task is successfully persisted."""
    event_type: str = field(default="TaskCreated", init=False)
    task_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    title: str = ""
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    due_at: Optional[datetime] = None
    recurrence_pattern: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskUpdatedEvent:
    """Emitted after any task field is modified."""
    event_type: str = field(default="TaskUpdated", init=False)
    task_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    updated_fields: List[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskCompletedEvent:
    """Emitted after a task's status changes from incomplete to complete."""
    event_type: str = field(default="TaskCompleted", init=False)
    task_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    title: str = ""
    completed_at: datetime = field(default_factory=datetime.utcnow)
    had_recurrence: bool = False
    was_overdue: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskDeletedEvent:
    """Emitted after a task is removed from the database."""
    event_type: str = field(default="TaskDeleted", init=False)
    task_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    title: str = ""
    deleted_at: datetime = field(default_factory=datetime.utcnow)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskReminderDueEvent:
    """Emitted when a reminder check finds due reminders."""
    event_type: str = field(default="TaskReminderDue", init=False)
    task_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    title: str = ""
    remind_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RecurringTaskGeneratedEvent:
    """Emitted after a new task instance is created from a completed recurring task."""
    event_type: str = field(default="RecurringTaskGenerated", init=False)
    new_task_id: UUID = field(default=None)
    parent_task_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    title: str = ""
    next_due_at: Optional[datetime] = None
    recurrence_pattern: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
