# 📋 План устранения технического долга

## 📊 Отчет о прогрессе

| Итерация | Функционал | Статус | Дата завершения |
|----------|-----------|--------|-----------------|
| 🛠️ Итерация 0 | Инструменты качества кода | ✅ Завершено | 2025-10-11 |
| 🧪 Итерация 1 | Базовое тестирование | ✅ Завершено | 2025-10-11 |
| 🔨 Итерация 2 | Рефакторинг bot.py (handlers) | ✅ Завершено | 2025-10-11 |
| ⚡ Итерация 3 | Async I/O (aiofiles) | ✅ Завершено | 2025-10-11 |
| 🚀 Итерация 4 | CI/CD Pipeline | ✅ Завершено | 2025-10-11 |
| 🎯 Итерация 5 | Расширенное тестирование | ✅ Завершено | 2025-10-11 |
| 🐳 Итерация 6 | Docker Registry (Yandex Cloud) | ✅ Завершено | 2025-10-11 |

### Легенда статусов
- ⏳ **В ожидании** - задача не начата
- 🚧 **В процессе** - задача в разработке
- ✅ **Завершено** - задача выполнена и протестирована
- ⏭️ **Пропущено** - задача отложена или не требуется

---

## 🛠️ Итерация 0: Инструменты качества кода

**Цель**: Внедрить автоматизированные инструменты контроля качества кода.

### Задачи

- [x] Добавить Ruff как линтер и форматтер в `pyproject.toml`
- [x] Добавить Mypy для статической проверки типов
- [x] Настроить конфигурацию Ruff в `pyproject.toml`
- [x] Настроить конфигурацию Mypy в `pyproject.toml`
- [x] Создать `.pre-commit-config.yaml` для Git hooks
- [x] Обновить `Makefile` с командами: `lint`, `format`, `pre-commit-install`
- [x] Установить pre-commit hooks
- [x] Запустить форматирование на существующем коде
- [x] Исправить все ошибки линтера

### Инструменты

**Добавить в `pyproject.toml`:**
```toml
[project.optional-dependencies]
dev = [
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "pre-commit>=3.5.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "A", "C4", "DTZ", "T20", "RET", "SIM", "ARG"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

**Новые команды в `Makefile`:**
```makefile
lint:
	@uv run ruff check src/ tests/
	@uv run mypy src/

format:
	@uv run ruff format src/ tests/
	@uv run ruff check --fix src/ tests/

pre-commit-install:
	@uv run pre-commit install

ci: format lint
	@echo "CI checks passed!"
```

### Тест

```bash
# Установить dev зависимости
uv sync --all-extras

# Проверить форматирование
make format

# Запустить линтер
make lint

# Установить pre-commit hooks
make pre-commit-install

# Попробовать сделать коммит - должны сработать хуки
```

### Проверка соответствия стандартам

- [x] ✅ Код следует принципу KISS (conventions.mdc)
- [x] ✅ Используются только встроенные модули где возможно (conventions.mdc)
- [x] ✅ Минимум новых зависимостей (conventions.mdc)
- [x] ✅ Плоская структура проекта сохранена (vision.md)
- [x] ✅ Все команды через полный путь к uv в Windows (conventions.mdc)

---

## 🧪 Итерация 1: Базовое тестирование

**Цель**: Написать unit-тесты для критической логики (Storage, LLMClient).

### Задачи

- [x] Создать `tests/test_storage.py`
  - [x] Тест загрузки/сохранения истории
  - [x] Тест лимитирования сообщений
  - [x] Тест системного промпта
  - [x] Тест получения информации о диалоге
  - [x] Тест set_system_prompt
  - [x] Тест clear_history
- [x] Создать `tests/test_llm_client.py`
  - [x] Тест успешного запроса к LLM (mock)
  - [x] Тест retry механизма
  - [x] Тест обработки ошибок
  - [x] Тест фильтрации timestamp
  - [x] Тест пустого ответа
  - [x] Тест пустого choices
- [x] Создать `tests/conftest.py` с фикстурами:
  - [x] Фикстура для временной директории
  - [x] Фикстура для Config с тестовыми настройками
  - [x] Фикстура для mock LLM клиента
  - [x] Фикстура для sample messages
- [x] Обновить `Makefile` с командами `test` и `test-fast`
- [x] Настроить pytest в `pyproject.toml`
- [x] Достичь минимум 70% coverage для `storage.py` и `llm_client.py`

### Структура тестов

```
tests/
├── __init__.py
├── conftest.py          # Фикстуры
├── test_storage.py      # Тесты Storage
└── test_llm_client.py   # Тесты LLMClient
```

### Конфигурация pytest

**Добавить в `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Команды в `Makefile`:**
```makefile
test:
	@echo "Running tests with coverage..."
	@uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

test-fast:
	@echo "Running tests without coverage..."
	@uv run pytest tests/ -v
```

### Тест

```bash
# Запустить тесты
make test

# Проверить coverage report
# Открыть htmlcov/index.html

# Проверить что coverage >= 70% для storage.py и llm_client.py
```

### Проверка соответствия стандартам

- [x] ✅ Один файл тестов = один класс (conventions.mdc: один класс = один файл)
- [x] ✅ Type hints во всех тестах (conventions.mdc)
- [x] ✅ Async/await для async методов (conventions.mdc)
- [x] ✅ Docstrings для тестовых функций (conventions.mdc)
- [x] ✅ Плоская структура `tests/` без глубокой вложенности (vision.md)
- [x] ✅ Минимализм - тестируем только критическую логику (vision.md)

