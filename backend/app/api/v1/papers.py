from fastapi import APIRouter

from app.schemas.domain import PaperSummary
from app.services.stub_impl import paper_service

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("", response_model=list[PaperSummary])
def list_papers() -> list[PaperSummary]:
    return paper_service.list_papers()
