"""Роутер для статистики диалогов."""

import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request

from ..middlewares.rate_limit import limiter
from ..stats.models import StatsResponse
from ..utils.auth import verify_credentials

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["stats"])


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Получить статистику диалогов",
    description="Возвращает агрегированную статистику диалогов за указанный период (day/week/month)",
    dependencies=[Depends(verify_credentials)],
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
        401: {"description": "Неправильные credentials"},
        422: {"description": "Невалидный параметр period"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
@limiter.limit("10/minute")
async def get_stats(
    period: Literal["day", "week", "month"],
    request: Request,
) -> StatsResponse:
    """
    Получить статистику за указанный период.

    Автоматически использует Mock или Real Collector на основе конфигурации.

    Args:
        period: Период для статистики ('day', 'week', 'month')
        request: FastAPI Request объект для доступа к app.state

    Returns:
        StatsResponse с полной статистикой

    Raises:
        HTTPException: При ошибке получения статистики
    """
    collector = request.app.state.collector

    try:
        logger.info(f"Fetching stats for period={period}")
        stats: StatsResponse = await collector.get_stats(period)
        logger.info(f"Successfully fetched stats for period={period}")
        return stats
    except ValueError as e:
        logger.error(f"Invalid period: {e}")
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e
