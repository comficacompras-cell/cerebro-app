from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.attempt import AdaptiveResult, AttemptCreate


class AdaptiveBrain:
    """Core adaptive learning engine.

    Adjusts exercise difficulty based on user performance:
    - Categorizes failures as Capacity (timeout/skip) or Knowledge (wrong answer).
    - Applies a 20% difficulty reduction on each failure: New Load = Current Load × 0.8.
    - Triggers a Fundamentals Review after 3 consecutive failures.
    """

    REDUCTION_FACTOR: float = 0.8
    MIN_DIFFICULTY: float = 0.1
    STREAK_THRESHOLD: int = 3

    def process_attempt(self, db: Session, attempt_data: AttemptCreate) -> AdaptiveResult:
        user = db.query(User).filter(User.id == attempt_data.user_id).first()
        if not user:
            raise ValueError(f"User {attempt_data.user_id} not found")

        exercise = db.query(Exercise).filter(Exercise.id == attempt_data.exercise_id).first()
        if not exercise:
            raise ValueError(f"Exercise {attempt_data.exercise_id} not found")

        if attempt_data.is_correct:
            return self._handle_correct(db, user, exercise, attempt_data)

        return self._handle_failure(db, user, exercise, attempt_data)

    def _handle_correct(
        self,
        db: Session,
        user: User,
        exercise: Exercise,
        attempt_data: AttemptCreate,
    ) -> AdaptiveResult:
        user.consecutive_failures = 0

        attempt = Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            is_correct=True,
            time_taken_seconds=attempt_data.time_taken_seconds,
            failure_type=None,
            difficulty_at_attempt=user.current_difficulty,
        )
        db.add(attempt)
        db.commit()
        db.refresh(user)

        return AdaptiveResult(
            status="correct",
            failure_type=None,
            new_difficulty=user.current_difficulty,
            consecutive_failures=0,
            review_triggered=False,
        )

    def _handle_failure(
        self,
        db: Session,
        user: User,
        exercise: Exercise,
        attempt_data: AttemptCreate,
    ) -> AdaptiveResult:
        failure_type = self._categorize_failure(attempt_data, exercise)

        new_difficulty = self._reduce_difficulty(user.current_difficulty)
        user.current_difficulty = new_difficulty
        user.consecutive_failures += 1

        attempt = Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            is_correct=False,
            time_taken_seconds=attempt_data.time_taken_seconds,
            failure_type=failure_type,
            difficulty_at_attempt=new_difficulty,
        )
        db.add(attempt)
        db.commit()
        db.refresh(user)

        review_triggered = self._check_fundamentals_review(user.consecutive_failures)

        status = "fundamentals_review" if review_triggered else "failed"

        return AdaptiveResult(
            status=status,
            failure_type=failure_type,
            new_difficulty=new_difficulty,
            consecutive_failures=user.consecutive_failures,
            review_triggered=review_triggered,
            review_topic=exercise.topic if review_triggered else None,
        )

    def _categorize_failure(self, attempt_data: AttemptCreate, exercise: Exercise) -> str:
        """Categorize failure as Capacity or Knowledge.

        - Capacity: user exceeded the time limit or skipped (no time recorded).
        - Knowledge: user answered within time but incorrectly.
        """
        if attempt_data.time_taken_seconds is None:
            return "capacity"
        if attempt_data.time_taken_seconds > exercise.time_limit_seconds:
            return "capacity"
        return "knowledge"

    def _reduce_difficulty(self, current_load: float) -> float:
        """Apply 20% difficulty reduction: New Load = Current Load × 0.8."""
        new_load = round(current_load * self.REDUCTION_FACTOR, 4)
        return max(new_load, self.MIN_DIFFICULTY)

    def _check_fundamentals_review(self, consecutive_failures: int) -> bool:
        """Trigger a fundamentals review after 3 consecutive failures."""
        return consecutive_failures >= self.STREAK_THRESHOLD


adaptive_brain = AdaptiveBrain()
