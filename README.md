# AI Telegram Bot

[![CI](https://github.com/jewishcoder/ai-tg-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/jewishcoder/ai-tg-bot/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen.svg)](./htmlcov/index.html)
[![Tests](https://img.shields.io/badge/tests-117%20passing-brightgreen.svg)](#-тестирование)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

**LLM-ассистент в виде Telegram-бота с интеграцией OpenRouter API.**

Надежный, производительный и хорошо протестированный бот для работы с различными LLM моделями через единый API.

---

## ✨ Ключевые возможности

- 🧠 **LLM интеграция** через OpenRouter с автоматическим fallback на резервную модель
- 🗄️ **PostgreSQL 16** с async SQLAlchemy 2.0, soft delete, per-user настройки
- 🛡️ **Enterprise-grade** надежность: rate limiting, error recovery, graceful shutdown
- 📊 **Stats Dashboard** с real-time мониторингом активности (Next.js + shadcn/ui)
- ⚡ **Высокая производительность**: кеширование, connection pooling, оптимизированные SQL запросы
- 🧪 **117 тестов** (89% coverage), строгая типизация (Mypy), CI/CD для всех сервисов
- 🐳 **Production-ready**: Docker multi-service, auto-deploy в Container Registry

---

## 📚 Документация

- 📖 **[Все гайды](docs/guides/README.md)** - полный индекс документации с quick start руководствами
- 🔧 **[API Reference](docs/backend/bot/api/README.md)** - Bot API (Bot, Storage, LLM Client, Database, Handlers)
- 📊 **[Stats API](docs/backend/api/README.md)** - REST API для статистики диалогов
- 🖥️ **[Frontend](frontend/README.md)** - Dashboard документация (Next.js + shadcn/ui)
- 🗺️ **[Roadmap](docs/roadmap.md)** - план развития (7 спринтов завершено)
- 🤝 **[CONTRIBUTING.md](CONTRIBUTING.md)** - стандарты кода, тестирование, contribution guide

---

## 🚀 Быстрый старт

### Требования
- Telegram Bot Token [@BotFather](https://t.me/botfather) и OpenRouter API Key [openrouter.ai](https://openrouter.ai)
- Docker Desktop или Docker Engine + Docker Compose v2.0+

### Запуск

```bash
# 1. Клонировать и настроить
git clone <repository-url>
cd ai-tg-bot
cp backend/bot/.env.example backend/bot/.env.development

# 2. Отредактировать backend/bot/.env.development:
#    TELEGRAM_TOKEN, OPENROUTER_API_KEY, DB_PASSWORD

# 3. Запустить все сервисы (Bot + PostgreSQL + API + Frontend)
docker-compose up -d

# 4. Проверить логи
docker-compose logs -f bot
```

📖 **Подробная документация:**
- 🐳 [DOCKER.md](DOCKER.md) - работа с Docker (отдельные сервисы, troubleshooting)
- 💻 [Локальный запуск](docs/guides/README.md) - для разработки без Docker
- 🚀 [Production deployment](docs/guides/ci-cd.md) - production развертывание с CI/CD

---

## 📊 Multi-Service Архитектура

### 🤖 Telegram Bot
Основной сервис с LLM интеграцией, PostgreSQL для хранения истории диалогов.

**Команды:** `/start` `/help` `/role <text>` `/reset` `/status`

📖 [Bot API Reference](docs/backend/bot/api/README.md) | [Database](docs/backend/bot/api/database.md)

### 📊 Stats API (FastAPI)
REST API для статистики диалогов с Mock/Real режимами.

```bash
# Swagger UI
http://localhost:8000/docs

# Endpoints
GET /api/v1/stats?period=day|week|month
GET /health
```

📖 [API Documentation](backend/api/README.md) | [API Contract](docs/backend/api/stats-api-contract.md)

### 🖥️ Dashboard (Next.js 15)
Web-интерфейс для мониторинга: Period Filter, Summary Cards, Activity Charts, Tables.

```bash
http://localhost:3000
```

📖 [Frontend Documentation](frontend/README.md) | [Requirements](docs/frontend/dashboard-requirements.md)

### 🗄️ PostgreSQL 16
Единая БД для всех сервисов: `users`, `messages` (soft delete), `user_settings`.

```bash
# Управление миграциями
make db-migrate        # Применить
make db-rollback       # Откатить
make db-revision message="..."  # Создать
```

📖 [Database API](docs/backend/bot/api/database.md)


---

## 🛡️ Отказоустойчивость

Автоматическое переключение на резервную LLM модель при недоступности основной (rate limit, ошибки API).

```bash
# Настройка в .env.development
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_FALLBACK_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

📖 [Подробная документация Fallback](docs/FALLBACK.md)

---

## 🚀 Production Deployment

```bash
# Pull образов из registry
make pull-images

# Запустить production
make deploy-prod
```

**Возможности:**
- Auto-deploy через CI/CD в Yandex Container Registry
- Multi-stage Docker builds для оптимизации размера
- Версионирование для Bot (1.4.2), API (0.1.0), Frontend (0.1.2), Nginx (1.0.0)
- Health checks и resource limits

📖 [CI/CD Guide](docs/guides/ci-cd.md) | [DOCKER.md](DOCKER.md)

---

## 🛠️ Development

```bash
# Установка для разработки
uv sync --all-extras
make pre-commit-install

# Проверка качества кода
make format      # Форматирование
make lint        # Линтинг + Mypy
make test        # 117 тестов (89% coverage)
make ci          # Все проверки (как в CI)
```

**Стандарты:**
- Один класс = один файл, type hints обязательны, async/await для I/O
- Ruff (linter + formatter), Mypy strict mode, pre-commit hooks
- 117 тестов (25 integration, 92 unit), coverage ≥ 70% для критической логики

📖 [CONTRIBUTING.md](CONTRIBUTING.md) | [vision.md](docs/vision.md)

---

## 🏗️ Архитектура

**Технологический стек:**
- **Backend**: Python 3.11+, aiogram 3.x, OpenAI SDK, FastAPI, SQLAlchemy 2.0, PostgreSQL 16
- **Frontend**: Next.js 15, TypeScript 5, shadcn/ui, TanStack Query, Recharts
- **DevOps**: Docker + Compose, GitHub Actions CI/CD, Yandex Container Registry

**Структура:**
```
ai-tg-bot/
├── backend/bot/      # Telegram Bot (aiogram, LLM, PostgreSQL)
├── backend/api/      # Stats API (FastAPI, Mock/Real collectors)
├── frontend/         # Dashboard (Next.js 15 + shadcn/ui)
├── docs/             # Документация
└── docker-compose.yml
```

📖 [vision.md](docs/vision.md) | [API Reference](docs/backend/bot/api/README.md)

---

## 🎯 Roadmap

**✅ Завершено (7 спринтов):**
- **S0-S2**: MVP, PostgreSQL, Качество кода (117 тестов, 89% coverage), Fallback, Rate limiting
- **S3-S5**: Mock API, Frontend Setup (Next.js 15), Dashboard Implementation
- **S7**: Real API Integration (PostgreSQL, оптимизированные SQL запросы)
- **S8**: CI/CD Infrastructure (4 workflows, auto-deploy в Container Registry)

**⏳ Планируется:**
- **S6**: AI Chat Implementation (WebSocket + text-to-SQL для natural language analytics)

📖 [docs/roadmap.md](docs/roadmap.md) | [CHANGELOG.md](CHANGELOG.md)

---

## 🐳 Docker Registry

Автоматическая публикация образов в Yandex Container Registry при push в `main`.

**Версии:**
- Bot: `1.4.2`, API: `0.1.0`, Frontend: `0.1.2`, Nginx: `1.0.0`

```bash
# Доступные образы
cr.yandex/{registry-id}/ai-tg-bot:{version|latest}
cr.yandex/{registry-id}/ai-tg-api:{version|latest}
cr.yandex/{registry-id}/ai-tg-frontend:{version|latest}
cr.yandex/{registry-id}/ai-tg-nginx:{version|latest}

# Обновить версию
echo "1.5.0" > backend/bot/VERSION
git commit -am "chore: bump version to 1.5.0"
git push origin main  # Автоматически соберется новый образ
```

**Требуемые GitHub Secrets:** `YA_CLOUD_REGISTRY`, `YC_REGISTRY_ID`

📖 [CI/CD Guide](docs/guides/ci-cd.md)

---

## 📄 Лицензия

MIT

---

## 🤝 Contributing

Приветствуем любой вклад! Стандарты кода, требования к тестам, процесс разработки описаны в [CONTRIBUTING.md](CONTRIBUTING.md).

---

**Сделано с ❤️ для сообщества разработчиков**
