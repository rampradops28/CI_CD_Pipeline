# CI/CD Pipeline — Documentation Manual
> **Microservices CI/CD Pipeline** powered by GitHub Actions Reusable Workflows, Docker & GHCR

---

## Table of Contents
1. [Project Overview & Architecture](#1-project-overview--architecture)
2. [Pipeline Stages](#2-pipeline-stages)
3. [Service Configurations](#3-service-configurations)
4. [Reusable Workflow Inputs Reference](#4-reusable-workflow-inputs-reference)
5. [Operator Runbook — Running Images from GHCR](#5-operator-runbook--running-images-from-ghcr)
6. [Troubleshooting Guide](#6-troubleshooting-guide)

---

## 1. Project Overview & Architecture

### What Does This Pipeline Do?

Instead of copying 50+ lines of CI/CD YAML into every microservice, this repository uses a **Reusable Workflow** pattern — a shared pipeline template that any service can call with custom inputs. Think of it as a parameterized function for software delivery.

| Feature | Description |
|:---|:---|
| **Reusable Workflow** | One shared `reusable-pipeline.yml` serves all microservices |
| **Parallel Pipelines** | All services run CI/CD simultaneously on every push |
| **Docker-Native** | Built, smoke-tested, scanned, and published to GHCR as OCI images |
| **Quality Gates** | Lint → 100% tests → coverage threshold → Trivy scan |
| **Dual CD Modes** | Continuous Deployment (zero-touch) or Continuous Delivery (staged + approval) |
| **Dual-Tag Publishing** | Every release tagged `:latest` AND `:<git-sha>` for rollback |

### End-to-End Flow

```
Git Push (main / PR)
        │
        ▼
[Job 1] Lint, Test & Coverage ──── FAIL → Pipeline halts
        │ PASS
        ▼
[Job 2] Build & Verify Container ─ FAIL → Pipeline halts
        │ PASS
        ├── Security Scan (Trivy, audit-only)
        └── Publish to GHCR (:latest + :<git-sha>)
               │
               ├─ deployment-type = "deployment" ──► Production (Zero-touch)
               │
               └─ deployment-type = "delivery"   ──► Staging (auto)
                                                        │
                                                        ▼
                                                  [Manual Approval Gate]
                                                        │
                                                        ▼
                                                  Production (gated)
```

> **On Pull Requests:** Only Lint/Test and Build/Verify stages run. Images are **never published** to GHCR on unmerged PRs.

### Repository Layout

```text
CI_CD_Pipeline/
├── .github/
│   └── workflows/
│       ├── reusable-pipeline.yml   ← Shared reusable workflow (the "function")
│       └── ci.yml                  ← Caller — invokes pipeline per service
│
├── services/
│   ├── learning_service/           ← FastAPI · Port 8000 · Continuous Deployment
│   │   ├── app/main.py
│   │   ├── tests/test_learning.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── pytest.ini
│   │
│   └── order_service/              ← FastAPI · Port 8080 · Continuous Delivery
│       ├── app/main.py
│       ├── tests/test_order.py
│       ├── Dockerfile
│       ├── requirements.txt
│       └── pytest.ini
│
└── docs/
    ├── pipeline-manual.html        ← Interactive HTML version of this manual
    └── CICD_PIPELINE_GUIDE.md      ← This file
```

---

## 2. Pipeline Stages

Every service call to `reusable-pipeline.yml` executes the following sequential job chain. Each job must succeed before the next begins.

---

### Stage 01 — Lint, Test & Coverage (`job: test`)

**Purpose:** Enforce code quality, correctness, and test coverage before any container is ever built.

**Runs on:** `ubuntu-latest` with pip dependency caching.

| Step | What Happens |
|:---|:---|
| Checkout code | Fetches repository at the triggering commit SHA |
| Setup Python | Provisions the configured Python version (default: `3.11`). Pip cache keyed to `requirements.txt`. |
| Install dependencies | Upgrades pip, installs `ruff` (linter) + all service requirements |
| **Lint with Ruff** | Scans for syntax errors, PEP 8 violations, unused imports, import ordering. Fails fast within seconds. |
| **Run Pytest + Coverage** | All tests must pass. Coverage below `min-coverage` blocks the Docker build entirely. |
| Upload coverage report | HTML `htmlcov/` report uploaded as artifact `coverage-report-{image-name}` |

```bash
# Exact command run inside the service working directory
pytest tests/ \
  --import-mode=importlib \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=html:htmlcov \
  --cov-fail-under=80   # (or 85 for order_service)
```

---

### Stage 02 — Build, Verify & Publish Container (`job: docker-build`)

**Purpose:** Assemble the OCI image, verify it runs, scan for CVEs, publish to GHCR.

**Condition:** Only starts if Stage 01 passes (`needs: test`).

| Step | What Happens |
|:---|:---|
| Set up Docker Buildx | Enables multi-platform build support |
| **Build Docker image** | `docker build -t {image-name}:latest .` using `python:3.11-slim` base |
| **Smoke Test** | Starts container, waits 3s for Uvicorn boot, curls health endpoint. Non-200 or crash = pipeline fail. |
| **Trivy security scan** | Audits image layers for CRITICAL/HIGH CVEs. Audit mode (`exit-code: 0`) — reports without blocking. |
| Login to GHCR | Authenticates via `GITHUB_TOKEN` (only on `main` branch or release events) |
| **Tag & Push to GHCR** | Publishes `:latest` (rolling) and `:{git-sha}` (immutable) tags. Owner auto-lowercased for OCI compliance. |

```bash
# Smoke Test sequence
docker run -d --name test-container \
  -p {app-port}:{app-port} {image-name}:latest
sleep 3
curl --fail http://localhost:{app-port}{health-endpoint}
docker stop test-container && docker rm test-container

# Dual-tag publish
IMAGE_URI="ghcr.io/${OWNER_LOWER}/{image-name}"
docker tag {image-name}:latest ${IMAGE_URI}:latest
docker tag {image-name}:latest ${IMAGE_URI}:{github.sha}
docker push ${IMAGE_URI}:latest
docker push ${IMAGE_URI}:{github.sha}
```

---

### Stage 3A — Continuous Deployment (`job: deploy-production-automated`)

**Activated when:** `deployment-type: "deployment"` *(Learning Service)*

**Philosophy:** Every commit that passes all quality gates is immediately live in production with zero human intervention.

**Flow:**
1. Pulls the exact SHA-tagged image from GHCR
2. Deploys to the `production-automated` GitHub Environment
3. Verifies the production container responds on its health route
4. Pipeline completes — no human approval required

> ✅ **Best for:** Fast-moving APIs, internal tools, learning systems where iteration speed outweighs manual oversight.

---

### Stage 3B — Continuous Delivery (`jobs: deploy-staging → deploy-production-gated`)

**Activated when:** `deployment-type: "delivery"` *(Order Service)*

**Philosophy:** The artifact is always production-ready, but actual production rollout requires human authorization.

**Flow:**
1. **Auto-deploy to Staging** — pulls SHA-tagged image, deploys to `staging` environment, health check verified
2. **Pause at Approval Gate** — pipeline enters *Waiting for review* state. GitHub notifies authorized reviewers via `production-manual-gate` environment protection rule
3. **Manual approval** — a reviewer inspects staging and clicks *Approve and deploy*
4. **Production deploy** — same SHA-pinned image deployed to production with health verification

> ⚠️ **Best for:** Financial services, order processing, billing — any system requiring human sign-off before reaching end users.

---

## 3. Service Configurations

Both microservices share the same reusable pipeline but are configured differently:

| Configuration | Learning Service | Order Service |
|:---|:---|:---|
| **Directory** | `services/learning_service` | `services/order_service` |
| **Port** | `8000` | `8080` |
| **Health Endpoint** | `/health` | `/healthz` |
| **Min Coverage** | `80%` | `85%` |
| **Image Name** | `learning-service` | `order-service` |
| **Deployment Type** | `deployment` (auto) | `delivery` (gated) |
| **Production Gate** | Zero-touch automation | Manual approval required |
| **Base Image** | `python:3.11-slim` | `python:3.11-slim` |
| **Framework** | FastAPI + Uvicorn | FastAPI + Uvicorn + Pydantic |
| **GHCR URI** | `ghcr.io/<owner>/learning-service` | `ghcr.io/<owner>/order-service` |

### Why Each Service Has Its Own `pytest.ini`

In a monorepo, pytest's discovery mechanism can accidentally pick up tests from sibling services. Each `pytest.ini` prevents this:

```ini
[pytest]
pythonpath = .           # Prevents ModuleNotFoundError: No module named 'app'
testpaths  = tests       # Restricts discovery to THIS service's test folder only
addopts    = --import-mode=importlib  # Isolated imports — prevents name collisions
```

---

## 4. Reusable Workflow Inputs Reference

All parameters accepted by `reusable-pipeline.yml` via `workflow_call`. Any service in `ci.yml` can override these defaults.

| Input | Type | Default | Required | Description |
|:---|:---|:---|:---|:---|
| `working-directory` | `string` | `"."` | No | Path to the service folder containing `Dockerfile` and `requirements.txt` |
| `python-version` | `string` | `"3.11"` | No | Python runtime version for the CI runner |
| `min-coverage` | `number` | `80` | No | Minimum code coverage % (0–100) for test job to pass |
| `image-name` | `string` | `"app"` | No | Docker image tag name and GHCR repository name (must be lowercase) |
| `app-port` | `number` | `8000` | No | Port the container exposes; used in smoke test and environment URLs |
| `health-endpoint` | `string` | `"/health"` | No | HTTP route for container health verification (must return HTTP 200) |
| `push-image` | `boolean` | `true` | No | Whether to publish to GHCR (only active on `main` or release events) |
| `deployment-type` | `string` | `"deployment"` | No | `"deployment"` = zero-touch auto; `"delivery"` = staged + manual gate |

### Adding a New Microservice (~3 minutes)

1. Create folder: `services/payment_service/`
2. Add: `app/main.py`, `tests/`, `Dockerfile`, `requirements.txt`, `pytest.ini`
3. Add one job block to `.github/workflows/ci.yml`:

```yaml
payment-service-ci:
  name: "Project 3: Payment Service"
  uses: ./.github/workflows/reusable-pipeline.yml
  with:
    working-directory: "services/payment_service"
    python-version:    "3.11"
    min-coverage:      80
    image-name:        "payment-service"
    app-port:          9000
    health-endpoint:   "/health"
    deployment-type:   "delivery"
```

No new CI/CD YAML to write. The new service automatically gets automated testing, coverage gates, and Docker verification.

---

## 5. Operator Runbook — Running Images from GHCR

### Step 1: Authenticate to GHCR (one-time setup)

Generate a GitHub Personal Access Token (PAT) with `read:packages` scope at:
*GitHub → Settings → Developer settings → Personal access tokens*

```bash
docker login ghcr.io -u YOUR_GITHUB_USERNAME
# When prompted for Password, paste your PAT (not your GitHub password)
```

> ⚠️ Store the PAT securely. Do not commit it to source control.

### Step 2: Pull the Latest Image

```bash
# Learning Service (port 8000)
docker pull ghcr.io/<owner>/learning-service:latest

# Order Service (port 8080)
docker pull ghcr.io/<owner>/order-service:latest

# Or pin to an exact version using the Git commit SHA
docker pull ghcr.io/<owner>/order-service:abc1234
```

### Step 3: Run the Container

```bash
# Learning Service
docker run -d \
  --name learning-api \
  -p 8000:8000 \
  ghcr.io/<owner>/learning-service:latest

# Order Service
docker run -d \
  --name order-api \
  -p 8080:8080 \
  ghcr.io/<owner>/order-service:latest
```

### Step 4: Verify the Service is Healthy

```bash
# Learning Service
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Order Service
curl http://localhost:8080/healthz
# Expected: {"status":"ok","service":"order-service"}

# Swagger API docs
# http://localhost:8000/docs  (Learning Service)
# http://localhost:8080/docs  (Order Service)
```

### Step 5: Rollback to a Previous Version

Because every pipeline run publishes an immutable SHA-tagged image, rolling back is instant:

```bash
# Stop and remove the current container
docker stop order-api && docker rm order-api

# Pull and run the previous known-good version by SHA
docker pull ghcr.io/<owner>/order-service:abc1234
docker run -d \
  --name order-api \
  -p 8080:8080 \
  ghcr.io/<owner>/order-service:abc1234
```

> ✅ Rollback is instant — the image is already in the registry. No re-build required.

### Step 6: Build & Test Locally (Without GHCR)

```bash
# Build from source
docker build -t learning-service:local services/learning_service
docker run -d --name learning-local -p 8000:8000 learning-service:local

# Run tests locally with coverage
cd services/learning_service
pytest --cov=app --cov-fail-under=80

# Cleanup
docker stop learning-local && docker rm learning-local
```

---

## 6. Troubleshooting Guide

| Issue | Root Cause | Recommended Action |
|:---|:---|:---|
| **Coverage Threshold Failure** | Test coverage below the service's configured minimum | Download `coverage-report-{service}` artifact from the build summary → open `index.html` → write tests for uncovered (red) lines |
| **Smoke Test Failure** | Container crashed on startup or health endpoint returned non-200 | Review CI logs for Uvicorn tracebacks; verify `app-port` and `health-endpoint` inputs match the Dockerfile `EXPOSE` and app route |
| **Local Port Conflict** | Container name or host port already allocated | `docker rm -f <container-name>` before re-running |
| **Registry Casing Error** | Uppercase characters in image name or owner | OCI spec requires lowercase. Pipeline auto-lowercases owner; ensure `image-name` input is all lowercase |
| **Ruff Lint Failure** | Style or import violations in source code | Run `ruff check .` locally in the service directory, fix the flagged issues, push again |
| **Image Not Found in GHCR** | Pipeline ran on a PR (not main branch) | Images are only published on pushes to `main` or release events — merge the PR first |
| **Virtual Environment Committed** | `.venv/` folder staged or pushed | Add `.venv/` to `.gitignore`. Virtual environments should never be committed. |

---

*CI/CD Pipeline Documentation Manual · GitHub Actions · Docker · GHCR · FastAPI*
