from datetime import datetime

from pydantic import BaseModel


class AttemptCreate(BaseModel):
    user_id: int
    exercise_id: int
    is_correct: bool
    time_taken_seconds: float | None = None


class AttemptResponse(BaseModel):
    id: int
    user_id: int
    exercise_id: int
    is_correct: bool
    time_taken_seconds: float | None
    failure_type: str | None
    difficulty_at_attempt: float
    created_at: datetime

    model_config = {"from_attributes": True}


class AdaptiveResult(BaseModel):
    status: str  # "correct" | "failed" | "fundamentals_review"
    failure_type: str | None = None
    new_difficulty: float
    consecutive_failures: int
    review_triggered: bool = False
    review_topic: str | None = None
