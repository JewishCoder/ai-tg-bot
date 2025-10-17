"""Pydantic модели для типизации статистики диалогов."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Summary(BaseModel):
    """
    Общая статистика за период.

    Attributes:
        total_users: Общее количество пользователей
        total_messages: Общее количество сообщений (без удаленных)
        active_dialogs: Количество активных диалогов (уникальные user_id)
    """

    total_users: int = Field(
        ...,
        ge=0,
        description="Общее количество пользователей",
        json_schema_extra={"example": 150},
    )
    total_messages: int = Field(
        ...,
        ge=0,
        description="Общее количество сообщений",
        json_schema_extra={"example": 4523},
    )
    active_dialogs: int = Field(
        ...,
        ge=0,
        description="Количество активных диалогов",
        json_schema_extra={"example": 89},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_users": 150,
                "total_messages": 4523,
                "active_dialogs": 89,
            }
        }
    )


class ActivityPoint(BaseModel):
    """
    Точка на графике активности.

    Attributes:
        timestamp: Метка времени в UTC (ISO 8601)
        message_count: Количество сообщений в период
        active_users: Количество уникальных пользователей в период
    """

    timestamp: datetime = Field(
        ...,
        description="Метка времени в UTC",
        json_schema_extra={"example": "2025-10-17T10:00:00Z"},
    )
    message_count: int = Field(
        ..., ge=0, description="Количество сообщений", json_schema_extra={"example": 145}
    )
    active_users: int = Field(
        ...,
        ge=0,
        description="Количество активных пользователей",
        json_schema_extra={"example": 42},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": "2025-10-17T10:00:00Z",
                "message_count": 145,
                "active_users": 42,
            }
        }
    )


class RecentDialog(BaseModel):
    """
    Информация о недавнем диалоге.

    Attributes:
        user_id: Telegram user ID
        message_count: Количество сообщений в диалоге
        last_message_at: Время последнего сообщения в UTC
        duration_minutes: Длительность диалога в минутах
    """

    user_id: int = Field(
        ..., gt=0, description="Telegram user ID", json_schema_extra={"example": 123456789}
    )
    message_count: int = Field(
        ..., ge=1, description="Количество сообщений", json_schema_extra={"example": 25}
    )
    last_message_at: datetime = Field(
        ...,
        description="Время последнего сообщения",
        json_schema_extra={"example": "2025-10-17T15:30:00Z"},
    )
    duration_minutes: int = Field(
        ..., ge=0, description="Длительность в минутах", json_schema_extra={"example": 45}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 123456789,
                "message_count": 25,
                "last_message_at": "2025-10-17T15:30:00Z",
                "duration_minutes": 45,
            }
        }
    )


class TopUser(BaseModel):
    """
    Топ пользователь по активности.

    Attributes:
        user_id: Telegram user ID
        total_messages: Общее количество сообщений пользователя
        dialog_count: Количество отдельных диалогов (сессий)
        last_activity: Время последней активности в UTC
    """

    user_id: int = Field(
        ..., gt=0, description="Telegram user ID", json_schema_extra={"example": 123456789}
    )
    total_messages: int = Field(
        ..., ge=1, description="Общее количество сообщений", json_schema_extra={"example": 523}
    )
    dialog_count: int = Field(
        ..., ge=1, description="Количество диалогов", json_schema_extra={"example": 45}
    )
    last_activity: datetime = Field(
        ...,
        description="Время последней активности",
        json_schema_extra={"example": "2025-10-17T15:30:00Z"},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 123456789,
                "total_messages": 523,
                "dialog_count": 45,
                "last_activity": "2025-10-17T15:30:00Z",
            }
        }
    )


class StatsResponse(BaseModel):
    """
    Корневая модель ответа API со статистикой.

    Attributes:
        summary: Общая статистика за период
        activity_timeline: График активности по времени
        recent_dialogs: Список недавних диалогов
        top_users: Топ пользователи по активности
    """

    summary: Summary = Field(..., description="Общая статистика")
    activity_timeline: list[ActivityPoint] = Field(
        ..., description="График активности", min_length=0
    )
    recent_dialogs: list[RecentDialog] = Field(..., description="Недавние диалоги", min_length=0)
    top_users: list[TopUser] = Field(..., description="Топ пользователи", min_length=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": {
                    "total_users": 150,
                    "total_messages": 4523,
                    "active_dialogs": 89,
                },
                "activity_timeline": [
                    {
                        "timestamp": "2025-10-17T10:00:00Z",
                        "message_count": 145,
                        "active_users": 42,
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
    )
