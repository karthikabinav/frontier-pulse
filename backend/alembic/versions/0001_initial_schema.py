"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-02-28 07:00:00
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_scope", sa.String(length=256), nullable=False),
        sa.Column("total_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
    )

    op.create_table(
        "papers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="arxiv"),
        sa.Column("source_id", sa.String(length=128), nullable=False),
        sa.Column("arxiv_id", sa.String(length=32), nullable=True),
        sa.Column("title", sa.String(length=1024), nullable=False),
        sa.Column("authors", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=False),
        sa.Column("full_text", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding_vector", Vector(dim=1024), nullable=True),
    )
    op.create_index("ix_papers_source", "papers", ["source"])
    op.create_index("ix_papers_source_id", "papers", ["source_id"], unique=True)
    op.create_index("ix_papers_arxiv_id", "papers", ["arxiv_id"])
    op.create_index("ix_papers_published_at", "papers", ["published_at"])

    op.create_table(
        "paper_chunks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("paper_id", sa.Integer(), sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section_name", sa.String(length=128), nullable=False, server_default="unknown"),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("estimated_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("embedding_vector", Vector(dim=1024), nullable=True),
        sa.UniqueConstraint("paper_id", "chunk_index", name="uq_chunk_position"),
    )
    op.create_index("ix_paper_chunks_paper_id", "paper_chunks", ["paper_id"])

    op.create_table(
        "paper_alpha_cards",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("paper_id", sa.Integer(), sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("bottleneck_attacked", sa.String(length=256), nullable=False, server_default="unknown"),
        sa.Column("mechanism_type", sa.String(length=256), nullable=False, server_default="unknown"),
        sa.Column("scaling_axis", sa.String(length=256), nullable=False, server_default="unknown"),
        sa.Column("compute_regime", sa.String(length=256), nullable=False, server_default="unknown"),
        sa.Column("claimed_improvement", sa.Text(), nullable=False, server_default=""),
        sa.Column("evaluation_risk", sa.Text(), nullable=False, server_default=""),
        sa.Column("implicit_assumptions", sa.Text(), nullable=False, server_default=""),
        sa.Column("novelty_bucket", sa.String(length=64), nullable=False, server_default="medium"),
        sa.Column("generalization_likelihood", sa.String(length=64), nullable=False, server_default="medium"),
        sa.Column("scaling_projection", sa.Text(), nullable=False, server_default=""),
        sa.Column("strategic_relevance", sa.Text(), nullable=False, server_default=""),
        sa.Column("short_alpha_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("provenance_snippets", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_paper_alpha_cards_paper_id", "paper_alpha_cards", ["paper_id"])
    op.create_index("ix_paper_alpha_cards_is_current", "paper_alpha_cards", ["is_current"])

    op.create_table(
        "hypotheses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("strength_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("user_override_strength", sa.Float(), nullable=True),
        sa.Column("week_introduced", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_hypotheses_type", "hypotheses", ["type"])
    op.create_index("ix_hypotheses_week_introduced", "hypotheses", ["week_introduced"])

    op.create_table(
        "hypothesis_paper_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("hypothesis_id", sa.Integer(), sa.ForeignKey("hypotheses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paper_id", sa.Integer(), sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("provenance", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_hypothesis_paper_links_hypothesis_id", "hypothesis_paper_links", ["hypothesis_id"])
    op.create_index("ix_hypothesis_paper_links_paper_id", "hypothesis_paper_links", ["paper_id"])

    op.create_table(
        "clusters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("dominant_bottleneck", sa.String(length=256), nullable=False, server_default="unknown"),
        sa.Column("mechanism_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("week_key", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_clusters_week_key", "clusters", ["week_key"])

    op.create_table(
        "cluster_paper_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paper_id", sa.Integer(), sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_cluster_paper_links_cluster_id", "cluster_paper_links", ["cluster_id"])
    op.create_index("ix_cluster_paper_links_paper_id", "cluster_paper_links", ["paper_id"])

    op.create_table(
        "research_briefs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("week_key", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_briefs_week_key", "research_briefs", ["week_key"], unique=True)
    op.create_index("ix_research_briefs_status", "research_briefs", ["status"])

    op.create_table(
        "research_brief_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("brief_id", sa.Integer(), sa.ForeignKey("research_briefs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("editor", sa.String(length=128), nullable=False, server_default="user"),
        sa.Column("markdown_content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_brief_versions_brief_id", "research_brief_versions", ["brief_id"])
    op.create_index("ix_research_brief_versions_created_at", "research_brief_versions", ["created_at"])

    op.create_table(
        "research_memory_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("memory_key", sa.String(length=128), nullable=False),
        sa.Column("memory_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("source_week", sa.String(length=16), nullable=False),
        sa.Column("provenance", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding_vector", Vector(dim=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_memory_entries_memory_key", "research_memory_entries", ["memory_key"], unique=True)
    op.create_index("ix_research_memory_entries_memory_type", "research_memory_entries", ["memory_type"])
    op.create_index("ix_research_memory_entries_source_week", "research_memory_entries", ["source_week"])

    op.create_table(
        "export_artifacts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("brief_version_id", sa.Integer(), sa.ForeignKey("research_brief_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_export_artifacts_brief_version_id", "export_artifacts", ["brief_version_id"])
    op.create_index("ix_export_artifacts_platform", "export_artifacts", ["platform"])


def downgrade() -> None:
    op.drop_index("ix_export_artifacts_platform", table_name="export_artifacts")
    op.drop_index("ix_export_artifacts_brief_version_id", table_name="export_artifacts")
    op.drop_table("export_artifacts")

    op.drop_index("ix_research_memory_entries_source_week", table_name="research_memory_entries")
    op.drop_index("ix_research_memory_entries_memory_type", table_name="research_memory_entries")
    op.drop_index("ix_research_memory_entries_memory_key", table_name="research_memory_entries")
    op.drop_table("research_memory_entries")

    op.drop_index("ix_research_brief_versions_created_at", table_name="research_brief_versions")
    op.drop_index("ix_research_brief_versions_brief_id", table_name="research_brief_versions")
    op.drop_table("research_brief_versions")

    op.drop_index("ix_research_briefs_status", table_name="research_briefs")
    op.drop_index("ix_research_briefs_week_key", table_name="research_briefs")
    op.drop_table("research_briefs")

    op.drop_index("ix_cluster_paper_links_paper_id", table_name="cluster_paper_links")
    op.drop_index("ix_cluster_paper_links_cluster_id", table_name="cluster_paper_links")
    op.drop_table("cluster_paper_links")

    op.drop_index("ix_clusters_week_key", table_name="clusters")
    op.drop_table("clusters")

    op.drop_index("ix_hypothesis_paper_links_paper_id", table_name="hypothesis_paper_links")
    op.drop_index("ix_hypothesis_paper_links_hypothesis_id", table_name="hypothesis_paper_links")
    op.drop_table("hypothesis_paper_links")

    op.drop_index("ix_hypotheses_week_introduced", table_name="hypotheses")
    op.drop_index("ix_hypotheses_type", table_name="hypotheses")
    op.drop_table("hypotheses")

    op.drop_index("ix_paper_alpha_cards_is_current", table_name="paper_alpha_cards")
    op.drop_index("ix_paper_alpha_cards_paper_id", table_name="paper_alpha_cards")
    op.drop_table("paper_alpha_cards")

    op.drop_index("ix_paper_chunks_paper_id", table_name="paper_chunks")
    op.drop_table("paper_chunks")

    op.drop_index("ix_papers_published_at", table_name="papers")
    op.drop_index("ix_papers_arxiv_id", table_name="papers")
    op.drop_index("ix_papers_source_id", table_name="papers")
    op.drop_index("ix_papers_source", table_name="papers")
    op.drop_table("papers")

    op.drop_table("ingestion_runs")
