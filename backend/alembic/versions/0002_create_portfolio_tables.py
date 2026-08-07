"""Create portfolio transaction and manual price mark tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-07
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "portfolio_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=10), nullable=False),
        sa.Column("cik", sa.String(length=10), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("side", sa.String(length=4), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=24, scale=8), nullable=False),
        sa.Column(
            "price_per_share",
            sa.Numeric(precision=24, scale=8),
            nullable=False,
        ),
        sa.Column(
            "fees",
            sa.Numeric(precision=24, scale=8),
            nullable=False,
            server_default="0",
        ),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(trim(company_name)) > 0",
            name="ck_portfolio_transactions_company_name_not_blank",
        ),
        sa.CheckConstraint(
            "length(cik) = 10",
            name="ck_portfolio_transactions_cik_length",
        ),
        sa.CheckConstraint(
            "fees >= 0",
            name="ck_portfolio_transactions_fees_nonnegative",
        ),
        sa.CheckConstraint(
            "price_per_share > 0",
            name="ck_portfolio_transactions_price_positive",
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_portfolio_transactions_quantity_positive",
        ),
        sa.CheckConstraint(
            "side IN ('BUY', 'SELL')",
            name="ck_portfolio_transactions_side",
        ),
        sa.CheckConstraint(
            "length(trim(ticker)) > 0",
            name="ck_portfolio_transactions_ticker_not_blank",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_portfolio_transactions_ticker",
        "portfolio_transactions",
        ["ticker"],
        unique=False,
    )

    op.create_table(
        "portfolio_price_marks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=10), nullable=False),
        sa.Column("price", sa.Numeric(precision=24, scale=8), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "source",
            sa.String(length=10),
            nullable=False,
            server_default="MANUAL",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "price > 0",
            name="ck_portfolio_price_marks_price_positive",
        ),
        sa.CheckConstraint(
            "source = 'MANUAL'",
            name="ck_portfolio_price_marks_source",
        ),
        sa.CheckConstraint(
            "length(trim(ticker)) > 0",
            name="ck_portfolio_price_marks_ticker_not_blank",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker"),
    )


def downgrade() -> None:
    op.drop_table("portfolio_price_marks")
    op.drop_index(
        "ix_portfolio_transactions_ticker",
        table_name="portfolio_transactions",
    )
    op.drop_table("portfolio_transactions")
