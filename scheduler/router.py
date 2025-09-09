from fastapi import APIRouter, HTTPException
from typing import List, Dict

from scheduler.scheduler import scheduler_service

router = APIRouter()


@router.get("/jobs", response_model=List[Dict])
async def get_scheduled_jobs():
    """Получить информацию о всех запланированных задачах."""
    return scheduler_service.get_jobs_info()


@router.post("/jobs/{job_id}/run")
async def run_job_manually(job_id: str):
    """Запустить задачу вручную."""
    try:
        await scheduler_service.run_job_now(job_id)
        return {"message": f"Задача {job_id} выполнена успешно"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка выполнения задачи: {str(e)}")


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    """Приостановить задачу."""
    scheduler_service.pause_job(job_id)
    return {"message": f"Задача {job_id} приостановлена"}


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    """Возобновить задачу."""
    scheduler_service.resume_job(job_id)
    return {"message": f"Задача {job_id} возобновлена"}


@router.delete("/jobs/{job_id}")
async def remove_job(job_id: str):
    """Удалить задачу."""
    scheduler_service.remove_job(job_id)
    return {"message": f"Задача {job_id} удалена"}
