"""
Cerebro — Adaptive Brain Demo

Simulates a user session where a learner fails an exercise 3 times in a row.
Prints the difficulty level after each failure and shows the Fundamentals Review activation.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.attempt import AttemptCreate
from app.services.adaptive_brain import AdaptiveBrain

SEPARATOR = "=" * 60


def main():
    # --- Setup: in-memory database ---
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()

    # --- Create a user and an exercise ---
    user = User(name="María García", email="maria@cerebro.app", current_difficulty=1.0)
    exercise = Exercise(
        title="Quadratic Equations",
        description="Solve: x² - 5x + 6 = 0",
        topic="algebra",
        difficulty=1.0,
        time_limit_seconds=60,
    )
    db.add_all([user, exercise])
    db.commit()
    db.refresh(user)
    db.refresh(exercise)

    brain = AdaptiveBrain()

    print(SEPARATOR)
    print("  CEREBRO — Adaptive Brain Demo")
    print(SEPARATOR)
    print(f"\n  User:     {user.name}")
    print(f"  Exercise: {exercise.title} (topic: {exercise.topic})")
    print(f"  Initial difficulty: {user.current_difficulty}")
    print("  Formula: New Load = Current Load x 0.8")
    print(f"  Review trigger: {brain.STREAK_THRESHOLD} consecutive failures")
    print()

    # --- Simulate 3 consecutive failures ---
    for attempt_num in range(1, 4):
        print(SEPARATOR)
        print(f"  ATTEMPT #{attempt_num} — Wrong answer (30s, within time limit)")
        print(SEPARATOR)

        attempt = AttemptCreate(
            user_id=user.id,
            exercise_id=exercise.id,
            is_correct=False,
            time_taken_seconds=30.0,
        )
        result = brain.process_attempt(db, attempt)

        print(f"  Status:                {result.status}")
        print(f"  Failure type:          {result.failure_type}")
        prev = round(result.new_difficulty / brain.REDUCTION_FACTOR, 4)
        print(f"  Difficulty BEFORE:     {prev}")
        print(f"  Difficulty AFTER:      {result.new_difficulty}")
        print(f"  Consecutive failures:  {result.consecutive_failures}")
        print(f"  Review triggered:      {result.review_triggered}")

        if result.review_triggered:
            print()
            print("  *** FUNDAMENTALS REVIEW ACTIVATED ***")
            print(f"  >>> Review topic: {result.review_topic}")
            print("  >>> The system pauses the current exercise and")
            print("  >>> directs the learner to prerequisite material.")

        print()

    # --- Summary ---
    print(SEPARATOR)
    print("  SUMMARY")
    print(SEPARATOR)
    print("  Starting difficulty:  1.0")
    print("  After failure #1:     1.0  x 0.8 = 0.8")
    print("  After failure #2:     0.8  x 0.8 = 0.64")
    print("  After failure #3:     0.64 x 0.8 = 0.512")
    print(f"  Final difficulty:     {user.current_difficulty}")
    print("  Fundamentals Review:  ACTIVATED (after 3 consecutive failures)")
    print(SEPARATOR)

    db.close()


if __name__ == "__main__":
    main()
