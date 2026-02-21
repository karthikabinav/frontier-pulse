from fastapi import APIRouter

from app.schemas.domain import IngestionPolicyResponse, WorkflowRunRequest, WorkflowRunResponse
from app.services.stub_impl import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/weekly-run", response_model=WorkflowRunResponse)
def run_weekly_pipeline(payload: WorkflowRunRequest) -> WorkflowRunResponse:
    return workflow_service.run_weekly(payload)


@router.get("/ingestion-policy", response_model=IngestionPolicyResponse)
def get_ingestion_policy() -> IngestionPolicyResponse:
    return workflow_service.ingestion_policy()
