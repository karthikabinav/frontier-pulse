from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import Paper
from app.services.pipeline import _heuristic_alpha


def test_heuristic_alpha_has_required_fields() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        paper = Paper(
            source="arxiv",
            source_id="x1",
            arxiv_id="x1",
            title="Inference-time scaling for reasoning",
            authors="A",
            published_at=datetime.now(timezone.utc),
            updated_at=None,
            abstract="We improve reasoning with additional compute at inference.",
            full_text="Inference-time compute improves reasoning.",
            source_url="http://example.com",
        )
        db.add(paper)
        db.flush()

        data = _heuristic_alpha(paper, chunks=[])

    assert data["bottleneck_attacked"]
    assert data["mechanism_type"]
    assert data["novelty_bucket"] in {"low", "medium", "high"}
