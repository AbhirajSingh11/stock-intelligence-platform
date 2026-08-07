"""Unit tests for clock-independent thesis rules."""

from datetime import date, datetime, timezone
from types import SimpleNamespace

from app.services.thesis_domain import dashboard_priority, is_overdue


def thesis(ticker: str, *, due: date | None, status: str = "ACTIVE", signal: str = "STABLE", day: int = 1):
    return SimpleNamespace(
        ticker=ticker,
        review_due_date=due,
        status=status,
        signal=signal,
        updated_at=datetime(2026, 1, day, tzinfo=timezone.utc),
    )


def test_overdue_is_derived_only_for_reviewable_statuses() -> None:
    today = date(2026, 8, 7)
    assert is_overdue("ACTIVE", date(2026, 8, 6), today)
    assert is_overdue("DRAFT", date(2026, 8, 6), today)
    assert not is_overdue("ACTIVE", today, today)
    assert not is_overdue("ARCHIVED", date(2026, 1, 1), today)
    assert not is_overdue("INVALIDATED", date(2026, 1, 1), today)
    assert not is_overdue("ACTIVE", None, today)


def test_dashboard_priority_is_overdue_then_review_required_then_recent_active() -> None:
    today = date(2026, 8, 7)
    items = [
        thesis("RECENT", due=None, day=5),
        thesis("REVIEW", due=None, signal="REVIEW_REQUIRED", day=2),
        thesis("OVER2", due=date(2026, 8, 2), day=3),
        thesis("OVER1", due=date(2026, 8, 1), day=4),
        thesis("OLD", due=None, day=1),
        thesis("ARCH", due=date(2026, 1, 1), status="ARCHIVED"),
    ]
    assert [item.ticker for item in dashboard_priority(items, today)] == [
        "OVER1", "OVER2", "REVIEW", "RECENT", "OLD"
    ]