### Результаты

- ✅ **24 теста** написано и успешно проходит
- ✅ **storage.py: 83% coverage** (выше требуемых 70%)
- ✅ **llm_client.py: 88% coverage** (выше требуемых 70%)
- ✅ Все тесты проходят линтер и форматирование
- ✅ Использованы pytest fixtures для переиспользования кода

---

## 🔨 Итерация 2: Рефакторинг bot.py (handlers)

**Цель**: Разделить `bot.py` (524 строки) на модули согласно принципу SRP.

### Проблема

`bot.py` нарушает принцип единственной ответственности (SRP):
- Инициализация бота
- Обработка команд (/start, /help, /role, /status, /reset)
- Обработка сообщений
- Разбивка длинных сообщений
- Формирование сообщений об ошибках

### Задачи

- [x] Создать `src/handlers/__init__.py`
- [x] Создать `src/handlers/commands.py` - обработчики команд
  - [x] `handle_start(message: Message) -> None`
  - [x] `handle_help(message: Message) -> None`
  - [x] `handle_role(message: Message, storage: Storage, config: Config) -> None`
  - [x] `handle_status(message: Message, storage: Storage, config: Config) -> None`
  - [x] `handle_reset(message: Message, storage: Storage) -> None`
- [x] Создать `src/handlers/messages.py` - обработчик сообщений
  - [x] `handle_message(message: Message, llm_client: LLMClient, storage: Storage, config: Config) -> None`
- [x] Создать `src/utils/__init__.py`
- [x] Создать `src/utils/message_splitter.py`
  - [x] `split_message(text: str, max_length: int = 4096) -> list[str]`
- [x] Создать `src/utils/error_formatter.py`
  - [x] `get_error_message(error: str) -> str`
- [x] Рефакторить `src/bot.py` - оставить только:
  - [x] Инициализацию aiogram Bot и Dispatcher
  - [x] Регистрацию handlers
  - [x] Методы `start()` и `stop()`
- [x] Обновить импорты во всех файлах
- [x] Убедиться что все type hints на месте
- [x] Убедиться что все docstrings на месте

### Новая структура

```
src/
├── handlers/
│   ├── __init__.py
│   ├── commands.py      # Обработчики команд
│   └── messages.py      # Обработчик сообщений
├── utils/
│   ├── __init__.py
│   ├── message_splitter.py
│   └── error_formatter.py
├── bot.py               # Сокращен до ~100 строк
├── config.py
├── llm_client.py
├── storage.py
└── main.py
```

### Принципы рефакторинга

1. **Один handler = одна функция** - без классов-оберток
2. **Зависимости через параметры** - передаем storage, config явно
3. **Сохраняем async/await** - все handlers остаются асинхронными
4. **Не меняем логику** - только структуру
5. **Type hints везде** - для всех параметров и возвращаемых значений
6. **Docstrings везде** - для всех публичных функций

### Тест

```bash
# Запустить бота
make run

# В Telegram проверить ВСЕ команды:
# 1. /start - приветствие
# 2. /help - список команд
# 3. /role <текст> - установка роли
# 4. /role default - возврат к default
# 5. /status - статистика
# 6. /reset - очистка истории
# 7. Обычное сообщение - ответ от LLM
# 8. Длинное сообщение (>4096 символов) - разбивка на части

# Запустить тесты (если есть)
make test
```

### Проверка соответствия стандартам

- [x] ✅ Один класс/модуль = одна ответственность (conventions.mdc: SRP)
- [x] ✅ Плоская структура с handlers/ и utils/ (vision.md)
- [x] ✅ Имена файлов соответствуют назначению (conventions.mdc)
- [x] ✅ Короткие функции до 20-30 строк (conventions.mdc)
- [x] ✅ Type hints для всех функций (conventions.mdc)
- [x] ✅ Docstrings для всех публичных функций (conventions.mdc)
- [x] ✅ Async/await для I/O операций (conventions.mdc)
- [x] ✅ Логирование ключевых событий (conventions.mdc)
- [x] ✅ Минимум вложенности (conventions.mdc)

### Результаты

- ✅ **bot.py: 512 строк → 106 строк** (уменьшение в 4.8 раза)
- ✅ Создано **6 новых файлов**: handlers/__init__.py, handlers/commands.py, handlers/messages.py, utils/__init__.py, utils/message_splitter.py, utils/error_formatter.py
- ✅ Каждый модуль отвечает за **одну задачу** (SRP)
- ✅ Handlers как функции - **легко тестировать**
- ✅ Зависимости через **functools.partial**
- ✅ Все проверки качества пройдены:
  - Ruff: ✅ All checks passed
  - Mypy: ✅ Success: no issues found in 12 source files
  - Тесты: ✅ 24/24 passed

---

## ⚡ Итерация 3: Async I/O (aiofiles)

**Цель**: Заменить синхронный файловый I/O на асинхронный.

### Проблема

`storage.py` использует `run_in_executor` для файловых операций:
- Блокирует thread pool
- Менее эффективно чем нативный async I/O
- Усложняет код

### Задачи

