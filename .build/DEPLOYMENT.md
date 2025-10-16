# 🚀 Production Deployment Guide

## Конфигурация через переменные окружения

Production версия бота **не требует `.env` файлов**. Все настройки передаются через переменные окружения напрямую в `docker-compose.prod.yml`.

---

## 📋 Переменные окружения

### Обязательные

| Переменная | Описание | Где получить |
|------------|----------|--------------|
| `TELEGRAM_TOKEN` | Telegram Bot API token | [@BotFather](https://t.me/BotFather) |
| `OPENROUTER_API_KEY` | OpenRouter API key | [openrouter.ai](https://openrouter.ai/) |
| `DB_PASSWORD` | PostgreSQL database password | Установи при настройке БД |

### База данных

| Переменная | Дефолт | Описание |
|------------|--------|----------|
| `DB_HOST` | `postgres` | Хост PostgreSQL (имя контейнера или IP) |
| `DB_PORT` | `5432` | Порт PostgreSQL |
| `DB_NAME` | `ai_tg_bot` | Имя базы данных |
| `DB_USER` | `botuser` | Пользователь БД |
| `DB_ECHO` | `False` | SQLAlchemy echo (для отладки SQL) |

### Опциональные (с дефолтными значениями)

| Переменная | Дефолт | Описание |
|------------|--------|----------|
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter API URL |
| `OPENROUTER_MODEL` | `anthropic/claude-3.5-sonnet` | Основная LLM модель |
| `OPENROUTER_FALLBACK_MODEL` | `meta-llama/llama-3.1-8b-instruct:free` | Резервная LLM модель |
| `SYSTEM_PROMPT` | `Ты полезный ассистент...` | Системный промпт по умолчанию |
| `LLM_TEMPERATURE` | `0.7` | Температура LLM (0.0 - 2.0) |
| `LLM_MAX_TOKENS` | `1000` | Максимум токенов в ответе |
| `MAX_HISTORY_MESSAGES` | `50` | Максимум сообщений в истории |
| `RETRY_ATTEMPTS` | `3` | Количество повторных попыток |
| `RETRY_DELAY` | `1.0` | Задержка между попытками (сек) |
| `DATA_DIR` | `data` | Директория для данных |
| `LOGS_DIR` | `logs` | Директория для логов |
| `LOG_LEVEL` | `INFO` | Уровень логирования |

---

## 🗄️ Настройка PostgreSQL

### Вариант 1: PostgreSQL в отдельном Docker Compose (рекомендуется для production)

Если PostgreSQL уже запущен на виртуальной машине через отдельный docker-compose:

1. **Убедись что PostgreSQL запущен:**
   ```bash
   docker ps | grep postgres
   ```

2. **Проверь сетевое подключение:**
   - Если бот и PostgreSQL в одной Docker сети - используй имя контейнера в `DB_HOST`
   - Если в разных сетях - используй `host.docker.internal` или IP адрес

3. **Создай базу данных и пользователя:**
   ```bash
   docker exec -it postgres-container psql -U postgres
   ```
   ```sql
   CREATE DATABASE ai_tg_bot;
   CREATE USER botuser WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE ai_tg_bot TO botuser;
   \q
   ```

4. **Обнови `.build/docker-compose.prod.yml`:**
   ```yaml
   environment:
     - DB_HOST=postgres                    # Имя контейнера PostgreSQL
     - DB_PASSWORD=your_secure_password    # Пароль из шага 3
   ```

### Вариант 2: PostgreSQL вместе с ботом (для тестирования)

Можно добавить PostgreSQL в `.build/docker-compose.prod.yml`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: ai-tg-bot-postgres
    environment:
      POSTGRES_USER: botuser
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: ai_tg_bot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U botuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  bot:
    depends_on:
      postgres:
        condition: service_healthy
    # ... остальная конфигурация

volumes:
  postgres_data:
```

### Важно: Миграции БД

Бот **автоматически запускает миграции** при старте через `entrypoint.sh`. Это создаст все необходимые таблицы:
- `users` - информация о пользователях
- `messages` - история сообщений (с soft delete)
- `user_settings` - настройки пользователей

---

## 🐳 Локальный деплой (Windows)

### 1. Настройка конфигурации

Открой файл `.build/docker-compose.prod.yml` и укажи свои значения переменных окружения:

```yaml
environment:
  # Обязательно укажи:
  - TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz  # Твой токен
  - OPENROUTER_API_KEY=sk-or-v1-...                        # Твой ключ
  - DB_PASSWORD=your_secure_password                        # Пароль от PostgreSQL
  
  # Настройки БД (если PostgreSQL на другом хосте):
  - DB_HOST=postgres                                        # Имя контейнера или IP
  
  # Остальные параметры можно оставить или настроить по желанию
```

### 2. Сборка образа

**Windows PowerShell:**
```powershell
.\.build\build-prod.ps1
```

Или напрямую через Docker:
```bash
docker-compose -f .build/docker-compose.prod.yml build
```

### 3. Запуск

```bash
docker-compose -f .build/docker-compose.prod.yml up -d
```

### 4. Проверка логов

```bash
docker-compose -f .build/docker-compose.prod.yml logs -f bot
```

### 5. Остановка

```bash
docker-compose -f .build/docker-compose.prod.yml down
```

---

## ☁️ Деплой в Yandex Cloud

### Подготовка образа

1. **Собери образ локально:**
   ```powershell
   .\.build\build-prod.ps1 -Tag 1.0
   ```

2. **Залогинься в Yandex Container Registry:**
   ```bash
   docker login cr.yandex
   ```

3. **Тегируй образ:**
   ```bash
   docker tag ai-tg-bot:1.0 cr.yandex/YOUR_REGISTRY_ID/aibotmvp:1.0
   ```

4. **Отправь в registry:**
   ```bash
   docker push cr.yandex/YOUR_REGISTRY_ID/aibotmvp:1.0
   ```

### Деплой на VM

1. **Подключись к VM:**
   ```bash
   ssh your-vm
   ```

2. **Создай директорию проекта:**
   ```bash
   mkdir -p ai-tg-bot/.build
   cd ai-tg-bot/.build
   ```

3. **Скопируй docker-compose.prod.yml на VM:**
   ```bash
   # На локальной машине
   scp .build/docker-compose.prod.yml your-vm:~/ai-tg-bot/.build/
   ```

4. **На VM отредактируй конфигурацию:**
   ```bash
   nano docker-compose.prod.yml
   ```
   
   Укажи:
   - Свой `image: cr.yandex/YOUR_REGISTRY_ID/aibotmvp:1.0`
   - `TELEGRAM_TOKEN`
   - `OPENROUTER_API_KEY`

5. **Залогинься в registry на VM:**
   ```bash
   docker login cr.yandex
   ```

6. **Запусти:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

7. **Проверь статус:**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   docker-compose -f docker-compose.prod.yml logs -f bot
   ```

---

## 📊 Named Volumes

Production конфигурация использует **Docker Named Volumes** для хранения данных:

### Преимущества:
- ✅ **Нет проблем с правами доступа** (Windows, Linux, Cloud)
- ✅ Docker автоматически управляет volumes
- ✅ Более безопасно и изолировано
- ✅ Простой backup и restore

### Работа с volumes:

**Просмотр логов:**
```bash
docker-compose -f .build/docker-compose.prod.yml exec bot cat /app/logs/bot.log
```

**Список диалогов:**
```bash
docker-compose -f .build/docker-compose.prod.yml exec bot ls -la /app/data
```

**Скопировать файл на хост:**
```bash
docker cp ai-tg-bot-prod:/app/logs/bot.log ./bot.log
docker cp ai-tg-bot-prod:/app/data/123456789.json ./dialog.json
```

**Где хранятся volumes:**
```bash
docker volume ls
docker volume inspect ai-tg-bot_bot-data
docker volume inspect ai-tg-bot_bot-logs
```

**Backup volume:**
```bash
# Backup данных
docker run --rm -v ai-tg-bot_bot-data:/data -v $(pwd):/backup alpine tar czf /backup/bot-data-backup.tar.gz -C /data .

# Backup логов
docker run --rm -v ai-tg-bot_bot-logs:/data -v $(pwd):/backup alpine tar czf /backup/bot-logs-backup.tar.gz -C /data .
```

**Restore volume:**
```bash
# Восстановление данных
docker run --rm -v ai-tg-bot_bot-data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/bot-data-backup.tar.gz"
```

---

## 🔒 Безопасность

### ✅ Что делаем правильно:

- Секреты передаются через переменные окружения
- Секреты **НЕ попадают** в Docker образ
- Non-root пользователь в контейнере (через su-exec)
- Resource limits для production
- Read-only filesystem опции
- Healthcheck для мониторинга

### ⚠️ Важно:

- **НИКОГДА не коммить** файлы с реальными токенами
- **НЕ публикуй** образы Docker с секретами внутри
- Используй `.gitignore` для конфигов с токенами
- Регулярно ротируй API ключи

---

## 📊 Мониторинг

### Логи

Просмотр логов в реальном времени:

```bash
docker-compose -f .build/docker-compose.prod.yml logs -f bot
```

Логи также сохраняются в volume `bot-logs` с ротацией (5 файлов по 10MB).

### Healthcheck

Docker автоматически проверяет здоровье контейнера каждые 60 секунд.

Статус можно посмотреть:

```bash
docker ps
```

Колонка `STATUS` покажет состояние healthcheck.

### Resource Usage

Мониторинг использования ресурсов:

```bash
docker stats ai-tg-bot-prod
```

---

## 🎯 Checklist перед деплоем

- [ ] Указаны `TELEGRAM_TOKEN` и `OPENROUTER_API_KEY`
- [ ] Проверены настройки модели (`OPENROUTER_MODEL`)
- [ ] Настроен `SYSTEM_PROMPT` (если нужен custom)
- [ ] Проверен размер лимитов памяти и CPU
- [ ] Настроен мониторинг логов
- [ ] Протестирован локально перед продакшеном
- [ ] Настроены автоматические backups volumes

---

## 🛠️ Полезные команды

### Пересборка и перезапуск

```bash
docker-compose -f .build/docker-compose.prod.yml down
docker-compose -f .build/docker-compose.prod.yml build --no-cache
docker-compose -f .build/docker-compose.prod.yml up -d
```

### Обновление образа из registry

```bash
docker-compose -f .build/docker-compose.prod.yml pull
docker-compose -f .build/docker-compose.prod.yml up -d
```

### Очистка volumes (осторожно!)

```bash
# Остановить контейнер
docker-compose -f .build/docker-compose.prod.yml down

# Удалить volumes (ВСЕ ДАННЫЕ БУДУТ ПОТЕРЯНЫ!)
docker volume rm ai-tg-bot_bot-data ai-tg-bot_bot-logs

# Запустить заново (создаст новые volumes)
docker-compose -f .build/docker-compose.prod.yml up -d
```

---

**Готово!** Твой бот готов к production деплою. 🚀
