from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

router = APIRouter()


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
):
    return crud.create_task(db, task)


@router.get(
    "",
    response_model=list[TaskResponse],
)
def list_tasks(
    db: Session = Depends(get_db),
):
    return crud.get_tasks(db)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
):
    updated_task = crud.update_task(
        db,
        task_id,
        task,
    )

    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return updated_task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    deleted_task = crud.delete_task(
        db,
        task_id,
    )

    if deleted_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return None