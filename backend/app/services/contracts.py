from abc import ABC, abstractmethod

from app.schemas.domain import (
    InferencePolicyResponse,
    IngestionPolicyResponse,
    PaperSummary,
    ProjectPolicyResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
)


class PaperService(ABC):
    @abstractmethod
    def list_papers(self) -> list[PaperSummary]:
        raise NotImplementedError


class WorkflowService(ABC):
    @abstractmethod
    def run_weekly(self, payload: WorkflowRunRequest) -> WorkflowRunResponse:
        raise NotImplementedError

    @abstractmethod
    def ingestion_policy(self) -> IngestionPolicyResponse:
        raise NotImplementedError

    @abstractmethod
    def inference_policy(self) -> InferencePolicyResponse:
        raise NotImplementedError

    @abstractmethod
    def project_policy(self) -> ProjectPolicyResponse:
        raise NotImplementedError
