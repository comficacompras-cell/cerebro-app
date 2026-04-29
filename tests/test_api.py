import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture
def client(override_get_db):
    with TestClient(app) as c:
        yield c


class TestUserEndpoints:
    def test_create_user(self, client):
        resp = client.post("/api/users/", json={"name": "Alice", "email": "alice@test.com"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Alice"
        assert data["current_difficulty"] == 1.0

    def test_create_duplicate_email(self, client):
        client.post("/api/users/", json={"name": "Alice", "email": "dup@test.com"})
        resp = client.post("/api/users/", json={"name": "Bob", "email": "dup@test.com"})
        assert resp.status_code == 400

    def test_get_user(self, client):
        create = client.post("/api/users/", json={"name": "Bob", "email": "bob@test.com"})
        user_id = create.json()["id"]
        resp = client.get(f"/api/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Bob"

    def test_get_nonexistent_user(self, client):
        resp = client.get("/api/users/999")
        assert resp.status_code == 404


class TestExerciseEndpoints:
    def test_create_exercise(self, client):
        resp = client.post(
            "/api/exercises/",
            json={"title": "Sum", "topic": "math", "difficulty": 0.5},
        )
        assert resp.status_code == 201
        assert resp.json()["title"] == "Sum"

    def test_get_exercise(self, client):
        create = client.post(
            "/api/exercises/",
            json={"title": "Div", "topic": "math"},
        )
        eid = create.json()["id"]
        resp = client.get(f"/api/exercises/{eid}")
        assert resp.status_code == 200


class TestAdaptiveEndpoints:
    def _setup_user_and_exercise(self, client):
        user = client.post(
            "/api/users/", json={"name": "Learner", "email": "learn@test.com"}
        ).json()
        exercise = client.post(
            "/api/exercises/",
            json={"title": "Quiz", "topic": "science", "time_limit_seconds": 60},
        ).json()
        return user["id"], exercise["id"]

    def test_correct_attempt(self, client):
        uid, eid = self._setup_user_and_exercise(client)
        resp = client.post(
            "/api/adaptive/attempt",
            json={
                "user_id": uid,
                "exercise_id": eid,
                "is_correct": True,
                "time_taken_seconds": 20,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "correct"

    def test_failed_attempt_reduces_difficulty(self, client):
        uid, eid = self._setup_user_and_exercise(client)
        resp = client.post(
            "/api/adaptive/attempt",
            json={
                "user_id": uid,
                "exercise_id": eid,
                "is_correct": False,
                "time_taken_seconds": 30,
            },
        )
        data = resp.json()
        assert data["status"] == "failed"
        assert data["new_difficulty"] == 0.8
        assert data["failure_type"] == "knowledge"

    def test_three_failures_trigger_review(self, client):
        uid, eid = self._setup_user_and_exercise(client)
        for _ in range(3):
            resp = client.post(
                "/api/adaptive/attempt",
                json={
                    "user_id": uid,
                    "exercise_id": eid,
                    "is_correct": False,
                    "time_taken_seconds": 30,
                },
            )
        data = resp.json()
        assert data["status"] == "fundamentals_review"
        assert data["review_triggered"] is True
        assert data["review_topic"] == "science"

    def test_adaptive_status(self, client):
        uid, eid = self._setup_user_and_exercise(client)
        resp = client.get(f"/api/adaptive/status/{uid}")
        assert resp.status_code == 200
        assert resp.json()["current_difficulty"] == 1.0
        assert resp.json()["consecutive_failures"] == 0

    def test_adaptive_status_nonexistent_user(self, client):
        resp = client.get("/api/adaptive/status/999")
        assert resp.status_code == 404
