# ==============================================================================
# Multi-Stage Production Dockerfile for FastAPI
# ==============================================================================
# Stage 1: Build virtual environment with dependencies
# Stage 2: Final lightweight, secure non-root runtime container
# ==============================================================================

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Configure Python environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install project dependencies into dedicated venv
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# ==============================================================================
# Stage 2: Final Production Runner
# ==============================================================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Ensure non-buffered stdout and clean Python runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Copy pre-built virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source code
COPY app/ ./app/
COPY pyproject.toml ./

# Create dedicated non-root user and assign permissions
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Native Python healthcheck (requires zero external network/curl dependencies)
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default startup command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
