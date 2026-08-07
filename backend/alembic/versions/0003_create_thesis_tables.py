"""Create investment thesis and evidence tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-07
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "investment_theses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=10), nullable=False),
        sa.Column("cik", sa.String(length=10), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("bull_case", sa.Text(), nullable=True),
        sa.Column("bear_case", sa.Text(), nullable=True),
        sa.Column("invalidation_criteria", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("conviction", sa.String(length=6), nullable=False),
        sa.Column("signal", sa.String(length=16), nullable=False),
        sa.Column("review_due_date", sa.Date(), nullable=True),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("ticker = upper(ticker)", name="ck_investment_theses_ticker_upper"),
        sa.CheckConstraint("length(trim(ticker)) > 0", name="ck_investment_theses_ticker_not_blank"),
        sa.CheckConstraint("length(cik) = 10", name="ck_investment_theses_cik_length"),
        sa.CheckConstraint("length(trim(company_name)) > 0", name="ck_investment_theses_company_not_blank"),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_investment_theses_title_not_blank"),
        sa.CheckConstraint("length(trim(summary)) > 0", name="ck_investment_theses_summary_not_blank"),
        sa.CheckConstraint("status IN ('DRAFT', 'ACTIVE', 'INVALIDATED', 'ARCHIVED')", name="ck_investment_theses_status"),
        sa.CheckConstraint("conviction IN ('LOW', 'MEDIUM', 'HIGH')", name="ck_investment_theses_conviction"),
        sa.CheckConstraint("signal IN ('STRENGTHENING', 'STABLE', 'WEAKENING', 'REVIEW_REQUIRED')", name="ck_investment_theses_signal"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investment_theses_ticker", "investment_theses", ["ticker"], unique=True)
    op.create_index("ix_investment_theses_review_due_date", "investment_theses", ["review_due_date"], unique=False)
    op.create_index("ix_investment_theses_status_signal", "investment_theses", ["status", "signal"], unique=False)

    op.create_table(
        "thesis_evidence",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("thesis_id", sa.Integer(), nullable=False),
        sa.Column("stance", sa.String(length=14), nullable=False),
        sa.Column("category", sa.String(length=11), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        sa.Column("observed_on", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("stance IN ('SUPPORTING', 'CONTRADICTING', 'NEUTRAL')", name="ck_thesis_evidence_stance"),
        sa.CheckConstraint("category IN ('FINANCIAL', 'COMPETITIVE', 'MANAGEMENT', 'VALUATION', 'CATALYST', 'RISK', 'FILING', 'OTHER')", name="ck_thesis_evidence_category"),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_thesis_evidence_title_not_blank"),
        sa.CheckConstraint("length(trim(description)) > 0", name="ck_thesis_evidence_description_not_blank"),
        sa.ForeignKeyConstraint(["thesis_id"], ["investment_theses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_thesis_evidence_thesis_id", "thesis_evidence", ["thesis_id"], unique=False)
    op.create_index("ix_thesis_evidence_observed_on", "thesis_evidence", ["observed_on"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_thesis_evidence_observed_on", table_name="thesis_evidence")
    op.drop_index("ix_thesis_evidence_thesis_id", table_name="thesis_evidence")
    op.drop_table("thesis_evidence")
    op.drop_index("ix_investment_theses_status_signal", table_name="investment_theses")
    op.drop_index("ix_investment_theses_review_due_date", table_name="investment_theses")
    op.drop_index("ix_investment_theses_ticker", table_name="investment_theses")
    op.drop_table("investment_theses")
