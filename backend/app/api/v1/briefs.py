from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.schemas.domain import BriefUpdateRequest, BriefVersionOut
from app.services.pipeline import brief_service

router = APIRouter(prefix="/briefs", tags=["briefs"])


@router.get("/latest", response_model=Optional[BriefVersionOut])
def latest_brief(week_key: Optional[str] = None, db: Session = Depends(get_db)) -> Optional[BriefVersionOut]:
    return brief_service.latest_version(db=db, week_key=week_key)


@router.post("/update", response_model=BriefVersionOut)
def update_brief(payload: BriefUpdateRequest, db: Session = Depends(get_db)) -> BriefVersionOut:
    return brief_service.update_brief(db=db, payload=payload)
