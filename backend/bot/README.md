# AI Telegram Bot

Telegram бот с интеграцией LLM через OpenRouter API.

## Структура

Этот каталог содержит весь код Telegram бота:

- `src/` - исходный код бота
- `tests/` - тесты (unit и integration)
- `alembic/` - миграции базы данных
- `pyproject.toml` - зависимости и конфигурация проекта
- `uv.lock` - lock-файл зависимостей
- `.env.example` - пример конфигурации
- `VERSION` - версия бота

## Конфигурация

### Для разработки

1. Скопируйте `.env.example`:
```bash
cp .env.example .env.development
```

2. Отредактируйте `.env.development` и укажите:
- `TELEGRAM_TOKEN` - токен бота (получить у @BotFather)
- `OPENROUTER_API_KEY` - API ключ OpenRouter
- `DB_PASSWORD` - пароль для PostgreSQL
- `DB_HOST=localhost` (для локального запуска вместо `postgres`)

### Для Docker

Конфигурация монтируется из этого файла в контейнер через volume в `../../docker-compose.yml`

## Документация

Полная документация проекта находится в корневой директории:

- `../../README.md` - основная документация
- `../../docs/` - подробная документация по архитектуре и API
- `../../CONTRIBUTING.md` - руководство по контрибуции

## Запуск

### Через Makefile (рекомендуется)

Используйте команды из корневой директории проекта:

```bash
# Из корня проекта (../../)
make run           # Запуск бота
make test          # Запуск тестов
make lint          # Проверка кода
make format        # Форматирование кода
```

### Через UV напрямую

```bash
# Из этой директории (backend/bot/)
uv run python -m src.main --env-file .env.development
```

### Через Docker

```bash
# Из корня проекта (../../)
docker-compose up -d
```

## Версия

Текущая версия: `1.4.2`

Версия автоматически используется при сборке Docker образов в CI/CD.

