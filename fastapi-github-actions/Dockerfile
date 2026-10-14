# ==============================================================================
# Multi-stage production Dockerfile leveraging uv for ultrafast resolution
# ==============================================================================
FROM ghcr.io/astral-sh/uv:0.4.15 AS uv-bin

FROM python:3.11-slim AS runner

WORKDIR /app

# Copy uv binary from official image
COPY --from=uv-bin /uv /uvx /bin/

# Environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install project dependencies into system environment using uv
COPY pyproject.toml ./
RUN uv pip install --no-cache .

# Copy application source code and migrations
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Native Python health check (Zero apt/curl external network dependency)
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
