"""Тесты для CORS middleware."""

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from src.app import app


@pytest.mark.asyncio
async def test_cors_preflight_request():
    """Тест preflight OPTIONS request."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.options(
            "/api/v1/stats",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )

    # Preflight должен вернуть 200
    assert response.status_code == status.HTTP_200_OK
    # Проверяем CORS headers
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-credentials" in response.headers
    assert "access-control-allow-methods" in response.headers


@pytest.mark.asyncio
async def test_cors_headers_for_allowed_origin():
    """Тест что CORS headers присутствуют для allowed origins."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={"Origin": "http://localhost:8081"},  # Allowed origin
        )

    assert response.status_code == status.HTTP_200_OK
    # Проверяем наличие CORS headers
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:8081"


@pytest.mark.asyncio
async def test_cors_credentials_support():
    """Тест что CORS поддерживает credentials."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={"Origin": "http://localhost:8081"},  # Allowed origin
        )

    assert response.status_code == status.HTTP_200_OK
    # Проверяем credentials support
    assert "access-control-allow-credentials" in response.headers
    assert response.headers["access-control-allow-credentials"] == "true"


@pytest.mark.asyncio
async def test_cors_allowed_methods():
    """Тест что только разрешенные методы доступны."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.options(
            "/api/v1/stats",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == status.HTTP_200_OK
    # Проверяем allowed methods
    allowed_methods = response.headers.get("access-control-allow-methods", "")
    # Должны быть GET, POST, OPTIONS
    assert "GET" in allowed_methods
    assert "POST" in allowed_methods
    assert "OPTIONS" in allowed_methods
    # Не должно быть PUT, DELETE
    assert "PUT" not in allowed_methods
    assert "DELETE" not in allowed_methods
