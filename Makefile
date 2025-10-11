.PHONY: help install run docker-build docker-up docker-down docker-logs docker-restart clean test lint format pre-commit-install ci

# Colors for output (works in some terminals)
BLUE := \033[0;34m
GREEN := \033[0;32m
NC := \033[0m # No Color

# Default target
help:
	@echo "==================================================="
	@echo "  AI Telegram Bot - Available Commands"
	@echo "==================================================="
	@echo ""
	@echo "Local Development:"
	@echo "  make install       - Install dependencies locally via UV"
	@echo "  make run           - Run bot locally"
	@echo "  make test          - Run tests (if available)"
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
	@powershell -Command "& '$$env:USERPROFILE\.local\bin\uv.exe' sync"
	@echo "Dependencies installed successfully!"

run:
	@echo "Starting bot locally..."
	@powershell -Command "& '$$env:USERPROFILE\.local\bin\uv.exe' run python -m src.main --env-file .env.development"

test:
	@echo "Running tests..."
	@powershell -Command "& '$$env:USERPROFILE\.local\bin\uv.exe' run pytest tests/"

lint:
	@echo "Running linter and type checker..."
	@powershell -Command "& '$$env:USERPROFILE\.local\bin\uv.exe' run ruff check src/ tests/"
	@powershell -Command "& '$$env:USERPROFILE\.local\bin\uv.exe' run mypy src/"

format:
	@echo "Formatting code..."
	@powershell -Command "& '$$env:USERPROFILE\.local\bin\uv.exe' run ruff format src/ tests/"
	@powershell -Command "& '$$env:USERPROFILE\.local\bin\uv.exe' run ruff check --fix src/ tests/"

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@powershell -Command "& '$$env:USERPROFILE\.local\bin\uv.exe' run pre-commit install"

ci: format lint
	@echo "CI checks passed!"

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
	@powershell -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue __pycache__, src\__pycache__, tests\__pycache__, .pytest_cache"
	@powershell -Command "Get-ChildItem -Recurse -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Recurse -Filter '*.pyo' | Remove-Item -Force -ErrorAction SilentlyContinue"
	@echo "Cleaned successfully!"

