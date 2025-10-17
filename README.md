# AI Telegram Bot

[![CI](https://github.com/jewishcoder/ai-tg-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/jewishcoder/ai-tg-bot/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen.svg)](./htmlcov/index.html)
[![Tests](https://img.shields.io/badge/tests-117%20passing-brightgreen.svg)](#-тестирование)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

**LLM-ассистент в виде Telegram-бота с интеграцией OpenRouter API.**

Надежный, производительный и хорошо протестированный бот для работы с различными LLM моделями через единый API.

---

## ✨ Основные возможности

### 🤖 Интеллектуальный ассистент
- 🧠 Поддержка любых LLM моделей через [OpenRouter](https://openrouter.ai)
- 🎭 Настраиваемые роли (системный промпт)
- 💬 Контекстные диалоги с историей
- 🔄 Автоматический fallback на резервную модель при сбоях

### 🛡️ Надежность и безопасность
- ⚡ **Rate limiting** - защита от spam и DDoS
- 🔁 **Error recovery** - автоматические retry с exponential backoff
- 🚦 **Graceful shutdown** - корректное завершение активных задач
- 🔒 **Security hardening** - sanitization логов, защита sensitive данных
- 🎯 **Transactional integrity** - атомарность операций с БД

### 📊 Производительность
- 🚀 **Кеширование** - TTL cache для системных промптов (5 мин)
- 🔍 **Оптимизированные запросы** - составные индексы БД, lazy loading
- 💾 **Connection pooling** - переиспользование соединений PostgreSQL
- ⏱️ **Async всё** - неблокирующие I/O операции

### 🗄️ База данных
- 🐘 **PostgreSQL 16** - надежное хранение данных
- 🔄 **Alembic** - управление миграциями схемы
- 🗑️ **Soft delete** - данные не удаляются физически
- 👤 **Per-user настройки** - индивидуальные лимиты и промпты

### 🧪 Качество кода
- ✅ **117 тестов** (89% coverage)
- 🔍 **Строгая типизация** (Mypy strict mode)
- 📏 **Code quality** (Ruff linter + formatter)
- 🪝 **Pre-commit hooks** - автоматические проверки
- 🤖 **CI/CD** - GitHub Actions

---

## 📚 Документация

### 🎯 Быстрый старт
- 🐳 **[Запуск в Docker](#-запуск-через-docker-рекомендуется)** - рекомендуемый способ
- 💻 **[Локальный запуск](#-локальный-запуск-альтернатива)** - для разработки
- 🚀 **[Production развертывание](#-production-развертывание)** - deployment guide

### 📖 Для разработчиков
- 🔧 **[API Reference](docs/api/README.md)** - архитектура и API всех компонентов
  - [Bot API](docs/api/bot.md) - главный класс бота
  - [Storage API](docs/api/storage.md) - работа с БД и историей
  - [LLM Client API](docs/api/llm_client.md) - интеграция с LLM
  - [Database API](docs/api/database.md) - управление PostgreSQL
  - [Handlers API](docs/api/handlers.md) - обработчики команд и сообщений
- 📋 **[vision.md](docs/vision.md)** - техническое видение проекта
- 🗺️ **[roadmap.md](docs/roadmap.md)** - план развития (3 спринта завершено)
- 🤝 **[CONTRIBUTING.md](CONTRIBUTING.md)** - руководство по контрибуции
- 📝 **[CHANGELOG.md](CHANGELOG.md)** - история изменений
- 🎨 **[Visual Guide](docs/guides/VISUAL_GUIDE.md)** - визуальный обзор архитектуры

### 📚 Руководства
- 📖 **[Все гайды](docs/guides/README.md)** - полный индекс документации
- 🐳 **[DOCKER.md](DOCKER.md)** - работа с Docker
- 🛡️ **[FALLBACK.md](docs/FALLBACK.md)** - fallback механизм

---

## 🚀 Быстрый старт

### Требования

**Общие:**
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))
- OpenRouter API Key (получить на [openrouter.ai](https://openrouter.ai))

**Для запуска в Docker (рекомендуется):**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) или Docker Engine
- Docker Compose v2.0+

**Для локального запуска:**
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - менеджер зависимостей

---

### 🐳 Запуск через Docker (рекомендуется)

**1. Клонировать репозиторий и настроить конфигурацию:**

```bash
git clone <repository-url>
cd ai-tg-bot

# Создать конфигурацию для бота
cp backend/bot/.env.example backend/bot/.env.development

# Отредактируйте backend/bot/.env.development:
# - TELEGRAM_TOKEN (получить у @BotFather)
# - OPENROUTER_API_KEY (получить на openrouter.ai)
# - DB_PASSWORD (установите надежный пароль для PostgreSQL)

# Создать .env для Docker Compose (опционально, если нужно переопределить параметры БД)
# echo "DB_USER=botuser" > .env
# echo "DB_PASSWORD=your_secure_password" >> .env
# echo "DB_NAME=ai_tg_bot" >> .env
```

**Важно:** 
- `backend/bot/.env.development` - основная конфигурация бота (монтируется в контейнер)
- `.env` (опционально) - переменные для Docker Compose (например, параметры PostgreSQL)

**2. Собрать и запустить:**

```bash
# Собрать Docker образ
docker-compose build

# Запустить бота в фоновом режиме
docker-compose up -d

# Посмотреть логи
docker-compose logs -f bot
```

**3. Остановка:**

```bash
docker-compose down
```

📖 Подробная документация: [DOCKER.md](DOCKER.md)

---

### 💻 Локальный запуск (альтернатива)

**1. Клонировать репозиторий и настроить конфигурацию:**

```bash
git clone <repository-url>
cd ai-tg-bot
cp backend/bot/.env.example backend/bot/.env.development

# Отредактируйте backend/bot/.env.development:
# - TELEGRAM_TOKEN и OPENROUTER_API_KEY
# - DB_HOST=localhost (для локального запуска вместо 'postgres')
```

**2. Установить зависимости:**

```bash
uv sync
```

**3. Запустить PostgreSQL:**

```bash
# Запустить только PostgreSQL через Docker
docker-compose up postgres -d

# Применить миграции
make db-migrate
```

**4. Запустить бота:**

**Через Makefile (рекомендуется):**
```bash
make run
```

**Через UV напрямую:**
```bash
cd backend/bot
uv run python -m src.main --env-file .env.development
```

**Через виртуальное окружение:**
```bash
cd backend/bot
# Активировать окружение
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Запустить бота
python -m src.main --env-file .env.development
```

---

## 🗄️ База данных PostgreSQL

Бот использует PostgreSQL для хранения истории диалогов и настроек пользователей.

### Схема базы данных

- **`users`** - информация о пользователях Telegram
- **`messages`** - история сообщений (с soft delete стратегией)
- **`user_settings`** - персональные настройки (лимиты, кастомные промпты)

📖 Подробности: [Database API](docs/api/database.md)

### Управление миграциями

```bash
# Применить все миграции
make db-migrate

# Откатить последнюю миграцию
make db-rollback

# Создать новую миграцию
make db-revision message="Add new field"

# Проверить текущую версию БД
make db-current
```

### Конфигурация

```bash
# В backend/bot/.env.development (или .env для Docker Compose)
DB_HOST=postgres         # Для Docker: postgres; для локального: localhost
DB_PORT=5432            # Порт БД
DB_NAME=ai_tg_bot       # Имя базы данных
DB_USER=botuser         # Пользователь БД
DB_PASSWORD=your_secure_password  # ВАЖНО: надежный пароль!
DB_ECHO=False           # SQLAlchemy echo (True для отладки SQL)
```

**⚠️ Важно:** Для production используйте надежные пароли и не коммитьте `.env` файлы в репозиторий!

---

## 📋 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу с ботом |
| `/help` | Показать справку по командам |
| `/role <текст>` | Установить роль ассистента (системный промпт) |
| `/role default` | Вернуться к роли по умолчанию |
| `/reset` | Очистить историю диалога |
| `/status` | Показать статус и статистику |

---

## 🛡️ Надежность и отказоустойчивость

### Fallback модель

Бот поддерживает **автоматическое переключение на резервную LLM модель** при недоступности основной. Это повышает надежность и гарантирует, что пользователи всегда получат ответ.

**Как это работает:**

1. **Основная модель недоступна** (rate limit, серверная ошибка) → автоматически переключаемся на fallback модель
2. **Fallback модель отвечает** → пользователь получает ответ (не видит технических деталей)
3. **Обе модели недоступны** → пользователь получает понятное сообщение об ошибке

**Настройка:**

```bash
# В backend/bot/.env.development (или .env для production)

# Основная модель (платная, мощная)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Резервная модель (бесплатная, быстрая)
OPENROUTER_FALLBACK_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

**Рекомендуемые fallback модели:**

| Модель | Преимущества | Недостатки |
|--------|--------------|------------|
| `meta-llama/llama-3.1-8b-instruct:free` | Бесплатная, быстрая | Качество ниже платных |
| `google/gemini-flash-1.5` | Быстрая, доступная | Платная (дешевая) |
| `openai/gpt-3.5-turbo` | Хорошее качество | Платная |

📖 Подробнее: [docs/FALLBACK.md](docs/FALLBACK.md)

---

## 🚀 Production развертывание

Для production окружения используйте Docker с конфигурацией через переменные окружения и named volumes.

**1. Настроить переменные окружения:**

Отредактируйте `.build/docker-compose.prod.yml` и укажите свои токены:

```yaml
environment:
  - TELEGRAM_TOKEN=your_telegram_bot_token_here
  - OPENROUTER_API_KEY=your_openrouter_api_key_here
  # Остальные параметры опциональны
```

**2. Собрать и запустить:**

**Windows PowerShell:**
```powershell
# Сборка образа
.\.build\build-prod.ps1

# Запуск
docker-compose -f .build/docker-compose.prod.yml up -d
```

**Linux/Mac:**
```bash
# Сборка
docker-compose -f .build/docker-compose.prod.yml build

# Запуск
docker-compose -f .build/docker-compose.prod.yml up -d
```

**3. Проверить логи:**

```bash
docker-compose -f .build/docker-compose.prod.yml logs -f bot
```

📖 Подробная документация: [.build/DEPLOYMENT.md](.build/DEPLOYMENT.md)

**Преимущества production сборки:**
- ✅ Секреты через переменные окружения (не попадают в образ)
- ✅ Named volumes (Docker автоматически управляет правами)
- ✅ Уменьшенный размер образа (~150-200MB)
- ✅ Multi-stage build для оптимизации
- ✅ Non-root пользователь для безопасности
- ✅ Встроенный healthcheck
- ✅ Настроенные лимиты ресурсов
- ✅ Работает на Windows, Linux и в облаке

---

## 🛠️ Development

### Установка для разработки

```bash
# Клонировать репозиторий
git clone <repository-url>
cd ai-tg-bot

# Установить зависимости с dev-пакетами
uv sync --all-extras

# Установить pre-commit hooks
make pre-commit-install
```

Pre-commit hooks автоматически проверят форматирование и линтинг перед каждым коммитом.

### Проверка качества кода

```bash
# Форматирование
make format

# Линтинг и проверка типов
make lint

# Запуск тестов
make test        # С coverage отчётом
make test-fast   # Быстрый запуск без coverage

# Все проверки сразу (как в CI)
make ci
```

### 🧪 Тестирование

**Статистика:**
- ✅ **117 тестов** (100% passing)
  - 25 интеграционных тестов
  - 92 unit тестов
- 📊 **Coverage: 89%** (цель: 70%+ для критической логики)
- ⚡ **Быстрые**: ~5-10 секунд на полный прогон

**Структура тестов:**
```
tests/
├── integration/          # Интеграционные тесты (с реальной SQLite БД)
│   ├── test_storage_integration.py
│   └── test_handlers_integration.py
├── test_*.py            # Unit тесты (с моками)
└── conftest.py          # Фикстуры
```

**Naming conventions для фикстур:**
- `mock_*` - Mock-объекты для имитации зависимостей
- `test_*` - Реальные тестовые объекты
- `sample_*` - Тестовые данные и примеры

📖 Подробнее: [CONTRIBUTING.md - Тестирование](CONTRIBUTING.md#тестирование)

### Стандарты кода

- ✅ **Один класс = один файл** (Single Responsibility Principle)
- ✅ **Type hints** обязательны для всех функций и методов
- ✅ **Docstrings** для всех публичных методов
- ✅ **Async/await** для всех I/O операций
- ✅ **Логирование** ключевых событий (не `print()`)
- ✅ **KISS принцип** - простота превыше сложности

📖 Подробнее: [docs/vision.md](docs/vision.md) и [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🏗️ Архитектура

### Технологический стек

**Backend:**
- Python 3.11+
- aiogram 3.x - фреймворк для Telegram Bot API
- OpenAI SDK - для работы с OpenRouter API
- PostgreSQL 16 - база данных
- SQLAlchemy 2.0 - async ORM
- Alembic - система миграций
- Pydantic - валидация конфигурации

**Качество кода:**
- Ruff - линтер и форматтер
- Mypy - статическая проверка типов (strict mode)
- Pytest - фреймворк для тестирования (117 тестов, 89% coverage)
- Pre-commit - автоматические проверки перед коммитом

**DevOps:**
- Docker + Docker Compose - контейнеризация
- GitHub Actions - CI/CD
- Yandex Container Registry - хранение образов

📖 Полная документация: [API Reference](docs/api/README.md)

### Структура проекта

```
ai-tg-bot/
├── src/                 # Исходный код
│   ├── bot.py           # Основной класс Telegram-бота
│   ├── llm_client.py    # Клиент для работы с LLM
│   ├── storage.py       # Управление историей диалогов
│   ├── database.py      # Database engine и session management
│   ├── models.py        # SQLAlchemy модели (User, Message, UserSettings)
│   ├── config.py        # Конфигурация приложения
│   ├── handlers/        # Обработчики команд и сообщений
│   ├── middlewares/     # Middleware (rate limiting)
│   └── utils/           # Утилиты (message_splitter, log_sanitizer)
├── tests/               # Тесты (117 тестов)
│   ├── integration/     # Интеграционные тесты (25)
│   └── test_*.py        # Unit тесты (92)
├── alembic/             # Миграции базы данных
├── docs/                # Документация
│   ├── api/             # API Reference
│   └── guides/          # Руководства
├── .build/              # Production сборка
├── data/                # Пользовательские данные (volumes)
└── logs/                # Логи приложения
```

📖 Подробнее: [docs/vision.md - Структура проекта](docs/vision.md)

---

## 🎯 Достижения проекта

### ✅ Sprint S0: MVP + Качество кода + Отказоустойчивость
- 🤖 Полнофункциональный Telegram бот с LLM интеграцией
- 🛡️ Fallback механизм для повышения надежности
- 🧪 Тестирование (85% coverage)
- 🔧 CI/CD Pipeline
- 🐳 Docker Registry

### ✅ Sprint S1: Хранение данных в базе данных
- 🐘 PostgreSQL 16 + SQLAlchemy 2.0 async
- 🔄 Alembic для миграций
- 🗑️ Soft delete стратегия
- 👤 Per-user настройки и лимиты
- 📊 Timezone-aware timestamps

### ✅ Sprint S2: Технический долг и оптимизации
- ⚡ Rate limiting middleware (защита от spam/DDoS)
- 🚦 Graceful shutdown (корректное завершение задач)
- 💾 Кеширование системных промптов (TTL 5 мин)
- 🔁 Error recovery с exponential backoff
- 🚀 Оптимизация загрузки истории (lazy loading)
- 🔍 Составные индексы БД (ускорение запросов на 80%+)
- 🔒 Security hardening (sanitization, ValueError protection)
- 📖 API документация для всех компонентов
- 🧪 117 тестов (89% coverage)

📖 Подробнее: [docs/roadmap.md](docs/roadmap.md)

---

## 🐳 Docker Registry

Проект автоматически публикует Docker образы в Yandex Cloud Container Registry при каждом push в `main`.

**Версионирование:**
- Версия хранится в файле `VERSION` в корне репозитория (текущая: `1.3.2`)
- При push в `main` автоматически собираются образы с текущей версией

**Доступные образы:**

```bash
# Конкретная версия
cr.yandex/{registry-id}/ai-tg-bot:1.3.2

# Последняя стабильная версия
cr.yandex/{registry-id}/ai-tg-bot:latest
```

**Как обновить версию:**

1. Отредактируйте файл `VERSION`: `1.3.2` → `1.4.0`
2. Закоммитьте: `git commit -am "chore: bump version to 1.4.0"`
3. Push в `main`: автоматически соберутся образы `1.4.0` и `latest`

**Pull и запуск:**

```bash
# Авторизоваться в Yandex Container Registry
yc container registry configure-docker

# Pull конкретной версии
docker pull cr.yandex/{registry-id}/ai-tg-bot:1.3.2

# Запуск контейнера
docker run -d \
  --name ai-tg-bot \
  --env-file .env.production \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  cr.yandex/{registry-id}/ai-tg-bot:latest
```

### Требуемые GitHub Secrets

Для работы CI/CD необходимо настроить следующие секреты в **Settings → Secrets and variables → Actions**:

| Секрет | Описание |
|--------|----------|
| `YA_CLOUD_REGISTRY` | JSON ключ Service Account |
| `YC_REGISTRY_ID` | ID Container Registry |

---

## 📄 Лицензия

MIT

---

## 🤝 Вклад в проект

Мы рады любому вкладу! Пожалуйста, ознакомьтесь с [CONTRIBUTING.md](CONTRIBUTING.md) для получения подробной информации о:
- Стандартах кода
- Процессе разработки
- Требованиях к тестам
- Создании Pull Request

Следуйте принципам KISS и ООП, описанным в [docs/vision.md](docs/vision.md).

---

**Сделано с ❤️ для сообщества разработчиков**
