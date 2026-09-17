# Task Management API

A production-style FastAPI CRUD application designed for
DevOps and DevSecOps CI/CD practice.

## Features

- FastAPI
- SQLAlchemy
- SQLite
- CRUD APIs
- Unit tests
- Integration tests
- Test coverage
- Ruff
- Black
- Bandit
- pip-audit
- Docker
- Docker Compose
- Jenkins CI/CD
- GitHub Actions

## API

### Health

GET /health

### Create task

POST /tasks

Example:

{
    "title": "Learn Docker",
    "description": "Build Docker image",
    "completed": false
}

### Get tasks

GET /tasks

### Get task

GET /tasks/{id}

### Update task

PUT /tasks/{id}

### Delete task

DELETE /tasks/{id}

## Local Setup

Create virtual environment:

python -m venv .venv

Linux/macOS:

source .venv/bin/activate

Windows:

.venv\Scripts\activate

Install:

pip install -r requirements-dev.txt

Run:

uvicorn app.main:app --reload

Open:

http://localhost:8000/docs

## Testing

All tests:

pytest

Unit tests:

pytest tests/unit

Integration tests:

pytest tests/integration

Coverage:

pytest --cov=app --cov-report=term-missing

## Security

Bandit:

bandit -r app

Dependency scan:

pip-audit

## Docker

Build:

docker build -t task-management-api:1.0 .

Run:

docker run -p 8000:8000 task-management-api:1.0

Docker Compose:

docker compose up --build