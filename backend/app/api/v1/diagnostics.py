from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.domain import DiagnosticsResponse
from app.services.pipeline import diagnostics_service

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("", response_model=DiagnosticsResponse)
def diagnostics_status(db: Session = Depends(get_db)) -> DiagnosticsResponse:
    return diagnostics_service.status(db=db)
