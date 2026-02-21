from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.schemas.domain import ClusterOut
from app.services.pipeline import analysis_service

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("", response_model=list[ClusterOut])
def list_clusters(week_key: Optional[str] = None, db: Session = Depends(get_db)) -> list[ClusterOut]:
    return analysis_service.list_clusters(db=db, week_key=week_key)
