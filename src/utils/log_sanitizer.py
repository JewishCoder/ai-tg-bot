"""Утилита для sanitization логов (защита sensitive данных)."""


def sanitize_content(content: str, max_length: int = 50, show_content: bool = False) -> str:
    """
    Sanitize содержимое сообщения для логирования.

    Args:
        content: Текст сообщения
        max_length: Максимальная длина для отображения (если show_content=True)
        show_content: Показывать ли содержимое (False в production)

    Returns:
        Sanitized строка для логирования
    """
    if not content:
        return "[empty]"

    if not show_content:
        return f"[{len(content)} chars]"

    # В dev режиме показываем первые N символов
    if len(content) <= max_length:
        return content

    return f"{content[:max_length]}... ({len(content)} chars total)"


def sanitize_token(token: str, show_length: int = 4) -> str:
    """
    Sanitize API токен для логирования.

    Args:
        token: API токен
        show_length: Количество символов для отображения с начала и конца

    Returns:
        Sanitized токен вида "abc...xyz"
    """
    if not token or len(token) < show_length * 2:
        return "***"

    return f"{token[:show_length]}...{token[-show_length:]}"
