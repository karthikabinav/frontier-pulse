from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.schemas.domain import HypothesisOut
from app.services.pipeline import analysis_service

router = APIRouter(prefix="/hypotheses", tags=["hypotheses"])


@router.get("", response_model=list[HypothesisOut])
def list_hypotheses(week_key: Optional[str] = None, db: Session = Depends(get_db)) -> list[HypothesisOut]:
    return analysis_service.list_hypotheses(db=db, week_key=week_key)
