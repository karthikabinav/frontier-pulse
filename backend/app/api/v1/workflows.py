from fastapi import APIRouter

from app.schemas.domain import (
    InferencePolicyResponse,
    IngestionPolicyResponse,
    ProjectPolicyResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
)
from app.services.stub_impl import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/weekly-run", response_model=WorkflowRunResponse)
def run_weekly_pipeline(payload: WorkflowRunRequest) -> WorkflowRunResponse:
    return workflow_service.run_weekly(payload)


@router.get("/ingestion-policy", response_model=IngestionPolicyResponse)
def get_ingestion_policy() -> IngestionPolicyResponse:
    return workflow_service.ingestion_policy()


@router.get("/inference-policy", response_model=InferencePolicyResponse)
def get_inference_policy() -> InferencePolicyResponse:
    return workflow_service.inference_policy()


@router.get("/project-policy", response_model=ProjectPolicyResponse)
def get_project_policy() -> ProjectPolicyResponse:
    return workflow_service.project_policy()
