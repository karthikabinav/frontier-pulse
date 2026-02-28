from fastapi import APIRouter

from app.api.v1.briefs import router as briefs_router
from app.api.v1.clusters import router as clusters_router
from app.api.v1.exports import router as exports_router
from app.api.v1.health import router as health_router
from app.api.v1.hypotheses import router as hypotheses_router
from app.api.v1.memory import router as memory_router
from app.api.v1.papers import router as papers_router
from app.api.v1.qa import router as qa_router
from app.api.v1.workflows import router as workflows_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(papers_router)
api_router.include_router(workflows_router)
api_router.include_router(hypotheses_router)
api_router.include_router(memory_router)
api_router.include_router(clusters_router)
api_router.include_router(briefs_router)
api_router.include_router(exports_router)
api_router.include_router(qa_router)
