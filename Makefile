.PHONY: help install run docker-build docker-up docker-down docker-logs docker-restart clean test test-fast lint format pre-commit-install ci

# ===== Platform Detection =====
# Автоопределение операционной системы
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

# Путь к директории бота и API
BOT_DIR := backend/bot
API_DIR := backend/api

# Определение команды UV в зависимости от ОС
ifeq ($(DETECTED_OS),Windows)
    # Windows: используем полный путь к uv.exe через PowerShell
    UV_BOT := powershell -Command "cd $(BOT_DIR); & '$$env:USERPROFILE\.local\bin\uv.exe'"
    UV_API := powershell -Command "cd $(API_DIR); & '$$env:USERPROFILE\.local\bin\uv.exe'"
    RM := powershell -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
    FIND_PYC := powershell -Command "Get-ChildItem -Recurse -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue"
    FIND_PYO := powershell -Command "Get-ChildItem -Recurse -Filter '*.pyo' | Remove-Item -Force -ErrorAction SilentlyContinue"
else
    # Linux/macOS: используем uv из PATH
    UV_BOT := cd $(BOT_DIR) && uv
    UV_API := cd $(API_DIR) && uv
    RM := rm -rf
    FIND_PYC := find . -type f -name '*.pyc' -delete
    FIND_PYO := find . -type f -name '*.pyo' -delete
endif

# Colors for output (works in most terminals)
BLUE := \033[0;34m
GREEN := \033[0;32m
NC := \033[0m # No Color

# Default target
help:
	@echo "==================================================="
	@echo "  AI Telegram Bot - Available Commands"
	@echo "==================================================="
	@echo ""
	@echo "Detected OS: $(DETECTED_OS)"
	@echo ""
	@echo "Bot Development:"
	@echo "  make install       - Install bot dependencies locally via UV"
	@echo "  make run           - Run bot locally"
	@echo "  make test          - Run bot tests with coverage"
	@echo "  make test-fast     - Run bot tests without coverage"
	@echo ""
	@echo "API Development:"
	@echo "  make api-install   - Install API dependencies"
	@echo "  make api-run       - Run API server locally (production mode)"
	@echo "  make api-dev       - Run API server with hot-reload"
	@echo "  make api-test      - Run API tests"
	@echo "  make api-test-cov  - Run API tests with coverage"
	@echo "  make api-lint      - Check API code quality"
	@echo "  make api-format    - Format API code"
	@echo ""
	@echo "Database Migrations:"
	@echo "  make db-migrate    - Apply all pending migrations"
	@echo "  make db-rollback   - Rollback last migration"
	@echo "  make db-revision   - Create new migration (use message='...')"
	@echo "  make db-current    - Show current migration version"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format        - Format all code (bot + API)"
	@echo "  make lint          - Run linter for all code"
	@echo "  make ci            - Run all CI checks (format + lint)"
	@echo "  make pre-commit-install - Install pre-commit hooks"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build  - Build all Docker images"
	@echo "  make docker-up     - Start all services in Docker"
	@echo "  make docker-down   - Stop all Docker containers"
	@echo "  make docker-logs   - View Docker logs (bot)"
	@echo "  make docker-api-logs - View API Docker logs"
	@echo "  make docker-restart- Restart Docker containers"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Clean temporary files and caches"
	@echo ""
	@echo "==================================================="

# ===== Bot Development =====

install:
	@echo "Installing bot dependencies via UV..."
	@$(UV_BOT) sync
	@echo "Dependencies installed successfully!"

run:
	@echo "Starting bot locally..."
	@$(UV_BOT) run python -m src.main --env-file .env.development

test:
	@echo "Running bot tests with coverage..."
	@$(UV_BOT) run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

test-fast:
	@echo "Running bot tests without coverage..."
	@$(UV_BOT) run pytest tests/ -v

lint:
	@echo "Running linter and type checker for bot..."
	@$(UV_BOT) run ruff check src/ tests/
	@$(UV_BOT) run mypy src/

format:
	@echo "Formatting bot code..."
	@$(UV_BOT) run ruff format src/ tests/
	@$(UV_BOT) run ruff check --fix src/ tests/

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@$(UV_BOT) run pre-commit install

ci: format lint api-format api-lint
	@echo "CI checks passed!"

# ===== API Development =====

api-install:
	@echo "Installing API dependencies..."
	@$(UV_API) sync
	@echo "API dependencies installed successfully!"

api-run:
	@echo "Starting API server (production mode)..."
	@$(UV_API) run python run_api.py

api-dev:
	@echo "Starting API server with hot-reload..."
	@$(UV_API) run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

api-test:
	@echo "Running API tests..."
	@$(UV_API) run pytest tests/ -v

api-test-cov:
	@echo "Running API tests with coverage..."
	@$(UV_API) run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

api-lint:
	@echo "Checking API code quality..."
	@$(UV_API) run ruff check src/ tests/
	@$(UV_API) run mypy src/

api-format:
	@echo "Formatting API code..."
	@$(UV_API) run ruff format src/ tests/
	@$(UV_API) run ruff check --fix src/ tests/

# ===== Database Migrations =====

db-migrate:
	@echo "Applying database migrations..."
	@$(UV_BOT) run alembic upgrade head
	@echo "Migrations applied successfully!"

db-rollback:
	@echo "Rolling back last migration..."
	@$(UV_BOT) run alembic downgrade -1
	@echo "Rollback completed!"

db-revision:
	@echo "Creating new migration..."
ifndef message
	@echo "Error: Please provide a migration message: make db-revision message='Your message here'"
	@exit 1
endif
	@$(UV_BOT) run alembic revision --autogenerate -m "$(message)"
	@echo "Migration created successfully!"

db-current:
	@echo "Current database version:"
	@$(UV_BOT) run alembic current

# ===== Docker Commands =====

docker-build:
	@echo "Building Docker image..."
	docker-compose build
	@echo "Docker image built successfully!"

docker-up:
	@echo "Starting bot in Docker..."
	docker-compose up -d
	@echo "Bot started! Use 'make docker-logs' to view logs"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "Containers stopped successfully!"

docker-logs:
	@echo "Showing bot Docker logs (Ctrl+C to exit)..."
	docker-compose logs -f bot

docker-api-logs:
	@echo "Showing API Docker logs (Ctrl+C to exit)..."
	docker-compose logs -f api

docker-restart: docker-down docker-up
	@echo "Docker containers restarted!"

# ===== Maintenance =====

clean:
	@echo "Cleaning temporary files..."
	@$(RM) $(BOT_DIR)/__pycache__ $(BOT_DIR)/src/__pycache__ $(BOT_DIR)/tests/__pycache__ $(BOT_DIR)/.pytest_cache $(BOT_DIR)/htmlcov $(BOT_DIR)/.coverage
	@$(FIND_PYC)
	@$(FIND_PYO)
	@echo "Cleaned successfully!"

