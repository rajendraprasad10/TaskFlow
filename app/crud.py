from sqlalchemy.orm import Session

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


def create_task(
    db: Session,
    task: TaskCreate,
) -> Task:

    db_task = Task(
        title=task.title,
        description=task.description,
        completed=task.completed,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def get_task(
    db: Session,
    task_id: int,
) -> Task | None:

    return (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )


def get_tasks(
    db: Session,
) -> list[Task]:

    return (
        db.query(Task)
        .order_by(Task.id)
        .all()
    )


def update_task(
    db: Session,
    task_id: int,
    task: TaskUpdate,
) -> Task | None:

    db_task = get_task(db, task_id)

    if db_task is None:
        return None

    update_data = task.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)

    return db_task


def delete_task(
    db: Session,
    task_id: int,
) -> Task | None:

    db_task = get_task(db, task_id)

    if db_task is None:
        return None

    db.delete(db_task)
    db.commit()

    return db_task
