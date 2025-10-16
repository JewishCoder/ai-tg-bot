"""Тесты для утилиты sanitization логов."""

from src.utils import sanitize_content, sanitize_token


def test_sanitize_content_empty() -> None:
    """Тест: пустое содержимое."""
    result = sanitize_content("", show_content=False)
    assert result == "[empty]"


def test_sanitize_content_hidden() -> None:
    """Тест: скрытие содержимого (production режим)."""
    text = "Секретное сообщение пользователя"
    result = sanitize_content(text, show_content=False)

    assert "[" in result
    assert "chars]" in result
    assert "Секретное" not in result
    assert len(text) == len("Секретное сообщение пользователя")


def test_sanitize_content_show_short() -> None:
    """Тест: показ короткого содержимого (dev режим)."""
    text = "Короткое сообщение"
    result = sanitize_content(text, show_content=True, max_length=50)

    assert result == text


def test_sanitize_content_show_long() -> None:
    """Тест: показ длинного содержимого с обрезкой (dev режим)."""
    text = "А" * 100
    result = sanitize_content(text, show_content=True, max_length=50)

    assert result.startswith("А" * 50)
    assert "..." in result
    assert "100 chars total" in result


def test_sanitize_content_unicode() -> None:
    """Тест: обработка Unicode символов."""
    text = "Привет! 👋 你好"
    result_hidden = sanitize_content(text, show_content=False)
    result_shown = sanitize_content(text, show_content=True)

    # В скрытом режиме только длина
    assert "chars]" in result_hidden

    # В открытом режиме показываем контент
    assert "Привет" in result_shown
    assert "👋" in result_shown


def test_sanitize_token_standard() -> None:
    """Тест: sanitize API токена."""
    token = "sk-test1234567890abcdefghij"
    result = sanitize_token(token, show_length=4)

    assert result == "sk-t...ghij"
    assert len(result) < len(token)


def test_sanitize_token_short() -> None:
    """Тест: короткий токен."""
    token = "abc"
    result = sanitize_token(token, show_length=4)

    assert result == "***"


def test_sanitize_token_empty() -> None:
    """Тест: пустой токен."""
    result = sanitize_token("", show_length=4)

    assert result == "***"


def test_sanitize_content_length_reporting() -> None:
    """Тест: корректное отображение длины."""
    text = "Test message with some content"
    result = sanitize_content(text, show_content=False)

    # Должен показать длину
    assert f"[{len(text)} chars]" == result
