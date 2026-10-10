from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app

from tests.conftest import TestingSessionLocal


def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[
    get_db
] = override_get_db


client = TestClient(app)


def setup_function():

    from app.database import Base
    from tests.conftest import engine

    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "UP"
    }


def test_create_task():

    response = client.post(
        "/tasks",
        json={
            "title": "Learn Docker",
            "description": "Build Docker image",
            "completed": False,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Learn Docker"
    assert data["completed"] is False
    assert "id" in data


def test_get_tasks():

    client.post(
        "/tasks",
        json={
            "title": "Task 1",
            "description": "First task",
        },
    )

    client.post(
        "/tasks",
        json={
            "title": "Task 2",
            "description": "Second task",
        },
    )

    response = client.get(
        "/tasks"
    )

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2


def test_get_task():

    create_response = client.post(
        "/tasks",
        json={
            "title": "Integration Test",
        },
    )

    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_nonexistent_task():

    response = client.get(
        "/tasks/99999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Task not found"
    }


def test_update_task():

    create_response = client.post(
        "/tasks",
        json={
            "title": "Original",
        },
    )

    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated",
            "completed": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated"
    assert data["completed"] is True


def test_delete_task():

    create_response = client.post(
        "/tasks",
        json={
            "title": "Delete Me",
        },
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/tasks/{task_id}"
    )

    assert response.status_code == 404
