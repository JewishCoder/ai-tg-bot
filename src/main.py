"""Точка входа приложения."""

import argparse
import asyncio
import contextlib
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

from src.bot import Bot
from src.config import Config


def parse_args() -> argparse.Namespace:
    """
    Парсинг аргументов командной строки.

    Returns:
        Распарсенные аргументы командной строки
    """
    parser = argparse.ArgumentParser(description="AI Telegram Bot - LLM-ассистент в Telegram")
    parser.add_argument(
        "--env-file",
        type=str,
        default=None,
        help="Путь к .env файлу с конфигурацией (опционально, если не указан - используются переменные окружения)",
    )
    return parser.parse_args()


def setup_logging(config: Config) -> None:
    """
    Настройка системы логирования.

    Настраивает вывод логов в консоль и файл с ротацией.

    Args:
        config: Конфигурация приложения
    """
    # Создаём директорию для логов, если её нет
    logs_dir = Path(config.logs_dir)
    logs_dir.mkdir(exist_ok=True)

    # Формат логов
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-22s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level.upper()))

    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Файловый handler с ротацией
    log_file = logs_dir / "bot.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(getattr(logging, config.log_level.upper()))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Подавляем избыточные логи от aiogram
    logging.getLogger("aiogram").setLevel(logging.WARNING)

    logging.info("Logging configured successfully")


async def main_async(env_file: Path | None) -> None:
    """
    Асинхронная главная функция.

    Args:
        env_file: Путь к .env файлу (опционально)
    """
    logger = logging.getLogger(__name__)

    # Загрузка .env файла если указан
    if env_file:
        load_dotenv(dotenv_path=env_file, override=True)
        logger.info(f"Loaded environment from {env_file.absolute()}")

    # Загрузка конфигурации
    try:
        config = Config()
        if env_file:
            logger.info(f"Configuration loaded from {env_file.absolute()}")
        else:
            logger.info("Configuration loaded from environment variables")

        logger.info(f"Log level: {config.log_level}")
        logger.info(f"Model: {config.openrouter_model}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
        sys.exit(1)

    # Инициализация бота
    try:
        bot = Bot(config)
        logger.info("Bot instance created")
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}", exc_info=True)
        sys.exit(1)

    # Запуск бота
    try:
        logger.info("=" * 60)
        logger.info("AI Telegram Bot started successfully")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        await bot.stop()
        logger.info("Bot shutdown complete")


def main() -> None:
    """Главная функция приложения."""
    args = parse_args()

    # Определяем путь к .env файлу (если указан)
    env_file = None
    if args.env_file:
        env_file = Path(args.env_file)
        if not env_file.exists():
            sys.stderr.write(f"ОШИБКА: Файл {env_file} не найден!\n")
            sys.stderr.write("Создайте .env файл на основе .env.example\n")
            sys.exit(1)
        # Загружаем .env файл
        load_dotenv(dotenv_path=env_file, override=True)

    # Загрузка конфигурации для настройки логирования
    try:
        config = Config()
    except Exception as e:
        sys.stderr.write(f"ОШИБКА: Не удалось загрузить конфигурацию: {e}\n")
        if not env_file:
            sys.stderr.write(
                "Подсказка: Убедитесь, что все необходимые переменные окружения установлены\n"
            )
            sys.stderr.write("Обязательные: TELEGRAM_TOKEN, OPENROUTER_API_KEY\n")
        sys.exit(1)

    # Настройка логирования
    setup_logging(config)

    # Запуск асинхронного event loop
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main_async(env_file))


if __name__ == "__main__":
    main()
