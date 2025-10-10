# AI Telegram Bot

LLM-ассистент в виде Telegram-бота с использованием OpenRouter API.

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - менеджер зависимостей
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))
- OpenRouter API Key (получить на [openrouter.ai](https://openrouter.ai))

### Установка

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd ai-tg-bot
```

2. Установить зависимости:
```bash
uv sync
```

3. Создать файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Заполнить `.env` файл:
```bash
# Обязательные параметры
TELEGRAM_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key

# Остальные параметры можно оставить по умолчанию
```

### Запуск

```bash
# Активировать виртуальное окружение
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Запустить бота
python -m src.main
```

Или с указанием пути к .env файлу:
```bash
python -m src.main --env-file /path/to/custom.env
```

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
- [`docker-compose.yml`](docker-compose.yml) - оркестрация контейнеров
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
- [Docker руководство](DOCKER.md) - использование Docker

## 📄 Лицензия

MIT

## 🤝 Вклад в проект

Следуйте принципам KISS и ООП, описанным в [docs/vision.md](docs/vision.md).

