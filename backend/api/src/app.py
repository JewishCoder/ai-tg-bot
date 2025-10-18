"""FastAPI приложение для статистики диалогов."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import config
from .database import Database
from .middlewares.rate_limit import limiter
from .routers import auth, stats
from .stats.factory import create_stat_collector

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifecycle manager для FastAPI приложения.

    Управляет инициализацией и очисткой ресурсов.
    """
    # Инициализация при старте
    logger.info("Starting AI TG Bot Stats API")
    logger.info("API Version: 1.0.0")
    logger.info(f"Collector Mode: {config.COLLECTOR_MODE}")
    logger.info(f"CORS Origins: {config.CORS_ORIGINS}")

    # Создаём Database instance для auth
    db = Database(
        database_url=config.database_url,
        pool_size=config.DB_POOL_SIZE,
        max_overflow=config.DB_MAX_OVERFLOW,
    )
    app.state.db = db

    # Создаём collector через Factory
    collector = create_stat_collector(config)
    app.state.collector = collector
    app.state.config = config

    yield

    # Cleanup при остановке
    logger.info("Shutting down AI TG Bot Stats API")

    # Закрываем Database для auth
    await db.close()
    logger.info("Auth database connections closed")

    # Закрываем Database если используется Real Collector
    if hasattr(collector, "db"):
        await collector.db.close()
        logger.info("Collector database connections closed")


# Создание FastAPI приложения
app = FastAPI(
    title="AI TG Bot Stats API",
    version="1.0.0",
    description="API для получения статистики диалогов Telegram-бота",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Настройка rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,  # Whitelist, не "*"
    allow_credentials=True,  # Для Basic Auth
    allow_methods=["GET", "POST", "OPTIONS"],  # Только нужные методы
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(stats.router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Статус здоровья сервиса
    """
    return {"status": "ok"}
