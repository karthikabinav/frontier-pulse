from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db.base import Base
from app.db import models  # noqa: F401

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def ensure_db_extensions() -> None:
    with engine.begin() as conn:
        if "postgresql" in settings.database_url:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


def init_db() -> None:
    """Fallback bootstrap for local/dev only.

    Production path should run Alembic migrations.
    """
    ensure_db_extensions()
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
