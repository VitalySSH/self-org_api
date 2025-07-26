import logging
import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)  # app/
root_dir = os.path.dirname(app_dir)  # корень проекта

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Теперь импортируем scheduler_service
try:
    from app.scheduler.scheduler import scheduler_service
except ImportError:
    # Альтернативный импорт для случаев, когда app недоступен
    import importlib.util

    scheduler_path = os.path.join(app_dir, 'scheduler', 'scheduler.py')
    spec = importlib.util.spec_from_file_location("scheduler", scheduler_path)
    scheduler_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scheduler_module)
    scheduler_service = scheduler_module.scheduler_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения FastAPI.
    Запускает планировщик при старте и останавливает при завершении.
    """
    logger.info("Запуск приложения...")

    try:
        # Настройка и запуск планировщика
        scheduler_service.setup_default_jobs()
        scheduler_service.start()
        logger.info("Планировщик успешно запущен")
    except Exception as e:
        logger.error(f"Ошибка запуска планировщика: {e}")

    yield

    # Остановка планировщика при завершении приложения
    logger.info("Завершение работы приложения...")
    try:
        scheduler_service.shutdown()
        logger.info("Планировщик успешно остановлен")
    except Exception as e:
        logger.error(f"Ошибка остановки планировщика: {e}")