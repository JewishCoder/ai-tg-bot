# Docker Guide

## Быстрый старт

### Использование через docker-compose (рекомендуется)

```bash
# Сборка образа
docker-compose build

# Запуск бота в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка бота
docker-compose down
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

### Dockerfile.dev
- Базовый образ: Python 3.11 Alpine Linux
- Размер образа: ~471MB
- UV package manager для управления зависимостями
- Автоматическая установка всех зависимостей

### docker-compose.yml
**Volume Mapping:**
- `./data:/app/data` - история диалогов (персистентна)
- `./logs:/app/logs` - логи бота
- `./.env.development:/app/.env.development:ro` - конфигурация (read-only)

**Restart Policy:**
- `unless-stopped` - автоматический перезапуск при сбоях

**Logging:**
- Max size: 10MB per file
- Max files: 3
- Driver: json-file

### .dockerignore
Исключает из образа:
- Python cache файлы
- Виртуальные окружения
- Git файлы
- Документацию и тесты
- Данные и логи (они монтируются через volumes)

## Требования

- Docker Engine 20.10+
- Docker Compose v2.0+
- Файл `.env.development` с настройками

## Проверка работы

После запуска проверьте логи:
```bash
docker-compose logs -f bot
```

Вы должны увидеть:
```
INFO | Bot initialized
INFO | Starting bot polling...
INFO | AI Telegram Bot started successfully
```

## Остановка перед запуском в Docker

⚠️ **Важно:** Telegram API не позволяет работать двум инстансам бота одновременно.

Если бот уже запущен локально, остановите его перед запуском в Docker:
- Ctrl+C в терминале, где запущен локальный бот
- Или завершите процесс вручную

## Обновление после изменений в коде

```bash
# Пересобрать образ
docker-compose build

# Перезапустить контейнер
docker-compose down
docker-compose up -d
```

## Отладка

### Просмотр логов контейнера
```bash
docker-compose logs bot
```

### Интерактивная работа с контейнером
```bash
docker-compose exec bot /bin/sh
```

### Проверка статуса контейнера
```bash
docker-compose ps
```

### Просмотр использования ресурсов
```bash
docker stats ai-tg-bot
```

## Production деплой

Для production окружения:
1. Создайте `docker-compose.prod.yml`
2. Используйте `.env.production` вместо `.env.development`
3. Настройте resource limits в docker-compose
4. Настройте мониторинг и алерты
5. Используйте Docker Swarm или Kubernetes для оркестрации

## Troubleshooting

**Проблема:** "Conflict: terminated by other getUpdates request"
- **Решение:** Остановите другие инстансы бота

**Проблема:** "Cannot connect to the Docker daemon"
- **Решение:** Убедитесь что Docker Desktop запущен

**Проблема:** Контейнер постоянно перезапускается
- **Решение:** Проверьте логи: `docker-compose logs bot`
- Проверьте наличие и корректность `.env.development`

