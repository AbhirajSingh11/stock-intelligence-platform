"""Persistence, API contract, concurrency, and restart tests for watchlists."""

import asyncio
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.routes.companies import get_company_service
from app.db.session import Database
from app.exceptions import WatchlistEntryExistsError
from app.main import app
from app.services.company_service import CompanyService
from app.services.watchlist_service import WatchlistService

WATCHLIST_URL = "/api/v1/watchlist"


class FixtureCompanySource:
    def __init__(self, tickers: dict[str, Any]) -> None:
        self._tickers = tickers

    async def get_company_tickers(self) -> dict[str, Any]:
        return self._tickers


@pytest.fixture
def company_service(company_tickers_payload: dict[str, Any]) -> CompanyService:
    return CompanyService(FixtureCompanySource(company_tickers_payload))


@pytest.fixture
def api_client(
    migrated_database_url: str,
    company_service: CompanyService,
) -> Iterator[TestClient]:
    del migrated_database_url
    app.dependency_overrides[get_company_service] = lambda: company_service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_empty_watchlist_contract(api_client: TestClient) -> None:
    response = api_client.get(WATCHLIST_URL)

    assert response.status_code == 200
    assert response.json() == {"entries": []}


def test_create_normalizes_and_persists_official_sec_identity(
    api_client: TestClient,
) -> None:
    response = api_client.post(WATCHLIST_URL, json={"ticker": " msft "})

    assert response.status_code == 201
    payload = response.json()
    assert payload["ticker"] == "MSFT"
    assert payload["cik"] == "0000789019"
    assert payload["company_name"] == "MICROSOFT CORP"
    assert datetime.fromisoformat(payload["added_at"]).tzinfo is not None
    assert datetime.fromisoformat(payload["updated_at"]).tzinfo is not None

    persisted = api_client.get(WATCHLIST_URL).json()["entries"]
    assert persisted == [payload]


def test_watchlist_is_ordered_alphabetically(api_client: TestClient) -> None:
    for ticker in ("UBER", "GOOG", "MSFT"):
        assert api_client.post(WATCHLIST_URL, json={"ticker": ticker}).status_code == 201

    tickers = [
        entry["ticker"]
        for entry in api_client.get(WATCHLIST_URL).json()["entries"]
    ]
    assert tickers == ["GOOG", "MSFT", "UBER"]


def test_duplicate_create_returns_stable_conflict(api_client: TestClient) -> None:
    assert api_client.post(WATCHLIST_URL, json={"ticker": "MSFT"}).status_code == 201
    duplicate = api_client.post(WATCHLIST_URL, json={"ticker": "msft"})

    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "watchlist_entry_exists"
    assert len(api_client.get(WATCHLIST_URL).json()["entries"]) == 1


@pytest.mark.parametrize("ticker", ["", "   ", "not_valid!", "TOO-LONG-11"])
def test_invalid_create_tickers_return_validation_errors(
    api_client: TestClient,
    ticker: str,
) -> None:
    response = api_client.post(WATCHLIST_URL, json={"ticker": ticker})

    assert response.status_code == 422
    assert response.json()["error"]["code"] in {
        "invalid_ticker",
        "validation_error",
    }


def test_unknown_company_returns_stable_not_found(api_client: TestClient) -> None:
    response = api_client.post(WATCHLIST_URL, json={"ticker": "ZZZZ"})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "company_not_found"


def test_delete_and_unknown_delete_have_stable_contracts(
    api_client: TestClient,
) -> None:
    api_client.post(WATCHLIST_URL, json={"ticker": "MSFT"})

    deleted = api_client.delete(f"{WATCHLIST_URL}/msft")
    missing = api_client.delete(f"{WATCHLIST_URL}/MSFT")

    assert deleted.status_code == 200
    assert deleted.json() == {"ticker": "MSFT", "deleted": True}
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "watchlist_entry_not_found"


def test_persistence_survives_application_restart(
    migrated_database_url: str,
    company_service: CompanyService,
) -> None:
    del migrated_database_url
    app.dependency_overrides[get_company_service] = lambda: company_service
    try:
        with TestClient(app) as first_client:
            assert first_client.post(
                WATCHLIST_URL,
                json={"ticker": "MSFT"},
            ).status_code == 201

        with TestClient(app) as restarted_client:
            entries = restarted_client.get(WATCHLIST_URL).json()["entries"]
            assert [entry["ticker"] for entry in entries] == ["MSFT"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_duplicate_failure_rolls_back_and_session_remains_usable(
    migrated_database_url: str,
    company_service: CompanyService,
) -> None:
    database = Database(migrated_database_url)
    try:
        async with database.session_factory() as session:
            service = WatchlistService(session)
            await service.add_entry("MSFT", company_service)
            with pytest.raises(WatchlistEntryExistsError):
                await service.add_entry("MSFT", company_service)
            created = await service.add_entry("UBER", company_service)
            assert created.ticker == "UBER"
    finally:
        await database.dispose()


@pytest.mark.anyio
async def test_concurrent_duplicate_creates_have_one_stable_winner(
    migrated_database_url: str,
    company_service: CompanyService,
) -> None:
    database = Database(migrated_database_url)

    async def create() -> object:
        async with database.session_factory() as session:
            return await WatchlistService(session).add_entry(
                "MSFT",
                company_service,
            )

    try:
        results = await asyncio.gather(create(), create(), return_exceptions=True)
        successes = [result for result in results if not isinstance(result, Exception)]
        conflicts = [
            result
            for result in results
            if isinstance(result, WatchlistEntryExistsError)
        ]
        assert len(successes) == 1
        assert len(conflicts) == 1

        async with database.session_factory() as session:
            entries = await WatchlistService(session).list_entries()
            assert [entry.ticker for entry in entries.entries] == ["MSFT"]
    finally:
        await database.dispose()


def test_watchlist_cors_supports_writes(api_client: TestClient) -> None:
    response = api_client.options(
        WATCHLIST_URL,
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
    assert "POST" in response.headers["access-control-allow-methods"]
