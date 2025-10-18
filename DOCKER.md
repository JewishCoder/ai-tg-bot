# Docker Guide

**Статус проекта**: Multi-service архитектура (Bot + API + Frontend + PostgreSQL)

## 🎯 Обзор

Проект использует Docker Compose для оркестрации всех сервисов:
- **Bot** - Telegram бот (Python 3.11 + aiogram)
- **API** - Stats API (Python 3.11 + FastAPI)
- **Frontend** - Dashboard (Node.js + Next.js)
- **PostgreSQL** - База данных для всех сервисов

## Быстрый старт

### Запуск всех сервисов

```bash
# Сборка всех образов
docker-compose build

# Запуск всех сервисов в фоновом режиме
docker-compose up -d

# Просмотр логов всех сервисов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f bot
docker-compose logs -f api
docker-compose logs -f frontend

# Остановка всех сервисов
docker-compose down
```

### Запуск отдельных сервисов

```bash
# Только бот + PostgreSQL
docker-compose up bot -d

# Только API + PostgreSQL
docker-compose up api -d

# Только Frontend
docker-compose up frontend -d
```

### Использование через Makefile (требует установки make)

```bash
# Локальная разработка
make install        # Установка зависимостей
make run            # Запуск бота локально

# Docker команды
make docker-build   # Сборка образа
make docker-up      # Запуск в Docker
make docker-logs    # Просмотр логов
make docker-down    # Остановка

# Обслуживание
make clean          # Очистка временных файлов
```

## Структура Docker окружения

### Образы

#### Bot (backend/bot/Dockerfile.dev)
- **Базовый образ**: Python 3.11 Alpine Linux
- **Размер**: ~200MB
- **Package manager**: UV для управления зависимостями
- **Конфигурация**: `backend/bot/.env.development`

#### API (backend/api/Dockerfile)
- **Базовый образ**: Python 3.11 Alpine Linux
- **Размер**: ~180MB
- **Package manager**: UV для управления зависимостями
- **Конфигурация**: переменные окружения в docker-compose.yml

#### Frontend (frontend/Dockerfile)
- **Базовый образ**: Node.js 18 Alpine
- **Размер**: ~300MB
- **Package manager**: npm
- **Build**: Multi-stage для оптимизации

#### PostgreSQL
- **Образ**: postgres:16-alpine
- **Размер**: ~238MB
- **Persistent storage**: named volume `postgres_data`

### docker-compose.yml

**Сервисы:**
- `postgres` - База данных (порт 5432)
- `bot` - Telegram бот (зависит от postgres)
- `api` - Stats API (порт 8000, зависит от postgres)
- `frontend` - Dashboard (порт 3000, зависит от api)

**Volume Mapping:**

Bot:
- `./backend/bot/logs:/app/logs` - логи бота
- `./backend/bot/.env.development:/app/.env.development:ro` - конфигурация (read-only)

API:
- Конфигурация через environment variables

Frontend:
- Конфигурация через environment variables

PostgreSQL:
- `postgres_data:/var/lib/postgresql/data` - persistent storage

**Restart Policy:**
- `unless-stopped` - автоматический перезапуск при сбоях для всех сервисов

**Logging:**
- Max size: 10MB per file
- Max files: 3
- Driver: json-file

### .dockerignore
Исключает из образов:
- Python/Node cache файлы (`__pycache__`, `node_modules`)
- Виртуальные окружения (`.venv`)
- Git файлы (`.git`, `.gitignore`)
- Документацию и тесты (`docs/`, `tests/`)
- Build артефакты (`.next/`, `dist/`)
- Данные и логи (монтируются через volumes)

## Требования

- Docker Engine 20.10+
- Docker Compose v2.0+
- Конфигурационные файлы:
  - `backend/bot/.env.development` - для бота
  - Environment variables в docker-compose.yml - для API и Frontend

## Проверка работы

### Проверка всех сервисов

```bash
# Проверить статус всех сервисов
docker-compose ps

# Должно показать:
# bot        running    0.0.0.0:xxxx
# api        running    0.0.0.0:8000->8000/tcp
# frontend   running    0.0.0.0:3000->3000/tcp
# postgres   running    5432/tcp
```

### Bot

```bash
docker-compose logs bot

# Вы должны увидеть:
# INFO | Bot initialized
# INFO | Starting bot polling...
# INFO | AI Telegram Bot started successfully
```

### API

```bash
# Проверить логи
docker-compose logs api

# Или проверить через curl
curl http://localhost:8000/health
# Ответ: {"status":"ok"}

# Swagger UI доступен на:
# http://localhost:8000/docs
```

### Frontend

```bash
# Проверить логи
docker-compose logs frontend

# Dashboard доступен на:
# http://localhost:3000
```

### PostgreSQL

```bash
# Проверить логи
docker-compose logs postgres

# Подключиться к БД
docker-compose exec postgres psql -U botuser -d ai_tg_bot
```

## Остановка перед запуском в Docker

⚠️ **Важно:** Telegram API не позволяет работать двум инстансам бота одновременно.