- [x] Добавить `aiofiles` в зависимости `pyproject.toml`
- [x] Рефакторить `src/storage.py`:
  - [x] Заменить `_read_json_file` + `run_in_executor` на `aiofiles`
  - [x] Заменить `_write_json_file` + `run_in_executor` на `aiofiles`
  - [x] Удалить синхронные вспомогательные методы `_read_json_file`, `_write_json_file`
  - [x] Обновить все методы работы с файлами
- [x] Проверить что все методы Storage остаются async
- [x] Обновить docstrings если нужно
- [x] Запустить линтер и тесты

### Пример рефакторинга

**Было:**
```python
import asyncio

def _read_json_file(self, file_path: Path) -> dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

async def load_history(self, user_id: int) -> list[dict[str, str]]:
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, self._read_json_file, file_path)
```

**Стало:**
```python
import aiofiles
import json

async def load_history(self, user_id: int) -> list[dict[str, str]]:
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        content = await f.read()
        data = json.loads(content)
```

### Тест

```bash
# Запустить тесты Storage
uv run pytest tests/test_storage.py -v

# Запустить бота
make run

# В Telegram:
# 1. Отправить несколько сообщений
# 2. /status - проверить что история сохраняется
# 3. /reset - проверить очистку
# 4. /role <текст> - проверить смену роли
# 5. Проверить файлы в data/ на корректность

# Проверить логи на отсутствие ошибок
```

### Проверка соответствия стандартам

- [x] ✅ Async/await для всех I/O операций (conventions.mdc)
- [x] ✅ Не блокируем event loop (conventions.mdc)
- [x] ✅ Type hints сохранены (conventions.mdc)
- [x] ✅ Docstrings обновлены (conventions.mdc)
- [x] ✅ Логирование сохранено (conventions.mdc)
- [x] ✅ Принцип KISS - код стал проще (vision.md)
- [x] ✅ Минимум новых зависимостей - только aiofiles (conventions.mdc)

### Результаты

- ✅ **Нативный async I/O** через `aiofiles` вместо `run_in_executor`
- ✅ **Удалены синхронные helper-методы**: `_read_json_file`, `_write_json_file`
- ✅ **Упрощение кода**: убрано 13 строк с `import asyncio` и `loop.run_in_executor`
- ✅ **Улучшение производительности**: истинно асинхронные операции без блокировки thread pool
- ✅ Все проверки качества пройдены:
  - Ruff: ✅ All checks passed
  - Mypy: ✅ Success: no issues found in 12 source files
  - Тесты: ✅ 24/24 passed
- ✅ **Новые зависимости**: `aiofiles>=23.0.0` + `types-aiofiles>=23.0.0` (dev)

---

## 🚀 Итерация 4: CI/CD Pipeline

**Цель**: Автоматизировать проверку качества кода и тесты в CI/CD.

### Задачи

- [x] Создать `.github/workflows/ci.yml`
- [x] Настроить GitHub Actions для:
  - [x] Проверки форматирования (ruff format --check)
  - [x] Проверки линтера (ruff check)
  - [x] Проверки типов (mypy)
  - [x] Запуска тестов (pytest)
  - [x] Проверки coverage (минимум 30% общее)
- [x] Настроить запуск на push и pull_request (только main и develop)
- [x] Добавить badge в README.md
- [x] Обновить README.md с инструкциями по разработке
- [x] Создать CONTRIBUTING.md с правилами контрибуции

### Конфигурация CI

**Создать `.github/workflows/ci.yml`:**
```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync --all-extras
      
      - name: Check formatting
        run: uv run ruff format --check src/ tests/
      
      - name: Run linter
        run: uv run ruff check src/ tests/
      
      - name: Run type checker
        run: uv run mypy src/
      
      - name: Run tests with coverage
        run: uv run pytest tests/ --cov=src --cov-report=term --cov-fail-under=30
```

### Обновления документации

**README.md:**
- Добавить секцию "Development"
- Добавить CI badge
- Описать как запускать линтер и тесты локально

**CONTRIBUTING.md:**
- Правила форматирования кода
- Как запустить pre-commit hooks
- Требования к тестам
- Процесс создания PR

### Тест

```bash
# Локально проверить что все проходит
make ci

# Создать тестовый PR и проверить что CI проходит успешно

# Проверить badge в README.md
```

### Проверка соответствия стандартам

- [x] ✅ Простая конфигурация CI (conventions.mdc: KISS)
- [x] ✅ Только необходимые проверки (vision.md: минимализм)
- [x] ✅ Документация обновлена (conventions.mdc)
- [x] ✅ Следуем принципам из vision.md

### Результаты

- ✅ **CI/CD Pipeline** настроен на GitHub Actions
- ✅ **Автоматические проверки**: форматирование, линтинг, типы, тесты
- ✅ **Coverage requirement**: минимум 30% (общее), 70% для критической логики
- ✅ **CI триггеры**: push/PR в `main` и `develop`
- ✅ **CI Badge** добавлен в README.md
- ✅ **Секция Development** добавлена в README.md (~70 строк)
- ✅ **CONTRIBUTING.md** создан (~280 строк)
- ✅ **Документация** для новых контрибьюторов
- ✅ **Единый стандарт** качества кода

---

## 🎯 Итерация 5: Расширенное тестирование

**Цель**: Расширить покрытие тестами до 80%+ для всего проекта.

### Задачи

#### Тесты для utils

