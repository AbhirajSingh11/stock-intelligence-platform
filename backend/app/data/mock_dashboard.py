"""Deterministic backend-owned thesis signals retained for Milestone 7."""

MOCK_DASHBOARD_OVERVIEW: dict[str, object] = {
    "as_of": "2026-07-28T20:00:00Z",
    "thesis_signals": [
        {
            "ticker": "MSFT",
            "company": "Microsoft",
            "state": "Strengthening",
            "tone": "positive",
            "last_reviewed": "2026-07-22",
        },
        {
            "ticker": "UBER",
            "company": "Uber",
            "state": "Review required",
            "tone": "warning",
            "last_reviewed": "2026-07-12",
        },
        {
            "ticker": "GOOG",
            "company": "Alphabet",
            "state": "Stable",
            "tone": "neutral",
            "last_reviewed": "2026-07-18",
        },
    ],
}
