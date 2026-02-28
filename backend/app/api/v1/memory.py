from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.domain import MemoryEntryOut
from app.services.pipeline import analysis_service

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=list[MemoryEntryOut])
def list_memory(
    week_key: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[MemoryEntryOut]:
    return analysis_service.list_memory(db=db, week_key=week_key, memory_type=memory_type, limit=limit)
