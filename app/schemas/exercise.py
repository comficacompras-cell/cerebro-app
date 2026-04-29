from pydantic import BaseModel


class ExerciseCreate(BaseModel):
    title: str
    description: str | None = None
    topic: str
    difficulty: float = 1.0
    time_limit_seconds: int = 60


class ExerciseResponse(BaseModel):
    id: int
    title: str
    description: str | None
    topic: str
    difficulty: float
    time_limit_seconds: int

    model_config = {"from_attributes": True}
