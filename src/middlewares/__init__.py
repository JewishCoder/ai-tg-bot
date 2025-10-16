"""Middleware для Telegram бота."""

from src.middlewares.rate_limit import RateLimitMiddleware

__all__ = ["RateLimitMiddleware"]
