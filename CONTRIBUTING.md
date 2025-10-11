# 🤝 Руководство по контрибуции

Спасибо за интерес к проекту! Мы рады любой помощи.

## 📋 Содержание

- [Как начать](#как-начать)
- [Процесс разработки](#процесс-разработки)
- [Стандарты кода](#стандарты-кода)
- [Тестирование](#тестирование)
- [Создание Pull Request](#создание-pull-request)
- [Полезные ссылки](#полезные-ссылки)

---

## 🚀 Как начать

### 1. Fork и клонирование

```bash
# Сделайте fork репозитория через GitHub UI
# Затем клонируйте свой fork
git clone https://github.com/<your-username>/ai-tg-bot.git
cd ai-tg-bot
```

### 2. Установка зависимостей

```bash
# Установить uv (если ещё не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Mac
# или
pip install uv  # Windows

# Установить зависимости с dev-пакетами
uv sync --all-extras
```

### 3. Установка pre-commit hooks

```bash
make pre-commit-install
```

Pre-commit hooks автоматически проверят код перед каждым коммитом.

---

## 🔨 Процесс разработки

### 1. Создайте ветку для своих изменений

```bash
git checkout -b feature/my-awesome-feature
# или
git checkout -b fix/some-bug
```

**Именование веток:**
- `feature/<название>` - новый функционал
- `fix/<название>` - исправление багов
- `refactor/<название>` - рефакторинг без изменения функционала
- `docs/<название>` - изменения документации

### 2. Внесите изменения

Следуйте [стандартам кода](#стандарты-кода) и [требованиям к тестам](#тестирование).

### 3. Проверьте качество кода

```bash
# Форматирование
make format

# Линтинг и проверка типов
make lint

# Тесты
make test

# Все проверки сразу (как в CI)
make ci
```

### 4. Закоммитьте изменения

```bash
git add .
git commit -m "feat: add awesome feature"
```

**Формат сообщений коммитов:**
- `feat: <описание>` - новый функционал
- `fix: <описание>` - исправление бага
- `refactor: <описание>` - рефакторинг кода
- `test: <описание>` - добавление/изменение тестов
- `docs: <описание>` - изменения документации
- `chore: <описание>` - технические изменения (зависимости, конфигурация)

**Примеры:**
```bash
git commit -m "feat: add /stats command for user statistics"
git commit -m "fix: handle rate limit errors correctly"
git commit -m "refactor: split bot.py into handlers"
git commit -m "test: add tests for Storage class"
git commit -m "docs: update README with deployment guide"
```

### 5. Отправьте изменения

```bash
git push origin feature/my-awesome-feature
```

---

## 📐 Стандарты кода

### Основные принципы

#### KISS (Keep It Simple, Stupid)
- Простые решения вместо сложных
- Без преждевременной оптимизации
- Код должен быть понятен с первого взгляда

#### ООП и структура
- **Один класс = один файл = одна ответственность (SRP)**
- Плоская структура без глубокой вложенности
- Имена файлов соответствуют классам: `llm_client.py` → класс `LLMClient`

### Обязательные требования

#### 1. Type Hints

```python
# ✅ Правильно
def process_message(user_id: int, text: str) -> dict[str, Any]:
    ...

# ❌ Неправильно
def process_message(user_id, text):
    ...
```

#### 2. Docstrings

```python
# ✅ Правильно
async def save_history(self, user_id: int, messages: list[dict[str, str]]) -> None:
    """
    Сохраняет историю диалога пользователя в JSON файл.

    Args:
        user_id: ID пользователя Telegram
        messages: Список сообщений для сохранения

    Raises:
        IOError: При ошибке записи в файл
    """
    ...

# ❌ Неправильно
async def save_history(self, user_id, messages):
    # Сохраняет историю
    ...
```

#### 3. Async/await для I/O операций

```python
# ✅ Правильно
async def load_data(path: Path) -> dict[str, Any]:
    async with aiofiles.open(path) as f:
        content = await f.read()
        return json.loads(content)

# ❌ Неправильно
def load_data(path: Path) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)
```

#### 4. Логирование

```python
# ✅ Правильно
import logging
logger = logging.getLogger(__name__)

async def process(user_id: int) -> None:
    logger.info(f"User {user_id}: processing started")
    try:
        result = await do_something()
        logger.debug(f"User {user_id}: result = {result}")
    except Exception as e:
        logger.error(f"User {user_id}: failed to process: {e}", exc_info=True)

# ❌ Неправильно
print(f"Processing user {user_id}")  # Не используйте print()
```

### Инструменты качества

Проект использует:
- **Ruff** - форматирование и линтинг
- **Mypy** - проверка типов
- **Pytest** - тестирование

Перед коммитом:
```bash
make ci  # Запустит все проверки
```

---

## 🧪 Тестирование

### Требования к тестам

- ✅ **Unit-тесты** для всей критической логики
- ✅ **Минимальное покрытие:**
  - Общее покрытие проекта: **30%**
  - Критическая логика (Storage, LLMClient, core компоненты): **70%**
- ✅ **Async тесты** через pytest-asyncio
- ✅ **Моки** для внешних зависимостей (API, файловая система)

### Структура тестов

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_save_history(storage, temp_data_dir):
    """Тест сохранения истории диалога."""
    user_id = 123
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
    ]
    
    await storage.save_history(user_id, messages)
    
    loaded = await storage.load_history(user_id)
    assert len(loaded) == 2
    assert loaded[0]["content"] == "Hello"
```

### Запуск тестов

```bash
# Все тесты с coverage
make test

# Быстрый запуск
make test-fast

# Конкретный файл
uv run pytest tests/test_storage.py -v

# Конкретный тест
uv run pytest tests/test_storage.py::test_save_history -v
```

### Что тестируем

✅ **Обязательно тестировать:**
- Логику обработки данных
- Обработку ошибок
- Граничные случаи
- Критические компоненты (Storage, LLMClient)

❌ **Не тестируем:**
- Внешние API (используем моки)
- Код библиотек (aiogram, openai)
- Тривиальные getter/setter методы

---

## 📤 Создание Pull Request

### 1. Проверьте что всё работает

```bash
# Запустить все проверки
make ci

# Протестировать бот локально
docker-compose up --build
```

### 2. Создайте Pull Request

- Откройте PR из вашей ветки в `develop` (не в `main`)
- Используйте понятный заголовок
- Опишите что изменилось и зачем
- Добавьте скриншоты если есть UI изменения

### Шаблон описания PR

```markdown
## Что изменилось

Краткое описание изменений.

## Зачем

Зачем нужны эти изменения? Какую проблему они решают?

## Как проверить

1. Шаги для воспроизведения/проверки
2. ...

## Чеклист

- [ ] Код следует стандартам проекта
- [ ] Добавлены/обновлены тесты
- [ ] Все тесты проходят
- [ ] Coverage требования выполнены (30% общее, 70% для критической логики)
- [ ] Документация обновлена (если нужно)
- [ ] Pre-commit hooks установлены и работают
```

### 3. CI проверки

После создания PR автоматически запустятся проверки:
- ✅ Форматирование (Ruff)
- ✅ Линтинг (Ruff)
- ✅ Проверка типов (Mypy)
- ✅ Тесты + Coverage (Pytest)

**PR будет принят только если все проверки пройдены.**

---

## 🔍 Code Review

Ваш код будет проверен мейнтейнерами. Ожидайте:
- Конструктивные комментарии
- Предложения по улучшению
- Вопросы о реализации

**Будьте открыты к фидбэку!** Это помогает улучшить код и проект.

---

## 📚 Полезные ссылки

### Документация проекта
- [Техническое видение](docs/vision.md) - архитектура и принципы
- [План разработки](docs/tasklist.md) - дорожная карта
- [Технический долг](docs/techDebtTasklist.md) - план улучшений
- [Docker руководство](DOCKER.md) - использование Docker

### Правила разработки (Cursor IDE)
- [Соглашения кода](.cursor/rules/conventions.mdc) - стиль и стандарты
- [Workflow](.cursor/rules/workflow.mdc) - процесс разработки

### Внешние ресурсы
- [aiogram 3.x docs](https://docs.aiogram.dev/en/latest/)
- [OpenRouter API](https://openrouter.ai/docs)
- [Pydantic docs](https://docs.pydantic.dev/)
- [Pytest docs](https://docs.pytest.org/)

---

## ❓ Вопросы?

Если у вас есть вопросы:
- Создайте [Issue](https://github.com/<username>/<repo>/issues)
- Посмотрите существующие Issues - возможно ответ уже есть

---

**Спасибо за ваш вклад! 🎉**

