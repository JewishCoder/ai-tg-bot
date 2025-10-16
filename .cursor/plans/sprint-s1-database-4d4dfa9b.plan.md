<!-- 4d4dfa9b-ceab-41c9-b81a-822d6659f309 9f0f2123-6bfe-435d-b83b-6017620c0117 -->
# Спринт S1: Хранение данных в БД

## Архитектура решения

### Схема базы данных (3 таблицы)

**1. users** - информация о пользователях

- id (BIGINT, PK) - Telegram user_id
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**2. messages** - история сообщений (с soft delete)

- id (UUID, PK)
- user_id (BIGINT, FK → users.id)
- role (VARCHAR) - "system" | "user" | "assistant"
- content (TEXT)
- content_length (INTEGER) - длина в символах
- created_at (TIMESTAMP)
- deleted_at (TIMESTAMP, nullable) - для soft delete

**3. user_settings** - настройки пользователей

- id (SERIAL, PK)
- user_id (BIGINT, FK → users.id, UNIQUE)
- max_history_messages (INTEGER, default=50)
- system_prompt (TEXT, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### Структура проекта

```
src/
├── database.py          # Database engine и session management
├── models.py            # SQLAlchemy модели (User, Message, UserSettings)
├── storage.py           # Рефакторинг для работы с БД вместо JSON
├── config.py            # Добавить DB настройки
alembic/                 # Директория миграций
├── env.py
├── versions/
│   └── 001_initial_schema.py
alembic.ini              # Конфигурация Alembic
docker-compose.yml       # Добавить PostgreSQL сервис
```

## Итерация 1: Настройка PostgreSQL и зависимостей

### Задачи:

1. Обновить `pyproject.toml` - добавить зависимости:

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - sqlalchemy[asyncio]>=2.0.0
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - asyncpg>=0.29.0
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - alembic>=1.13.0
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - psycopg2-binary (для Alembic)

2. Обновить `docker-compose.yml` - добавить PostgreSQL:
   ```yaml
   services:
     postgres:
       image: postgres:16-alpine
       container_name: ai-tg-bot-db
       environment:
         POSTGRES_USER: botuser
         POSTGRES_PASSWORD: botpass
         POSTGRES_DB: ai_tg_bot
       volumes:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 - postgres_data:/var/lib/postgresql/data
       ports:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 - "5432:5432"
       restart: unless-stopped
     
     bot:
       depends_on:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 - postgres
       # ... existing config
   
   volumes:
     postgres_data:
   ```

3. Обновить `src/config.py` - добавить параметры БД:
   ```python
   # Database
   db_host: str = Field(default="localhost")
   db_port: int = Field(default=5432)
   db_name: str = Field(default="ai_tg_bot")
   db_user: str = Field(default="botuser")
   db_password: str = Field(...)
   db_echo: bool = Field(default=False)  # SQLAlchemy echo для debug
   
   @property
   def database_url(self) -> str:
       return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
   ```

4. Обновить `.env.development` - добавить DB_PASSWORD

### Тест:

```bash
& "$env:USERPROFILE\.local\bin\uv.exe" sync
docker-compose up postgres -d
docker-compose logs postgres  # проверить что БД запустилась
```

## Итерация 2: SQLAlchemy модели

### Задачи:

1. Создать `src/models.py` с тремя моделями:
```python
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    
    messages: Mapped[list["Message"]] = relationship(back_populates="user")
    settings: Mapped["UserSettings"] = relationship(back_populates="user", uselist=False)

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))  # system/user/assistant
    content: Mapped[str] = mapped_column(Text)
    content_length: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)  # soft delete
    
    user: Mapped["User"] = relationship(back_populates="messages")

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    max_history_messages: Mapped[int] = mapped_column(default=50)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    
    user: Mapped["User"] = relationship(back_populates="settings")
```

2. Создать `src/database.py` - database engine и session factory:
```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import Config

class Database:
    def __init__(self, config: Config) -> None:
        self.engine = create_async_engine(
            config.database_url,
            echo=config.db_echo,
            pool_pre_ping=True,  # проверка соединения
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def close(self) -> None:
        await self.engine.dispose()
```


### Тест:

```python
# Проверка что модели импортируются
from src.models import Base, User, Message, UserSettings
from src.database import Database
```

## Итерация 3: Настройка Alembic и первая миграция

### Задачи:

1. Инициализировать Alembic:
```bash
& "$env:USERPROFILE\.local\bin\uv.exe" run alembic init alembic
```

2. Настроить `alembic.ini`:
```ini
# Закомментировать sqlalchemy.url, берём из config
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

3. Настроить `alembic/env.py`:
```python
from src.config import Config
from src.models import Base

config_obj = Config()
config.set_main_option("sqlalchemy.url", config_obj.database_url.replace('+asyncpg', ''))  # psycopg2 для миграций

target_metadata = Base.metadata
```

4. Создать миграцию:
```bash
& "$env:USERPROFILE\.local\bin\uv.exe" run alembic revision --autogenerate -m "Initial schema"
```

5. Применить миграцию:
```bash
& "$env:USERPROFILE\.local\bin\uv.exe" run alembic upgrade head
```


### Тест:

```bash
# Проверить что таблицы созданы
docker exec -it ai-tg-bot-db psql -U botuser -d ai_tg_bot -c "\dt"
# Должны быть: users, messages, user_settings, alembic_version
```

## Итерация 4: Рефакторинг Storage для работы с БД

### Задачи:

1. Полностью переписать `src/storage.py`:

**Основные изменения:**

- Убрать работу с JSON файлами
- Добавить Database dependency injection
- Реализовать все методы через SQLAlchemy queries
- Использовать soft delete для messages (deleted_at)
- Лимиты брать из user_settings таблицы

**Ключевые методы:**

```python
class Storage:
    def __init__(self, database: Database, config: Config) -> None:
        self.db = database
        self.config = config
    
    async def load_history(self, user_id: int) -> list[dict[str, str]]:
        """Загрузка истории из БД с учетом soft delete и лимитов"""
        # SELECT * FROM messages WHERE user_id = ? AND deleted_at IS NULL
        # ORDER BY created_at, с учетом лимита из user_settings
    
    async def save_history(self, user_id: int, messages: list[dict[str, str]]) -> None:
        """Сохранение новых сообщений с автоматическим soft delete старых"""
        # Получить лимит из user_settings
        # Если превышен - пометить старые как deleted (кроме system)
        # INSERT новых сообщений
    
    async def clear_history(self, user_id: int) -> None:
        """Soft delete всех сообщений пользователя (используется в /reset)"""
        # UPDATE messages SET deleted_at = NOW() WHERE user_id = ?
    
    async def get_system_prompt(self, user_id: int) -> str | None:
        """Получить кастомный промпт из user_settings (используется в /status, /reset)"""
    
    async def set_system_prompt(self, user_id: int, system_prompt: str) -> None:
        """Установить кастомный промпт и очистить историю (используется в /role, /reset)"""
    
    async def get_dialog_info(self, user_id: int) -> dict[str, Any]:
        """Статистика диалога из БД (используется в /status)"""
    
    async def _ensure_user_exists(self, user_id: int) -> None:
        """Создать user и user_settings если не существуют"""
        # INSERT ... ON CONFLICT DO NOTHING
    
    async def _get_user_settings(self, user_id: int) -> UserSettings:
        """Получить настройки пользователя"""
```

2. Обновить `src/bot.py`:
```python
# Инициализация Database и передача в Storage
from src.database import Database

database = Database(config)
storage = Storage(database, config)

# В shutdown handler добавить await database.close()
```


### Тест:

- Запустить бота, отправить сообщение
- Проверить через psql что данные сохранились
- Протестировать команды /reset (вызывает clear_history), /status (вызывает get_dialog_info)

## Итерация 5: Обновление тестов

### Задачи:

1. Создать тестовую БД fixture в `tests/conftest.py`:
```python
@pytest.fixture
async def test_db(test_config: Config) -> AsyncGenerator[Database, None]:
    # Создать тестовую БД in-memory или через testcontainers
    db = Database(test_config)
    
    # Создать таблицы
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield db
    
    # Cleanup
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await db.close()
```

2. Обновить `tests/test_storage.py` для работы с БД:

- Все тесты переписать для async БД
- Проверить soft delete
- Проверить работу лимитов из user_settings
- Проверить content_length заполняется

3. Добавить тесты для models.py и database.py

### Тест:

```bash
make test
# Покрытие должно остаться >= 70%
```

## Итерация 6: Документация и финализация

### Задачи:

1. Обновить `README.md`:

- Добавить раздел про PostgreSQL
- Документировать переменные окружения БД
- Инструкции по запуску миграций

2. Создать `docs/tasklists/tasklist-S1.md` по аналогии с S0

3. Обновить `.gitignore`:
```
alembic/versions/*.pyc
```

4. Создать Makefile команды:
```makefile
db-migrate:
	& "$(USERPROFILE)\.local\bin\uv.exe" run alembic upgrade head

db-rollback:
	& "$(USERPROFILE)\.local\bin\uv.exe" run alembic downgrade -1

db-revision:
	& "$(USERPROFILE)\.local\bin\uv.exe" run alembic revision --autogenerate -m "$(message)"
```


### Тест:

- Полное ручное тестирование через Telegram
- Проверка всех команд: /start, /help, /role, /status, /reset
- Проверка работы лимитов

## Ключевые моменты реализации

### Soft Delete стратегия

- Физически сообщения не удаляются
- При `clear_history()` (вызывается из /reset) устанавливается `deleted_at = NOW()`
- При загрузке фильтруем `WHERE deleted_at IS NULL`
- При превышении лимита старые сообщения помечаются deleted

### Метрики сообщений

- `content_length` вычисляется при INSERT: `len(content)`
- `created_at` автоматически через `server_default=func.now()`

### Управляемые лимиты

- Default лимит из Config (50)
- Для каждого пользователя свой лимит в `user_settings.max_history_messages`
- Можно расширить в будущем для per-user настроек

### Миграция данных

- Начинаем с чистого листа (по требованию)
- Старые JSON файлы остаются в `data/` но не используются
- При желании можно написать отдельный скрипт миграции позже

### Взаимосвязь команд и методов Storage

- `/start`, `/help` - не используют Storage напрямую
- `/role` - вызывает `set_system_prompt()` (очищает историю и устанавливает новый промпт)
- `/status` - вызывает `get_dialog_info()` и `get_system_prompt()`
- `/reset` - вызывает `get_system_prompt()` и `set_system_prompt()` (сохраняя текущий промпт)
- Обработка сообщений - вызывает `load_history()` и `save_history()`

### To-dos

- [ ] Настройка PostgreSQL и зависимостей: обновить pyproject.toml, docker-compose.yml, config.py, .env
- [ ] Создать SQLAlchemy модели: models.py (User, Message, UserSettings) и database.py (engine, session management)
- [ ] Настроить Alembic и создать первую миграцию схемы БД
- [ ] Рефакторинг Storage для работы с PostgreSQL вместо JSON файлов, реализация soft delete
- [ ] Обновить тесты для работы с БД, добавить тестовую БД fixture, проверить coverage >= 70%
- [ ] Обновить документацию: README.md, создать tasklist-S1.md, добавить Makefile команды для миграций