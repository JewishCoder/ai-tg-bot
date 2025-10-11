# 📋 План устранения технического долга

## 📊 Отчет о прогрессе

| Итерация | Функционал | Статус | Дата завершения |
|----------|-----------|--------|-----------------|
| 🛠️ Итерация 0 | Инструменты качества кода | ✅ Завершено | 2025-10-11 |
| 🧪 Итерация 1 | Базовое тестирование | ✅ Завершено | 2025-10-11 |
| 🔨 Итерация 2 | Рефакторинг bot.py (handlers) | ✅ Завершено | 2025-10-11 |
| ⚡ Итерация 3 | Async I/O (aiofiles) | ✅ Завершено | 2025-10-11 |
| 🚀 Итерация 4 | CI/CD Pipeline | ⏳ В ожидании | - |

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

- [ ] Создать `.github/workflows/ci.yml`
- [ ] Настроить GitHub Actions для:
  - [ ] Проверки форматирования (ruff format --check)
  - [ ] Проверки линтера (ruff check)
  - [ ] Проверки типов (mypy)
  - [ ] Запуска тестов (pytest)
  - [ ] Проверки coverage (минимум 70%)
- [ ] Настроить запуск на push и pull_request
- [ ] Добавить badge в README.md
- [ ] Обновить README.md с инструкциями по разработке
- [ ] Создать CONTRIBUTING.md с правилами контрибуции

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
        run: uv run pytest tests/ --cov=src --cov-report=term --cov-fail-under=70
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

- [ ] ✅ Простая конфигурация CI (conventions.mdc: KISS)
- [ ] ✅ Только необходимые проверки (vision.md: минимализм)
- [ ] ✅ Документация обновлена (conventions.mdc)
- [ ] ✅ Следуем принципам из vision.md

---

## 📝 Дополнительные улучшения (опционально)

Эти задачи можно выполнить после основных итераций:

### Code Quality
- [ ] Добавить bandit для проверки безопасности
- [ ] Добавить coverage badge в README.md
- [ ] Настроить dependabot для обновления зависимостей

### Testing
- [ ] Написать интеграционные тесты для handlers
- [ ] Добавить тесты для utils (message_splitter, error_formatter)
- [ ] Достичь 80%+ coverage для всего проекта

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

**Примечание**: Этот план создан на основе рекомендаций Senior Python Tech Lead после code review проекта. Следуй принципам KISS, DRY, SOLID и best practices Python.

