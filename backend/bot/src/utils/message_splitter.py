"""Утилита для разбивки длинных сообщений."""


def split_message(text: str, max_length: int = 4096) -> list[str]:
    """
    Разбивает длинный текст на части, не превышающие max_length символов.

    Старается разбивать по границам абзацев и предложений для читаемости.

    Args:
        text: Текст для разбивки
        max_length: Максимальная длина одной части (по умолчанию 4096)

    Returns:
        Список частей текста
    """
    # Если текст короче лимита, возвращаем как есть
    if len(text) <= max_length:
        return [text]

    parts = []
    remaining_text = text

    while remaining_text:
        # Если остаток меньше лимита, добавляем и выходим
        if len(remaining_text) <= max_length:
            parts.append(remaining_text)
            break

        # Ищем место для разрыва
        chunk = remaining_text[:max_length]

        # Пытаемся разбить по двойному переводу строки (абзацы)
        split_pos = chunk.rfind("\n\n")

        # Если не нашли, пытаемся по одинарному переводу строки
        if split_pos == -1:
            split_pos = chunk.rfind("\n")

        # Если не нашли, пытаемся по точке с пробелом (конец предложения)
        if split_pos == -1:
            split_pos = chunk.rfind(". ")
            if split_pos != -1:
                split_pos += 1  # Включаем точку в текущую часть

        # Если не нашли, пытаемся по любому пробелу
        if split_pos == -1:
            split_pos = chunk.rfind(" ")

        # В крайнем случае режем по лимиту (оставляем небольшой margin)
        if split_pos == -1 or split_pos < max_length * 0.5:
            split_pos = max_length - 100  # Оставляем margin для безопасности

        # Добавляем часть и продолжаем с остатком
        parts.append(remaining_text[:split_pos].strip())
        remaining_text = remaining_text[split_pos:].strip()

    return parts
