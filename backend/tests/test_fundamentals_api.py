"""HTTP contract tests for the company fundamentals endpoint."""

from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.routes.fundamentals import get_fundamentals_service
from app.main import app
from app.services.company_service import CompanyService
from app.services.fundamentals_service import FundamentalsService


class FixtureSecClient:
    def __init__(
        self,
        tickers: dict[str, Any],
        company_facts: dict[str, Any],
    ) -> None:
        self.tickers = tickers
        self.company_facts = company_facts

    async def get_company_tickers(self) -> dict[str, Any]:
        return self.tickers

    async def get_company_facts(self, _cik: str | int) -> dict[str, Any]:
        return self.company_facts

    async def get_company_submissions(self, _cik: str | int) -> dict[str, Any]:
        raise AssertionError("Unexpected submissions request")


@pytest.fixture
def fundamentals_api_client(
    company_tickers_payload: dict[str, Any],
    msft_company_facts_payload: dict[str, Any],
) -> Iterator[TestClient]:
    sec_client = FixtureSecClient(
        company_tickers_payload,
        msft_company_facts_payload,
    )
    company_service = CompanyService(sec_client)
    service = FundamentalsService(
        sec_client,
        company_service,
        now=lambda: datetime(2025, 5, 1, tzinfo=timezone.utc),
    )
    app.dependency_overrides[get_fundamentals_service] = lambda: service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_fundamentals_contract(fundamentals_api_client: TestClient) -> None:
    response = fundamentals_api_client.get(
        "/api/v1/companies/MSFT/fundamentals"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["company"] == {
        "ticker": "MSFT",
        "company_name": "MICROSOFT CORPORATION",
        "cik": "0000789019",
    }
    assert payload["data_as_of"] == "2025-04-30T00:00:00Z"
    assert {series["metric_key"] for series in payload["annual"]} == {
        "revenue",
        "operating_income",
        "net_income",
        "diluted_eps",
        "cash",
        "debt",
        "operating_margin",
        "net_margin",
    }
    assert len(payload["quarterly"]) == 8
    revenue = next(
        series for series in payload["annual"] if series["metric_key"] == "revenue"
    )
    assert isinstance(revenue["facts"][-1]["value"], int)
    assert revenue["facts"][-1]["period_end"] == "2024-06-30"
    assert payload["provenance"]["company_facts_url"].endswith(
        "CIK0000789019.json"
    )


def test_fundamentals_preserves_company_error_contracts(
    fundamentals_api_client: TestClient,
) -> None:
    unknown = fundamentals_api_client.get(
        "/api/v1/companies/ZZZZ/fundamentals"
    )
    invalid = fundamentals_api_client.get(
        "/api/v1/companies/not_valid!/fundamentals"
    )

    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "company_not_found"
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_ticker"


def test_existing_routes_remain_available(
    fundamentals_api_client: TestClient,
) -> None:
    assert fundamentals_api_client.get("/health").status_code == 200
    assert fundamentals_api_client.get("/api/v1/dashboard/overview").status_code == 200