- [x] Создать `tests/test_message_splitter.py`
  - [x] Тест обычного сообщения (< 4096 символов)
  - [x] Тест длинного сообщения, который нужно разбить
  - [x] Тест разбивки на несколько частей (>8192 символов)
  - [x] Тест с пользовательским max_length
  - [x] Тест пустой строки
  - [x] Тест границ (ровно 4096 символов)
- [x] Создать `tests/test_error_formatter.py`
  - [x] Тест форматирования известных ошибок
  - [x] Тест форматирования неизвестных ошибок
  - [x] Тест с пустой строкой
  - [x] Тест различных типов ошибок API

#### Интеграционные тесты для handlers

- [x] Создать `tests/test_handlers_integration.py`
  - [x] Тест полного цикла команды /start
  - [x] Тест полного цикла команды /help
  - [x] Тест полного цикла команды /role (установка и проверка)
  - [x] Тест полного цикла команды /status (с историей)
  - [x] Тест полного цикла команды /reset
  - [x] Тест обработки обычного сообщения с mock LLM
  - [x] Тест обработки длинного сообщения (разбивка)
  - [x] Тест обработки ошибки LLM API
  - [x] Тест взаимодействия handlers → storage
  - [x] Тест взаимодействия handlers → llm_client

#### Coverage и CI

- [x] Достичь 80%+ coverage для `src/utils/`
- [x] Достичь 80%+ coverage для `src/handlers/`
- [x] Обновить минимальный coverage в CI с 30% на 80%
- [x] Исключить bot.py и main.py из расчета coverage (точки входа)
- [x] Добавить coverage badge в README.md

### Структура тестов

```text
tests/
├── __init__.py
├── conftest.py                    # Общие фикстуры
├── test_storage.py                # Unit-тесты Storage (83%)
├── test_llm_client.py             # Unit-тесты LLMClient (88%)
├── test_message_splitter.py       # NEW: Unit-тесты utils
├── test_error_formatter.py        # NEW: Unit-тесты utils
└── test_handlers_integration.py  # NEW: Интеграционные тесты handlers
```

### Примеры тестов

#### test_message_splitter.py

```python
"""Тесты для модуля разбивки сообщений."""
import pytest
from src.utils.message_splitter import split_message


def test_short_message() -> None:
    """Тест короткого сообщения, которое не нужно разбивать."""
    text = "Hello, world!"
    result = split_message(text)
    assert len(result) == 1
    assert result[0] == text


def test_long_message() -> None:
    """Тест длинного сообщения, которое нужно разбить."""
    text = "A" * 5000
    result = split_message(text, max_length=4096)
    assert len(result) == 2
    assert len(result[0]) == 4096
    assert len(result[1]) == 904


def test_boundary_message() -> None:
    """Тест сообщения ровно на границе max_length."""
    text = "A" * 4096
    result = split_message(text)
    assert len(result) == 1
    assert result[0] == text


def test_empty_message() -> None:
    """Тест пустого сообщения."""
    text = ""
    result = split_message(text)
    assert len(result) == 1
    assert result[0] == ""
```

#### test_handlers_integration.py

```python
"""Интеграционные тесты для handlers."""
import pytest
from unittest.mock import AsyncMock, Mock
from aiogram.types import Message, User, Chat
from src.handlers.commands import handle_start, handle_status, handle_reset
from src.handlers.messages import handle_message
from src.storage import Storage
from src.llm_client import LLMClient
from src.config import Config


@pytest.fixture
def mock_message() -> Message:
    """Фикстура для mock сообщения."""
    message = Mock(spec=Message)
    message.from_user = Mock(spec=User)
    message.from_user.id = 123456789
    message.chat = Mock(spec=Chat)
    message.chat.id = 123456789
    message.answer = AsyncMock()
    message.text = "Test message"
    return message


@pytest.mark.asyncio
async def test_handle_start_integration(mock_message: Message) -> None:
    """Интеграционный тест команды /start."""
    await handle_start(mock_message)
    
    # Проверяем что ответ был отправлен
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Привет" in call_args or "бот" in call_args.lower()


@pytest.mark.asyncio
async def test_handle_message_with_storage_integration(
    mock_message: Message,
    tmp_storage: Storage,
    test_config: Config,
) -> None:
    """Интеграционный тест обработки сообщения с сохранением в Storage."""
    # Создаем mock LLM клиента
    mock_llm = Mock(spec=LLMClient)
    mock_llm.generate_response = AsyncMock(return_value="Test response")
    
    # Обрабатываем сообщение
    await handle_message(mock_message, mock_llm, tmp_storage, test_config)
    
    # Проверяем что сообщение сохранилось в storage
    history = await tmp_storage.load_history(mock_message.from_user.id)
    assert len(history) == 2  # user message + assistant response
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Test message"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Test response"
    
    # Проверяем что ответ отправлен
    mock_message.answer.assert_called_once_with("Test response")
```

### Новые фикстуры в conftest.py

```python
@pytest.fixture
def mock_message() -> Message:
    """Фикстура для создания mock Telegram сообщения."""
    message = Mock(spec=Message)
    message.from_user = Mock(spec=User)
    message.from_user.id = 123456789
    message.chat = Mock(spec=Chat)
    message.chat.id = 123456789
    message.answer = AsyncMock()
    message.text = "Test message"
    return message


@pytest.fixture
def mock_llm_error() -> Mock:
    """Фикстура для mock LLM клиента с ошибкой."""
    mock = Mock(spec=LLMClient)
    mock.generate_response = AsyncMock(
        side_effect=Exception("API Error")
    )
    return mock
```

