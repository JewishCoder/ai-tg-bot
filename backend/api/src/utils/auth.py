"""Утилиты для аутентификации и авторизации."""

import hashlib
import sys
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from sqlalchemy import select

# Добавляем shared models из Bot сервиса в путь
sys.path.insert(0, "/app/shared")
from models import ApiUser  # type: ignore[import-not-found]  # noqa: E402

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Basic Auth security scheme
security = HTTPBasic()


def _prehash_password(password: str) -> bytes:
    """
    Pre-hash password with SHA256 для обработки длинных паролей.

    Bcrypt имеет ограничение в 72 байта. Для длинных паролей используем
    SHA256 pre-hashing как рекомендованный подход.

    Args:
        password: Открытый пароль

    Returns:
        SHA256 hash пароля в hex формате (64 символа)
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("ascii")


def hash_password(password: str) -> str:
    """
    Хеширует пароль с использованием SHA256 + bcrypt.

    Использует SHA256 pre-hashing для обработки длинных паролей,
    затем применяет bcrypt для финального хеширования.

    Args:
        password: Открытый пароль

    Returns:
        Хешированный пароль
    """
    prehashed = _prehash_password(password)
    return pwd_context.hash(prehashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие открытого пароля хешу.

    Применяет тот же SHA256 pre-hashing перед проверкой через bcrypt.

    Args:
        plain_password: Открытый пароль
        hashed_password: Хешированный пароль

    Returns:
        True если пароли совпадают, False иначе
    """
    prehashed = _prehash_password(plain_password)
    return pwd_context.verify(prehashed, hashed_password)


async def verify_credentials(
    request: Request,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> ApiUser:
    """
    Проверяет Basic Auth credentials против базы данных.

    Dependency для защиты endpoints через Basic Authentication.
    Проверяет username и password пользователя в БД.

    Args:
        credentials: HTTP Basic Auth credentials
        request: FastAPI Request объект

    Returns:
        ApiUser объект для авторизованного пользователя

    Raises:
        HTTPException: 401 если credentials невалидны или пользователь неактивен
    """
    async with request.app.state.db.session() as session:
        result = await session.execute(
            select(ApiUser).where(ApiUser.username == credentials.username)
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

        return user
