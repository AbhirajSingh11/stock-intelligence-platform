"""Persisted portfolio transaction and manual price mark models."""

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PortfolioTransaction(Base):
    """One immutable-identity buy or sell ledger event."""

    __tablename__ = "portfolio_transactions"
    __table_args__ = (
        CheckConstraint(
            "length(trim(ticker)) > 0",
            name="ck_portfolio_transactions_ticker_not_blank",
        ),
        CheckConstraint(
            "length(cik) = 10",
            name="ck_portfolio_transactions_cik_length",
        ),
        CheckConstraint(
            "length(trim(company_name)) > 0",
            name="ck_portfolio_transactions_company_name_not_blank",
        ),
        CheckConstraint(
            "side IN ('BUY', 'SELL')",
            name="ck_portfolio_transactions_side",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_portfolio_transactions_quantity_positive",
        ),
        CheckConstraint(
            "price_per_share > 0",
            name="ck_portfolio_transactions_price_positive",
        ),
        CheckConstraint(
            "fees >= 0",
            name="ck_portfolio_transactions_fees_nonnegative",
        ),
        Index("ix_portfolio_transactions_ticker", "ticker"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False)
    cik: Mapped[str] = mapped_column(String(10), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    side: Mapped[str] = mapped_column(String(4), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    price_per_share: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    fees: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
        default=Decimal("0"),
    )
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class PortfolioPriceMark(Base):
    """Latest user-entered current price for one portfolio security."""

    __tablename__ = "portfolio_price_marks"
    __table_args__ = (
        CheckConstraint(
            "length(trim(ticker)) > 0",
            name="ck_portfolio_price_marks_ticker_not_blank",
        ),
        CheckConstraint(
            "price > 0",
            name="ck_portfolio_price_marks_price_positive",
        ),
        CheckConstraint(
            "source = 'MANUAL'",
            name="ck_portfolio_price_marks_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(10), nullable=False, default="MANUAL")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
