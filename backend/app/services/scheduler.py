from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.db.session import SessionLocal
from app.schemas.domain import WorkflowRunRequest
from app.services.pipeline import workflow_service

scheduler = BackgroundScheduler(timezone=settings.weekly_timezone)


def run_nightly_job() -> None:
    with SessionLocal() as db:
        workflow_service.run_weekly(
            db=db,
            payload=WorkflowRunRequest(
                max_papers=settings.default_max_papers,
                sources=settings.ingest_sources_list,
                include_revised_papers=settings.include_revised_papers,
            ),
        )


def start_scheduler() -> None:
    if scheduler.running:
        return

    minute, hour, *_ = settings.weekly_cron.split()
    trigger = CronTrigger(minute=minute, hour=hour)
    scheduler.add_job(run_nightly_job, trigger=trigger, id="nightly_pipeline", replace_existing=True)
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