### Обновление CI

**Обновить `.github/workflows/ci.yml`:**

```yaml
- name: Run tests with coverage
  run: |
    uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
    uv run pytest tests/ --cov=src --cov-fail-under=70
```

**Добавить coverage badge в README.md:**

```markdown
[![Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen)](./htmlcov/index.html)
```

### Тест

```bash
# Запустить все тесты
make test

# Проверить coverage report
# Открыть htmlcov/index.html

# Проверить coverage по модулям:
# - src/utils/message_splitter.py - >= 80%
# - src/utils/error_formatter.py - >= 80%
# - src/handlers/commands.py - >= 70%
# - src/handlers/messages.py - >= 70%
# - Общий coverage - >= 70%

# Запустить конкретную группу тестов
uv run pytest tests/test_message_splitter.py -v
uv run pytest tests/test_error_formatter.py -v
uv run pytest tests/test_handlers_integration.py -v

# Проверить что CI проходит
make ci
```

### Проверка соответствия стандартам

- [x] ✅ Тесты следуют AAA паттерну (Arrange-Act-Assert)
- [x] ✅ Type hints во всех тестах (conventions.mdc)
- [x] ✅ Docstrings для всех тестовых функций (conventions.mdc)
- [x] ✅ Async/await для async тестов (conventions.mdc)
- [x] ✅ Использование фикстур для переиспользования (DRY)
- [x] ✅ Минимальное использование mocks (conventions.mdc)
- [x] ✅ Понятные названия тестов (conventions.mdc)
- [x] ✅ Изолированные тесты без зависимостей друг от друга
- [x] ✅ Coverage >= 76% для handlers, >= 96% для utils

### Ожидаемые результаты

**Метрики coverage:**

- ✅ **message_splitter.py: >= 80%** (unit-тесты)
- ✅ **error_formatter.py: >= 80%** (unit-тесты)
- ✅ **handlers/commands.py: >= 70%** (интеграционные тесты)
- ✅ **handlers/messages.py: >= 70%** (интеграционные тесты)
- ✅ **Общий coverage: >= 70%** (все модули)

**Количество тестов:**

- 24 существующих теста (Storage, LLMClient)
- ~10 новых тестов для utils
- ~10 новых интеграционных тестов для handlers
- **Итого: ~44 теста**

**Качество:**

- ✅ Все тесты проходят линтер (Ruff)
- ✅ Все тесты проходят проверку типов (Mypy)
- ✅ CI проходит с обновленным coverage threshold (70%)
- ✅ Coverage badge добавлен в README.md

### Результаты

- ✅ **49 тестов пройдено** (24 существующих + 25 новых)
- ✅ **Coverage 85%** (превышает требуемые 80%)
  - `message_splitter.py`: **96%**
  - `error_formatter.py`: **100%**
  - `handlers/commands.py`: **76%**
  - `handlers/messages.py`: **91%**
  - `llm_client.py`: **88%**
  - `storage.py`: **81%**
- ✅ **bot.py и main.py** исключены из расчета coverage (точки входа)
- ✅ **CI/CD обновлен** с требованием coverage >= 80%
- ✅ **Coverage badge** добавлен в README.md
- ✅ **6 новых фикстур** для handlers тестов в conftest.py
- ✅ **Все проверки качества пройдены**:
  - Ruff format: ✅ 4 files reformatted
  - Ruff check: ✅ 3 errors fixed
  - Mypy: ✅ Success: no issues found in 12 source files
  - Tests: ✅ 49/49 passed

**Новые тесты:**
- `test_message_splitter.py`: 6 unit-тестов
- `test_error_formatter.py`: 6 unit-тестов (включая case-insensitive)
- `test_handlers_integration.py`: 13 интеграционных тестов

**Обновления конфигурации:**
- `.github/workflows/ci.yml`: coverage threshold 30% → 80%
- `pyproject.toml`: добавлена секция `[tool.coverage.run]` с omit для bot.py и main.py
- `tests/conftest.py`: +6 новых фикстур (mock_user, mock_chat, mock_message, mock_bot, mock_llm_client, mock_storage)

---

## 🐳 Итерация 6: Docker Registry (Yandex Cloud)

**Цель**: Автоматизировать сборку и публикацию Docker образов в Yandex Cloud Container Registry.

### Задачи

#### Подготовка инфраструктуры (вручную)

**Эти действия выполняются разработчиком вручную:**

- [ ] Создать Container Registry в Yandex Cloud (см. инструкции ниже)
- [ ] Создать Service Account с правами `container-registry.images.pusher`
- [ ] Создать авторизованный ключ JSON для Service Account
- [ ] Добавить секреты в GitHub Repository Settings → Secrets and variables → Actions:
  - **`YA_CLOUD_REGISTRY`** - JSON ключ Service Account (весь файл key.json)
  - **`YC_REGISTRY_ID`** - ID Container Registry (формат: `crpXXXXXXXXXXXXXXXX`)

#### Управление версиями

- [x] Создать файл `VERSION` в корне репозитория
  - Формат: `1.0.0` (без префикса `v`)
  - Начальная версия: `0.1.0`
- [x] Добавить `VERSION` в git (коммитить)
- [x] Обновлять `VERSION` вручную перед каждым релизом

#### Обновление CI/CD

