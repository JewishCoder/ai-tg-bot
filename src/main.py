"""Точка входа приложения."""

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """
    Парсинг аргументов командной строки.
    
    Returns:
        Распарсенные аргументы командной строки
    """
    parser = argparse.ArgumentParser(
        description="AI Telegram Bot - LLM-ассистент в Telegram"
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Путь к .env файлу с конфигурацией (по умолчанию: .env)"
    )
    return parser.parse_args()


def main() -> None:
    """Главная функция приложения."""
    args = parse_args()
    
    # Устанавливаем путь к .env файлу
    env_file = Path(args.env_file)
    
    print(f"AI Telegram Bot")
    print(f"Конфигурация: {env_file.absolute()}")
    
    if not env_file.exists():
        print(f"ОШИБКА: Файл {env_file} не найден!", file=sys.stderr)
        print(f"Создайте .env файл на основе .env.example", file=sys.stderr)
        sys.exit(1)
    
    # TODO: Здесь будет инициализация и запуск бота
    print("Запуск бота... (пока не реализовано)")


if __name__ == "__main__":
    main()

