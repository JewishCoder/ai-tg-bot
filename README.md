# AI Telegram Bot

[![CI](https://github.com/jewishcoder/ai-tg-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/jewishcoder/ai-tg-bot/actions/workflows/ci.yml)

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

**1. Клонировать репозиторий и настроить конфигурацию:**
```bash
git clone <repository-url>
cd ai-tg-bot
cp .env.example .env.development
# Отредактируйте .env.development - укажите TELEGRAM_TOKEN и OPENROUTER_API_KEY
```

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
cp .env.example .env.development
# Отредактируйте .env.development - укажите TELEGRAM_TOKEN и OPENROUTER_API_KEY
```

**2. Установить зависимости:**
```bash
uv sync
```

**3. Запустить бота:**

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

## 🛠️ Development

### Установка для разработки

Следуйте инструкциям из раздела [💻 Локальный запуск](#-локальный-запуск-альтернатива), затем установите дополнительные инструменты:

```bash
# Установить зависимости с dev-пакетами
uv sync --all-extras

# Установить pre-commit hooks
make pre-commit-install
```

Pre-commit hooks автоматически проверят форматирование и линтинг перед каждым коммитом.

### Проверка качества кода

**Форматирование:**
```bash
make format
```

**Линтинг и проверка типов:**
```bash
make lint
```

**Запуск тестов:**
```bash
make test        # С coverage отчётом
make test-fast   # Быстрый запуск без coverage
```

**Все проверки сразу (как в CI):**
```bash
make ci
```

### Стандарты кода

- ✅ **Один класс = один файл** (Single Responsibility Principle)
- ✅ **Type hints** обязательны для всех функций и методов
- ✅ **Docstrings** для всех публичных методов
- ✅ **Async/await** для всех I/O операций
- ✅ **Логирование** ключевых событий (не `print()`)
- ✅ **Покрытие тестами** не менее 70% для критической логики

Подробнее: [docs/vision.md](docs/vision.md) и [CONTRIBUTING.md](CONTRIBUTING.md)

### CI/CD

Проект использует **GitHub Actions** для автоматической проверки качества:
- ✅ Форматирование (Ruff)
- ✅ Линтинг (Ruff)
- ✅ Проверка типов (Mypy)
- ✅ Тесты с coverage (Pytest)

**Coverage требования:**
- Общее покрытие проекта: минимум 30%
- Критическая логика (Storage, LLMClient): минимум 70% ✅

CI запускается при push/PR в ветки `main` и `develop`.

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
- [`Makefile`](Makefile) - автоматизация команд
- [`DOCKER.md`](DOCKER.md) - руководство по использованию Docker

### Документация и правила разработки
- [`docs/`](docs/) - техническая документация (vision, tasklist, idea)
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - руководство по контрибуции
- [`.cursor/rules/`](.cursor/rules/) - правила разработки для Cursor IDE

## 🛠️ Технологии

- **Python 3.11+** - основной язык
- **aiogram 3.x** - фреймворк для Telegram Bot API
- **OpenAI SDK** - для работы с OpenRouter API
- **Pydantic** - валидация конфигурации
- **uv** - управление зависимостями
- **Docker** - контейнеризация приложения

## 📄 Лицензия

MIT

## 🤝 Вклад в проект

Мы рады любому вкладу! Пожалуйста, ознакомьтесь с [CONTRIBUTING.md](CONTRIBUTING.md) для получения подробной информации о:
- Стандартах кода
- Процессе разработки
- Требованиях к тестам
- Создании Pull Request

Следуйте принципам KISS и ООП, описанным в [docs/vision.md](docs/vision.md).

