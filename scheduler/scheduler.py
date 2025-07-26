import logging
from typing import Dict, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from commands.update_expired_events import update_expired_events

logger = logging.getLogger(__name__)


class SchedulerService:
    """Сервис для управления запланированными задачами с использованием APScheduler."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_listeners()

    def _setup_listeners(self):
        """Настройка слушателей событий планировщика."""

        def job_listener(event):
            if event.exception:
                logger.error(
                    f"Задача {event.job_id} завершилась с ошибкой: {event.exception}")
            else:
                logger.info(f"Задача {event.job_id} выполнена успешно")

        self.scheduler.add_listener(job_listener,
                                    EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def add_job(
            self,
            func,
            job_id: str,
            hour: int = 0,
            minute: int = 0,
            second: int = 0,
            **kwargs
    ):
        """
        Добавляет задачу в планировщик.

        Args:
            func: Функция для выполнения
            job_id: Уникальный ID задачи
            hour: Час выполнения (0-23)
            minute: Минута выполнения (0-59)
            second: Секунда выполнения (0-59)
            **kwargs: Дополнительные параметры для CronTrigger
        """
        trigger = CronTrigger(hour=hour, minute=minute, second=second,
                              **kwargs)

        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            max_instances=1  # Предотвращаем перекрытие выполнения
        )

        logger.info(
            f"Задача {job_id} запланирована на {hour:02d}:{minute:02d}:{second:02d}")

    def setup_default_jobs(self):
        """Настройка задач по умолчанию."""

        # Обновление просроченных событий каждый день в 00:01
        self.add_job(
            func=update_expired_events,
            job_id="update_expired_events",
            hour=0,
            minute=1
        )

        # Пример добавления других задач:

        # # Ежечасная задача
        # self.add_job(
        #     func=some_hourly_task,
        #     job_id="hourly_task",
        #     minute=30  # Каждый час в 30 минут
        # )

        # # Еженедельная задача (каждый понедельник в 03:00)
        # self.add_job(
        #     func=weekly_cleanup,
        #     job_id="weekly_cleanup",
        #     hour=3,
        #     minute=0,
        #     day_of_week=0  # 0 = понедельник
        # )

        # # Ежемесячная задача (1 число каждого месяца в 02:00)
        # self.add_job(
        #     func=monthly_report,
        #     job_id="monthly_report",
        #     hour=2,
        #     minute=0,
        #     day=1
        # )

    def start(self):
        """Запускает планировщик."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Планировщик APScheduler запущен")
        else:
            logger.warning("Планировщик уже запущен")

    def shutdown(self):
        """Останавливает планировщик."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Планировщик APScheduler остановлен")

    def get_jobs_info(self) -> List[Dict]:
        """Возвращает информацию о запланированных задачах."""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'func': str(job.func),
                'trigger': str(job.trigger),
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'max_instances': job.max_instances,
            })
        return jobs_info

    def pause_job(self, job_id: str):
        """Приостанавливает задачу."""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Задача {job_id} приостановлена")
        except Exception as e:
            logger.error(f"Ошибка приостановки задачи {job_id}: {e}")

    def resume_job(self, job_id: str):
        """Возобновляет задачу."""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Задача {job_id} возобновлена")
        except Exception as e:
            logger.error(f"Ошибка возобновления задачи {job_id}: {e}")

    def remove_job(self, job_id: str):
        """Удаляет задачу."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Задача {job_id} удалена")
        except Exception as e:
            logger.error(f"Ошибка удаления задачи {job_id}: {e}")

    async def run_job_now(self, job_id: str):
        """Запускает задачу немедленно."""
        job = self.scheduler.get_job(job_id)
        if job:
            try:
                await job.func()
                logger.info(f"Задача {job_id} выполнена вручную")
            except Exception as e:
                logger.error(f"Ошибка ручного выполнения задачи {job_id}: {e}")
                raise
        else:
            raise ValueError(f"Задача {job_id} не найдена")


# Глобальный экземпляр планировщика
scheduler_service = SchedulerService()
