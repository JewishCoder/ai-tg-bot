"""SQLAlchemy модели для базы данных бота."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""

    pass


class User(Base):
    """
    Модель пользователя Telegram.

    Хранит информацию о пользователе и связи с его сообщениями и настройками.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    settings: Mapped["UserSettings"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class Message(Base):
    """
    Модель сообщения в диалоге.

    Хранит историю сообщений с поддержкой soft delete.
    Каждое сообщение принадлежит конкретному пользователю.
    """

    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))  # system/user/assistant
    content: Mapped[str] = mapped_column(Text)
    content_length: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, index=True
    )  # soft delete

    # Relationships
    user: Mapped["User"] = relationship(back_populates="messages")

    # Indexes
    __table_args__ = (
        Index(
            "ix_messages_user_deleted_created",
            "user_id",
            "deleted_at",
            "created_at",
        ),
    )


class UserSettings(Base):
    """
    Модель настроек пользователя.

    Хранит персональные настройки каждого пользователя,
    включая лимиты истории и кастомные системные промпты.
    """

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    max_history_messages: Mapped[int] = mapped_column(Integer, default=50)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="settings")