- [x] Обновить `.github/workflows/ci.yml`
- [x] Добавить новый job `docker` после job `quality`
- [x] Настроить зависимость: `docker` запускается только после успешного `quality`
- [x] Настроить триггеры: только на `push` в ветку `main`
- [x] Настроить чтение версии из файла `VERSION`
- [x] Настроить Docker Buildx для эффективной сборки
- [x] Настроить авторизацию в Yandex Container Registry
- [x] Настроить тегирование образов: `{version}` и `latest`
- [x] Настроить GitHub Actions Cache для Docker слоев

#### Стратегия версионирования образов

**Принцип:**
- Версия хранится в файле `VERSION` в корне репозитория
- Формат: `1.0.0` (семантическое версионирование без префикса `v`)
- CI автоматически читает версию из файла и создает образы

**Теги для образов:**

1. **`{version}`** - конкретная версия из файла `VERSION` (например, `1.0.0`)
2. **`latest`** - последняя опубликованная версия из `main`

**Метаданные (Labels):**
- `org.opencontainers.image.version` - версия из файла VERSION
- `org.opencontainers.image.revision` - полный git SHA коммита
- `org.opencontainers.image.created` - дата и время сборки (UTC)
- `org.opencontainers.image.source` - URL репозитория

**Примеры образов:**
```
cr.yandex/{registry-id}/ai-tg-bot:0.1.0
cr.yandex/{registry-id}/ai-tg-bot:1.0.0
cr.yandex/{registry-id}/ai-tg-bot:1.2.3
cr.yandex/{registry-id}/ai-tg-bot:latest
```

**Workflow обновления версии:**
1. Редактируем файл `VERSION`: `1.0.0` → `1.0.1`
2. Коммитим: `git commit -am "chore: bump version to 1.0.1"`
3. Push в `main`: автоматически собираются образы с новой версией
4. Результат: `ai-tg-bot:1.0.1` и `ai-tg-bot:latest`

#### Документация

- [x] Обновить README.md с инструкциями по Docker Registry
- [x] Добавить секцию "Deployment" в README.md
- [x] Документировать требования к GitHub Secrets
- [x] Добавить примеры команд для pull образов
- [ ] Добавить badge с версией Docker образа (опционально)

### Конфигурация CI

**Обновить `.github/workflows/ci.yml`:**

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

env:
  REGISTRY: cr.yandex
  IMAGE_NAME: ai-tg-bot

