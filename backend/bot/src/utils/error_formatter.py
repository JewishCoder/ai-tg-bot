"""Утилита для форматирования сообщений об ошибках."""


def get_error_message(error: str) -> str:
    """
    Преобразует техническую ошибку в понятное пользователю сообщение.

    Args:
        error: Текст технической ошибки

    Returns:
        Сообщение для пользователя
    """
    error_lower = error.lower()

    if "rate limit" in error_lower:
        return "⏳ Превышен лимит запросов. Попробуйте через минуту."
    if "timeout" in error_lower:
        return "⏱️ Запрос к LLM занял слишком много времени. Попробуйте ещё раз."
    if "connection" in error_lower:
        return "🔌 Проблема с подключением к LLM. Попробуйте позже."
    return "❌ Не удалось получить ответ от LLM. Попробуйте позже."
