install:
	pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload

test:
	pytest

unit:
	pytest tests/unit

integration:
	pytest tests/integration

coverage:
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint:
	ruff check .

format:
	black .

security:
	bandit -r app

dependency-scan:
	pip-audit

docker-build:
	docker build -t task-management-api:1.0 .

docker-run:
	docker run -p 8000:8000 task-management-api:1.0