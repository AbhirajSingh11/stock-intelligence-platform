"""Pure thesis rules kept independent from HTTP, clocks, and persistence."""

from datetime import date, datetime
from typing import Protocol

from app.models.thesis import InvestmentThesis, ThesisEvidence
from app.schemas.thesis import EvidenceCounts, ThesisJournalCounts

REVIEWABLE_STATUSES = {"DRAFT", "ACTIVE"}


class ThesisLike(Protocol):
    ticker: str
    status: str
    signal: str
    review_due_date: date | None
    updated_at: datetime


def is_overdue(status: str, review_due_date: date | None, today: date) -> bool:
    return status in REVIEWABLE_STATUSES and review_due_date is not None and review_due_date < today


def evidence_counts(evidence: list[ThesisEvidence]) -> EvidenceCounts:
    supporting = sum(item.stance == "SUPPORTING" for item in evidence)
    contradicting = sum(item.stance == "CONTRADICTING" for item in evidence)
    neutral = sum(item.stance == "NEUTRAL" for item in evidence)
    return EvidenceCounts(
        supporting=supporting,
        contradicting=contradicting,
        neutral=neutral,
        total=supporting + contradicting + neutral,
    )


def ordered_evidence(evidence: list[ThesisEvidence]) -> list[ThesisEvidence]:
    return sorted(evidence, key=lambda item: (item.observed_on, item.created_at, item.id), reverse=True)


def ordered_theses(theses: list[InvestmentThesis], today: date) -> list[InvestmentThesis]:
    far_future = date.max
    return sorted(
        theses,
        key=lambda item: (
            not is_overdue(item.status, item.review_due_date, today),
            item.review_due_date is None,
            item.review_due_date or far_future,
            item.ticker,
        ),
    )


def journal_counts(theses: list[InvestmentThesis], today: date) -> ThesisJournalCounts:
    return ThesisJournalCounts(
        total=len(theses),
        active=sum(item.status == "ACTIVE" for item in theses),
        overdue=sum(is_overdue(item.status, item.review_due_date, today) for item in theses),
        review_required=sum(item.signal == "REVIEW_REQUIRED" for item in theses),
    )


def dashboard_priority(theses: list[InvestmentThesis], today: date, limit: int = 5) -> list[InvestmentThesis]:
    candidates = [item for item in theses if item.status in REVIEWABLE_STATUSES]

    def key(item: InvestmentThesis) -> tuple[int, int, date, float, str]:
        overdue = is_overdue(item.status, item.review_due_date, today)
        tier = 0 if overdue else 1 if item.signal == "REVIEW_REQUIRED" else 2
        due = item.review_due_date or date.max
        return (tier, item.review_due_date is None, due, -item.updated_at.timestamp(), item.ticker)

    return sorted(candidates, key=key)[:limit]
