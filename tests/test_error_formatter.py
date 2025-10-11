"""Тесты для утилиты форматирования ошибок."""

from src.utils.error_formatter import get_error_message


def test_rate_limit_error() -> None:
    """Тест: форматирование ошибки rate limit."""
    error = "Rate limit exceeded for API calls"
    result = get_error_message(error)

    assert "лимит запросов" in result.lower()
    assert "⏳" in result


def test_timeout_error() -> None:
    """Тест: форматирование ошибки timeout."""
    error = "Request timeout after 30 seconds"
    result = get_error_message(error)

    assert "слишком много времени" in result.lower()
    assert "⏱️" in result


def test_connection_error() -> None:
    """Тест: форматирование ошибки connection."""
    error = "Connection refused to API server"
    result = get_error_message(error)

    assert "подключени" in result.lower()
    assert "🔌" in result


def test_unknown_error() -> None:
    """Тест: форматирование неизвестной ошибки."""
    error = "Some random unknown error"
    result = get_error_message(error)

    # Должно вернуть общее сообщение об ошибке
    assert "не удалось" in result.lower() or "ошибка" in result.lower()
    assert "❌" in result


def test_empty_error() -> None:
    """Тест: пустая строка ошибки."""
    result = get_error_message("")

    # Должно вернуть дефолтное сообщение
    assert len(result) > 0
    assert "❌" in result


def test_case_insensitive_matching() -> None:
    """Тест: поиск ошибок не зависит от регистра."""
    # Rate limit в разных регистрах
    result1 = get_error_message("RATE LIMIT exceeded")
    result2 = get_error_message("rate limit exceeded")
    result3 = get_error_message("Rate Limit Exceeded")

    assert result1 == result2 == result3
    assert "⏳" in result1
