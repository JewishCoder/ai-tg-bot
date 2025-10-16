# Changelog

Все значимые изменения в проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added
- ⚡ **Спринт S2: Технический долг и оптимизации** (117 тестов, 89% coverage)
  - Rate limiting middleware для защиты от spam/DDoS (настраиваемые лимиты)
  - Graceful shutdown с корректным завершением активных задач
  - Кеширование системных промптов (TTLCache, 5 мин, 1000 entries)
  - Error recovery с exponential backoff для `save_history()`
  - Оптимизация загрузки истории (`load_recent_history(limit=20)`)
  - Составные индексы БД (`ix_messages_user_deleted_created`) для ускорения запросов
  - Security hardening: sanitization логов, защита от ValueError при парсинге timestamp
  - `log_message_content=False` по умолчанию для production безопасности
  - API документация для всех компонентов (6 MD файлов с Mermaid диаграммами)
  - 7 интеграционных тестов Storage с SQLite in-memory
  - 18 интеграционных тестов handlers
  - 13 новых edge case тестов (unicode, emoji, 15k chars, concurrency)
  - Naming conventions для фикстур (`mock_*`, `test_*`, `sample_*`)
- 🗄️ **Спринт S1: Миграция на PostgreSQL** (взамен JSON файлов)
  - PostgreSQL 16 для хранения истории диалогов и настроек пользователей
  - SQLAlchemy 2.0 async ORM для работы с БД
  - Alembic для управления миграциями схемы БД
  - Три таблицы: `users`, `messages`, `user_settings`
  - Soft delete стратегия - данные не удаляются физически, помечаются `deleted_at`
  - Timezone-aware timestamps (`TIMESTAMP WITH TIME ZONE`) для корректной работы с датами
  - Управляемые лимиты истории - каждый пользователь имеет свой лимит в `user_settings.max_history_messages`
  - Метрики сообщений: `content_length` (длина в символах), `created_at`
  - Docker Compose с PostgreSQL контейнером и healthcheck
  - Makefile команды для миграций: `db-migrate`, `db-rollback`, `db-revision`, `db-current`
- 🛡️ **Fallback механизм для повышения надежности**
  - Автоматическое переключение на резервную LLM модель при недоступности основной
  - Поддержка `OPENROUTER_FALLBACK_MODEL` в конфигурации
  - Умное определение когда нужен fallback (Rate Limit, API Errors)
  - Retry механизм для fallback модели (3 попытки)
  - Логирование всех fallback операций с уровнем WARNING
  - Полная прозрачность для пользователя (не видят технических деталей)
- 📖 Документация fallback механизма (`docs/FALLBACK.md`)
- 🧪 Интеграционные тесты для fallback флоу (5 новых тестов)
- 📊 Coverage увеличен до 85% (с 80%)

### Changed
- 🗄️ **`Storage` полностью переписан для работы с PostgreSQL вместо JSON**
  - Dependency injection: `Database` и `Config` передаются в конструктор
  - Все методы используют async SQLAlchemy queries
  - Soft delete для `clear_history()` - устанавливается `deleted_at`
  - Лимиты берутся из `user_settings` таблицы (per-user настройки)
- 🤖 **`Bot` обновлен для работы с Database**
  - Инициализация `Database` перед `Storage`
  - Graceful shutdown с `await database.close()`
- 📝 Обновлена вся документация:
  - `README.md` - раздел про PostgreSQL, миграции, переменные окружения
  - `docs/vision.md` - архитектура с БД, структура проекта, технологии
  - `docs/idea.md` - упоминание PostgreSQL + SQLAlchemy
  - `docs/roadmap.md` - статус Спринта S1 "✅ Завершено"
- 🐳 **`docker-compose.yml` обновлен**
  - Добавлен сервис `postgres` с persistent volume
  - Healthcheck для PostgreSQL перед запуском бота
  - Переменные окружения через `.env` и `.env.development`
- ⚡ `LLMClient` теперь поддерживает fallback модель
- 🎯 `Config` расширен параметрами БД (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_ECHO)

### Technical Details

**PostgreSQL Integration:**
- Новые файлы:
  - `src/database.py` - Database engine и session management
  - `src/models.py` - SQLAlchemy модели (User, Message, UserSettings)
  - `alembic/` - директория миграций
  - `alembic.ini` - конфигурация Alembic
