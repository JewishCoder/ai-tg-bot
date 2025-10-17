"""FastAPI приложение для статистики диалогов."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import config
from .routers import stats

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="AI TG Bot Stats API",
    version="1.0.0",
    description="API для получения статистики диалогов Telegram-бота",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(stats.router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Статус здоровья сервиса
    """
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event() -> None:
    """Событие при запуске приложения."""
    logger.info("Starting AI TG Bot Stats API")
    logger.info("API Version: 1.0.0")
    logger.info(f"Stat Collector Type: {config.STAT_COLLECTOR_TYPE}")
    logger.info(f"CORS Origins: {config.CORS_ORIGINS}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Событие при остановке приложения."""
    logger.info("Shutting down AI TG Bot Stats API")
