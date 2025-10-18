"""Роутер для аутентификации пользователей API."""

import logging
import sys

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select

# Добавляем shared models из Bot сервиса в путь
sys.path.insert(0, "/app/shared")
from models import ApiUser  # type: ignore[import-not-found]  # noqa: E402

from ..config import config
from ..utils.auth import hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    """Запрос на регистрацию нового пользователя."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(
        ..., min_length=8, max_length=72, description="Password (8-72 characters, bcrypt limit)"
    )
    admin_token: str = Field(..., description="Admin registration token")


class RegisterResponse(BaseModel):
    """Ответ на успешную регистрацию."""

    message: str
    username: str


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя API",
    description="Создает нового пользователя для доступа к Stats API. Требуется admin token.",
    responses={
        201: {"description": "User successfully registered"},
        400: {"description": "Username already exists"},
        403: {"description": "Invalid admin token"},
        500: {"description": "Internal server error"},
    },
)
async def register_user(request_data: RegisterRequest, request: Request) -> RegisterResponse:
    """
    Регистрирует нового пользователя для Stats API.

    Требует валидный admin token для создания аккаунта.
    Пароль хешируется с использованием bcrypt.

    Args:
        request_data: Данные регистрации (username, password, admin_token)
        request: FastAPI Request объект

    Returns:
        RegisterResponse с подтверждением регистрации

    Raises:
        HTTPException: При невалидном admin token или существующем username
    """
    # Verify admin token
    if request_data.admin_token != config.ADMIN_REGISTRATION_TOKEN:
        logger.warning(
            f"Failed registration attempt with invalid admin token for user: {request_data.username}"
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")

    try:
        # Check if username exists
        async with request.app.state.db.session() as session:
            result = await session.execute(
                select(ApiUser).where(ApiUser.username == request_data.username)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                logger.warning(
                    f"Registration attempt with existing username: {request_data.username}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists",
                )

            # Create user
            hashed_password = hash_password(request_data.password)
            new_user = ApiUser(
                username=request_data.username,
                hashed_password=hashed_password,
                is_active=True,
            )
            session.add(new_user)
            await session.commit()

            logger.info(f"Successfully registered new API user: {request_data.username}")
            return RegisterResponse(
                message="User registered successfully", username=request_data.username
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user registration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e
