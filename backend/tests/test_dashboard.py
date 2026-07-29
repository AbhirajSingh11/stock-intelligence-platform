"""Contract tests for the versioned dashboard overview endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
DASHBOARD_URL = "/api/v1/dashboard/overview"


def test_dashboard_overview_returns_success() -> None:
    response = client.get(DASHBOARD_URL)

    assert response.status_code == 200


def test_dashboard_overview_has_expected_structure() -> None:
    payload = client.get(DASHBOARD_URL).json()

    assert set(payload) == {
        "as_of",
        "currency",
        "portfolio_summary",
        "performance",
        "thesis_signals",
        "watchlist",
    }
    assert payload["as_of"] == "2026-07-28T20:00:00Z"
    assert payload["currency"] == "USD"
    assert set(payload["portfolio_summary"]) == {
        "total_value",
        "total_gain",
        "total_return_percent",
        "today_change",
        "today_change_percent",
        "position_count",
    }


def test_dashboard_overview_contains_representative_portfolio_values() -> None:
    summary = client.get(DASHBOARD_URL).json()["portfolio_summary"]

    assert summary["total_value"] == 24860.42
    assert summary["total_gain"] == 2814.16
    assert summary["total_return_percent"] == 12.8
    assert summary["today_change"] == 184.32


def test_dashboard_overview_contains_every_chart_period() -> None:
    performance = client.get(DASHBOARD_URL).json()["performance"]

    assert [series["period"] for series in performance] == [
        "1M",
        "3M",
        "6M",
        "1Y",
        "ALL",
    ]
    assert all(series["points"] for series in performance)
    assert all(
        series["start_date"] <= series["end_date"] for series in performance
    )


def test_dashboard_overview_contains_thesis_and_watchlist_data() -> None:
    payload = client.get(DASHBOARD_URL).json()

    assert [signal["ticker"] for signal in payload["thesis_signals"]] == [
        "MSFT",
        "UBER",
        "GOOG",
    ]
    assert payload["thesis_signals"][1]["state"] == "Review required"
    assert [company["ticker"] for company in payload["watchlist"]] == [
        "MSFT",
        "UBER",
        "GOOG",
    ]
    assert payload["watchlist"][0]["position_value"] == 10560.40


def test_dashboard_cors_allows_local_frontend_origin() -> None:
    response = client.get(
        DASHBOARD_URL,
        headers={"Origin": "http://127.0.0.1:3000"},
    )

    assert response.headers["access-control-allow-origin"] == (
        "http://127.0.0.1:3000"
    )

