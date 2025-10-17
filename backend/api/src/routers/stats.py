"""Роутер для статистики диалогов."""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException

from ..config import config
from ..stats.collector import StatCollector
from ..stats.mock_collector import MockStatCollector
from ..stats.models import StatsResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["stats"])


def get_stat_collector() -> StatCollector:
    """
    Dependency: получить сборщик статистики.

    Returns:
        StatCollector (Mock или Real в зависимости от конфигурации)

    Raises:
        NotImplementedError: Если тип коллектора не поддерживается
    """
    if config.STAT_COLLECTOR_TYPE == "mock":
        return MockStatCollector()
    raise NotImplementedError("Real collector not implemented yet")


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
                            "total_users": 234,
                            "total_messages": 5678,
                            "active_dialogs": 123,
                        },
                        "activity_timeline": [
                            {
                                "timestamp": "2025-10-17T10:00:00Z",
                                "message_count": 150,
                                "active_users": 45,
                            }
                        ],
                        "recent_dialogs": [
                            {
                                "user_id": 123456789,
                                "message_count": 25,
                                "last_message_at": "2025-10-17T15:30:00Z",
                                "duration_minutes": 45,
                            }
                        ],
                        "top_users": [
                            {
                                "user_id": 123456789,
                                "total_messages": 523,
                                "dialog_count": 45,
                                "last_activity": "2025-10-17T15:30:00Z",
                            }
                        ],
                    }
                }
            },
        },
        422: {"description": "Невалидный параметр period"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_stats(
    period: Annotated[
        Literal["day", "week", "month"],
        "Период для статистики",
    ],
    collector: Annotated[StatCollector, Depends(get_stat_collector)],
) -> StatsResponse:
    """
    Получить статистику за указанный период.

    Args:
        period: Период для статистики ('day', 'week', 'month')
        collector: Сборщик статистики (инжектируется через Depends)

    Returns:
        StatsResponse с полной статистикой

    Raises:
        HTTPException: При ошибке получения статистики
    """
    try:
        logger.info(f"Fetching stats for period={period}")
        stats = await collector.get_stats(period)
        logger.info(f"Successfully fetched stats for period={period}")
        return stats
    except ValueError as e:
        logger.error(f"Invalid period: {e}")
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e