- Схема БД:
  - `users`: id (PK, Telegram user_id), created_at, updated_at
  - `messages`: id (UUID, PK), user_id (FK), role, content, content_length, created_at, deleted_at
  - `user_settings`: id (PK), user_id (FK, UNIQUE), max_history_messages, system_prompt, created_at, updated_at
- Миграции через Alembic:
  - `001_initial_schema` - создание таблиц
  - `002_add_timezone_to_datetime_fields` - исправление timezone для datetime полей
- Database session management через context manager с автоматическим commit/rollback

**LLMClient Fallback:**
- Новые методы в `LLMClient`:
  - `_should_try_fallback(error)` - определяет нужен ли fallback
  - `_try_fallback_model(messages, user_id, error)` - выполняет fallback запрос
- Интеграция fallback в `generate_response()` для RateLimitError и APIError
- Fallback НЕ срабатывает для Timeout и Connection ошибок (проблема сети)
- Полная обратная совместимость - fallback опционален

### Removed
- ❌ **JSON файлы для хранения истории диалогов**
  - Полностью заменены на PostgreSQL
  - Старые JSON файлы в `data/` больше не используются
  - Методы работы с JSON удалены из `Storage`

### Fixed
- 🐛 **Timezone issues с datetime полями**
  - Исправлена ошибка `TypeError: can't subtract offset-naive and offset-aware datetimes`
  - Все datetime поля теперь используют `TIMESTAMP WITH TIME ZONE`
  - Python использует `datetime.now(UTC)` для timezone-aware объектов
  - Миграция `002_add_timezone_to_datetime_fields` для обновления существующих БД

### Tests
- ✅ **PostgreSQL тесты:**
  - `tests/test_storage.py` полностью переписан для работы с БД через моки
  - `tests/integration/test_storage_integration.py` - 7 тестов с реальной БД (SQLite in-memory)
  - `tests/integration/test_handlers_integration.py` - 18 тестов handlers
  - Тестовые фикстуры: `mock_database` (unit-тесты), `integration_db` (интеграционные)
  - Проверка soft delete, управляемых лимитов, content_length
- ✅ **Fallback тесты:**
  - 4 новых unit-теста для Config (fallback model)
  - 7 новых unit-тестов для LLMClient (fallback логика)
  - 5 новых интеграционных тестов (end-to-end fallback флоу)
- ✅ **Sprint S2 тесты:**
  - 9 тестов sanitization (content, tokens, unicode)
  - 13 edge case тестов (unicode, emoji, long content, concurrency)
  - 2 теста ValueError handling для timestamps
- ✅ **Итого: 117 тестов (coverage 89%)**

## [0.1.0] - 2025-10-11

### Added
- 🤖 Базовая функциональность Telegram бота
- 🧠 Интеграция с OpenRouter API для LLM
- 💾 Управление историей диалогов (Storage)
- 🎭 Система ролей через системный промпт
- 🔄 Retry механизм для временных сбоев
- 📝 Логирование всех операций
- 🐳 Docker support с development и production сборками
- 🧪 Unit и интеграционные тесты (coverage 80%)
- 📚 Документация (README, CONTRIBUTING, docs/)
- 🔧 CI/CD через GitHub Actions
- 🚀 Автоматическая публикация в Yandex Container Registry

### Commands
- `/start` - начать работу с ботом
- `/help` - справка по командам
- `/role <текст>` - установить роль ассистента
- `/role default` - вернуться к роли по умолчанию
- `/reset` - очистить историю диалога
- `/status` - показать статус и статистику

### Tech Stack
- Python 3.11+
- aiogram 3.x - Telegram Bot API
- OpenAI SDK - для работы с OpenRouter
- PostgreSQL 16 - база данных
- SQLAlchemy 2.0 - async ORM
- Alembic - миграции БД
- Pydantic - валидация конфигурации
- uv - управление зависимостями
- Docker + Docker Compose - контейнеризация
- Pytest - тестирование
- Ruff - линтер и форматтер
- Mypy - проверка типов

---

## Типы изменений

- `Added` - новые функции
- `Changed` - изменения в существующем функционале
- `Deprecated` - функции, которые скоро будут удалены
- `Removed` - удаленные функции
- `Fixed` - исправления багов
- `Security` - изменения безопасности

---

[Unreleased]: https://github.com/jewishcoder/ai-tg-bot/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jewishcoder/ai-tg-bot/releases/tag/v0.1.0

