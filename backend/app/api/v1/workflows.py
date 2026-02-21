from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.domain import (
    InferencePolicyResponse,
    IngestionPolicyResponse,
    ProjectPolicyResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
)
from app.services.pipeline import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/weekly-run", response_model=WorkflowRunResponse)
def run_weekly_pipeline(payload: WorkflowRunRequest, db: Session = Depends(get_db)) -> WorkflowRunResponse:
    return workflow_service.run_weekly(db=db, payload=payload)


@router.get("/ingestion-policy", response_model=IngestionPolicyResponse)
def get_ingestion_policy() -> IngestionPolicyResponse:
    return workflow_service.ingestion_policy()


@router.get("/inference-policy", response_model=InferencePolicyResponse)
def get_inference_policy() -> InferencePolicyResponse:
    return workflow_service.inference_policy()


@router.get("/project-policy", response_model=ProjectPolicyResponse)
def get_project_policy() -> ProjectPolicyResponse:
    return workflow_service.project_policy()
