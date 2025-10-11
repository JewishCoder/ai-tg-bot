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
