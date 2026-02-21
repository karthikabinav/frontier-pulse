from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.domain import ExportRequest, ExportResponse
from app.services.pipeline import export_service

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/generate", response_model=ExportResponse)
def generate_exports(payload: ExportRequest, db: Session = Depends(get_db)) -> ExportResponse:
    try:
        return export_service.generate(db=db, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
