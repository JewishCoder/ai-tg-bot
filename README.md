# AI Telegram Bot

[![CI](https://github.com/jewishcoder/ai-tg-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/jewishcoder/ai-tg-bot/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](./htmlcov/index.html)

LLM-ассистент в виде Telegram-бота с использованием OpenRouter API.

---

## 📚 Документация

### Для новичков
- 🎨 **[Visual Guide](docs/guides/VISUAL_GUIDE.md)** - Визуальный обзор архитектуры с диаграммами
- 📖 **[Все гайды](docs/guides/README.md)** - Полный индекс документации для разработчиков и DevOps

### Для разработчиков
- 📋 [vision.md](docs/vision.md) - Техническое видение проекта
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - Руководство по контрибуции
- 📝 [CHANGELOG.md](CHANGELOG.md) - История изменений

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

## 🛡️ Надежность и отказоустойчивость

### Fallback модель

Бот поддерживает **автоматическое переключение на резервную LLM модель** при недоступности основной. Это повышает надежность и гарантирует, что пользователи всегда получат ответ.

**Как это работает:**

1. **Основная модель недоступна** (rate limit, серверная ошибка) → автоматически переключаемся на fallback модель
2. **Fallback модель отвечает** → пользователь получает ответ (не видит технических деталей)
3. **Обе модели недоступны** → пользователь получает понятное сообщение об ошибке

**Настройка fallback модели:**

Добавьте в `.env.development` (или `.env.production`):

```bash
# Основная модель (платная, мощная)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Резервная модель (бесплатная, быстрая)
OPENROUTER_FALLBACK_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

**Рекомендации по выбору fallback модели:**

- ✅ **Бесплатная модель** - для снижения затрат при сбоях
- ✅ **Быстрая модель** - для минимальной задержки
- ✅ **Доступная модель** - высокий rate limit
- ✅ **Качественная модель** - хороший fallback лучше чем ошибка

**Популярные варианты fallback моделей:**

| Модель | Преимущества | Недостатки |
|--------|--------------|------------|
| `meta-llama/llama-3.1-8b-instruct:free` | Бесплатная, быстрая | Качество ниже платных |
| `google/gemini-flash-1.5` | Быстрая, доступная | Платная (дешевая) |
| `openai/gpt-3.5-turbo` | Хорошее качество | Платная |

**Мониторинг:**

Fallback события логируются с уровнем `WARNING`:

```
WARNING: Primary model failed for user 12345: Rate limit exceeded. Trying fallback model: meta-llama/llama-3.1-8b-instruct:free
INFO: Fallback model succeeded for user 12345. Model: meta-llama/llama-3.1-8b-instruct:free. Tokens: 45
```

Подробнее: [docs/FALLBACK.md](docs/FALLBACK.md)

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

## 🐳 Deployment

### Docker Registry

Проект автоматически публикует Docker образы в Yandex Cloud Container Registry при каждом push в `main`.

**Версионирование:**
- Версия хранится в файле `VERSION` в корне репозитория (формат: `1.0.0`)
- При push в `main` автоматически собираются образы с текущей версией

**Доступные образы:**

```bash
# Конкретная версия
cr.yandex/{registry-id}/ai-tg-bot:0.1.0

# Последняя стабильная версия
cr.yandex/{registry-id}/ai-tg-bot:latest
```

**Как обновить версию:**

1. Отредактируйте файл `VERSION`: `0.1.0` → `0.2.0`
2. Закоммитьте: `git commit -am "chore: bump version to 0.2.0"`
3. Push в `main`: автоматически соберутся образы `0.2.0` и `latest`

**Pull образа:**

```bash
# Авторизоваться в Yandex Container Registry
yc container registry configure-docker

# Pull конкретной версии
docker pull cr.yandex/{registry-id}/ai-tg-bot:0.1.0

# Pull последней версии
docker pull cr.yandex/{registry-id}/ai-tg-bot:latest
```

**Запуск контейнера:**

```bash
docker run -d \
  --name ai-tg-bot \
  --env-file .env.production \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  cr.yandex/{registry-id}/ai-tg-bot:latest
```

**Проверка запущенного контейнера:**

```bash
# Логи
docker logs ai-tg-bot -f

# Статус
docker ps | grep ai-tg-bot

# Остановка
docker stop ai-tg-bot

# Удаление
docker rm ai-tg-bot
```

### Требуемые GitHub Secrets

Для работы CI/CD необходимо настроить следующие секреты в **Settings → Secrets and variables → Actions**:

| Секрет | Описание | Пример значения |
|--------|----------|-----------------|
| `YA_CLOUD_REGISTRY` | JSON ключ Service Account | `{"id": "aje...", "service_account_id": "...", ...}` |
| `YC_REGISTRY_ID` | ID Container Registry | `crp1234567890abcdef` |

Подробные инструкции по настройке Yandex Cloud смотрите в [docs/techDebtTasklist.md](docs/techDebtTasklist.md) (Итерация 6).

## 📄 Лицензия

MIT

## 🤝 Вклад в проект

Мы рады любому вкладу! Пожалуйста, ознакомьтесь с [CONTRIBUTING.md](CONTRIBUTING.md) для получения подробной информации о:
- Стандартах кода
- Процессе разработки
- Требованиях к тестам
- Создании Pull Request

Следуйте принципам KISS и ООП, описанным в [docs/vision.md](docs/vision.md).

