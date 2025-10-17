# Tasklist: Спринт S3 - API Requirements & Mock Implementation

**Статус**: ✅ Завершено  
**Дата создания**: 2025-10-17  
**Дата завершения**: 2025-10-17

---

## 📋 Описание спринта

Разработка функциональных требований к дашборду статистики диалогов и реализация Mock API для быстрой проверки концепции frontend. Создание архитектуры сборщика статистики с поддержкой Mock и Real реализаций.

**Основная цель**: Подготовить backend API для дашборда статистики с Mock данными, позволяющими начать разработку frontend без ожидания интеграции с реальной БД.

---

## 🎯 Цели спринта

1. Сформировать лаконичные функциональные требования к UI дашборда
2. Спроектировать REST API контракт (KISS - один endpoint)
3. Реализовать архитектуру StatCollector с Mock/Real стратегией
4. Создать Mock реализацию с реалистичными тестовыми данными
5. Настроить автогенерацию API документации (OpenAPI/Swagger)
6. Добавить entrypoint и команды для запуска API сервера

---

## 📊 Структура работ

### 📝 Блок 1: Требования и проектирование

#### Задача 1.1: Сформировать функциональные требования к дашборду
**Приоритет**: 🔴 Критично  
**Сложность**: Средняя  
**Оценка**: 3 часа

**Цель**: Определить минимальный набор метрик и визуализаций для дашборда статистики диалогов.

**Что нужно сделать**:
- [x] Проанализировать существующую БД схему (users, messages, user_settings)
- [x] Определить ключевые метрики для отображения:
  - Общая статистика (всего пользователей, сообщений, активных диалогов)
  - Временные метрики (сообщения за период, новые пользователи)
  - Топ активных пользователей
  - Распределение по времени суток/дням недели
- [x] Описать UI компоненты дашборда:
  - Cards с основными метриками
  - Timeline график активности
  - Таблица топ пользователей
  - Фильтры по периодам (день, неделя, месяц, всё время)
- [x] Создать документ `docs/frontend/dashboard-requirements.md`
- [x] Определить минимальный датасет для Mock API

**Файлы для создания**:
- `docs/frontend/dashboard-requirements.md` (новый)

**Критерии приемки**:
- Документ содержит полный список метрик
- UI компоненты описаны с референсами
- Требования соответствуют принципу KISS
- Все метрики можно получить из существующей БД схемы

---

#### Задача 1.2: Спроектировать REST API контракт
**Приоритет**: 🔴 Критично  
**Сложность**: Средняя  
**Оценка**: 4 часа

**Цель**: Разработать минималистичный API контракт с единым endpoint для статистики.

**Что нужно сделать**:
- [x] Спроектировать endpoint `GET /stats`
- [x] Определить query параметры:
  - `period` (обязательно): `day`, `week`, `month`
- [x] Спроектировать Response Schema (JSON):
  ```json
  {
    "summary": {
      "total_dialogs": int,
      "active_users": int,
      "avg_dialog_length": float
    },
    "activity_timeline": [
      {
        "timestamp": "2025-10-17T10:00:00Z",
        "message_count": 150,
        "active_users": 45
      }
    ],
    "recent_dialogs": [
      {
        "dialog_id": "uuid",
        "user_id": 123,
        "message_count": 25,
        "last_activity": "2025-10-17T10:00:00Z",
        "duration_minutes": 120
      }
    ],
    "top_users": [
      {
        "user_id": 123,
        "username": "user123",
        "message_count": 89,
        "dialog_count": 15,
        "last_activity": "2025-10-17T10:00:00Z"
      }
    ]
  }
  ```
- [x] Создать dataclasses для типизации (Python):
  ```python
  @dataclass
  class Summary:
      total_dialogs: int
      active_users: int
      avg_dialog_length: float
  
  @dataclass
  class ActivityPoint:
      timestamp: datetime
      message_count: int
      active_users: int
  
  @dataclass
  class RecentDialog:
      dialog_id: str
      user_id: int
      message_count: int
      last_activity: datetime
      duration_minutes: int
  
  @dataclass
  class TopUser:
      user_id: int
      username: str
      message_count: int
      dialog_count: int
      last_activity: datetime
  
  @dataclass
  class StatsResponse:
      summary: Summary
      activity_timeline: list[ActivityPoint]
      recent_dialogs: list[RecentDialog]
      top_users: list[TopUser]
  ```
- [x] Определить Error Responses (400, 500)
- [x] Создать документ `docs/api/stats-api-contract.md`
- [x] Добавить примеры запросов/ответов для всех периодов

**Файлы для создания**:
- `docs/api/stats-api-contract.md` (новый)

**Критерии приемки**:
- API контракт следует REST best practices
- Response schema покрывает все требования к дашборду
- Документация содержит примеры использования
- Контракт согласован с требованиями из задачи 1.1

---

### 🏗️ Блок 2: Архитектура StatCollector

#### Задача 2.1: Спроектировать интерфейс StatCollector
**Приоритет**: 🔴 Критично  
**Сложность**: Средняя  
**Оценка**: 3 часа

**Цель**: Создать абстрактный интерфейс для сборщиков статистики с поддержкой Mock и Real реализаций.

**Что нужно сделать**:
- [x] Создать `backend/api/src/__init__.py`
- [x] Создать `backend/api/src/stats/__init__.py`
- [x] Создать `backend/api/src/stats/collector.py` с абстрактным классом `StatCollector`
- [x] Определить интерфейс:
  ```python
  from abc import ABC, abstractmethod
  from dataclasses import dataclass
  from datetime import datetime
  
  class StatCollector(ABC):
      @abstractmethod
      async def get_stats(self, period: str) -> dict:
          """
          Получить статистику за указанный период.
          
          Args:
              period: Период для статистики ('day', 'week', 'month')
              
          Returns:
              Словарь со статистикой
              
          Raises:
              ValueError: Если период невалиден
          """
          pass
  ```
- [x] Добавить dataclasses для типизации в `backend/api/src/stats/models.py`:
  - `Summary` (всего диалогов, активных пользователей, средняя длина)
  - `ActivityPoint` (точка на графике активности)
  - `RecentDialog` (последний диалог с метаданными)
  - `TopUser` (топ пользователь)
  - `StatsResponse` (root model)
- [x] Создать `backend/api/src/stats/models.py` с dataclasses
- [x] Добавить docstrings и type hints
- [x] Добавить валидацию периода (enum или literal type)

**Файлы для создания**:
- `backend/api/src/__init__.py` (новый)
- `backend/api/src/stats/__init__.py` (новый)
- `backend/api/src/stats/collector.py` (новый)
- `backend/api/src/stats/models.py` (новый)

**Критерии приемки**:
- Интерфейс `StatCollector` четко определен
- Pydantic модели валидируют все поля
- Код следует принципам SOLID (Interface Segregation)
- Type hints для всех методов и полей
- Docstrings описывают назначение и параметры

---

#### Задача 2.2: Реализовать Mock StatCollector
**Приоритет**: 🔴 Критично  
**Сложность**: Средняя  
**Оценка**: 5 часов

**Цель**: Создать Mock реализацию StatCollector, генерирующую реалистичные тестовые данные.

**Что нужно сделать**:
- [x] Создать `backend/api/src/stats/mock_collector.py`
- [x] Реализовать класс `MockStatCollector(StatCollector)`
- [x] Реализовать генерацию реалистичных данных:
  - Summary: всего диалогов (100-500), активных пользователей (50-200), средняя длина диалога (10-30 сообщений)
  - Activity Timeline: почасовые/дневные данные в зависимости от периода с естественными вариациями
  - Recent Dialogs: 10-20 последних диалогов с метаданными (ID, пользователь, длина, длительность)
  - Top Users: 10-15 пользователей с различной активностью (количество диалогов и сообщений)
- [x] Добавить логику фильтрации по периодам:
  - `day`: почасовые данные за последние 24 часа
  - `week`: дневные данные за последние 7 дней
  - `month`: дневные данные за последние 30 дней
- [x] Использовать `random` с фиксированным seed для воспроизводимости
- [x] Добавить логирование генерации данных
- [x] Написать unit-тесты для Mock реализации (3 теста для разных периодов)

**Файлы для создания**:
- `backend/api/src/stats/mock_collector.py` (новый)
- `backend/api/tests/__init__.py` (новый)
- `backend/api/tests/test_mock_collector.py` (новый)

**Пример генерации**:
```python
import random
from datetime import datetime, timedelta
from .models import Summary, ActivityPoint, RecentDialog, TopUser, StatsResponse

class MockStatCollector(StatCollector):
    def __init__(self, seed: int = 42):
        self._random = random.Random(seed)
    
    async def get_stats(self, period: str) -> dict:
        """Генерация Mock данных для указанного периода."""
        if period not in ('day', 'week', 'month'):
            raise ValueError(f"Invalid period: {period}")
        
        # Summary
        summary = Summary(
            total_dialogs=self._random.randint(100, 500),
            active_users=self._random.randint(50, 200),
            avg_dialog_length=round(self._random.uniform(10.0, 30.0), 1)
        )
        
        # Activity Timeline (зависит от периода)
        points_count = {'day': 24, 'week': 7, 'month': 30}[period]
        activity_timeline = [
            ActivityPoint(
                timestamp=datetime.now() - timedelta(hours=i if period == 'day' else 0, days=0 if period == 'day' else i),
                message_count=self._random.randint(50, 200),
                active_users=self._random.randint(10, 50)
            )
            for i in range(points_count)
        ]
        
        # Recent Dialogs
        recent_dialogs = [
            RecentDialog(
                dialog_id=f"dialog-{i}",
                user_id=self._random.randint(1000, 9999),
                message_count=self._random.randint(5, 50),
                last_activity=datetime.now() - timedelta(hours=i),
                duration_minutes=self._random.randint(10, 180)
            )
            for i in range(15)
        ]
        
        # Top Users
        top_users = [
            TopUser(
                user_id=self._random.randint(1000, 9999),
                username=f"user{i}",
                message_count=self._random.randint(50, 300),
                dialog_count=self._random.randint(5, 50),
                last_activity=datetime.now() - timedelta(days=i)
            )
            for i in range(10)
        ]
        
        return StatsResponse(
            summary=summary,
            activity_timeline=activity_timeline,
            recent_dialogs=recent_dialogs,
            top_users=top_users
        )
```

**Критерии приемки**:
- Mock генерирует реалистичные данные
- Поддерживаются все периоды фильтрации
- Данные воспроизводимы (фиксированный seed)
- Тесты покрывают все сценарии (разные периоды)
- Coverage >= 80%

---

### 🚀 Блок 3: API Server Implementation

#### Задача 3.1: Создать FastAPI приложение
**Приоритет**: 🔴 Критично  
**Сложность**: Средняя  
**Оценка**: 4 часа

**Цель**: Реализовать REST API сервер на FastAPI с поддержкой OpenAPI документации.

**Что нужно сделать**:
- [x] Добавить зависимости в `backend/api/pyproject.toml`:
  - `fastapi`
  - `uvicorn[standard]`
  - `pydantic`
  - `pydantic-settings`
- [x] Создать `backend/api/src/config.py` с конфигурацией API:
  - `API_HOST`, `API_PORT`
  - `API_VERSION`
  - `STAT_COLLECTOR_TYPE` (mock/real)
  - `CORS_ORIGINS`
- [x] Создать `backend/api/src/app.py` с FastAPI приложением:
  - Настроить CORS
  - Настроить OpenAPI metadata
  - Добавить healthcheck endpoint (`GET /health`)
  - Подключить роутер для stats
- [x] Создать `backend/api/src/routers/__init__.py`
- [x] Создать `backend/api/src/routers/stats.py` с endpoints:
  - `GET /stats` (единственный endpoint)
- [x] Добавить dependency injection для StatCollector
- [x] Настроить логирование запросов

**Файлы для создания**:
- `backend/api/pyproject.toml` (новый)
- `backend/api/src/config.py` (новый)
- `backend/api/src/app.py` (новый)
- `backend/api/src/routers/__init__.py` (новый)
- `backend/api/src/routers/stats.py` (новый)

**Пример кода**:
```python
# backend/api/src/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI TG Bot Stats API",
    version="1.0.0",
    description="API для получения статистики диалогов"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**Критерии приемки**:
- FastAPI приложение запускается без ошибок
- OpenAPI документация доступна на `/docs`
- Healthcheck endpoint работает
- CORS настроен корректно
- Логирование работает

---

#### Задача 3.2: Реализовать Stats Router
**Приоритет**: 🔴 Критично  
**Сложность**: Средняя  
**Оценка**: 3 часа

**Цель**: Создать роутер для stats endpoints с валидацией и обработкой ошибок.

**Что нужно сделать**:
- [x] Реализовать `GET /stats` endpoint:
  - Query параметр: `period` (обязательный, enum: 'day', 'week', 'month')
  - Response: `StatsResponse` модель
  - Валидация параметра period
- [x] Добавить обработку ошибок:
  - 400 Bad Request (невалидный period)
  - 500 Internal Server Error
- [x] Реализовать dependency для получения StatCollector:
  ```python
  from typing import Literal
  
  async def get_stat_collector() -> StatCollector:
      if config.STAT_COLLECTOR_TYPE == "mock":
          return MockStatCollector()
      else:
          # В будущем - RealStatCollector
          raise NotImplementedError("Real collector not implemented yet")
  
  @router.get("/stats")
  async def get_stats(
      period: Literal["day", "week", "month"],
      collector: StatCollector = Depends(get_stat_collector)
  ):
      """Получить статистику за указанный период."""
      return await collector.get_stats(period)
  ```
- [x] Добавить OpenAPI описания и примеры для каждого периода
- [x] Написать интеграционные тесты для endpoint (3 теста для разных периодов)

**Файлы для изменения**:
- `backend/api/src/routers/stats.py` - реализация роутера
- `backend/api/tests/test_stats_router.py` (новый) - тесты

**Критерии приемки**:
- Endpoint возвращает корректные данные
- Валидация параметров работает
- Обработка ошибок корректна
- OpenAPI документация актуальна
- Тесты покрывают все сценарии

---

### 🔧 Блок 4: Entrypoint и автоматизация

#### Задача 4.1: Создать entrypoint для API сервера
**Приоритет**: 🔴 Критично  
**Сложность**: Низкая  
**Оценка**: 2 часа

**Цель**: Создать отдельную точку входа для запуска API сервера (не main.py).

**Что нужно сделать**:
- [x] Создать `backend/api/run_api.py` (отдельный entrypoint):
  - Загрузка конфигурации из `.env`
  - Настройка логирования
  - Запуск uvicorn сервера
  - Обработка сигналов (graceful shutdown)
  - Пример кода:
  ```python
  import uvicorn
  import logging
  from src.config import config
  
  if __name__ == "__main__":
      logging.basicConfig(
          level=logging.INFO,
          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      )
      
      uvicorn.run(
          "src.app:app",
          host=config.API_HOST,
          port=config.API_PORT,
          reload=False,
          log_level=config.LOG_LEVEL.lower()
      )
  ```
- [x] Создать `backend/api/.env.example` с примером конфигурации:
  ```env
  API_HOST=0.0.0.0
  API_PORT=8000
  API_VERSION=v1
  STAT_COLLECTOR_TYPE=mock
  CORS_ORIGINS=["http://localhost:3000"]
  LOG_LEVEL=INFO
  ```
- [x] Добавить README для API в `backend/api/README.md`:
  - Описание API
  - Инструкция по запуску
  - Примеры использования
  - Ссылка на документацию

**Файлы для создания**:
- `backend/api/run_api.py` (новый, отдельный entrypoint)
- `backend/api/.env.example` (новый)
- `backend/api/README.md` (новый)

**Критерии приемки**:
- API сервер запускается через `python run_api.py`
- Конфигурация загружается из `.env`
- Логирование работает корректно
- README содержит полную инструкцию
- Entrypoint отделен от основного приложения

---

#### Задача 4.2: Добавить команды в Makefile
**Приоритет**: 🔴 Критично  
**Сложность**: Низкая  
**Оценка**: 2 часа

**Цель**: Автоматизировать запуск и тестирование API через Makefile.

**Что нужно сделать**:
- [x] Добавить команды в корневой `Makefile`:
  ```makefile
  # API команды
  .PHONY: api-install
  api-install:
      @echo "Установка зависимостей для API..."
      cd backend/api && & "$(USERPROFILE)\.local\bin\uv.exe" sync
  
  .PHONY: api-run
  api-run:
      @echo "Запуск API сервера..."
      cd backend/api && & "$(USERPROFILE)\.local\bin\uv.exe" run python run_api.py
  
  .PHONY: api-dev
  api-dev:
      @echo "Запуск API в dev режиме с hot-reload..."
      cd backend/api && & "$(USERPROFILE)\.local\bin\uv.exe" run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
  
  .PHONY: api-test
  api-test:
      @echo "Запуск тестов API..."
      cd backend/api && & "$(USERPROFILE)\.local\bin\uv.exe" run pytest -v
  
  .PHONY: api-test-cov
  api-test-cov:
      @echo "Запуск тестов с coverage..."
      cd backend/api && & "$(USERPROFILE)\.local\bin\uv.exe" run pytest --cov=src --cov-report=html --cov-report=term
  
  .PHONY: api-lint
  api-lint:
      @echo "Проверка качества кода API..."
      cd backend/api && & "$(USERPROFILE)\.local\bin\uv.exe" run ruff check src tests
      cd backend/api && & "$(USERPROFILE)\.local\bin\uv.exe" run mypy src
  
  .PHONY: api-format
  api-format:
      @echo "Форматирование кода API..."
      cd backend/api && & "$(USERPROFILE)\.local\bin\uv.exe" run ruff format src tests
  
  .PHONY: api-docs
  api-docs:
      @echo "API документация доступна на: http://localhost:8000/docs"
      @echo "Запустите 'make api-dev' для доступа к документации"
  ```
- [x] Добавить скрипт для тестирования API `scripts/test-api.sh`:
  - Запуск API
  - Проверка healthcheck
  - Тестовый запрос к stats endpoint
  - Вывод результатов
- [x] Обновить корневой `README.md` с инструкциями по API

**Файлы для изменения**:
- `Makefile` - добавить API команды
- `scripts/test-api.sh` (новый) - скрипт тестирования
- `README.md` - обновить с API секцией

**Критерии приемки**:
- Все Makefile команды работают
- Скрипт тестирования успешно проверяет API
- README содержит актуальные инструкции
- Документация легко доступна

---

### 📚 Блок 5: Документация

#### Задача 5.1: Настроить автогенерацию OpenAPI документации
**Приоритет**: 🟡 Средне  
**Сложность**: Низкая  
**Оценка**: 2 часа

**Цель**: Настроить FastAPI для автоматической генерации качественной API документации.

**Что нужно сделать**:
- [x] Улучшить OpenAPI metadata в `app.py`:
  - Подробное описание API
  - Контактная информация
  - Лицензия
  - Теги для группировки endpoints
- [x] Добавить детальные описания для endpoints:
  - Summary и description
  - Примеры запросов
  - Примеры ответов
  - Описание error codes
- [x] Настроить Swagger UI кастомизацию
- [x] Добавить примеры в Pydantic модели (через `Config.json_schema_extra`)
- [x] Экспортировать OpenAPI schema в JSON файл для использования в frontend

**Файлы для изменения**:
- `backend/api/src/app.py` - улучшить metadata
- `backend/api/src/routers/stats.py` - добавить описания
- `backend/api/src/stats/models.py` - примеры в моделях

**Пример**:
```python
from typing import Literal

