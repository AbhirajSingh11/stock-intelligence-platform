"""Create the persisted watchlist table.

Revision ID: 0001
Revises: None
Create Date: 2026-08-07
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "watchlist_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=10), nullable=False),
        sa.Column("cik", sa.String(length=10), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(trim(company_name)) > 0",
            name="ck_watchlist_company_name_not_blank",
        ),
        sa.CheckConstraint("length(cik) = 10", name="ck_watchlist_cik_length"),
        sa.CheckConstraint(
            "length(trim(ticker)) > 0",
            name="ck_watchlist_ticker_not_blank",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker"),
    )
    op.create_index(
        "ix_watchlist_entries_cik",
        "watchlist_entries",
        ["cik"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_watchlist_entries_cik", table_name="watchlist_entries")
    op.drop_table("watchlist_entries")
