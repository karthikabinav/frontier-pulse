from datetime import datetime, timezone
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    arxiv_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(1024))
    authors: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    abstract: Mapped[str] = mapped_column(Text)
    full_text: Mapped[str] = mapped_column(Text)
    embedding_vector: Mapped[Optional[list[float]]] = mapped_column(Vector(1024), nullable=True)


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(64), index=True)
    strength_score: Mapped[float] = mapped_column(Float, default=0.0)
    week_introduced: Mapped[str] = mapped_column(String(16), index=True)


class HypothesisPaperLink(Base):
    __tablename__ = "hypothesis_paper_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hypothesis_id: Mapped[int] = mapped_column(ForeignKey("hypotheses.id", ondelete="CASCADE"), index=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), index=True)
    relation: Mapped[str] = mapped_column(String(32))

    hypothesis: Mapped[Hypothesis] = relationship()
    paper: Mapped[Paper] = relationship()


class ResearchBrief(Base):
    __tablename__ = "research_briefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    week_key: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
