"""Persistent investment theses and their user-entered evidence."""

from datetime import date, datetime, timezone

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InvestmentThesis(Base):
    __tablename__ = "investment_theses"
    __table_args__ = (
        CheckConstraint("ticker = upper(ticker)", name="ck_investment_theses_ticker_upper"),
        CheckConstraint("length(trim(ticker)) > 0", name="ck_investment_theses_ticker_not_blank"),
        CheckConstraint("length(cik) = 10", name="ck_investment_theses_cik_length"),
        CheckConstraint("length(trim(company_name)) > 0", name="ck_investment_theses_company_not_blank"),
        CheckConstraint("length(trim(title)) > 0", name="ck_investment_theses_title_not_blank"),
        CheckConstraint("length(trim(summary)) > 0", name="ck_investment_theses_summary_not_blank"),
        CheckConstraint("status IN ('DRAFT', 'ACTIVE', 'INVALIDATED', 'ARCHIVED')", name="ck_investment_theses_status"),
        CheckConstraint("conviction IN ('LOW', 'MEDIUM', 'HIGH')", name="ck_investment_theses_conviction"),
        CheckConstraint("signal IN ('STRENGTHENING', 'STABLE', 'WEAKENING', 'REVIEW_REQUIRED')", name="ck_investment_theses_signal"),
        Index("ix_investment_theses_ticker", "ticker", unique=True),
        Index("ix_investment_theses_review_due_date", "review_due_date"),
        Index("ix_investment_theses_status_signal", "status", "signal"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False)
    cik: Mapped[str] = mapped_column(String(10), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    bull_case: Mapped[str | None] = mapped_column(Text)
    bear_case: Mapped[str | None] = mapped_column(Text)
    invalidation_criteria: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(12), nullable=False)
    conviction: Mapped[str] = mapped_column(String(6), nullable=False)
    signal: Mapped[str] = mapped_column(String(16), nullable=False)
    review_due_date: Mapped[date | None] = mapped_column(Date)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    evidence: Mapped[list["ThesisEvidence"]] = relationship(
        back_populates="thesis",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ThesisEvidence(Base):
    __tablename__ = "thesis_evidence"
    __table_args__ = (
        CheckConstraint("stance IN ('SUPPORTING', 'CONTRADICTING', 'NEUTRAL')", name="ck_thesis_evidence_stance"),
        CheckConstraint("category IN ('FINANCIAL', 'COMPETITIVE', 'MANAGEMENT', 'VALUATION', 'CATALYST', 'RISK', 'FILING', 'OTHER')", name="ck_thesis_evidence_category"),
        CheckConstraint("length(trim(title)) > 0", name="ck_thesis_evidence_title_not_blank"),
        CheckConstraint("length(trim(description)) > 0", name="ck_thesis_evidence_description_not_blank"),
        Index("ix_thesis_evidence_thesis_id", "thesis_id"),
        Index("ix_thesis_evidence_observed_on", "observed_on"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    thesis_id: Mapped[int] = mapped_column(ForeignKey("investment_theses.id", ondelete="CASCADE"), nullable=False)
    stance: Mapped[str] = mapped_column(String(14), nullable=False)
    category: Mapped[str] = mapped_column(String(11), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    observed_on: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    thesis: Mapped[InvestmentThesis] = relationship(back_populates="evidence")
