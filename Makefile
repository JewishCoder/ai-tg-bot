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
	@echo "Frontend Development:"
	@echo "  make frontend-install     - Install frontend dependencies"
	@echo "  make frontend-dev         - Run frontend dev server"
	@echo "  make frontend-build       - Build frontend for production"
	@echo "  make frontend-start       - Start production server"
	@echo "  make frontend-lint        - Check frontend code quality"
	@echo "  make frontend-format      - Format frontend code"
	@echo "  make frontend-type-check  - Check TypeScript types"
	@echo "  make frontend-test        - Run frontend tests"
	@echo "  make frontend-test-cov    - Run frontend tests with coverage"
	@echo "  make frontend-check       - Run all frontend checks"
	@echo "  make frontend-clean       - Clean frontend build files"
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
	@echo "Production Deployment:"
	@echo "  make pull-images   - Pull Docker images from registry"
	@echo "  make deploy-prod   - Deploy production environment"
	@echo "  make restart-service service=<name> - Restart specific service"
	@echo "  make prod-logs     - View all production logs"
	@echo "  make prod-status   - Show production services status"
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

# ===== Frontend Development =====

FRONTEND_DIR := frontend

frontend-install:
	@echo "Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo "Frontend dependencies installed successfully!"

frontend-dev:
	@echo "Starting frontend dev server..."
	cd $(FRONTEND_DIR) && npm run dev

frontend-build:
	@echo "Building frontend for production..."
	cd $(FRONTEND_DIR) && npm run build
	@echo "Frontend built successfully!"

frontend-start:
	@echo "Starting production server..."
	cd $(FRONTEND_DIR) && npm start

frontend-lint:
	@echo "Checking frontend code quality..."
	cd $(FRONTEND_DIR) && npm run lint

frontend-format:
	@echo "Formatting frontend code..."
	cd $(FRONTEND_DIR) && npm run format

frontend-type-check:
	@echo "Checking TypeScript types..."
	cd $(FRONTEND_DIR) && npm run type-check

frontend-test:
	@echo "Running frontend tests..."
	cd $(FRONTEND_DIR) && npm run test -- --run

frontend-test-cov:
	@echo "Running frontend tests with coverage..."
	cd $(FRONTEND_DIR) && npm run test:coverage -- --run

frontend-clean:
	@echo "Cleaning frontend build files..."
ifeq ($(DETECTED_OS),Windows)
	cd $(FRONTEND_DIR) && powershell -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .next,out,node_modules"
else
	cd $(FRONTEND_DIR) && rm -rf .next out node_modules
endif
	@echo "Frontend cleaned successfully!"

frontend-check: frontend-lint frontend-type-check frontend-test
	@echo "✅ All frontend checks passed!"

frontend-docker-build:
	@echo "Building frontend Docker image..."
	cd $(FRONTEND_DIR) && docker build -t ai-tg-bot-frontend .
	@echo "Frontend Docker image built successfully!"

frontend-docker-run:
	@echo "Running frontend in Docker..."
	docker run -p 3000:3000 ai-tg-bot-frontend

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

# ===== Production Deployment =====

pull-images:
	@echo "Pulling Docker images from registry..."
	@echo "Note: Make sure YC_REGISTRY_ID and version variables are set in .env"
	docker-compose pull
	@echo "Images pulled successfully!"

deploy-prod:
	@echo "Deploying production environment..."
	@echo "Note: Make sure to configure docker-compose.yml to use 'image' instead of 'build'"
	docker-compose --env-file .env.production up -d
	@echo "Production deployment started!"

restart-service:
ifndef service
	@echo "Error: Please specify service name: make restart-service service=<bot|api|frontend|nginx>"
	@exit 1
endif
	@echo "Restarting service: $(service)..."
	docker-compose restart $(service)
	@echo "Service $(service) restarted!"

prod-logs:
	@echo "Showing all production logs (Ctrl+C to exit)..."
	docker-compose logs -f

prod-status:
	@echo "Production services status:"
	docker-compose ps

