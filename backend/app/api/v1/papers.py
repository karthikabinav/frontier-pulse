from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.domain import PaperDetail, PaperSummary
from app.services.pipeline import paper_service

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("", response_model=list[PaperSummary])
def list_papers(limit: int = 100, db: Session = Depends(get_db)) -> list[PaperSummary]:
    return paper_service.list_papers(db=db, limit=limit)


@router.get("/{paper_id}", response_model=PaperDetail)
def get_paper(paper_id: int, db: Session = Depends(get_db)) -> PaperDetail:
    try:
        return paper_service.get_paper(db=db, paper_id=paper_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
