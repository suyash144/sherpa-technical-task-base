# syntax=docker/dockerfile:1

# Use multi-stage build for efficiency
FROM python:3.12-slim AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies into the system
RUN uv sync --frozen --no-install-project --no-dev

# Development stage
FROM python:3.12-slim AS development

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy UV from builder stage
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

WORKDIR /app

# Copy the virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# Production stage (same as before but with proper src path)
FROM development AS production

# Copy source code
COPY src ./src

# Create data directories with proper permissions
RUN mkdir -p /app/data/{uploads,documents,vector_store,logs}

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
