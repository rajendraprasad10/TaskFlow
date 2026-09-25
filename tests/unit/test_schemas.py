import pytest
from pydantic import ValidationError

from app.schemas import TaskCreate, TaskUpdate


def test_valid_task():

    task = TaskCreate(
        title="Learn FastAPI",
        description="Build CRUD API",
        completed=False,
    )

    assert task.title == "Learn FastAPI"
    assert task.completed is False


def test_empty_title_is_invalid():

    with pytest.raises(ValidationError):
        TaskCreate(title="")


def test_title_too_long_is_invalid():

    with pytest.raises(ValidationError):
        TaskCreate(title="A" * 201)


def test_default_completed_value():

    task = TaskCreate(
        title="Docker"
    )

    assert task.completed is False


def test_partial_update():

    task = TaskUpdate(
        completed=True
    )

    assert task.completed is True
    assert task.title is None
