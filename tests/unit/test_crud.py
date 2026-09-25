from app.crud import (
    create_task,
    delete_task,
    get_task,
    get_tasks,
    update_task,
)
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


def test_create_task(db_session):

    task_data = TaskCreate(
        title="Unit Test",
        description="Testing CRUD",
    )

    task = create_task(
        db_session,
        task_data,
    )

    assert task.id is not None
    assert task.title == "Unit Test"


def test_get_task(db_session):

    task = Task(
        title="Get Task",
        description="Test",
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    result = get_task(
        db_session,
        task.id,
    )

    assert result is not None
    assert result.title == "Get Task"


def test_get_tasks(db_session):

    db_session.add(
        Task(title="Task 1")
    )

    db_session.add(
        Task(title="Task 2")
    )

    db_session.commit()

    tasks = get_tasks(db_session)

    assert len(tasks) == 2


def test_update_task(db_session):

    task = Task(
        title="Old Title"
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    update = TaskUpdate(
        title="New Title",
        completed=True,
    )

    result = update_task(
        db_session,
        task.id,
        update,
    )

    assert result.title == "New Title"
    assert result.completed is True


def test_delete_task(db_session):

    task = Task(
        title="Delete Me"
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    result = delete_task(
        db_session,
        task.id,
    )

    assert result is not None

    deleted = get_task(
        db_session,
        task.id,
    )

    assert deleted is None
