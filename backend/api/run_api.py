"""Entrypoint для запуска API сервера."""

import uvicorn

from src.config import config

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=False,
        log_level=config.LOG_LEVEL.lower(),
    )
