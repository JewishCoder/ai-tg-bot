# AI TG Bot Stats API

REST API для получения статистики диалогов Telegram-бота.

## Статус

✅ **Блоки 1-2 завершены** - Mock API готов к использованию

## Версия

**Текущая версия**: `0.1.0` (см. [VERSION](./VERSION))

### Схема версионирования (SemVer)

Проект использует [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR.MINOR.PATCH** (например: `0.1.0`)
- **MAJOR**: Breaking changes (несовместимые изменения API)
- **MINOR**: Новые функции (обратно совместимые)
- **PATCH**: Bug fixes (обратно совместимые исправления)

## Возможности

- 📊 **Статистика диалогов** - получение агрегированной статистики
- 🔄 **Mock данные** - генерация реалистичных тестовых данных
- 📝 **OpenAPI документация** - автоматическая генерация API docs
- 🐳 **Docker support** - упрощенное развертывание

## Быстрый старт

### Docker (рекомендуется)

```bash
# Из корня проекта
docker-compose up api

# API доступен на http://localhost:8000
```

### Локальный запуск (без Docker)

```bash
# Перейти в директорию API
cd backend/api

# Установить зависимости
& "$env:USERPROFILE\.local\bin\uv.exe" sync

# Запустить сервер
& "$env:USERPROFILE\.local\bin\uv.exe" run python run_api.py
```

## API Endpoints

### GET /health
Health check endpoint

```bash
curl http://localhost:8000/health
```

### GET /api/v1/stats?period={day|week|month}
Получить статистику диалогов за указанный период

```bash
# День
curl http://localhost:8000/api/v1/stats?period=day

# Неделя
curl http://localhost:8000/api/v1/stats?period=week

# Месяц
curl http://localhost:8000/api/v1/stats?period=month
```

## Документация

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Конфигурация

Создайте `.env` файл на основе `.env.example`:

```bash
cp .env.example .env
```

Доступные параметры:
- `API_HOST` - хост сервера (по умолчанию: 0.0.0.0)
- `API_PORT` - порт сервера (по умолчанию: 8000)
- `STAT_COLLECTOR_TYPE` - тип коллектора: mock или real (по умолчанию: mock)
- `LOG_LEVEL` - уровень логирования: DEBUG, INFO, WARNING, ERROR (по умолчанию: INFO)

## Разработка

### Установка dev зависимостей

```bash
# Через глобальный Makefile (рекомендуется)
make api-install

# Или напрямую через UV
cd backend/api
& "$env:USERPROFILE\.local\bin\uv.exe" sync --all-extras
```

### Запуск тестов

```bash
# Все тесты с coverage
make api-test-cov

# Только unit тесты (быстро)
make api-test
```

### Проверка качества кода

```bash
# Проверка линтером + типами (MyPy)
make api-lint

# Автоматическое форматирование
make api-format
```

### Запуск API сервера

```bash
# Development режим (с hot reload)
make api-dev

# Production режим
make api-run
```

### Доступные Makefile команды

Из корня проекта:

```bash
make help  # Показать все доступные команды
```

| Команда | Описание |
|---------|----------|
| `make api-install` | Установить все зависимости |
| `make api-format` | Отформатировать код (Ruff) |
| `make api-lint` | Проверить код (Ruff + MyPy) |
| `make api-test` | Запустить тесты |
| `make api-test-cov` | Запустить тесты с coverage |
| `make api-dev` | Запустить сервер (dev с hot-reload) |
| `make api-run` | Запустить сервер (production) |

## Структура проекта

```
backend/api/
├── src/
│   ├── __init__.py
│   ├── app.py              # FastAPI приложение
│   ├── config.py           # Конфигурация
│   ├── routers/
│   │   ├── __init__.py
│   │   └── stats.py        # Stats router
│   └── stats/
│       ├── __init__.py
│       ├── collector.py    # Абстрактный StatCollector
│       ├── models.py       # Pydantic модели
│       └── mock_collector.py  # Mock реализация
├── tests/
│   ├── __init__.py
│   └── test_mock_collector.py  # Тесты
├── run_api.py              # Entrypoint
├── Dockerfile              # Docker образ
├── pyproject.toml          # Конфигурация проекта
└── README.md
```

## Связанные документы

- [API Contract](../../docs/backend/api/stats-api-contract.md) - спецификация REST API
- [Dashboard Requirements](../../docs/frontend/dashboard-requirements.md) - требования к UI
- [Roadmap](../../docs/roadmap.md) - план развития проекта
- [Tasklist S3](../../docs/tasklists/tasklist-S3.md) - детальный план спринта

## Следующие шаги

- [ ] Блок 3: FastAPI приложение и Stats Router ✅
- [ ] Блок 4: Entrypoint и автоматизация (Makefile команды)
- [ ] Блок 5: Документация (OpenAPI улучшения, архитектура)

