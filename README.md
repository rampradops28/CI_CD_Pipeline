# 🚀 Microservices CI/CD Pipeline

A production-ready, modular CI/CD architecture powered by **GitHub Actions Reusable Workflows** and **Docker**.

---

## 📌 What Does This Repository Do?

Instead of copying and pasting the same 50 lines of CI/CD configuration into every microservice, this repository uses a **Reusable Pipeline (`reusable-pipeline.yml`)**. 

Think of it like a **Python function**:
* **The Template (`reusable-pipeline.yml`)**: Defines *how* to test code, check coverage, and build/verify Docker containers.
* **The Callers (`ci.yml`)**: Passes *inputs* (e.g. port, health check route, coverage threshold) for each individual service.

---

## 🗂️ Project Structure

```text
CI_CD_Pipeline/
│
├── .github/
│   └── workflows/
│       ├── reusable-pipeline.yml     <-- 📦 THE SHARED REUSABLE WORKFLOW
│       └── ci.yml                    <-- 🚀 THE CALLER (Runs both services in parallel)
│
└── services/
    ├── learning_service/             <-- 🔵 SERVICE 1: Learning API
    │   ├── app/main.py               • Port: 8000
    │   ├── tests/test_learning.py    • Health Route: /health
    │   ├── requirements.txt          • Min Coverage: 80%
    │   ├── Dockerfile
    │   └── pytest.ini
    │
    └── order_service/                <-- 🟢 SERVICE 2: Order Service
        ├── app/main.py               • Port: 8080
        ├── tests/test_order.py       • Health Route: /healthz
        ├── requirements.txt          • Min Coverage: 85%
        ├── Dockerfile
        └── pytest.ini
```

---

## 🔄 How the CI/CD Pipeline Works

When you push code to GitHub, **two independent jobs start in parallel**:

```text
                          ┌───────────────────────────┐
                          │         git push          │
                          └─────────────┬─────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
  ┌───────────────────────────────┐             ┌───────────────────────────────┐
  │  Job 1: Learning Service CI   │             │   Job 2: Order Service CI     │
  └──────────────┬────────────────┘             └──────────────┬────────────────┘
                 │                                             │
                 │ Calls reusable-pipeline.yml                 │ Calls reusable-pipeline.yml
                 ▼                                             ▼
  1. Checkout code                              1. Checkout code
  2. Setup Python 3.11                          2. Setup Python 3.11
  3. Install dependencies                       3. Install dependencies
  4. Run Pytest (Must be > 80% coverage)        4. Run Pytest (Must be > 85% coverage)
  5. Build Docker Image (fastapi-app:latest)    5. Build Docker Image (order-service:latest)
  6. Smoke Test (curl :8000/health)             6. Smoke Test (curl :8080/healthz)
```

---

## 🛠️ The Core Components Explained

### 1. The Reusable Pipeline (`.github/workflows/reusable-pipeline.yml`)
Accepts configurable inputs so any microservice can use it:

| Input | Description | Default | Example |
| :--- | :--- | :--- | :--- |
| `working-directory` | Path to the service folder | `.` | `services/order_service` |
| `python-version` | Python runtime version | `3.11` | `3.11` |
| `min-coverage` | Minimum test coverage required to pass | `80` | `85` |
| `image-name` | Name tag for the Docker image | `app` | `order-service` |
| `app-port` | Port exposed by the container | `8000` | `8080` |
| `health-endpoint` | Route checked during smoke test | `/health` | `/healthz` |

### 2. The Strict Quality Gate
```bash
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=80
```
* **100% Tests Must Pass**: If any test fails, the build stops.
* **Code Coverage Threshold**: If lines covered are below the minimum threshold (e.g. 80% or 85%), pytest exits with failure. The Docker image is **never built**.

### 3. Docker Smoke Testing
Just building a Docker image isn't enough. The pipeline:
1. Starts the container in the background (`docker run -d`).
2. Waits 3 seconds for Uvicorn to boot.
3. Curls the health endpoint (`curl --fail http://localhost:<port><endpoint>`).
4. If it returns HTTP 200, the container is verified healthy!

---

## ⚙️ Why `pytest.ini` is in Each Service

Each microservice has its own `pytest.ini`:

```ini
[pytest]
pythonpath = .
testpaths = tests
addopts = --import-mode=importlib
```

* **`pythonpath = .`**: Prevents `ModuleNotFoundError: No module named 'app'` by adding the service directory to Python's import search path.
* **`testpaths = tests`**: Restricts test discovery strictly to that service's `tests/` directory so it never accidentally runs tests from other microservices.
* **`addopts = --import-mode=importlib`**: Uses Python's isolated import mode so identically named helper modules in different services never collide.

---

## 💻 Running & Testing Locally

### Run Tests and Coverage Locally:
```powershell
# Service 1: Learning Service
cd services/learning_service
pytest --cov=app --cov-fail-under=80

# Service 2: Order Service
cd ../order_service
pytest --cov=app --cov-fail-under=85
```

### Build & Run Containers Locally:
```powershell
# Build Learning Service
docker build -t learning-service:latest services/learning_service

# Run Learning Service on Port 8000
docker run -d --name learning-api -p 8000:8000 learning-service:latest

# Open in Browser
# http://localhost:8000/docs
```

---

## ➕ How to Add a 3rd Microservice (In 3 Minutes!)

1. Create a folder: `services/payment_service/`
2. Add your code: `app/main.py`, `tests/test_payment.py`, `Dockerfile`, `requirements.txt`, `pytest.ini`.
3. In [.github/workflows/ci.yml](.github/workflows/ci.yml), simply add:

```yaml
  payment-service-ci:
    name: "Project 3: Payment Service"
    uses: ./.github/workflows/reusable-pipeline.yml
    with:
      working-directory: "services/payment_service"
      python-version: "3.11"
      min-coverage: 80
      image-name: "payment-service"
      app-port: 9000
      health-endpoint: "/health"
```
**Done!** No need to write any new CI/CD YAML. The new service automatically gets automated testing, coverage gates, and Docker verification.
