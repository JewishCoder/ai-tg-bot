"""Тесты для auth endpoints."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

# Mock shared models before importing app
sys.path.insert(0, "/app/shared")

# Mock models module
mock_models = MagicMock()


class MockApiUser:
    """Mock ApiUser class."""

    def __init__(self, username: str, hashed_password: str, is_active: bool = True):
        self.username = username
        self.hashed_password = hashed_password
        self.is_active = is_active


mock_models.ApiUser = MockApiUser
sys.modules["models"] = mock_models

from src.app import app  # noqa: E402
from src.utils.auth import hash_password, verify_password  # noqa: E402


@pytest.fixture
def mock_config():
    """Mock config with test admin token."""
    with patch("src.routers.auth.config") as mock_cfg:
        mock_secret = MagicMock()
        mock_secret.get_secret_value.return_value = "test_admin_token_123"
        mock_cfg.ADMIN_REGISTRATION_TOKEN = mock_secret
        yield mock_cfg


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


@pytest.fixture
def mock_app_state(mock_db_session):
    """Mock app state with database."""
    mock_db = MagicMock()
    mock_db.session.return_value = mock_db_session
    app.state.db = mock_db
    yield mock_db
    # Cleanup
    if hasattr(app.state, "db"):
        delattr(app.state, "db")


@pytest.mark.asyncio
async def test_register_user_success(mock_app_state, mock_db_session, mock_config):
    """Тест успешной регистрации пользователя."""
    # Mock database query to return None (user doesn't exist)
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "testpassword123",
                "admin_token": "test_admin_token_123",
            },
        )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert data["username"] == "testuser"

    # Verify session.add was called
    assert mock_db_session.add.called
    # Verify session.commit was called
    assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_register_user_invalid_admin_token(mock_app_state, mock_db_session, mock_config):
    """Тест регистрации с неправильным admin token."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "testpassword123",
                "admin_token": "wrong_token",
            },
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid admin token"


@pytest.mark.asyncio
async def test_register_user_username_already_exists(mock_app_state, mock_db_session, mock_config):
    """Тест регистрации с существующим username."""
    # Mock database query to return existing user
    existing_user = MockApiUser("testuser", "hashedpass")
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_db_session.execute.return_value = mock_result

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "testpassword123",
                "admin_token": "test_admin_token_123",
            },
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.asyncio
async def test_register_user_short_password(mock_app_state, mock_db_session, mock_config):
    """Тест регистрации с коротким паролем (< 8 символов)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "short",
                "admin_token": "test_admin_token_123",
            },
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_register_user_short_username(mock_app_state, mock_db_session, mock_config):
    """Тест регистрации с коротким username (< 3 символов)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "ab",
                "password": "testpassword123",
                "admin_token": "test_admin_token_123",
            },
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_hash_password():
    """Тест хеширования пароля."""
    password = "testpassword123"
    hashed = hash_password(password)

    # Hashed password должен отличаться от открытого
    assert hashed != password
    # Hashed password должен начинаться с $2b$ (bcrypt)
    assert hashed.startswith("$2b$")


def test_verify_password():
    """Тест проверки пароля."""
    password = "testpassword123"
    hashed = hash_password(password)

    # Правильный пароль должен верифицироваться
    assert verify_password(password, hashed) is True
    # Неправильный пароль не должен верифицироваться
    assert verify_password("wrongpassword", hashed) is False


@pytest.mark.asyncio
async def test_stats_endpoint_with_valid_credentials(mock_app_state, mock_db_session):
    """Тест доступа к /api/v1/stats с правильными credentials."""
    # Mock user with hashed password
    test_password = "testpassword123"
    hashed_password = hash_password(test_password)
    test_user = MockApiUser("testuser", hashed_password, is_active=True)

    # Mock database query to return user
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_db_session.execute.return_value = mock_result

    # Mock collector in app state
    mock_collector = MagicMock()
    mock_stats_response = {
        "summary": {"total_users": 10, "total_messages": 100, "active_dialogs": 5},
        "activity_timeline": [],
        "recent_dialogs": [],
        "top_users": [],
    }
    mock_collector.get_stats = AsyncMock(return_value=mock_stats_response)
    app.state.collector = mock_collector

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/stats?period=day", auth=("testuser", "testpassword123")
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "summary" in data
    assert data["summary"]["total_users"] == 10


@pytest.mark.asyncio
async def test_stats_endpoint_without_credentials(mock_app_state):
    """Тест доступа к /api/v1/stats без credentials."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/stats?period=day")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_stats_endpoint_with_invalid_credentials(mock_app_state, mock_db_session):
    """Тест доступа к /api/v1/stats с неправильными credentials."""
    # Mock database query to return None (user doesn't exist)
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/stats?period=day", auth=("wronguser", "wrongpassword"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_stats_endpoint_with_inactive_user(mock_app_state, mock_db_session):
    """Тест доступа к /api/v1/stats с неактивным пользователем."""
    # Mock inactive user
    test_password = "testpassword123"
    hashed_password = hash_password(test_password)
    inactive_user = MockApiUser("testuser", hashed_password, is_active=False)

    # Mock database query to return inactive user
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = inactive_user
    mock_db_session.execute.return_value = mock_result

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/stats?period=day", auth=("testuser", "testpassword123")
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"
