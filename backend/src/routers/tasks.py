"""Task CRUD router with all task management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from datetime import datetime
from src.database import get_db
from src.models.user import User
from src.models.task import Task, TaskStatus
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from src.dependencies.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all tasks for the current user.

    Args:
        current_user: Authenticated user from token
        db: Database session

    Returns:
        List[TaskResponse]: List of user's tasks
    """
    result = await db.execute(
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task for the current user.

    Args:
        task_data: Task creation data
        current_user: Authenticated user from token
        db: Database session

    Returns:
        TaskResponse: Created task

    Raises:
        HTTPException 422: If validation fails
    """
    new_task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        status=TaskStatus.INCOMPLETE,
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single task by ID.

    Args:
        task_id: UUID of the task
        current_user: Authenticated user from token
        db: Database session

    Returns:
        TaskResponse: Task details

    Raises:
        HTTPException 404: If task not found or not owned by user
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a task by ID.

    Args:
        task_id: UUID of the task
        task_data: Task update data
        current_user: Authenticated user from token
        db: Database session

    Returns:
        TaskResponse: Updated task

    Raises:
        HTTPException 404: If task not found or not owned by user
        HTTPException 422: If validation fails
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a task by ID.

    Args:
        task_id: UUID of the task
        current_user: Authenticated user from token
        db: Database session

    Raises:
        HTTPException 404: If task not found or not owned by user
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await db.delete(task)
    await db.commit()


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Toggle task completion status (incomplete ↔ complete).

    Args:
        task_id: UUID of the task
        current_user: Authenticated user from token
        db: Database session

    Returns:
        TaskResponse: Updated task

    Raises:
        HTTPException 404: If task not found or not owned by user
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Toggle status
    if task.status == TaskStatus.INCOMPLETE:
        task.status = TaskStatus.COMPLETE
    else:
        task.status = TaskStatus.INCOMPLETE

    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return task
