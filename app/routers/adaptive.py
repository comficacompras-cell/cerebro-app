from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.attempt import AdaptiveResult, AttemptCreate
from app.services.adaptive_brain import adaptive_brain

router = APIRouter(prefix="/api/adaptive", tags=["adaptive"])


@router.post("/attempt", response_model=AdaptiveResult)
def submit_attempt(attempt_data: AttemptCreate, db: Session = Depends(get_db)):
    try:
        result = adaptive_brain.process_attempt(db, attempt_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/status/{user_id}")
def get_adaptive_status(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "current_difficulty": user.current_difficulty,
        "consecutive_failures": user.consecutive_failures,
        "review_needed": user.consecutive_failures >= 3,
    }
