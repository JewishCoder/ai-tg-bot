"""Тесты для утилиты разбивки сообщений."""

from src.utils.message_splitter import split_message


def test_split_short_message() -> None:
    """Тест: короткое сообщение не разбивается."""
    text = "Короткое сообщение"
    result = split_message(text)

    assert len(result) == 1
    assert result[0] == text


def test_split_long_message() -> None:
    """Тест: длинное сообщение разбивается на части."""
    # Создаём сообщение длиннее 4096 символов
    text = "a" * 5000
    result = split_message(text)

    assert len(result) == 2
    # Проверяем что все части <= 4096
    for part in result:
        assert len(part) <= 4096

    # Проверяем что весь текст сохранился
    combined = "".join(result)
    assert len(combined) == 5000


def test_split_multiple_parts() -> None:
    """Тест: очень длинное сообщение разбивается на несколько частей."""
    text = "b" * 10000
    result = split_message(text)

    assert len(result) >= 3
    # Все части должны быть <= 4096
    for part in result:
        assert len(part) <= 4096

    # Проверяем что весь текст сохранился
    combined = "".join(result)
    assert len(combined) == 10000


def test_split_custom_max_length() -> None:
    """Тест: разбивка с пользовательским max_length."""
    text = "c" * 500
    result = split_message(text, max_length=200)

    assert len(result) >= 3
    for part in result:
        assert len(part) <= 200

    # Проверяем что весь текст сохранился
    combined = "".join(result)
    assert len(combined) == 500


def test_split_empty_string() -> None:
    """Тест: пустая строка."""
    result = split_message("")

    assert len(result) == 1
    assert result[0] == ""


def test_split_exact_boundary() -> None:
    """Тест: сообщение ровно max_length не разбивается."""
    text = "d" * 4096
    result = split_message(text)

    assert len(result) == 1
    assert result[0] == text


# Edge Cases Tests


def test_split_unicode_and_emoji() -> None:
    """Тест: разбивка сообщений с Unicode и эмодзи."""
    # Создаём длинный текст с эмодзи и unicode
    text = "Привет! 👋 " * 500  # ~8000 символов с эмодзи

    result = split_message(text)

    # Проверяем что разбилось
    assert len(result) >= 2

    # Проверяем что все части <= 4096
    for part in result:
        assert len(part) <= 4096

    # Проверяем что эмодзи сохранились
    combined = "".join(result)
    assert "👋" in combined
    assert "Привет" in combined


def test_split_very_long_message_10k() -> None:
    """Тест: очень длинное сообщение (>10k символов)."""
    # Генерируем текст длиной 15k символов
    text = "А" * 15000

    result = split_message(text)

    # Проверяем что разбилось на 4+ частей
    assert len(result) >= 4

    # Все части должны быть <= 4096
    for part in result:
        assert len(part) <= 4096

    # Проверяем что весь текст сохранился
    combined = "".join(result)
    assert len(combined) == 15000


def test_split_newlines_and_paragraphs() -> None:
    """Тест: разбивка текста с переносами строк и абзацами."""
    # Создаём текст с абзацами
    paragraphs = ["Абзац " + str(i) + ". " + ("Текст. " * 50) for i in range(50)]
    text = "\n\n".join(paragraphs)  # ~15k символов

    result = split_message(text)

    # Проверяем что разбилось
    assert len(result) >= 2

    # Все части должны быть <= 4096
    for part in result:
        assert len(part) <= 4096

    # Проверяем что абзацы сохранились
    combined = "".join(result)
    assert "Абзац 0" in combined
    assert "Абзац 49" in combined


def test_split_whitespace_only() -> None:
    """Тест: строка из пробелов и переносов."""
    text = "   \n\n   \t\t   \n   "

    result = split_message(text)

    # Должна вернуться одна часть (короткая)
    assert len(result) == 1
    assert result[0] == text


def test_split_special_characters() -> None:
    """Тест: спецсимволы и экранирование."""
    # Текст с различными спецсимволами
    text = "Привет\\n\\t<script>alert('test')</script>\\r\\n\"\\'{}[]|!@#$%^&*()" * 100

    result = split_message(text, max_length=500)

    # Проверяем что разбилось
    assert len(result) >= 2

    # Все части должны быть <= 500
    for part in result:
        assert len(part) <= 500

    # Проверяем что спецсимволы сохранились
    combined = "".join(result)
    assert "<script>" in combined
    assert "\\n" in combined
