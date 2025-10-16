# 🗄️ Database API

## Обзор

`Database` - класс для управления подключением к PostgreSQL через async SQLAlchemy 2.0.

## Основные возможности

- ✅ Async SQLAlchemy 2.0
- ✅ Connection pooling
- ✅ Async session management
- ✅ Context manager для транзакций
- ✅ Alembic для миграций
- ✅ Graceful shutdown

## Класс `Database`

### Инициализация

```python
from src.database import Database
from src.config import Config

config = Config()
database = Database(config)
```

**Что происходит:**
1. Создается async engine
2. Настраивается connection pool
3. Создается session factory

## Основные методы

### `session() -> AsyncContextManager[AsyncSession]`

Async context manager для работы с сессией БД.

**Возвращает:**
- `AsyncSession`: Асинхронная сессия SQLAlchemy

**Пример:**
```python
async with database.session() as session:
    # Выполнение запросов
    result = await session.execute(select(User).where(User.id == 12345))
    user = result.scalar_one_or_none()
    
    # Автоматический commit при успехе
    # Автоматический rollback при исключении
```

### `async close() -> None`

Закрывает все соединения с БД (graceful shutdown).

**Пример:**
```python
# При остановке приложения
await database.close()
```

## Connection Pool

Database использует connection pooling для эффективного использования соединений:

### Параметры пула

```python
engine = create_async_engine(
    database_url,
    echo=False,                    # Логирование SQL запросов
    pool_size=5,                   # Размер пула
    max_overflow=10,               # Дополнительные соединения
    pool_pre_ping=True,            # Проверка соединений перед использованием
    pool_recycle=3600,             # Переиспользование соединений (1 час)
)
```

**Характеристики:**
- `pool_size=5`: До 5 постоянных соединений
- `max_overflow=10`: +10 временных соединений при нагрузке
- `pool_pre_ping=True`: Проверка живости соединения
- `pool_recycle=3600`: Обновление соединений каждый час

```mermaid
graph LR
    A[App] -->|Запрос сессии| B[Session Factory]
    B -->|Берет из пула| C[Connection Pool]
    C -->|Если есть| D[Существующее<br/>соединение]
    C -->|Если нет| E[Новое<br/>соединение]
    D --> F[PostgreSQL]
    E --> F
    
    style C fill:#2196F3
    style F fill:#9C27B0
```

## Session Management

### Async Session

Все операции с БД выполняются через async сессии:

```python
from sqlalchemy import select
from src.models import User

async with database.session() as session:
    # SELECT
    result = await session.execute(
        select(User).where(User.id == 12345)
    )
    user = result.scalar_one_or_none()
    
    # INSERT
    new_user = User(id=67890)
    session.add(new_user)
    
    # UPDATE
    user.updated_at = datetime.now(UTC)
    
    # DELETE (soft delete в нашем случае)
    message.deleted_at = datetime.now(UTC)
    
    # Commit происходит автоматически при выходе из context manager
```

### Транзакции

Context manager автоматически управляет транзакциями:

```python
try:
    async with database.session() as session:
        # Операция 1
        session.add(user)
        
        # Операция 2
        await session.execute(update_stmt)
        
        # ✅ Автоматический COMMIT при успехе
except Exception as e:
    # ❌ Автоматический ROLLBACK при ошибке
    logger.error(f"Transaction failed: {e}")
```

## Модели данных

Database работает с SQLAlchemy моделями, определенными в `src/models.py`:

### User

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)  # Telegram user ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Message

```python
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # system | user | assistant
    content = Column(Text, nullable=False)
    content_length = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
```

### UserSettings

```python
class UserSettings(Base):
    __tablename__ = "user_settings"
    
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    max_history_messages = Column(Integer, nullable=False)
    system_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

## Миграции (Alembic)

Database использует Alembic для управления схемой БД.

### Команды миграций

```bash
# Применить все миграции
make db-migrate
# или
uv run alembic upgrade head

# Откатить последнюю миграцию
make db-rollback
# или
uv run alembic downgrade -1

# Создать новую миграцию
make db-revision message="Add new column"
# или
uv run alembic revision --autogenerate -m "Add new column"

# Показать текущую версию БД
make db-current
# или
uv run alembic current
```

### Структура миграций

```
alembic/
├── env.py                    # Конфигурация Alembic
├── script.py.mako           # Шаблон миграций
└── versions/
    ├── e9844b552bfa_initial_schema.py
    └── b03417887b93_add_timezone_to_datetime_fields.py
