from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.orm import Session

from app.schemas.domain import (
    BriefUpdateRequest,
    BriefVersionOut,
    ClusterOut,
    ExportRequest,
    ExportResponse,
    InferencePolicyResponse,
    IngestionPolicyResponse,
    PaperDetail,
    PaperSummary,
    ProjectPolicyResponse,
    QAResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    HypothesisOut,
)


class PaperService(ABC):
    @abstractmethod
    def list_papers(self, db: Session, limit: int = 100) -> list[PaperSummary]:
        raise NotImplementedError

    @abstractmethod
    def get_paper(self, db: Session, paper_id: int) -> PaperDetail:
        raise NotImplementedError


class WorkflowService(ABC):
    @abstractmethod
    def run_weekly(self, db: Session, payload: WorkflowRunRequest) -> WorkflowRunResponse:
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


class AnalysisService(ABC):
    @abstractmethod
    def list_hypotheses(self, db: Session, week_key: Optional[str] = None) -> list[HypothesisOut]:
        raise NotImplementedError

    @abstractmethod
    def list_clusters(self, db: Session, week_key: Optional[str] = None) -> list[ClusterOut]:
        raise NotImplementedError


class BriefService(ABC):
    @abstractmethod
    def latest_version(self, db: Session, week_key: Optional[str] = None) -> Optional[BriefVersionOut]:
        raise NotImplementedError

    @abstractmethod
    def update_brief(self, db: Session, payload: BriefUpdateRequest) -> BriefVersionOut:
        raise NotImplementedError


class ExportService(ABC):
    @abstractmethod
    def generate(self, db: Session, payload: ExportRequest) -> ExportResponse:
        raise NotImplementedError


class QAService(ABC):
    @abstractmethod
    def checklist(self, db: Session) -> QAResponse:
        raise NotImplementedError
