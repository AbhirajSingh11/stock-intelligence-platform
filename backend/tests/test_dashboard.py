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
        "thesis_signals",
    }
    assert payload["as_of"] == "2026-07-28T20:00:00Z"


def test_dashboard_overview_contains_thesis_data_without_mock_watchlist() -> None:
    payload = client.get(DASHBOARD_URL).json()

    assert [signal["ticker"] for signal in payload["thesis_signals"]] == [
        "MSFT",
        "UBER",
        "GOOG",
    ]
    assert payload["thesis_signals"][1]["state"] == "Review required"
    assert "watchlist" not in payload
    assert "portfolio_summary" not in payload
    assert "performance" not in payload


def test_dashboard_cors_allows_local_frontend_origin() -> None:
    response = client.get(
        DASHBOARD_URL,
        headers={"Origin": "http://127.0.0.1:3000"},
    )

    assert response.headers["access-control-allow-origin"] == (
        "http://127.0.0.1:3000"
    )
