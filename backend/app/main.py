from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings
from app.db.session import init_db
from app.services.scheduler import start_scheduler, stop_scheduler

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    if settings.scheduler_mode == "in_process":
        start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    if settings.scheduler_mode == "in_process":
        stop_scheduler()
