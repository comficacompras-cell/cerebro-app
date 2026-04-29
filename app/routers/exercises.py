from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseResponse

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.post("/", response_model=ExerciseResponse, status_code=201)
def create_exercise(exercise_data: ExerciseCreate, db: Session = Depends(get_db)):
    exercise = Exercise(**exercise_data.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise
