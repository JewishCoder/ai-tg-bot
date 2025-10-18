# 📋 Tasklist: Спринт S9 - Production Readiness & Observability

**Статус:** 🚧 В процессе (Блок 1 завершен ✅)  
**Дата начала:** 2025-10-18  
**Дата завершения:** TBD

---

## 🎯 Цель спринта

Подготовить систему к production deployment на основе результатов **code review-0002**. Устранить найденные проблемы (0 критических, 4 важных, 4 незначительных) и реализовать рекомендации по безопасности, observability и производительности.

**Референс:** [review-0002.md](../reviews/review-0002.md)

---

## 📊 Общий прогресс

**Блоки работ:**
- [x] Блок 1: Security Hardening (5 задач) ✅
- [ ] Блок 2: Observability (4 задачи)
- [ ] Блок 3: Performance Optimization (2 задачи)
- [ ] Блок 4: Testing & Quality (3 задачи)
- [ ] Блок 5: DevOps Improvements (3 задачи)
- [ ] Блок 6: Documentation (3 задачи)

**Всего задач:** 20  
**Выполнено:** 5  
**Осталось:** 15

---

## 🔒 Блок 1: Security Hardening (High Priority)

**Цель:** Устранить проблемы безопасности, найденные в code review (#1, #2)

### Задача 1.1: Authentication для Stats API
**Приоритет:** ⭐ High  
**Статус:** ✅ Завершено (2025-10-18)  
**Референс:** review-0002.md - Задача #1

**Описание:**
Stats API не имеет authentication/authorization. Нужно добавить защиту endpoints.

**Технические требования:**
- [x] Выбрать механизм auth: Basic Auth или JWT (выбран Basic Auth с БД)
- [x] Добавить FastAPI dependency для проверки credentials
- [x] Защитить endpoint `/api/v1/stats`
- [x] Добавить конфигурацию credentials через `.env` (credentials в PostgreSQL через ApiUser)
- [x] Обновить API client в frontend (добавить Authorization header)
- [x] Unit тесты: успешная auth, неуспешная auth (401)
- [x] Integration тест: полный workflow с auth

**Примерная реализация:**
```python
# backend/api/src/routers/stats.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
    config: Config = Depends(get_config)
) -> None:
    """Verify Basic Auth credentials."""
    if (
        credentials.username != config.stats_api_username
        or credentials.password != config.stats_api_password.get_secret_value()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

@router.get("/api/v1/stats", dependencies=[Depends(verify_credentials)])
async def get_stats(...):
    ...
```

**Ожидаемый результат:**
- ✅ Stats API защищен Basic Auth (через БД с ApiUser модель)
- ✅ Credentials хранятся в PostgreSQL
- ✅ Frontend корректно авторизуется
- ✅ Тесты покрывают auth workflow

---

### Задача 1.2: Rate Limiting для Stats API
**Приоритет:** ⭐ High  
**Статус:** ✅ Завершено (2025-10-18)  
**Референс:** review-0002.md - Задача #2

**Описание:**
Нет защиты от DDoS или abuse для Stats API endpoint. Нужно добавить rate limiting.

**Технические требования:**
- [x] Добавить `slowapi` в зависимости
- [x] Создать `src/middlewares/rate_limit.py` с настройкой Limiter
- [x] Применить rate limit к `/api/v1/stats` endpoint
- [x] Настроить лимиты через конфигурацию (STATS_API_RATE_LIMIT="10/minute")
- [x] Добавить custom error handler для 429 Too Many Requests
- [x] Unit тесты: нормальные запросы, превышение лимита (429)
- [x] Документировать rate limits в API docs (OpenAPI)

**Примерная реализация:**
```python
# backend/api/src/middlewares/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# backend/api/src/app.py
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."}
    )

# backend/api/src/routers/stats.py
@router.get("/api/v1/stats")
@limiter.limit(lambda: get_config().stats_api_rate_limit)
async def get_stats(...):
    ...
```

**Ожидаемый результат:**
- ✅ Rate limiting работает для Stats API (10/minute)
- ✅ Лимиты настраиваются через конфигурацию
- ✅ Понятные ошибки при превышении лимита (429)
- ✅ Тесты проверяют rate limiting

---

### Задача 1.3: CORS настройки для API
**Приоритет:** 🟡 Medium  
**Статус:** ✅ Завершено (2025-10-18)  
**Референс:** review-0002.md - Рекомендация #2.2

**Описание:**
Настроить CORS middleware с whitelist origins для production.

**Технические требования:**
- [x] Добавить CORS middleware в `backend/api/src/app.py`
- [x] Настроить allowed origins через конфигурацию (CORS_ORIGINS)
- [x] Ограничить allowed methods только нужными (GET, POST, OPTIONS)
- [x] Добавить credentials support (для Basic Auth)
- [x] Unit тесты: preflight OPTIONS, CORS headers
- [x] Документировать CORS настройки

**Примерная реализация:**
```python
# backend/api/src/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allowed_origins,  # Не "*" для production!
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],  # Только нужные
    allow_headers=["*"],
)
```

**Ожидаемый результат:**
- ✅ CORS настроен с whitelist origins
- ✅ Production-safe конфигурация с validator
- ✅ Тесты проверяют CORS headers
- ✅ Credentials support для Basic Auth

---

### Задача 1.4: User Registration для Stats API
**Приоритет:** ⭐ High  
**Статус:** ✅ Завершено (2025-10-18)  

**Описание:**
Реализовать механизм регистрации пользователей для Stats API Dashboard на основе админского токена. Только пользователи с правильным admin token смогут создать аккаунт для доступа к дашборду.

**Технические требования:**
- [x] Добавить конфигурацию в `backend/api/src/config.py` (ADMIN_REGISTRATION_TOKEN)
- [x] Создать модель ApiUser в `backend/bot/src/models.py` (модели централизованы в Bot)
- [x] Создать `backend/api/src/routers/auth.py` с endpoint `/api/v1/auth/register`
- [x] Реализовать `/api/v1/auth/register` с проверкой admin token
- [x] Обновить Задачу 1.1 для проверки credentials из БД через ApiUser
- [x] Создать Alembic миграцию для таблицы `api_users`
- [x] Добавить `passlib[bcrypt]` и `bcrypt>=4.0.0,<5.0.0` в зависимости (Bot и API)
- [x] Unit тесты:
  - Успешная регистрация с правильным admin token
  - Отказ при неправильном admin token (403)
  - Отказ при дубликате username (400)
  - Проверка что пароль хешируется
- [x] Integration с Basic Auth из Задачи 1.1
- [x] Frontend integration (config/api.ts, lib/api.ts с Basic Auth)

**Примерная структура:**
```
backend/api/src/
├── models.py              # + User model
├── routers/
│   ├── auth.py            # NEW: authentication endpoints
│   └── stats.py           # UPDATED: проверка через DB users
└── utils/
    └── auth.py            # NEW: password hashing, user verification
```

**Workflow:**
1. Админ устанавливает `ADMIN_REGISTRATION_TOKEN` в `.env`
2. Новый аналитик получает admin token от админа
3. Аналитик регистрируется: `POST /api/v1/auth/register` с admin token
4. После регистрации аналитик использует свой username/password для доступа к `/api/v1/stats`

**Ожидаемый результат:**
- ✅ User registration endpoint работает (`POST /api/v1/auth/register`)
- ✅ Admin token валидируется (ADMIN_REGISTRATION_TOKEN)
- ✅ Пароли хешируются (bcrypt 4.x)
- ✅ Credentials хранятся в PostgreSQL (таблица api_users)
- ✅ Integration с Basic Auth из Задачи 1.1
- ✅ Тесты покрывают registration flow
- ✅ Модели централизованы в Bot сервисе, копируются в API при build

---

### Задача 1.5: Документация Secrets Management
**Приоритет:** 🟢 Low  
**Статус:** ✅ Завершено (2025-10-18)  
**Референс:** review-0002.md - Рекомендация #2.1

**Описание:**
Создать документацию по управлению секретами для production deployment.

**Технические требования:**
- [x] Создать `docs/guides/secrets-management.md`
- [x] Описать варианты:
  - HashiCorp Vault
  - AWS Secrets Manager
  - Kubernetes Secrets
- [x] Рекомендации для каждого варианта
- [x] Примеры интеграции с текущей конфигурацией
- [x] Best practices: ротация ключей, минимальные права доступа

**Ожидаемый результат:**
- ✅ Comprehensive guide по secrets management (docs/guides/secrets-management.md)
- ✅ Примеры для популярных платформ (Vault, AWS, K8s)
- ✅ Рекомендации для production

---

## 📈 Блок 2: Observability (High Priority)

**Цель:** Добавить metrics экспорт и улучшить логирование для production мониторинга

### Задача 2.1: Улучшенное логирование Real Collector
**Приоритет:** ⭐ High  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Задача #3

**Описание:**
Real Collector выполняет сложные SQL запросы, но не логирует время выполнения и не предупреждает о медленных запросах.

**Технические требования:**
- [ ] Добавить измерение времени выполнения для всех методов:
  - `get_stats()`
  - `_get_summary_stats()`
  - `_get_activity_stats()`
  - `_get_recent_dialogs()`
  - `_get_top_users()`
- [ ] Логировать время выполнения каждого запроса (DEBUG level)
- [ ] Предупреждать о медленных запросах > 1s (WARNING level):
  ```python
  if elapsed > 1.0:
      logger.warning(f"Slow query in {method_name}: {elapsed:.2f}s, period={period}")
  ```
- [ ] Добавить structured logging с контекстом (period, user_id если применимо)
- [ ] Unit тесты: проверить логирование для fast и slow queries

**Примерная реализация:**
```python
# backend/api/src/stats/real_collector.py
import time
import logging

logger = logging.getLogger(__name__)

async def get_stats(self, period: PeriodEnum) -> DialogStats:
    """Collect real stats from database."""
    start_time = time.time()
    
    logger.info(f"Fetching stats for period={period.value}")
    
    async with self.db.session() as session:
        summary = await self._get_summary_stats(session, period)
        # ... other calls
        
    elapsed = time.time() - start_time
    
    if elapsed > 1.0:
        logger.warning(f"Slow stats collection: {elapsed:.2f}s for period={period.value}")
    else:
        logger.debug(f"Stats collected in {elapsed:.2f}s for period={period.value}")
    
    return result

async def _get_summary_stats(self, session, period):
    """Get summary statistics with query timing."""
    start_time = time.time()
    
    # Execute query
    result = await session.execute(stmt)
    
    elapsed = time.time() - start_time
    if elapsed > 0.5:
        logger.warning(f"Slow summary query: {elapsed:.2f}s")
    else:
        logger.debug(f"Summary query: {elapsed:.2f}s")
    
    return result
```

**Ожидаемый результат:**
- ✅ Все SQL запросы логируют время выполнения
- ✅ Предупреждения о медленных запросах
- ✅ Structured logging с контекстом
- ✅ Тесты проверяют логирование

---

### Задача 2.2: Prometheus Metrics для Bot
**Приоритет:** ⭐ High  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Рекомендация #1.1

**Описание:**
Добавить Prometheus metrics экспорт для Bot сервиса.

**Технические требования:**
- [ ] Добавить `prometheus-client` в зависимости:
  ```bash
  cd backend/bot
  uv add prometheus-client
  ```
- [ ] Создать `src/middlewares/metrics.py` с metrics definitions
- [ ] Добавить `/metrics` endpoint в Bot (через aiogram или отдельный HTTP server)
- [ ] Реализовать metrics:
  - `llm_request_duration_seconds` (Histogram) - latency LLM запросов
  - `llm_requests_total` (Counter) - количество LLM запросов
  - `llm_errors_total` (Counter) - количество ошибок LLM
  - `llm_fallback_used_total` (Counter) - использование fallback модели
  - `telegram_messages_received_total` (Counter) - полученные сообщения
  - `telegram_messages_sent_total` (Counter) - отправленные сообщения
- [ ] Интегрировать в `llm_client.py` для измерения запросов
- [ ] Unit тесты: проверить metrics increment
- [ ] Документировать metrics в `docs/backend/bot/api/metrics.md`

**Примерная реализация:**
```python
# backend/bot/src/middlewares/metrics.py
from prometheus_client import Counter, Histogram

llm_request_duration = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['model', 'status']
)

llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model']
)

llm_errors_total = Counter(
    'llm_errors_total',
    'Total LLM errors',
    ['model', 'error_type']
)

llm_fallback_used_total = Counter(
    'llm_fallback_used_total',
    'Total fallback model uses'
)

# backend/bot/src/llm_client.py
from src.middlewares.metrics import (
    llm_request_duration,
    llm_requests_total,
    llm_errors_total,
    llm_fallback_used_total
)

async def generate_response(self, messages, user_id):
    llm_requests_total.labels(model=self.config.openrouter_model).inc()
    
    with llm_request_duration.labels(
        model=self.config.openrouter_model,
        status='success'
    ).time():
        try:
            response = await self._call_llm(messages, model=self.config.openrouter_model)
        except Exception as e:
            llm_errors_total.labels(
                model=self.config.openrouter_model,
                error_type=type(e).__name__
            ).inc()
            
            if self._should_try_fallback(e):
                llm_fallback_used_total.inc()
                response = await self._call_fallback(messages)
```

**Ожидаемый результат:**
- ✅ Prometheus metrics экспортируются на `/metrics`
- ✅ Metrics покрывают критичные операции
- ✅ Labels для детализации (model, status, error_type)
- ✅ Документация metrics

---

### Задача 2.3: Prometheus Metrics для API
**Приоритет:** ⭐ High  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Рекомендация #1.1

**Описание:**
Добавить Prometheus metrics экспорт для API сервиса.

**Технические требования:**
- [ ] Добавить `prometheus-fastapi-instrumentator` в зависимости:
  ```bash
  cd backend/api
  uv add prometheus-fastapi-instrumentator
  ```
- [ ] Настроить instrumentator в `src/app.py`
- [ ] Добавить custom metrics:
  - `database_query_duration_seconds` (Histogram) - latency DB запросов
  - `database_connection_pool_size` (Gauge) - размер connection pool
  - `database_connection_pool_available` (Gauge) - доступные connections
  - `stats_api_requests_total` (Counter) - запросы к stats API
- [ ] Интегрировать в `stats/real_collector.py` для измерения запросов
- [ ] Unit тесты: проверить metrics
- [ ] Документировать metrics в `docs/backend/api/metrics.md`

**Примерная реализация:**
```python
# backend/api/src/app.py
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")

# backend/api/src/stats/real_collector.py
from prometheus_client import Histogram

db_query_duration = Histogram(
    'database_query_duration_seconds',
    'Database query duration',
    ['query_name']
)

async def _get_summary_stats(self, session, period):
    with db_query_duration.labels(query_name='summary_stats').time():
        result = await session.execute(stmt)
    return result
```

**Ожидаемый результат:**
- ✅ FastAPI metrics из коробки (request latency, etc)
- ✅ Custom metrics для DB и stats
- ✅ Metrics экспортируются на `/metrics`
- ✅ Документация metrics

---

### Задача 2.4: Enhanced Health Check Endpoints
**Приоритет:** 🟡 Medium  
**Статус:** ⏳ Планируется  

**Описание:**
Расширить health check endpoints детальной информацией о состоянии сервисов.

**Технические требования:**
- [ ] Улучшить `/health` endpoint в Bot:
  - Проверка подключения к PostgreSQL
  - Проверка доступности OpenRouter API (опционально)
  - Статус rate limiter
  - Uptime
- [ ] Улучшить `/health` endpoint в API:
  - Проверка подключения к PostgreSQL
  - Connection pool stats
  - Uptime
- [ ] Добавить `/ready` endpoint (readiness probe для Kubernetes)
- [ ] Unit и integration тесты для health checks
- [ ] Документировать endpoints

**Примерная реализация:**
```python
# backend/bot/src/main.py
from datetime import datetime

start_time = datetime.utcnow()

@app.get("/health")
async def health_check():
    """Detailed health check."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    # Check database
    db_healthy = await check_database()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "uptime_seconds": uptime,
        "database": "connected" if db_healthy else "disconnected",
        "rate_limiter": "active"
    }

async def check_database() -> bool:
    """Check database connectivity."""
    try:
        async with database.session() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
```

**Ожидаемый результат:**
- ✅ Health checks возвращают детальную информацию
- ✅ Separate readiness probes
- ✅ Тесты покрывают health checks

---

## ⚡ Блок 3: Performance Optimization (Medium Priority)

**Цель:** Оптимизировать производительность DB запросов и connection pooling

### Задача 3.1: Database Query Optimization
**Приоритет:** 🟡 Medium  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Рекомендация #3.1

**Описание:**
Добавить EXPLAIN ANALYZE для сложных запросов и query performance logging в development mode.

**Технические требования:**
- [ ] Добавить флаг в конфигурацию API:
  ```python
  enable_query_analysis: bool = Field(default=False, description="Enable EXPLAIN ANALYZE")
  ```
- [ ] Создать `backend/api/src/utils/query_analyzer.py` с функцией explain
- [ ] Интегрировать в Real Collector для всех сложных запросов
- [ ] Логировать query plans (DEBUG level) когда `enable_query_analysis=True`
- [ ] Документировать как использовать для оптимизации
- [ ] Unit тесты: проверить что analysis включается/выключается

**Примерная реализация:**
```python
# backend/api/src/utils/query_analyzer.py
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def explain_query(session, stmt, config):
    """Run EXPLAIN ANALYZE for a query if enabled."""
    if not config.enable_query_analysis:
        return
    
    # Convert compiled statement to string
    compiled = stmt.compile(compile_kwargs={"literal_binds": True})
    query_str = str(compiled)
    
    # Run EXPLAIN ANALYZE
    explain_stmt = text(f"EXPLAIN ANALYZE {query_str}")
    result = await session.execute(explain_stmt)
    
    plan = "\n".join([row[0] for row in result])
    logger.debug(f"Query plan:\n{plan}")

# backend/api/src/stats/real_collector.py
from src.utils.query_analyzer import explain_query

async def _get_summary_stats(self, session, period):
    stmt = select(...)
    
    # Analyze query in development
    await explain_query(session, stmt, self.config)
    
    # Execute query
    result = await session.execute(stmt)
    return result
```

**Ожидаемый результат:**
- ✅ EXPLAIN ANALYZE доступен для всех сложных запросов
- ✅ Query plans логируются в development mode
- ✅ Документация по использованию для оптимизации
- ✅ Тесты проверяют query analysis

---

### Задача 3.2: Connection Pooling Tuning
**Приоритет:** 🟡 Medium  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Рекомендация #3.2

**Описание:**
Улучшить настройки connection pooling для production workloads.

**Технические требования:**
- [ ] Увеличить `pool_size` и `max_overflow` для production:
  ```python
  # backend/bot/src/database.py
  db_pool_size: int = Field(default=20, description="Connection pool size")
  db_max_overflow: int = Field(default=30, description="Max overflow connections")
  ```
- [ ] Добавить `pool_pre_ping=True` для connection health checks
- [ ] Добавить `pool_recycle=3600` для ротации connections
- [ ] Логировать pool stats (WARNING при > 80% utilization):
  ```python
  pool_usage = engine.pool.size() / (engine.pool.size() + engine.pool.overflow())
  if pool_usage > 0.8:
      logger.warning(f"High pool utilization: {pool_usage:.0%}")
  ```
- [ ] Создать `docs/guides/database-tuning.md` с рекомендациями
- [ ] Документировать рекомендованные настройки для разных нагрузок

**Примерная реализация:**
```python
# backend/bot/src/database.py
class Database:
    def __init__(self, config: Config) -> None:
        self.engine = create_async_engine(
            config.database_url,
            echo=config.db_echo,
            pool_size=config.db_pool_size,       # 20 для production
            max_overflow=config.db_max_overflow, # 30 для production
            pool_pre_ping=True,                  # Health checks
            pool_recycle=3600,                   # 1 hour rotation
        )
    
    async def get_pool_stats(self) -> dict:
        """Get connection pool statistics."""
        pool = self.engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total": pool.size() + pool.overflow()
        }
```

**Ожидаемый результат:**
- ✅ Production-ready pool настройки
- ✅ Pool health checks и ротация
- ✅ Логирование при высокой утилизации
- ✅ Документация с рекомендациями

---

## 🧪 Блок 4: Testing & Quality (Medium Priority)

**Цель:** Улучшить качество тестов и добавить load testing

### Задача 4.1: Рефакторинг тестовых констант
**Приоритет:** 🟢 Low  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Задача #4

**Описание:**
Тестовые токены хардкоджены в фикстурах. Вынести в константы для переиспользования.

**Технические требования:**
- [ ] Создать `backend/bot/tests/constants.py`:
  ```python
  TEST_TELEGRAM_TOKEN = "test_token_123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
  TEST_OPENROUTER_KEY = "test_openrouter_key_abc123"
  TEST_USER_ID = 12345
  TEST_MESSAGE_CONTENT = "Hello, bot!"
  ```
- [ ] Обновить `conftest.py` для использования констант
- [ ] Обновить все тесты для использования констант
- [ ] Аналогично для `backend/api/tests/constants.py`
- [ ] Убедиться что все тесты проходят

**Ожидаемый результат:**
- ✅ Все тестовые константы в одном месте
- ✅ Легко изменить тестовые данные
- ✅ Все тесты проходят

---

### Задача 4.2: Frontend Unit тесты
**Приоритет:** 🟢 Low  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Задача #6

**Описание:**
Добавить unit тесты для недостающих frontend компонентов.

**Технические требования:**
- [ ] Создать `frontend/tests/unit/ActivityChart.test.tsx`:
  - Рендеринг с данными
  - Рендеринг с пустыми данными
  - Проверка legend
  - Responsive behavior
- [ ] Создать `frontend/tests/unit/PeriodFilter.test.tsx`:
  - Рендеринг всех периодов (day, week, month)
  - Клик по периоду вызывает onChange
  - Активный период выделен
- [ ] Создать `frontend/tests/unit/app-sidebar.test.tsx`:
  - Рендеринг navigation items
  - Active state для текущей страницы
  - Mobile toggle behavior
- [ ] Все тесты должны проходить
- [ ] Coverage должен вырасти до >= 80%

**Ожидаемый результат:**
- ✅ Unit тесты для всех основных компонентов
- ✅ Coverage >= 80%
- ✅ Все тесты проходят в CI

---

### Задача 4.3: Load Testing Infrastructure
**Приоритет:** 🟡 Medium  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Рекомендация #4.1

**Описание:**
Настроить load testing infrastructure для Bot и API.

**Технические требования:**
- [ ] Выбрать инструмент: locust или k6
- [ ] Создать `backend/api/scripts/load_test.py` (locust) или `load_test.js` (k6)
- [ ] Сценарии для API:
  - GET /api/v1/stats?period=day (основной)
  - GET /health
  - Rate limiting behavior
- [ ] Сценарии для Bot (опционально, через Telegram API)
- [ ] Создать `docs/guides/load-testing.md` с инструкциями
- [ ] Документировать baseline performance:
  - Requests per second
  - Average latency
  - P95/P99 latency
  - Error rate

**Примерная реализация (locust):**
```python
# backend/api/scripts/load_test.py
from locust import HttpUser, task, between

class StatsAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_stats_day(self):
        self.client.get("/api/v1/stats?period=day", auth=("admin", "password"))
    
    @task(2)
    def get_stats_week(self):
        self.client.get("/api/v1/stats?period=week", auth=("admin", "password"))
    
    @task(1)
    def get_stats_month(self):
        self.client.get("/api/v1/stats?period=month", auth=("admin", "password"))
    
    @task
    def health_check(self):
        self.client.get("/health")
```

**Запуск:**
```bash
cd backend/api
locust -f scripts/load_test.py --host http://localhost:8000
```

**Ожидаемый результат:**
- ✅ Load testing скрипты для API
- ✅ Документированные baseline metrics
- ✅ Инструкции по запуску

---

## 🚀 Блок 5: DevOps Improvements (Low Priority)

**Цель:** Улучшить DevOps практики и deployment процесс

### Задача 5.1: Healthcheck Improvements в docker-compose
**Приоритет:** 🟢 Low  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Задача #5

**Описание:**
Postgres имеет healthcheck, но bot не использует `depends_on` с condition.

**Технические требования:**
- [ ] Обновить `docker-compose.yml`:
  ```yaml
  bot:
    depends_on:
      postgres:
        condition: service_healthy
  
  api:
    depends_on:
      postgres:
        condition: service_healthy
  ```
- [ ] Добавить healthcheck для bot сервиса:
  ```yaml
  bot:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  ```
- [ ] Добавить healthcheck для api сервиса:
  ```yaml
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s
  ```
- [ ] Тестировать что сервисы стартуют в правильном порядке

**Ожидаемый результат:**
- ✅ Сервисы стартуют только после готовности зависимостей
- ✅ Healthchecks для всех сервисов
- ✅ Production-ready docker-compose

---

### Задача 5.2: Production Profiles в docker-compose
**Приоритет:** 🟢 Low  
**Статус:** ⏳ Планируется  

**Описание:**
Добавить production profiles для deployment.

**Технические требования:**
- [ ] Создать `docker-compose.prod.yml` с production overrides:
  - Использовать образы из registry вместо local build
  - Production environment variables
  - Resource limits (CPU, memory)
  - Restart policies
- [ ] Обновить `Makefile` с командами:
  ```makefile
  .PHONY: prod-up
  prod-up:
  	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
  
  .PHONY: prod-down
  prod-down:
  	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
  ```
- [ ] Документировать в `docs/guides/deployment.md`

**Ожидаемый результат:**
- ✅ Separate production configuration
- ✅ Easy deployment commands
- ✅ Документация deployment процесса

---

### Задача 5.3: Graceful Shutdown Improvements
**Приоритет:** 🟢 Low  
**Статус:** ⏳ Планируется  

**Описание:**
Улучшить graceful shutdown для всех сервисов.

**Технические требования:**
- [ ] Убедиться что Bot корректно завершает обработку сообщений:
  - Завершить текущие LLM запросы
  - Закрыть DB connections
  - Flush логи
- [ ] Убедиться что API корректно завершает запросы:
  - Завершить текущие HTTP requests
  - Закрыть DB connections
- [ ] Добавить timeout для shutdown (30s)
- [ ] Логировать shutdown events
- [ ] Unit тесты для graceful shutdown

**Ожидаемый результат:**
- ✅ Нет потери данных при остановке
- ✅ Корректное завершение всех операций
- ✅ Proper cleanup ресурсов

---

## 📚 Блок 6: Documentation (Low Priority)

**Цель:** Улучшить документацию для production deployment и troubleshooting

### Задача 6.1: Архитектурные диаграммы (Mermaid)
**Приоритет:** 🟡 Medium  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Рекомендация #5.1

**Описание:**
Создать архитектурные диаграммы для визуализации системы.

**Технические требования:**
- [ ] Создать `docs/architecture/diagrams.md`
- [ ] **Sequence diagram** для LLM request flow:
  ```mermaid
  sequenceDiagram
    User->>Bot: Send message
    Bot->>Storage: Load history
    Storage->>PostgreSQL: SELECT messages
    PostgreSQL-->>Storage: Messages
    Storage-->>Bot: History
    Bot->>LLMClient: Generate response
    LLMClient->>OpenRouter: API request (primary model)
    alt Success
      OpenRouter-->>LLMClient: Response
    else Error (Rate Limit / API Error)
      LLMClient->>OpenRouter: API request (fallback model)
      OpenRouter-->>LLMClient: Response
    end
    LLMClient-->>Bot: Generated text
    Bot->>Storage: Save messages
    Storage->>PostgreSQL: INSERT messages
    Bot->>User: Send response
  ```
- [ ] **Architecture diagram** для multi-service:
  ```mermaid
  graph TB
    User[Telegram User] --> Bot[Bot Service]
    Admin[Admin] --> Frontend[Frontend Dashboard]
    Frontend --> Nginx[Nginx]
    Nginx --> API[API Service]
    Bot --> PostgreSQL[(PostgreSQL)]
    API --> PostgreSQL
    Bot --> OpenRouter[OpenRouter API]
    
    subgraph "Docker Network"
      Bot
      API
      Frontend
      Nginx
      PostgreSQL
    end
  ```
- [ ] **ER diagram** для database schema:
  ```mermaid
  erDiagram
    USER ||--o{ MESSAGE : creates
    USER ||--|| USER_SETTINGS : has
    USER {
        bigint id PK
        timestamp created_at
        timestamp updated_at
    }
    MESSAGE {
        uuid id PK
        bigint user_id FK
        string role
        text content
        int content_length
        timestamp created_at
        timestamp deleted_at
    }
    USER_SETTINGS {
        bigint user_id PK,FK
        int max_history_messages
        text system_prompt
        timestamp created_at
        timestamp updated_at
    }
  ```
- [ ] Добавить ссылки на диаграммы в главный README

**Ожидаемый результат:**
- ✅ 3 архитектурные диаграммы в Mermaid
- ✅ Визуализация всех ключевых компонентов
- ✅ Диаграммы доступны в документации

---

### Задача 6.2: Troubleshooting Guide
**Приоритет:** 🟡 Medium  
**Статус:** ⏳ Планируется  
**Референс:** review-0002.md - Рекомендация #5.2

**Описание:**
Создать comprehensive troubleshooting guide для частых проблем.

**Технические требования:**
- [ ] Создать `docs/guides/troubleshooting.md`
- [ ] Секция **Common Errors**:
  - Bot не запускается
  - API не отвечает
  - Frontend не подключается к API
  - Database connection errors
- [ ] Секция **Database Migration Issues**:
  - Migration failed
  - Rollback migration
  - Manual migration fixes
  - Schema mismatch
- [ ] Секция **LLM API Problems**:
  - Rate limit errors (429)
  - Timeout errors
  - Fallback не работает
  - Invalid API key
  - Model not available
- [ ] Секция **Docker Problems**:
  - Container не стартует
  - Port already in use
  - Volume permissions
  - Network issues
- [ ] Секция **Performance Issues**:
  - Slow database queries
  - High memory usage
  - Connection pool exhausted
- [ ] Добавить для каждой проблемы:
  - Симптомы
  - Причина
  - Решение
  - Как предотвратить

**Пример структуры:**
```markdown
## Common Errors

### Bot не запускается

**Симптомы:**
- Container exits immediately
- Logs показывают "Invalid token"

**Причина:**
- Неправильный TELEGRAM_TOKEN в .env

**Решение:**
1. Проверьте TELEGRAM_TOKEN в .env файле
2. Убедитесь что токен получен от @BotFather
3. Перезапустите bot: `make bot-restart`

**Как предотвратить:**
- Используйте .env.example как template
- Валидируйте токен перед запуском
```

**Ожидаемый результат:**
- ✅ Comprehensive troubleshooting guide
- ✅ Покрытие всех частых проблем
- ✅ Пошаговые решения

---

### Задача 6.3: Production Deployment Guide
**Приоритет:** 🟢 Low  
**Статус:** ⏳ Планируется  

**Описание:**
Создать руководство по production deployment.

**Технические требования:**
- [ ] Создать `docs/guides/production-deployment.md`
- [ ] Секция **Pre-deployment Checklist**:
  - ✅ Environment variables настроены
  - ✅ Secrets management настроен
  - ✅ Database migrations применены
  - ✅ CI/CD pipelines проходят
  - ✅ Load testing выполнен
  - ✅ Monitoring настроен
- [ ] Секция **Deployment Steps**:
  - Pull образов из registry
  - Apply database migrations
  - Start services
  - Health checks
  - Smoke tests
- [ ] Секция **Post-deployment**:
  - Monitoring dashboards
  - Log aggregation
  - Alerts configuration
  - Backup strategy
- [ ] Секция **Rollback Procedure**:
  - Когда делать rollback
  - Как откатить services
  - Как откатить database
- [ ] Секция **Security Hardening**:
  - Firewall rules
  - SSL/TLS certificates
  - Rate limiting
  - Authentication

**Ожидаемый результат:**
- ✅ Complete production deployment guide
- ✅ Checklists для каждого этапа
- ✅ Rollback procedures

---

## ✅ Критерии завершения спринта

Спринт считается завершенным когда:

### Обязательные требования (Must Have)
- [x] ✅ **Задача #1.4**: User Registration для Stats API реализована (admin token)
- [x] ✅ **Задача #1.1**: Stats API защищен authentication с проверкой через БД
- [x] ✅ **Задача #1.2**: Rate limiting настроен для Stats API
- [x] ✅ **Задача #1.3**: CORS улучшен для production
- [x] ✅ **Задача #1.5**: Документация Secrets Management создана
- [ ] **Задача #2.1**: Логирование Real Collector улучшено (query timing, slow query warnings)
- [ ] Prometheus metrics экспортируются для Bot и API
- [ ] Блок 1 (Security Hardening) завершен ✅
- [ ] Блок 2 (Observability) завершен
- [ ] Все тесты проходят (coverage >= 80% для bot, >= 70% для api, >= 80% для frontend)
- [ ] CI/CD pipelines проходят без ошибок
- [ ] Архитектурные диаграммы созданы (3 диаграммы)
- [ ] Troubleshooting guide создан

### Желательные требования (Should Have)
- [ ] Performance optimization завершен (блок 3)
- [ ] Load testing infrastructure настроен
- [ ] DevOps improvements завершены (блок 5)
- [ ] Production deployment guide создан

### Опциональные требования (Nice to Have)
- [ ] Contract testing между Frontend и API
- [ ] Redis для session management (будущий спринт)

---

## 📊 Метрики успеха

После завершения спринта:

1. **Security:** ✅ ЗАВЕРШЕНО
   - ✅ User Registration работает с admin token (Задача 1.4)
   - ✅ Stats API защищен authentication (credentials в PostgreSQL через ApiUser)
   - ✅ Rate limiting предотвращает abuse (10/minute)
   - ✅ CORS настроен для production (whitelist origins, credentials support)
   - ✅ Secrets management документирован

2. **Observability:** 🚧 В ПРОЦЕССЕ
   - ⏳ Prometheus metrics экспортируются
   - ⏳ Логирование включает query timing
   - ⏳ Health checks возвращают детальную информацию

3. **Performance:**
   - ✅ Медленные запросы (> 1s) логируются
   - ✅ Connection pooling настроен для high load
   - ✅ EXPLAIN ANALYZE доступен для оптимизации

4. **Testing:**
   - ✅ Frontend coverage >= 80%
   - ✅ Load testing baseline задокументирован
   - ✅ Все тесты стабильны

5. **Documentation:**
   - ✅ Архитектурные диаграммы визуализируют систему
   - ✅ Troubleshooting guide покрывает частые проблемы
   - ✅ Production deployment guide готов

---

## 🎯 Приоритизация задач

### Week 1 (High Priority) ✅ ЗАВЕРШЕНО
1. ✅ Задача 1.4: User Registration для Stats API (admin token)
2. ✅ Задача 1.1: Authentication для Stats API (с проверкой через БД)
3. ✅ Задача 1.2: Rate limiting для Stats API
4. ⏳ Задача 2.1: Улучшенное логирование Real Collector

### Week 2 (High → Medium Priority) 🚧 В ПРОЦЕССЕ
5. ⏳ Задача 2.2: Prometheus Metrics для Bot
6. ⏳ Задача 2.3: Prometheus Metrics для API
7. ✅ Задача 1.3: CORS настройки
8. ⏳ Задача 3.1: Database Query Optimization
9. ⏳ Задача 3.2: Connection Pooling Tuning

### Week 3 (Medium Priority)
10. ⏳ Задача 2.4: Enhanced Health Check Endpoints
11. ⏳ Задача 4.3: Load Testing Infrastructure
12. ⏳ Задача 6.1: Архитектурные диаграммы
13. ⏳ Задача 6.2: Troubleshooting Guide

### Week 4 (Low Priority)
14. ⏳ Задача 4.1: Рефакторинг тестовых констант
15. ⏳ Задача 4.2: Frontend Unit тесты
16. ⏳ Задача 5.1: Healthcheck improvements
17. ⏳ Задача 5.2: Production Profiles
18. ⏳ Задача 5.3: Graceful Shutdown
19. ✅ Задача 1.5: Документация Secrets Management
20. ⏳ Задача 6.3: Production Deployment Guide

---

## 📝 Примечания

- Спринт фокусируется на production readiness
- Все изменения должны быть backward compatible
- Метрики и логирование не должны существенно влиять на performance
- Документация критична для успешного production deployment
- Load testing поможет установить baseline для мониторинга

**Связанные документы:**
- [review-0002.md](../reviews/review-0002.md) - Code review с найденными проблемами
- [roadmap.md](../roadmap.md) - Общий план развития проекта
- [vision.md](../vision.md) - Техническое видение проекта

---

**История изменений:**
- 2025-10-18: Создан tasklist на основе review-0002.md
- 2025-10-18: Завершен Блок 1 (Security Hardening) - все 5 задач выполнены
  - Задача 1.4: User Registration с admin token (ApiUser модель, миграция, auth router)
  - Задача 1.1: Basic Auth для Stats API с проверкой через PostgreSQL
  - Задача 1.2: Rate Limiting (slowapi, 10/minute)
  - Задача 1.3: CORS improvements (whitelist origins, credentials support)
  - Задача 1.5: Secrets Management документация
  - CI/CD исправления (Dockerfile context, frontend build-args)

