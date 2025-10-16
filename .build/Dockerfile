# Production Dockerfile for AI Telegram Bot
# Multi-stage build for optimized image size and security

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev

# Install UV package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Configure UV to use explicit venv location
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Install dependencies (no dev dependencies)
RUN uv sync --frozen --no-dev

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.11-alpine AS runtime

# Set labels
LABEL maintainer="AI Telegram Bot"
LABEL description="AI-powered Telegram bot with LLM integration (Production)"
LABEL version="1.0"

# Install only runtime dependencies
RUN apk add --no-cache \
    libffi \
    procps \
    su-exec \
    && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -g 1000 bot && \
    adduser -D -u 1000 -G bot bot

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder /app/.venv /app/.venv

# Copy source code and version file
COPY --chown=bot:bot src/ ./src/
COPY --chown=bot:bot README.md VERSION ./

# Copy Alembic configuration and migrations
COPY --chown=bot:bot alembic.ini ./
COPY --chown=bot:bot alembic/ ./alembic/

# Copy entrypoint script
COPY .build/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Create directories for data and logs with proper permissions
RUN mkdir -p data logs .cache && \
    chown -R bot:bot data logs .cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"
ENV UV_NO_CACHE=1

# Healthcheck - проверяем что процесс бота запущен
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "python -m src.main" || exit 1

# Entrypoint для исправления прав доступа при старте
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Run the bot (без --env-file, конфигурация из environment variables)
CMD ["su-exec", "bot", "uv", "run", "python", "-m", "src.main"]
