from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String, nullable=False, index=True)
    difficulty = Column(Float, default=1.0)
    time_limit_seconds = Column(Integer, default=60)

    attempts = relationship("Attempt", back_populates="exercise")
