from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    completed: bool | None = None


class TaskResponse(TaskBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )