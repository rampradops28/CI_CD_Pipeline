# FastAPI Project — GitHub Actions CI Pipeline

> **Complete 4-Stage Continuous Integration (CI) Pipeline for FastAPI using GitHub Actions, uv, Ruff, Pytest, Alembic, and PostgreSQL Service Containers.**

---

## 1. Project Overview

This project demonstrates a production-grade CI pipeline implemented exclusively with **GitHub Actions**:
- **Dependency Management**: Standard PEP 621 `pyproject.toml` managed via ultra-fast **Astral `uv`**.
- **Stage 1 (Code Quality)**: Fast Ruff linting and format verification.
- **Stage 2 (Unit Testing)**: In-memory isolated pytest execution with JUnit XML report upload.
- **Stage 3 (Integration Testing)**: Starts a temporary `postgres:15-alpine` service container, runs Alembic migrations (`uv run alembic upgrade head`), executes database integration tests, and enforces an **80% code coverage threshold**.
- **Stage 4 (Docker Build Validation)**: Builds the production multi-stage Dockerfile locally on the GitHub runner with **zero push to any registry**.

---

## 2. Directory Structure

```text
fastapi-github-actions/
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # 🚀 Complete 4-stage GitHub Actions workflow
│
├── app/
│   ├── __init__.py
│   ├── config.py                  # Pydantic BaseSettings loading DATABASE_URL
│   ├── database.py                # SQLAlchemy engine, SessionLocal, Base
│   ├── main.py                    # FastAPI application with /health and /items/ routes
│   └── models/
│       ├── __init__.py
│       └── item.py                # Item SQLAlchemy model
│
├── alembic/
│   ├── env.py                     # Dynamically configured migration runner
│   ├── script.py.mako             # Revision template
│   └── versions/
│       └── 001_initial_schema.py  # Initial migration creating items table
├── alembic.ini                    # Alembic configuration
│
├── tests/
│   ├── conftest.py                # Pytest fixtures (TestClient, db_session)
│   ├── unit/
│   │   ├── __init__.py
│   │   └── test_models.py         # Isolated unit tests (@pytest.mark.unit)
│   └── integration/
│       ├── __init__.py
│       └── test_database_api.py   # PostgreSQL integration tests (@pytest.mark.integration)
│
├── pyproject.toml                 # Dependencies, dev extras, ruff & pytest configs
├── pytest.ini                     # Pytest configuration
├── Dockerfile                     # Multi-stage production container build using uv
├── .dockerignore                  # Container build context exclusions
└── README.md                      # Operational manual
```

---

## 3. Local Verification Commands (PowerShell)

```powershell
# 1. Sync dependencies with uv
uv sync --extra dev

# 2. Run Ruff Linting and Formatting
uv run ruff check .
uv run ruff format --check .

# 3. Run Unit Tests (In-Memory)
uv run pytest tests/unit -m unit -v

# 4. Run Integration Tests & Verify 80% Coverage Gate
uv run pytest tests/integration -m integration -v --cov=app --cov-fail-under=80

# 5. Build Docker Image Locally
docker build -t fastapi-gh-app:local .
docker image inspect fastapi-gh-app:local
docker rmi fastapi-gh-app:local
```
