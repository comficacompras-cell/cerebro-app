import pytest

from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.attempt import AttemptCreate
from app.services.adaptive_brain import AdaptiveBrain


@pytest.fixture
def brain():
    return AdaptiveBrain()


@pytest.fixture
def sample_user(db):
    user = User(name="Test User", email="test@example.com", current_difficulty=1.0)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_exercise(db):
    exercise = Exercise(
        title="Basic Math",
        description="Solve a simple equation",
        topic="algebra",
        difficulty=1.0,
        time_limit_seconds=60,
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


class TestDifficultyReduction:
    def test_reduce_difficulty_applies_20_percent_reduction(self, brain):
        assert brain._reduce_difficulty(1.0) == 0.8

    def test_reduce_difficulty_compounds_on_successive_calls(self, brain):
        load = 1.0
        load = brain._reduce_difficulty(load)
        assert load == 0.8
        load = brain._reduce_difficulty(load)
        assert load == 0.64

    def test_reduce_difficulty_respects_minimum(self, brain):
        assert brain._reduce_difficulty(0.05) == brain.MIN_DIFFICULTY

    def test_reduce_difficulty_at_exact_minimum(self, brain):
        result = brain._reduce_difficulty(brain.MIN_DIFFICULTY)
        assert result == brain.MIN_DIFFICULTY


class TestFailureCategorization:
    def test_knowledge_failure_when_answered_within_time(self, brain, sample_exercise):
        attempt = AttemptCreate(
            user_id=1, exercise_id=1, is_correct=False, time_taken_seconds=30.0
        )
        assert brain._categorize_failure(attempt, sample_exercise) == "knowledge"

    def test_capacity_failure_when_exceeded_time_limit(self, brain, sample_exercise):
        attempt = AttemptCreate(
            user_id=1, exercise_id=1, is_correct=False, time_taken_seconds=90.0
        )
        assert brain._categorize_failure(attempt, sample_exercise) == "capacity"

    def test_capacity_failure_when_skipped(self, brain, sample_exercise):
        attempt = AttemptCreate(
            user_id=1, exercise_id=1, is_correct=False, time_taken_seconds=None
        )
        assert brain._categorize_failure(attempt, sample_exercise) == "capacity"

    def test_capacity_failure_at_exact_time_limit(self, brain, sample_exercise):
        attempt = AttemptCreate(
            user_id=1, exercise_id=1, is_correct=False, time_taken_seconds=60.0
        )
        assert brain._categorize_failure(attempt, sample_exercise) == "knowledge"


class TestFundamentalsReview:
    def test_no_review_under_threshold(self, brain):
        assert brain._check_fundamentals_review(0) is False
        assert brain._check_fundamentals_review(1) is False
        assert brain._check_fundamentals_review(2) is False

    def test_review_triggered_at_threshold(self, brain):
        assert brain._check_fundamentals_review(3) is True

    def test_review_triggered_above_threshold(self, brain):
        assert brain._check_fundamentals_review(5) is True


class TestProcessAttempt:
    def test_correct_answer_resets_streak(self, brain, db, sample_user, sample_exercise):
        sample_user.consecutive_failures = 2
        db.commit()

        attempt = AttemptCreate(
            user_id=sample_user.id,
            exercise_id=sample_exercise.id,
            is_correct=True,
            time_taken_seconds=20.0,
        )
        result = brain.process_attempt(db, attempt)

        assert result.status == "correct"
        assert result.consecutive_failures == 0
        assert result.review_triggered is False

    def test_single_failure_reduces_difficulty(self, brain, db, sample_user, sample_exercise):
        attempt = AttemptCreate(
            user_id=sample_user.id,
            exercise_id=sample_exercise.id,
            is_correct=False,
            time_taken_seconds=30.0,
        )
        result = brain.process_attempt(db, attempt)

        assert result.status == "failed"
        assert result.new_difficulty == 0.8
        assert result.consecutive_failures == 1
        assert result.failure_type == "knowledge"

    def test_three_consecutive_failures_trigger_review(
        self, brain, db, sample_user, sample_exercise
    ):
        for _ in range(3):
            attempt = AttemptCreate(
                user_id=sample_user.id,
                exercise_id=sample_exercise.id,
                is_correct=False,
                time_taken_seconds=30.0,
            )
            result = brain.process_attempt(db, attempt)

        assert result.status == "fundamentals_review"
        assert result.review_triggered is True
        assert result.review_topic == "algebra"
        assert result.consecutive_failures == 3

    def test_difficulty_compounds_across_failures(
        self, brain, db, sample_user, sample_exercise
    ):
        for i in range(3):
            attempt = AttemptCreate(
                user_id=sample_user.id,
                exercise_id=sample_exercise.id,
                is_correct=False,
                time_taken_seconds=30.0,
            )
            result = brain.process_attempt(db, attempt)

        # 1.0 * 0.8 = 0.8 → 0.8 * 0.8 = 0.64 → 0.64 * 0.8 = 0.512
        assert result.new_difficulty == 0.512

    def test_nonexistent_user_raises(self, brain, db, sample_exercise):
        attempt = AttemptCreate(
            user_id=999, exercise_id=sample_exercise.id, is_correct=False, time_taken_seconds=10.0
        )
        with pytest.raises(ValueError, match="User 999 not found"):
            brain.process_attempt(db, attempt)

    def test_nonexistent_exercise_raises(self, brain, db, sample_user):
        attempt = AttemptCreate(
            user_id=sample_user.id, exercise_id=999, is_correct=False, time_taken_seconds=10.0
        )
        with pytest.raises(ValueError, match="Exercise 999 not found"):
            brain.process_attempt(db, attempt)
