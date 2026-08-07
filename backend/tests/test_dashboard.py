"""Contract tests for the persisted dashboard thesis summary."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.routes.companies import get_company_service
from app.main import app
from app.services.company_service import CompanyService

DASHBOARD_URL = "/api/v1/dashboard/overview"


class CompanySource:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    async def get_company_tickers(self) -> dict:
        return self.payload


@pytest.fixture
def client(migrated_database_url: str, company_tickers_payload: dict) -> Iterator[TestClient]:
    del migrated_database_url
    app.dependency_overrides[get_company_service] = lambda: CompanyService(CompanySource(company_tickers_payload))
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_dashboard_is_empty_before_theses_exist(client: TestClient) -> None:
    response = client.get(DASHBOARD_URL)
    assert response.status_code == 200
    assert response.json()["thesis_signals"] == []
    assert response.json()["as_of"].endswith("Z")


def test_dashboard_returns_persisted_review_priority(client: TestClient) -> None:
    created = client.post(
        "/api/v1/theses",
        json={
            "ticker": "MSFT",
            "title": "Durable enterprise AI distribution",
            "summary": "Microsoft can monetize AI through enterprise distribution.",
            "status": "ACTIVE",
            "conviction": "HIGH",
            "signal": "REVIEW_REQUIRED",
        },
    )
    assert created.status_code == 201, created.text

    payload = client.get(DASHBOARD_URL).json()
    assert len(payload["thesis_signals"]) == 1
    assert payload["thesis_signals"][0]["ticker"] == "MSFT"
    assert payload["thesis_signals"][0]["signal"] == "REVIEW_REQUIRED"
    assert "watchlist" not in payload
    assert "portfolio_summary" not in payload


def test_dashboard_cors_allows_local_frontend_origin(client: TestClient) -> None:
    response = client.get(DASHBOARD_URL, headers={"Origin": "http://127.0.0.1:3000"})
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
