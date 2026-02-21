from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.domain import QAResponse
from app.services.pipeline import qa_service

router = APIRouter(prefix="/qa", tags=["qa"])


@router.get("/checklist", response_model=QAResponse)
def qa_checklist(db: Session = Depends(get_db)) -> QAResponse:
    return qa_service.checklist(db=db)