Если бот уже запущен локально, остановите его перед запуском в Docker:
- Ctrl+C в терминале, где запущен локальный бот
- Или завершите процесс вручную

## Обновление после изменений в коде

### Пересборка конкретного сервиса

```bash
# Только бот
docker-compose build bot
docker-compose up -d bot

# Только API
docker-compose build api
docker-compose up -d api

# Только Frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Пересборка всех сервисов

```bash
# Пересобрать все образы
docker-compose build

# Перезапустить все контейнеры
docker-compose down
docker-compose up -d
```

### Быстрый перезапуск без пересборки

```bash
# Перезапуск конкретного сервиса
docker-compose restart bot
docker-compose restart api
docker-compose restart frontend

# Перезапуск всех сервисов
docker-compose restart
```

## Отладка

### Просмотр логов

```bash
# Все сервисы
docker-compose logs

# Конкретный сервис
docker-compose logs bot
docker-compose logs api
docker-compose logs frontend
docker-compose logs postgres

# Follow режим (live)
docker-compose logs -f bot

# Последние N строк
docker-compose logs --tail=100 bot
```

### Интерактивная работа с контейнерами

```bash
# Bot/API (Python + Alpine)
docker-compose exec bot /bin/sh
docker-compose exec api /bin/sh

# Frontend (Node.js + Alpine)
docker-compose exec frontend /bin/sh

# PostgreSQL
docker-compose exec postgres psql -U botuser -d ai_tg_bot
```

### Проверка статуса

```bash
# Все контейнеры
docker-compose ps

# Использование ресурсов
docker stats

# Детальная информация о контейнере
docker inspect ai-tg-bot-bot-1
docker inspect ai-tg-bot-api-1
docker inspect ai-tg-bot-frontend-1
```

### Проверка сети

```bash
# Список сетей Docker
docker network ls

# Детали сети проекта
docker network inspect ai-tg-bot_default

# Проверка подключения между сервисами
docker-compose exec bot ping api
docker-compose exec api ping postgres
```

## Production деплой

Для production окружения:
1. Создайте `docker-compose.prod.yml`
2. Используйте переменные окружения или секреты вместо `.env.development`
3. Настройте resource limits в docker-compose
4. Настройте мониторинг и алерты
5. Используйте Docker Swarm или Kubernetes для оркестрации

## Troubleshooting

### Bot

**Проблема:** "Conflict: terminated by other getUpdates request"
- **Причина:** Два инстанса бота работают одновременно
- **Решение:** Остановите другие инстансы бота (локальные или другие контейнеры)

**Проблема:** Bot контейнер не стартует
- **Решение:** 
  - Проверьте логи: `docker-compose logs bot`
  - Убедитесь что `backend/bot/.env.development` существует и корректен
  - Проверьте что PostgreSQL запустился: `docker-compose logs postgres`

### API

**Проблема:** API недоступен на порту 8000
- **Решение:**
  - Проверьте логи: `docker-compose logs api`
  - Убедитесь что порт не занят: `netstat -an | grep 8000`
  - Проверьте health: `curl http://localhost:8000/health`

**Проблема:** API не может подключиться к PostgreSQL
- **Решение:**
  - Проверьте что PostgreSQL запущен: `docker-compose ps postgres`
  - Проверьте сетевое подключение: `docker-compose exec api ping postgres`

### Frontend

**Проблема:** Frontend не доступен на порту 3000
- **Решение:**
  - Проверьте логи: `docker-compose logs frontend`
  - Убедитесь что порт не занят: `netstat -an | grep 3000`
  - Проверьте переменную `NEXT_PUBLIC_API_URL` в docker-compose.yml

**Проблема:** Frontend не может получить данные от API
- **Решение:**
  - Убедитесь что API запущен: `curl http://localhost:8000/health`
  - Проверьте CORS настройки в API
  - Проверьте browser console для ошибок

### PostgreSQL

**Проблема:** PostgreSQL не стартует
- **Решение:**
  - Проверьте логи: `docker-compose logs postgres`
  - Убедитесь что порт 5432 не занят другим postgres
  - Проверьте права доступа к volume: `docker volume ls`

**Проблема:** "Connection refused" при подключении к БД
- **Решение:**
  - Дождитесь полной инициализации БД (может занять 10-20 секунд)
  - Проверьте credentials в `.env.development`

### Общие проблемы

**Проблема:** "Cannot connect to the Docker daemon"
- **Решение:** Убедитесь что Docker Desktop запущен

**Проблема:** Контейнер постоянно перезапускается
- **Решение:** 
  - Проверьте логи: `docker-compose logs <service>`
  - Проверьте конфигурацию
  - Проверьте зависимости между сервисами

**Проблема:** Медленная сборка образов
- **Решение:**
  - Используйте BuildKit: `DOCKER_BUILDKIT=1 docker-compose build`
  - Очистите старые образы: `docker system prune -a`

**Проблема:** Нет места на диске
- **Решение:**
  - Удалите неиспользуемые образы: `docker image prune -a`
  - Удалите неиспользуемые volumes: `docker volume prune`
  - Полная очистка: `docker system prune -a --volumes`

