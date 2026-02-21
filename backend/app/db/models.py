from datetime import datetime, timezone
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_scope: Mapped[str] = mapped_column(String(256))
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), default="arxiv", index=True)
    source_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    arxiv_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(1024))
    authors: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    abstract: Mapped[str] = mapped_column(Text)
    full_text: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text, default="")
    embedding_vector: Mapped[Optional[list[float]]] = mapped_column(Vector(1024), nullable=True)


class PaperChunk(Base):
    __tablename__ = "paper_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), index=True)
    section_name: Mapped[str] = mapped_column(String(128), default="unknown")
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    estimated_tokens: Mapped[int] = mapped_column(Integer, default=0)
    embedding_vector: Mapped[Optional[list[float]]] = mapped_column(Vector(1024), nullable=True)

    paper: Mapped[Paper] = relationship()

    __table_args__ = (UniqueConstraint("paper_id", "chunk_index", name="uq_chunk_position"),)


class PaperAlphaCard(Base):
    __tablename__ = "paper_alpha_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    bottleneck_attacked: Mapped[str] = mapped_column(String(256), default="unknown")
    mechanism_type: Mapped[str] = mapped_column(String(256), default="unknown")
    scaling_axis: Mapped[str] = mapped_column(String(256), default="unknown")
    compute_regime: Mapped[str] = mapped_column(String(256), default="unknown")
    claimed_improvement: Mapped[str] = mapped_column(Text, default="")
    evaluation_risk: Mapped[str] = mapped_column(Text, default="")
    implicit_assumptions: Mapped[str] = mapped_column(Text, default="")
    novelty_bucket: Mapped[str] = mapped_column(String(64), default="medium")
    generalization_likelihood: Mapped[str] = mapped_column(String(64), default="medium")
    scaling_projection: Mapped[str] = mapped_column(Text, default="")
    strategic_relevance: Mapped[str] = mapped_column(Text, default="")
    short_alpha_summary: Mapped[str] = mapped_column(Text, default="")
    provenance_snippets: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    paper: Mapped[Paper] = relationship()


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(64), index=True)
    strength_score: Mapped[float] = mapped_column(Float, default=0.0)
    user_override_strength: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    week_introduced: Mapped[str] = mapped_column(String(16), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class HypothesisPaperLink(Base):
    __tablename__ = "hypothesis_paper_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hypothesis_id: Mapped[int] = mapped_column(ForeignKey("hypotheses.id", ondelete="CASCADE"), index=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), index=True)
    relation: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    provenance: Mapped[str] = mapped_column(Text, default="")

    hypothesis: Mapped[Hypothesis] = relationship()
    paper: Mapped[Paper] = relationship()


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256))
    dominant_bottleneck: Mapped[str] = mapped_column(String(256), default="unknown")
    mechanism_summary: Mapped[str] = mapped_column(Text, default="")
    week_key: Mapped[str] = mapped_column(String(16), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ClusterPaperLink(Base):
    __tablename__ = "cluster_paper_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("clusters.id", ondelete="CASCADE"), index=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), index=True)


class ResearchBrief(Base):
    __tablename__ = "research_briefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    week_key: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ResearchBriefVersion(Base):
    __tablename__ = "research_brief_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brief_id: Mapped[int] = mapped_column(ForeignKey("research_briefs.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    editor: Mapped[str] = mapped_column(String(128), default="user")
    markdown_content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    brief: Mapped[ResearchBrief] = relationship()


class ResearchMemoryEntry(Base):
    __tablename__ = "research_memory_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    memory_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    memory_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(512))
    summary: Mapped[str] = mapped_column(Text)
    source_week: Mapped[str] = mapped_column(String(16), index=True)
    provenance: Mapped[str] = mapped_column(Text, default="")
    embedding_vector: Mapped[Optional[list[float]]] = mapped_column(Vector(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ExportArtifact(Base):
    __tablename__ = "export_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brief_version_id: Mapped[int] = mapped_column(
        ForeignKey("research_brief_versions.id", ondelete="CASCADE"), index=True
    )
    platform: Mapped[str] = mapped_column(String(32), index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