@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Получить статистику диалогов",
    description="Возвращает агрегированную статистику диалогов за указанный период (day/week/month)",
    responses={
        200: {
            "description": "Успешный ответ",
            "content": {
                "application/json": {
                    "example": {
                        "summary": {
                            "total_dialogs": 234,
                            "active_users": 89,
                            "avg_dialog_length": 15.3
                        },
                        "activity_timeline": [
                            {
                                "timestamp": "2025-10-17T10:00:00Z",
                                "message_count": 150,
                                "active_users": 45
                            }
                        ],
                        "recent_dialogs": [],
                        "top_users": []
                    }
                }
            }
        },
        422: {"description": "Невалидный параметр period"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)
async def get_stats(
    period: Literal["day", "week", "month"],
    collector: StatCollector = Depends(get_stat_collector)
):
    """Получить статистику за указанный период."""
    pass
```

**Критерии приемки**:
- OpenAPI документация полная и информативная
- Swagger UI удобен для использования
- Примеры запросов/ответов актуальны
- Schema экспортируется в JSON

---

#### Задача 5.2: Создать документацию по архитектуре API
**Приоритет**: 🟡 Средне  
**Сложность**: Низкая  
**Оценка**: 2 часа

**Цель**: Документировать архитектурные решения и структуру API проекта.

**Что нужно сделать**:
- [x] Создать `docs/api/architecture.md`:
  - Общая архитектура API
  - Диаграмма компонентов (Mermaid)
  - StatCollector pattern (Strategy)
  - Dependency Injection
- [x] Создать `docs/api/mock-collector.md`:
  - Описание Mock реализации
  - Алгоритм генерации данных
  - Примеры использования
- [x] Обновить `docs/roadmap.md`:
  - Отметить прогресс спринта S3
  - Добавить ссылку на план спринта
- [x] Создать диаграммы:
  - Структура API проекта
  - Flow запроса к stats endpoint
  - StatCollector Strategy pattern

**Файлы для создания**:
- `docs/api/architecture.md` (новый)
- `docs/api/mock-collector.md` (новый)

**Критерии приемки**:
- Документация описывает архитектуру понятно
- Диаграммы визуализируют структуру
- Примеры кода актуальны
- Roadmap обновлен

---

## 🧪 Тестирование спринта

После завершения всех задач необходимо провести:

1. **Unit тесты**: `make api-test` - все тесты должны проходить
2. **Coverage**: `make api-test-cov` - должен быть >= 80%
3. **Lint и type checking**: добавить в Makefile и проверить
4. **Ручное тестирование**:
   - [x] Запустить API: `make api-dev`
   - [x] Открыть Swagger UI: http://localhost:8000/docs
   - [x] Проверить healthcheck endpoint: `GET /health`
   - [x] Выполнить запросы к `/stats` с разными периодами:
     - `GET /stats?period=day`
     - `GET /stats?period=week`
     - `GET /stats?period=month`
   - [x] Проверить response schema соответствует спецификации:
     - summary (total_dialogs, active_users, avg_dialog_length)
     - activity_timeline (массив с timestamp, message_count, active_users)
     - recent_dialogs (массив с метаданными диалогов)
     - top_users (массив топ пользователей)
   - [x] Проверить обработку невалидных параметров:
     - Запрос без параметра period (ошибка 422)
     - Запрос с невалидным period=invalid (ошибка 422)
5. **Integration тестирование**:
   - [x] Запустить скрипт: `bash scripts/test-api.sh`
   - [x] Проверить что все endpoints отвечают корректно
   - [x] Проверить CORS headers

---

## 📈 Метрики успеха

1. **Функциональность**:
   - API сервер запускается и работает стабильно
   - Все endpoints возвращают корректные данные
   - OpenAPI документация полная и актуальная

2. **Качество кода**:
   - Coverage >= 80% для API кода
   - 0 ошибок линтера и mypy
   - Код следует принципам SOLID и KISS

3. **Документация**:
   - Функциональные требования к дашборду определены
   - API контракт четко документирован
   - Архитектура описана с диаграммами

4. **Автоматизация**:
   - Makefile команды работают
   - Скрипты тестирования проходят успешно

---

## 📝 Примечания

### Технологический стек API

- **Framework**: FastAPI (высокая производительность, автогенерация OpenAPI)
- **Validation**: Pydantic (type-safe модели)
- **ASGI Server**: Uvicorn (production-ready)
- **Testing**: pytest + httpx (async тестирование)

### Принципы разработки

- Следовать принципам из `docs/vision.md` и `.cursor/rules/conventions.mdc`
- KISS - минимальный API контракт
- Strategy Pattern для StatCollector (легкое переключение Mock/Real)
- Dependency Injection для тестируемости
- Type hints и docstrings обязательны

### Структура backend/api проекта

```
backend/api/
├── src/
│   ├── __init__.py
│   ├── app.py               # FastAPI приложение
│   ├── config.py            # Конфигурация (Pydantic Settings)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── stats.py         # Stats router (GET /stats)
│   └── stats/
│       ├── __init__.py
│       ├── collector.py     # Абстрактный StatCollector
│       ├── models.py        # Dataclasses для типизации
│       └── mock_collector.py # Mock реализация
├── tests/
│   ├── __init__.py
│   ├── test_mock_collector.py  # Unit-тесты Mock
│   └── test_stats_router.py    # Integration-тесты API
├── run_api.py               # Entrypoint для запуска API
├── pyproject.toml
├── .env.example
└── README.md
```

**Ключевые моменты**:
- `run_api.py` - отдельный entrypoint (не main.py)
- `src/app.py` - FastAPI приложение с роутерами
- `src/stats/models.py` - dataclasses (не Pydantic модели)
- Один endpoint: `GET /stats?period={day|week|month}`

---

## ✅ Чеклист завершения спринта

- [x] Все задачи из Блока 1 (Требования и проектирование) завершены
- [x] Все задачи из Блока 2 (Архитектура StatCollector) завершены
- [x] Все задачи из Блока 3 (API Server) завершены
- [x] Все задачи из Блока 4 (Entrypoint и автоматизация) завершены
- [x] Все задачи из Блока 5 (Документация) завершены
- [x] Coverage >= 80%
- [x] Все тесты проходят
- [x] OpenAPI документация полная и актуальна
- [x] Makefile команды работают
- [x] Ручное тестирование пройдено
- [x] Документация обновлена
- [x] README.md актуализирован
- [x] Roadmap обновлен со ссылкой на план спринта

---

**Статус обновления**: 2025-10-17 - Спринт завершен, все задачи выполнены, чеклисты обновлены


