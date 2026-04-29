from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    current_difficulty = Column(Float, default=1.0)
    consecutive_failures = Column(Integer, default=0)

    attempts = relationship("Attempt", back_populates="user")
