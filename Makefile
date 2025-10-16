.PHONY: help install run docker-build docker-up docker-down docker-logs docker-restart clean test test-fast lint format pre-commit-install ci

# ===== Platform Detection =====
# Автоопределение операционной системы
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

# Определение команды UV в зависимости от ОС
ifeq ($(DETECTED_OS),Windows)
    # Windows: используем полный путь к uv.exe через PowerShell
    UV := powershell -Command "& '$$env:USERPROFILE\.local\bin\uv.exe'"
    RM := powershell -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
    FIND_PYC := powershell -Command "Get-ChildItem -Recurse -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue"
    FIND_PYO := powershell -Command "Get-ChildItem -Recurse -Filter '*.pyo' | Remove-Item -Force -ErrorAction SilentlyContinue"
else
    # Linux/macOS: используем uv из PATH
    UV := uv
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
	@echo "Local Development:"
	@echo "  make install       - Install dependencies locally via UV"
	@echo "  make run           - Run bot locally"
	@echo "  make test          - Run tests with coverage"
	@echo "  make test-fast     - Run tests without coverage"
	@echo ""
	@echo "Database Migrations:"
	@echo "  make db-migrate    - Apply all pending migrations"
	@echo "  make db-rollback   - Rollback last migration"
	@echo "  make db-revision   - Create new migration (use message='...')"
	@echo "  make db-current    - Show current migration version"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format        - Format code with ruff"
	@echo "  make lint          - Run linter and type checker"
	@echo "  make ci            - Run all CI checks (format + lint)"
	@echo "  make pre-commit-install - Install pre-commit hooks"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start bot in Docker (detached)"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - View Docker logs (follow mode)"
	@echo "  make docker-restart- Restart Docker containers"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Clean temporary files and caches"
	@echo ""
	@echo "==================================================="

# ===== Local Development =====

install:
	@echo "Installing dependencies via UV..."
	@$(UV) sync
	@echo "Dependencies installed successfully!"

run:
	@echo "Starting bot locally..."
	@$(UV) run python -m src.main --env-file .env.development

test:
	@echo "Running tests with coverage..."
	@$(UV) run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

test-fast:
	@echo "Running tests without coverage..."
	@$(UV) run pytest tests/ -v

lint:
	@echo "Running linter and type checker..."
	@$(UV) run ruff check src/ tests/
	@$(UV) run mypy src/

format:
	@echo "Formatting code..."
	@$(UV) run ruff format src/ tests/
	@$(UV) run ruff check --fix src/ tests/

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@$(UV) run pre-commit install

ci: format lint
	@echo "CI checks passed!"

# ===== Database Migrations =====

db-migrate:
	@echo "Applying database migrations..."
	@$(UV) run alembic upgrade head
	@echo "Migrations applied successfully!"

db-rollback:
	@echo "Rolling back last migration..."
	@$(UV) run alembic downgrade -1
	@echo "Rollback completed!"

db-revision:
	@echo "Creating new migration..."
ifndef message
	@echo "Error: Please provide a migration message: make db-revision message='Your message here'"
	@exit 1
endif
	@$(UV) run alembic revision --autogenerate -m "$(message)"
	@echo "Migration created successfully!"

db-current:
	@echo "Current database version:"
	@$(UV) run alembic current

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
	@echo "Showing Docker logs (Ctrl+C to exit)..."
	docker-compose logs -f bot

docker-restart: docker-down docker-up
	@echo "Docker containers restarted!"

# ===== Maintenance =====

clean:
	@echo "Cleaning temporary files..."
	@$(RM) __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache htmlcov .coverage
	@$(FIND_PYC)
	@$(FIND_PYO)
	@echo "Cleaned successfully!"

