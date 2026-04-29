# Cerebro — Adaptive Learning App

An intelligent adaptive learning backend that dynamically adjusts exercise difficulty based on user performance.

## Core Feature: Adaptive Brain

The **Adaptive Brain** module (`app/services/adaptive_brain.py`) implements three key behaviors:

1. **Failure Categorization** — classifies each incorrect answer as:
   - **Capacity** — user exceeded the time limit or skipped the exercise.
   - **Knowledge** — user answered within time but incorrectly.

2. **Difficulty Reduction** — on every failure the difficulty is reduced by 20%:
   ```
   New Load = Current Load × 0.8
   ```
   A minimum floor of `0.1` prevents difficulty from reaching zero.

3. **Fundamentals Review** — after **3 consecutive failures** the system pauses the current exercise and returns a review prompt for the topic's prerequisites.

## Tech Stack

| Layer       | Choice                          |
|-------------|---------------------------------|
| Framework   | FastAPI                         |
| Validation  | Pydantic v2                     |
| ORM         | SQLAlchemy 2.0                  |
| Database    | SQLite (easily swappable)       |
| Testing     | pytest + httpx                  |
| Linting     | ruff                            |

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the server
uvicorn app.main:app --reload

# Run tests
pytest -v

# Lint
ruff check .
```

## API Endpoints

| Method | Path                             | Description                                   |
|--------|----------------------------------|-----------------------------------------------|
| POST   | `/api/users/`                    | Create a new user                             |
| GET    | `/api/users/{user_id}`           | Get user profile & current difficulty         |
| POST   | `/api/exercises/`                | Create a new exercise                         |
| GET    | `/api/exercises/{exercise_id}`   | Get exercise details                          |
| POST   | `/api/adaptive/attempt`          | Submit an answer → triggers Adaptive Brain    |
| GET    | `/api/adaptive/status/{user_id}` | Get user's adaptive state (streak, load)      |
