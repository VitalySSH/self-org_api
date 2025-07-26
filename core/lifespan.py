import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.scheduler.scheduler import scheduler_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения FastAPI.
    Запускает планировщик при старте и останавливает при завершении.
    """
    logger.info("Запуск приложения...")

    # Настройка и запуск планировщика
    scheduler_service.setup_default_jobs()
    scheduler_service.start()

    yield

    # Остановка планировщика при завершении приложения
    logger.info("Завершение работы приложения...")
    scheduler_service.shutdown()