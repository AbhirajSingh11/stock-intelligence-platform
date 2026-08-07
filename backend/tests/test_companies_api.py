"""Contract tests for versioned company research endpoints."""

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.routes.companies import get_company_service
from app.exceptions import (
    SecConfigurationError,
    SecMalformedResponseError,
    SecRateLimitError,
    SecTimeoutError,
    SecUpstreamError,
)
from app.main import app
from app.services.company_service import CompanyService


class FixtureSecClient:
    def __init__(
        self,
        tickers: dict[str, Any],
        submissions: dict[str, Any],
    ) -> None:
        self.tickers = tickers
        self.submissions = submissions

    async def get_company_tickers(self) -> dict[str, Any]:
        return self.tickers

    async def get_company_submissions(self, _cik: str | int) -> dict[str, Any]:
        return self.submissions


@pytest.fixture
def api_client(
    migrated_database_url: str,
    company_tickers_payload: dict[str, Any],
    msft_submissions_payload: dict[str, Any],
) -> Iterator[TestClient]:
    del migrated_database_url
    service = CompanyService(
        FixtureSecClient(
            company_tickers_payload,
            msft_submissions_payload,
        )
    )
    app.dependency_overrides[get_company_service] = lambda: service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_search_contract_and_ranking(api_client: TestClient) -> None:
    response = api_client.get(
        "/api/v1/companies/search",
        params={"query": "msft", "limit": 2},
    )

    assert response.status_code == 200
    assert response.json() == {
        "query": "msft",
        "results": [
            {
                "ticker": "MSFT",
                "company_name": "MICROSOFT CORP",
                "cik": "0000789019",
            },
            {
                "ticker": "XMSFT",
                "company_name": "Example Holdings",
                "cik": "0001000002",
            },
        ],
    }


@pytest.mark.parametrize("query", ["", "m", "   "])
def test_short_or_blank_query_has_stable_error(
    api_client: TestClient,
    query: str,
) -> None:
    response = api_client.get(
        "/api/v1/companies/search",
        params={"query": query},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_query"


def test_company_and_filings_contracts(api_client: TestClient) -> None:
    company_response = api_client.get("/api/v1/companies/msft")
    filings_response = api_client.get(
        "/api/v1/companies/msft/filings",
        params={"forms": "10-K,8-K", "limit": 1},
    )
    default_filings_response = api_client.get(
        "/api/v1/companies/msft/filings"
    )

    assert company_response.status_code == 200
    assert company_response.json()["cik"] == "0000789019"
    assert filings_response.status_code == 200
    assert filings_response.json()["forms"] == ["10-K", "8-K"]
    assert filings_response.json()["filings"][0]["form"] == "8-K"
    assert default_filings_response.status_code == 200
    assert default_filings_response.json()["forms"] == ["10-K", "10-Q", "8-K"]


def test_unknown_and_invalid_tickers_are_distinct(api_client: TestClient) -> None:
    unknown = api_client.get("/api/v1/companies/ZZZZ")
    invalid = api_client.get("/api/v1/companies/not_valid!")

    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "company_not_found"
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_ticker"


def test_invalid_limit_has_stable_validation_contract(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        "/api/v1/companies/search",
        params={"query": "MSFT", "limit": 999},
    )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "validation_error",
            "message": "One or more request parameters are invalid.",
        }
    }


@pytest.mark.parametrize(
    ("error", "status_code", "code"),
    [
        (SecConfigurationError(), 503, "sec_configuration_missing"),
        (SecTimeoutError(), 504, "sec_timeout"),
        (SecRateLimitError(), 429, "sec_rate_limited"),
        (SecUpstreamError(), 502, "sec_upstream_failure"),
        (SecMalformedResponseError(), 502, "sec_malformed_response"),
    ],
)
def test_upstream_errors_have_stable_public_contracts(
    error: Exception,
    status_code: int,
    code: str,
) -> None:
    def raise_error() -> None:
        raise error

    app.dependency_overrides[get_company_service] = raise_error
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/companies/search",
            params={"query": "MSFT"},
        )
    app.dependency_overrides.clear()

    assert response.status_code == status_code
    assert response.json()["error"]["code"] == code
    assert "SEC" in response.json()["error"]["message"]


def test_existing_endpoints_remain_available(api_client: TestClient) -> None:
    assert api_client.get("/health").status_code == 200
    assert api_client.get("/api/v1/dashboard/overview").status_code == 200
