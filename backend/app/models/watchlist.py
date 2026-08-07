"""Persisted watchlist entry model."""

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WatchlistEntry(Base):
    """One SEC-validated company followed by the local investor."""

    __tablename__ = "watchlist_entries"
    __table_args__ = (
        CheckConstraint("length(trim(ticker)) > 0", name="ck_watchlist_ticker_not_blank"),
        CheckConstraint("length(cik) = 10", name="ck_watchlist_cik_length"),
        CheckConstraint(
            "length(trim(company_name)) > 0",
            name="ck_watchlist_company_name_not_blank",
        ),
        Index("ix_watchlist_entries_cik", "cik"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    cik: Mapped[str] = mapped_column(String(10), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    added_at: Mapped[datetime] = mapped_column(
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
