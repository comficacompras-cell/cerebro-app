from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Float, nullable=True)
    failure_type = Column(String, nullable=True)  # "capacity" | "knowledge" | None
    difficulty_at_attempt = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="attempts")
    exercise = relationship("Exercise", back_populates="attempts")
