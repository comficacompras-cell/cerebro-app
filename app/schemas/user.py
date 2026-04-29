from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    current_difficulty: float
    consecutive_failures: int

    model_config = {"from_attributes": True}
