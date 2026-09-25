from fastapi import FastAPI

from app.database import Base, engine
from app.routers.tasks import router as task_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    description="Production-style FastAPI CRUD application",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Task Management API",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "UP"
    }


app.include_router(
    task_router,
    prefix="/tasks",
    tags=["Tasks"],
)