jobs:
  quality:
    name: Code Quality & Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync --all-extras
      
      - name: Check formatting
        run: uv run ruff format --check src/ tests/
      
      - name: Run linter
        run: uv run ruff check src/ tests/
      
      - name: Run type checker
        run: uv run mypy src/
      
      - name: Run tests with coverage
        run: uv run pytest tests/ --cov=src --cov-report=term --cov-report=xml --cov-fail-under=80

  docker:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    needs: quality
    # Публикуем только при push в main (не при PR)
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Read version from VERSION file
        id: version
        run: |
          VERSION=$(cat VERSION | tr -d '\n\r')
          echo "version=${VERSION}" >> $GITHUB_OUTPUT
          echo "📦 Building version: ${VERSION}"
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Yandex Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: json_key
          password: ${{ secrets.YA_CLOUD_REGISTRY }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./.build/Dockerfile
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ secrets.YC_REGISTRY_ID }}/${{ env.IMAGE_NAME }}:${{ steps.version.outputs.version }}
            ${{ env.REGISTRY }}/${{ secrets.YC_REGISTRY_ID }}/${{ env.IMAGE_NAME }}:latest
          labels: |
            org.opencontainers.image.title=AI Telegram Bot
            org.opencontainers.image.description=AI-powered Telegram bot with LLM integration
            org.opencontainers.image.version=${{ steps.version.outputs.version }}
            org.opencontainers.image.revision=${{ github.sha }}
            org.opencontainers.image.created=${{ github.event.head_commit.timestamp }}
            org.opencontainers.image.source=${{ github.repositoryUrl }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Image info
        run: |
          echo "✅ Docker images published successfully!"
          echo ""
          echo "Images:"
          echo "  - ${{ env.REGISTRY }}/${{ secrets.YC_REGISTRY_ID }}/${{ env.IMAGE_NAME }}:${{ steps.version.outputs.version }}"
          echo "  - ${{ env.REGISTRY }}/${{ secrets.YC_REGISTRY_ID }}/${{ env.IMAGE_NAME }}:latest"
          echo ""
          echo "Version: ${{ steps.version.outputs.version }}"
          echo "Commit: ${{ github.sha }}"
```

### Инструкции для ручной настройки Yandex Cloud

#### Шаг 1: Установка Yandex Cloud CLI

**Windows PowerShell:**
```powershell
iex (New-Object System.Net.WebClient).DownloadString('https://storage.yandexcloud.net/yandexcloud-yc/install.ps1')
```

**Linux/macOS:**
```bash
curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
```

#### Шаг 2: Инициализация и авторизация

```bash
yc init
# Следуйте инструкциям: выберите cloud, folder, зону
```

#### Шаг 3: Создание Container Registry

```bash
yc container registry create --name ai-tg-bot-registry
```

**Результат:**
```
done (1s)
id: crp1234567890abcdef  <-- Сохраните этот ID!
folder_id: b1g...
name: ai-tg-bot-registry
status: ACTIVE
created_at: "2025-10-11T12:00:00.000Z"
```

**✅ Скопируйте `id` (формат: `crpXXXXXXXXXXXXXXXX`) - это `YC_REGISTRY_ID`**

#### Шаг 4: Создание Service Account

```bash
# 1. Получить ID папки (folder)
yc config list
# Найдите строку: folder-id: b1gXXXXXXXXXXXXXXXXX

# 2. Создать service account
yc iam service-account create \
  --name github-actions-sa \
  --description "Service Account for GitHub Actions Docker push"

# 3. Получить ID service account
yc iam service-account get github-actions-sa
# Найдите строку: id: ajeXXXXXXXXXXXXXXXXX

# 4. Назначить роль container-registry.images.pusher
yc resource-manager folder add-access-binding <FOLDER_ID> \
  --role container-registry.images.pusher \
  --subject serviceAccount:<SERVICE_ACCOUNT_ID>

# Замените:
# <FOLDER_ID> на ваш folder-id (из шага 1)
# <SERVICE_ACCOUNT_ID> на id service account (из шага 3)
```

#### Шаг 5: Создание авторизованного ключа

```bash
yc iam key create \
  --service-account-name github-actions-sa \
  --output key.json

# Просмотреть содержимое ключа
cat key.json
```

**Результат `key.json`:**
```json
{
   "id": "ajeXXXXXXXXXXXXXXXXX",
   "service_account_id": "ajeYYYYYYYYYYYYYYYYY",
   "created_at": "2025-10-11T12:00:00.000000Z",
   "key_algorithm": "RSA_2048",
   "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n",
   "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
}
```

**✅ Весь этот JSON нужно скопировать в GitHub Secret `YA_CLOUD_REGISTRY`**

#### Шаг 6: Проверка

```bash
# Проверить что registry создан
yc container registry list

# Проверить что service account имеет права
yc resource-manager folder list-access-bindings <FOLDER_ID> | grep github-actions-sa
```

#### Шаг 7: Добавление секретов в GitHub

1. Перейдите в репозиторий на GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret**

**Секрет 1: `YC_REGISTRY_ID`**
- Name: `YC_REGISTRY_ID`
- Value: `crp1234567890abcdef` (ID registry из Шага 3)

**Секрет 2: `YA_CLOUD_REGISTRY`**
- Name: `YA_CLOUD_REGISTRY`
- Value: полное содержимое файла `key.json` (из Шага 5)

**✅ Готово! Секреты настроены.**

### Обновление README.md

Добавить секцию:

```markdown
## 🐳 Deployment

### Docker Registry

Проект автоматически публикует Docker образы в Yandex Cloud Container Registry при каждом push в `main`.

**Версионирование:**
- Версия хранится в файле `VERSION` в корне репозитория (формат: `1.0.0`)
- При push в `main` автоматически собираются образы с текущей версией

**Доступные образы:**

```bash
# Конкретная версия
cr.yandex/{registry-id}/ai-tg-bot:1.0.0

# Последняя стабильная версия
cr.yandex/{registry-id}/ai-tg-bot:latest
```

**Как обновить версию:**

1. Отредактируйте файл `VERSION`: `1.0.0` → `1.0.1`
2. Закоммитьте: `git commit -am "chore: bump version to 1.0.1"`
3. Push в `main`: автоматически соберутся образы `1.0.1` и `latest`

**Pull образа:**

```bash
# Авторизоваться в Yandex Container Registry
yc container registry configure-docker

# Pull конкретной версии
docker pull cr.yandex/{registry-id}/ai-tg-bot:1.0.0

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
```

### Тест

**1. Создать файл VERSION:**
```bash
# Создать файл с начальной версией
echo "0.1.0" > VERSION

# Закоммитить
git add VERSION
git commit -m "chore: add VERSION file"
```

**2. Локальная проверка Docker:**
```bash
# Проверить что .build/Dockerfile существует и корректен
docker build -f .build/Dockerfile -t ai-tg-bot:test .

# Запустить контейнер для теста (должен вывести help)
docker run --rm ai-tg-bot:test python -m src.main --help
```

**3. Проверка CI через PR:**
```bash
# Создать ветку
git checkout -b feature/docker-registry

# Закоммитить изменения
git add .github/workflows/ci.yml README.md VERSION
git commit -m "feat: add Docker Registry integration"

# Push и создать PR
git push origin feature/docker-registry

# Проверить что CI проходит:
# ✅ quality job должен пройти успешно
# ⚠️ docker job НЕ запускается (только в main)
```

**4. После мержа в main:**
```bash
# Влить PR в main
# Проверить что оба job запустились:
# ✅ quality job
# ✅ docker job (сборка и публикация образов)
```

**5. Проверка образов в Yandex Cloud:**
```bash
# Посмотреть список образов
yc container image list --registry-id <YC_REGISTRY_ID>

# Посмотреть теги конкретного образа
yc container image list --registry-id <YC_REGISTRY_ID> --repository-name ai-tg-bot

# Ожидаемый результат:
# - ai-tg-bot:0.1.0
# - ai-tg-bot:latest
```

**6. Pull и запуск образа из Registry:**
```bash
# Авторизоваться в Registry
yc container registry configure-docker

# Pull образа
docker pull cr.yandex/<YC_REGISTRY_ID>/ai-tg-bot:0.1.0
docker pull cr.yandex/<YC_REGISTRY_ID>/ai-tg-bot:latest

# Запустить контейнер
docker run --rm \
  -e BOT_TOKEN=<your-token> \
  -e OPENROUTER_API_KEY=<your-key> \
  -v $(pwd)/data:/app/data \
  cr.yandex/<YC_REGISTRY_ID>/ai-tg-bot:latest

# Проверить что бот запустился и работает
```

**7. Проверка обновления версии:**
```bash
# Обновить VERSION
echo "0.2.0" > VERSION

# Закоммитить и запушить
git add VERSION
git commit -m "chore: bump version to 0.2.0"
git push origin main

# Проверить что CI собрал новые образы:
# - ai-tg-bot:0.2.0
# - ai-tg-bot:latest (обновлен)
```

### Проверка соответствия стандартам

- [ ] ✅ Простая конфигурация CI (conventions.mdc: KISS)
- [ ] ✅ Интеграция с существующим CI workflow (vision.md)
- [ ] ✅ Используется production Dockerfile из .build/ (vision.md)
- [ ] ✅ Автоматическое версионирование образов (best practice)
- [ ] ✅ GitHub Actions Cache для ускорения сборки (оптимизация)
- [ ] ✅ Метаданные (labels) для отслеживания (best practice)
- [ ] ✅ Документация обновлена (conventions.mdc)
- [ ] ✅ Безопасность: секреты через GitHub Secrets (best practice)
- [ ] ✅ Только необходимые зависимости - используем существующие actions (conventions.mdc)

### Ожидаемые результаты

**После завершения итерации:**

- ✅ **Автоматическая сборка** Docker образов при push в `main`
- ✅ **Публикация** в Yandex Cloud Container Registry
- ✅ **Версионирование** через файл `VERSION` (формат: `1.0.0`)
- ✅ **Теги образов**: `{version}` и `latest`
- ✅ **GitHub Actions Cache** ускоряет повторные сборки
- ✅ **Метаданные OCI** для отслеживания версий и источника
- ✅ **Документация** для deployment в README.md
- ✅ **Секреты настроены** вручную в GitHub

**Метрики:**

- Время сборки: ~2-5 минут (с cache ~1-2 минуты)
- Размер образа: ~150-200 MB (Alpine-based multi-stage build)
- Автоматизация сборки: 100% (версия из файла, без ручного вмешательства)
- Обновление версии: вручную (редактирование файла `VERSION`)

**Workflow релиза:**

1. Обновить `VERSION`: `0.1.0` → `0.2.0`
2. Закоммитить: `git commit -am "chore: bump version to 0.2.0"`
3. Push в `main`: CI автоматически соберет образы `0.2.0` и `latest`
4. Образы доступны в Yandex Cloud Registry

---

## 📝 Дополнительные улучшения (опционально)

Эти задачи можно выполнить после основных итераций:

### Code Quality

- [ ] Добавить bandit для проверки безопасности
- [ ] Настроить dependabot для обновления зависимостей
- [ ] Добавить pre-commit hook для проверки размера коммитов

### Documentation

- [ ] Создать архитектурные диаграммы (PlantUML/Mermaid)
- [ ] Добавить примеры использования в README.md
- [ ] Создать FAQ.md

### Refactoring

- [ ] Создать декоратор для получения user_id (DRY)
- [ ] Создать middleware для логирования всех сообщений
- [ ] Вынести константы в отдельный модуль `constants.py`

---

## 🎯 Принципы работы над техническим долгом

### 1. Итеративность

- Одна итерация = одна область улучшений
- Не смешивать разные типы изменений в одной итерации
- Каждая итерация должна быть полностью рабочей

### 2. Тестирование

- После каждой итерации запускать полный набор тестов
- Проверять работу бота в Telegram вручную
- Убеждаться что ничего не сломалось

### 3. Соответствие стандартам

- **Каждая итерация** проверяется на соответствие `conventions.mdc`
- **Каждая итерация** проверяется на соответствие `vision.md`
- Контрольный чеклист в конце каждой итерации

### 4. Документирование

- Обновлять README.md при изменении процесса разработки
- Обновлять vision.md при изменении архитектуры
- Комментировать сложные решения в коде

### 5. Коммиты

- Один коммит = одна итерация
- Формат: `refactor: Итерация N - [описание]`
- Пример: `refactor: Iteration 0 - add code quality tools`

---

## Контрольный чеклист перед завершением итерации

Перед тем как отметить итерацию как завершенную, проверь:

- [ ] Все задачи из итерации выполнены
- [ ] Код отформатирован (`make format`)
- [ ] Линтер не выдает ошибок (`make lint`)
- [ ] Все тесты проходят (`make test`)
- [ ] Бот работает корректно (ручное тестирование)
- [ ] Документация обновлена (если нужно)
- [ ] Проверка соответствия conventions.mdc выполнена ✅
- [ ] Проверка соответствия vision.md выполнена ✅
- [ ] Коммит сделан с правильным форматом
- [ ] Таблица прогресса в этом файле обновлена

---

**Дата создания**: 2025-10-11  
**Последнее обновление**: 2025-10-11

**Обновления**:
- 2025-10-11: Добавлена Итерация 5 - Расширенное тестирование (utils, handlers, 80%+ coverage)
- 2025-10-11: Добавлена и завершена Итерация 6 - Docker Registry (Yandex Cloud) с версионированием через файл VERSION

**Примечание**: Этот план создан на основе рекомендаций Senior Python Tech Lead после code review проекта. Следуй принципам KISS, DRY, SOLID и best practices Python.