```

### Пример миграции

```python
def upgrade() -> None:
    # Добавление колонки
    op.add_column(
        'messages',
        sa.Column('content_length', sa.Integer(), nullable=True)
    )
    
    # Добавление индекса
    op.create_index(
        'ix_messages_user_deleted_created',
        'messages',
        ['user_id', 'deleted_at', 'created_at']
    )

def downgrade() -> None:
    # Откат изменений
    op.drop_index('ix_messages_user_deleted_created', 'messages')
    op.drop_column('messages', 'content_length')
```

## Конфигурация БД

Параметры подключения настраиваются через Config:

```python
config = Config(
    db_host="localhost",
    db_port=5432,
    db_name="ai_tg_bot",
    db_user="postgres",
    db_password="your-password",
)
```

**Database URL формат:**
```
postgresql+asyncpg://user:password@host:port/database
```

## Примеры использования

### Базовое использование

```python
from src.database import Database
from src.config import Config
from sqlalchemy import select
from src.models import User

# Инициализация
config = Config()
database = Database(config)

# Запрос
async with database.session() as session:
    result = await session.execute(
        select(User).where(User.id == 12345)
    )
    user = result.scalar_one_or_none()
    print(f"User: {user.id}")
```

### Создание записи

```python
from src.models import User, UserSettings

async with database.session() as session:
    # Создание пользователя
    user = User(id=12345)
    session.add(user)
    
    # Создание настроек
    settings = UserSettings(
        user_id=12345,
        max_history_messages=50,
        system_prompt="Custom prompt"
    )
    session.add(settings)
    
    # Commit автоматический при выходе
```

### Обновление записи

```python
from sqlalchemy import update
from src.models import UserSettings

async with database.session() as session:
    stmt = (
        update(UserSettings)
        .where(UserSettings.user_id == 12345)
        .values(max_history_messages=100)
    )
    await session.execute(stmt)
```

### Soft Delete

```python
from sqlalchemy import update, func
from src.models import Message

async with database.session() as session:
    stmt = (
        update(Message)
        .where(Message.user_id == 12345)
        .values(deleted_at=func.now())
    )
    await session.execute(stmt)
```

### Загрузка с фильтрацией

```python
from sqlalchemy import select
from src.models import Message

async with database.session() as session:
    stmt = (
        select(Message)
        .where(
            Message.user_id == 12345,
            Message.deleted_at.is_(None)  # Только активные
        )
        .order_by(Message.created_at.desc())
        .limit(20)
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()
```

### Graceful shutdown

```python
import signal

async def shutdown_handler():
    logger.info("Closing database connections...")
    await database.close()
    logger.info("Database closed")

# Регистрация обработчика
signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(shutdown_handler()))
```

## Производительность

### Индексы

Database использует составные индексы для оптимизации запросов:

```sql
-- Ускоряет запросы к истории сообщений
CREATE INDEX ix_messages_user_deleted_created 
ON messages (user_id, deleted_at, created_at);

-- Ускоряет поиск пользователей
CREATE INDEX ix_users_id 
ON users (id);
```

### Connection Pooling

- Переиспользование соединений снижает latency
- `pool_pre_ping` предотвращает ошибки с мертвыми соединениями
- `pool_recycle` предотвращает накопление stale соединений

### Async I/O

- Не блокирует event loop
- Позволяет обрабатывать множество запросов одновременно
- Эффективное использование системных ресурсов

## Атрибуты

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `engine` | AsyncEngine | Async SQLAlchemy engine |
| `session_factory` | async_sessionmaker | Фабрика сессий |

## Зависимости

- `sqlalchemy[asyncio]>=2.0.0`: Async ORM
- `asyncpg>=0.29.0`: Async PostgreSQL драйвер
- `alembic>=1.13.0`: Миграции БД
- `src.config.Config`: Конфигурация
- `src.models`: Определения моделей

## Best Practices

### ✅ Правильно

```python
# 1. Всегда используйте context manager
async with database.session() as session:
    result = await session.execute(stmt)

# 2. Используйте async/await
result = await session.execute(select(User))

# 3. Graceful shutdown
await database.close()
```

### ❌ Неправильно

```python
# 1. Ручное управление сессией (забываем commit/rollback)
session = database.session_factory()
result = await session.execute(stmt)
# Забыли close!

# 2. Синхронные операции
session.execute(stmt)  # Блокирует event loop!

# 3. Жесткое завершение
database.engine.dispose()  # Обрывает активные соединения
```

## См. также

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Models](../../src/models.py)
- [Config](../../src/config.py)

