# AI Telegram Bot

LLM-ассистент в виде Telegram-бота с использованием OpenRouter API.

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

**1. Клонировать репозиторий:**
```bash
git clone <repository-url>
cd ai-tg-bot
```

**2. Создать файл конфигурации:**
```bash
cp .env.example .env.development
```

**3. Заполнить `.env.development`:**
```bash
# Обязательные параметры
TELEGRAM_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key

# Остальные параметры можно оставить по умолчанию
```

**4. Собрать и запустить:**
```bash
# Собрать Docker образ
docker-compose build

# Запустить бота в фоновом режиме
docker-compose up -d

# Посмотреть логи
docker-compose logs -f bot
```

**5. Остановка:**
```bash
docker-compose down
```

📖 Подробная документация: [DOCKER.md](DOCKER.md)

---

### 💻 Локальный запуск (альтернатива)

**1. Клонировать репозиторий:**
```bash
git clone <repository-url>
cd ai-tg-bot
```

**2. Установить зависимости:**
```bash
uv sync
```

**3. Создать файл конфигурации:**
```bash
cp .env.example .env.development
```

**4. Заполнить `.env.development`:**
```bash
# Обязательные параметры
TELEGRAM_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key

# Остальные параметры можно оставить по умолчанию
```

**5. Запустить бота:**

**Через UV (рекомендуется):**
```bash
uv run python -m src.main --env-file .env.development
```

**Через виртуальное окружение:**
```bash
# Активировать окружение
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Запустить бота
python -m src.main --env-file .env.development
```

---

### 🚀 Production развертывание

Для production окружения используйте Docker с конфигурацией через переменные окружения и named volumes:

**1. Настроить переменные окружения:**

Отредактируй `.build/docker-compose.prod.yml` и укажи свои токены:

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
- ✅ Работает на Windows, Linux и в облаке без проблем

---

## 📋 Команды бота

- `/start` - начать работу с ботом
- `/help` - показать справку по командам
- `/role <текст>` - установить роль ассистента (системный промпт)
- `/role default` - вернуться к роли по умолчанию
- `/reset` - очистить историю диалога
- `/status` - показать статус и статистику

## 🏗️ Структура проекта

```
ai-tg-bot/
├── src/              # Исходный код
├── data/             # JSON файлы с историей диалогов
├── logs/             # Логи приложения
├── tests/            # Тесты
├── docs/             # Документация
├── .env              # Конфигурация (не в git)
├── .env.example      # Шаблон конфигурации
└── pyproject.toml    # Зависимости и настройки проекта
```

## 📂 Ключевые файлы

### Исходный код
- [`src/main.py`](src/main.py) - точка входа в приложение
- [`src/bot.py`](src/bot.py) - основной класс Telegram-бота
- [`src/llm_client.py`](src/llm_client.py) - клиент для работы с LLM через OpenRouter
- [`src/storage.py`](src/storage.py) - управление историей диалогов
- [`src/config.py`](src/config.py) - конфигурация приложения

### Конфигурация
- [`.env.example`](.env.example) - шаблон конфигурации
- [`pyproject.toml`](pyproject.toml) - зависимости и настройки проекта
- [`uv.lock`](uv.lock) - зафиксированные версии зависимостей

### Docker
- [`Dockerfile.dev`](Dockerfile.dev) - Docker образ для разработки
- [`docker-compose.yml`](docker-compose.yml) - оркестрация контейнеров (development)
- [`.build/`](.build/) - production сборка и развертывание
  - [`.build/Dockerfile`](.build/Dockerfile) - production-ready multi-stage образ
  - [`.build/docker-compose.prod.yml`](.build/docker-compose.prod.yml) - production конфигурация с named volumes
  - [`.build/build-prod.ps1`](.build/build-prod.ps1) - скрипт сборки для Windows PowerShell
  - [`.build/entrypoint.sh`](.build/entrypoint.sh) - entrypoint скрипт для инициализации контейнера
  - [`.build/DEPLOYMENT.md`](.build/DEPLOYMENT.md) - руководство по production деплою
- [`.dockerignore`](.dockerignore) - исключения для Docker
- [`Makefile`](Makefile) - автоматизация команд
- [`DOCKER.md`](DOCKER.md) - руководство по использованию Docker

### Документация
- [`docs/vision.md`](docs/vision.md) - техническое видение и архитектура
- [`docs/tasklist.md`](docs/tasklist.md) - план разработки и прогресс
- [`docs/idea.md`](docs/idea.md) - концепция и идея проекта

### Правила разработки (Cursor IDE)
- [`.cursor/rules/conventions.mdc`](.cursor/rules/conventions.mdc) - стиль кода и соглашения
- [`.cursor/rules/workflow.mdc`](.cursor/rules/workflow.mdc) - процесс разработки

## 🛠️ Технологии

- **Python 3.11+** - основной язык
- **aiogram 3.x** - фреймворк для Telegram Bot API
- **OpenAI SDK** - для работы с OpenRouter API
- **Pydantic** - валидация конфигурации
- **uv** - управление зависимостями
- **Docker** - контейнеризация приложения

## 📚 Документация

Подробная документация доступна в директории [`docs/`](docs/):
- [Техническое видение](docs/vision.md) - полное описание архитектуры
- [План разработки](docs/tasklist.md) - дорожная карта проекта
- [Идея проекта](docs/idea.md) - концепция и цели
- [Docker руководство](DOCKER.md) - использование Docker для разработки
- [Production деплой](.build/DEPLOYMENT.md) - развертывание в production

## 📄 Лицензия

MIT

## 🤝 Вклад в проект

Следуйте принципам KISS и ООП, описанным в [docs/vision.md](docs/vision.md).

