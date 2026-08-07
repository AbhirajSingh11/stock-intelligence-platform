"""Persistence, API, evidence, review, and validation tests for theses."""

from collections.abc import Iterator
from datetime import datetime, timezone
import sqlite3
from typing import Any

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.companies import get_company_service
from app.api.routes.theses import get_thesis_service
from app.db.session import get_db_session
from app.main import app
from app.services.company_service import CompanyService
from app.services.thesis_service import ThesisService

THESIS_URL = "/api/v1/theses"
FIXED_NOW = datetime(2026, 8, 7, 15, 30, tzinfo=timezone.utc)


class CountingCompanySource:
    def __init__(self, tickers: dict[str, Any]) -> None:
        self.tickers = tickers
        self.requests = 0

    async def get_company_tickers(self) -> dict[str, Any]:
        self.requests += 1
        return self.tickers


@pytest.fixture
def company_source(company_tickers_payload: dict[str, Any]) -> CountingCompanySource:
    return CountingCompanySource(company_tickers_payload)


@pytest.fixture
def client(migrated_database_url: str, company_source: CountingCompanySource) -> Iterator[TestClient]:
    del migrated_database_url
    company_service = CompanyService(company_source)

    def fixed_service(session: AsyncSession = Depends(get_db_session)) -> ThesisService:
        return ThesisService(session, now_provider=lambda: FIXED_NOW)

    app.dependency_overrides[get_company_service] = lambda: company_service
    app.dependency_overrides[get_thesis_service] = fixed_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def thesis_payload(ticker: str = "MSFT", **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ticker": ticker,
        "title": "Durable enterprise AI distribution",
        "summary": "Microsoft can monetize AI through its existing enterprise distribution.",
        "bull_case": "Azure and Copilot expand revenue per customer.",
        "bear_case": "AI infrastructure costs pressure margins.",
        "invalidation_criteria": "Sustained Copilot weakness combined with declining Azure growth.",
        "status": "ACTIVE",
        "conviction": "HIGH",
        "signal": "STABLE",
        "review_due_date": "2026-09-30",
    }
    payload.update(overrides)
    return payload


def create_thesis(client: TestClient, ticker: str = "MSFT", **overrides: Any) -> dict[str, Any]:
    response = client.post(THESIS_URL, json=thesis_payload(ticker, **overrides))
    assert response.status_code == 201, response.text
    return response.json()


def evidence_payload(**overrides: Any) -> dict[str, Any]:
    payload = {
        "stance": "SUPPORTING",
        "category": "FINANCIAL",
        "title": "Cloud growth remains resilient",
        "description": "User-entered test evidence",
        "source_url": "https://www.sec.gov/example",
        "observed_on": "2026-08-01",
    }
    payload.update(overrides)
    return payload


def test_create_uses_official_identity_and_enforces_one_thesis_per_ticker(client: TestClient, company_source: CountingCompanySource) -> None:
    created = create_thesis(client)
    duplicate = client.post(THESIS_URL, json=thesis_payload(ticker=" msft "))
    assert created["ticker"] == "MSFT"
    assert created["cik"] == "0000789019"
    assert created["company_name"] == "MICROSOFT CORP"
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "thesis_exists"
    assert company_source.requests == 1


def test_full_manual_scenario_counts_order_updates_and_review_semantics(client: TestClient) -> None:
    created = create_thesis(client)
    supporting = client.post(f"{THESIS_URL}/MSFT/evidence", json=evidence_payload())
    contradicting = client.post(
        f"{THESIS_URL}/MSFT/evidence",
        json=evidence_payload(
            stance="CONTRADICTING",
            category="RISK",
            title="AI infrastructure spending is increasing",
            description="User-entered risk evidence",
            source_url="",
            observed_on="2026-08-03",
        ),
    )
    assert supporting.status_code == 201
    assert contradicting.status_code == 201
    detail = contradicting.json()
    assert detail["evidence_counts"] == {"supporting": 1, "contradicting": 1, "neutral": 0, "total": 2}
    assert [item["stance"] for item in detail["evidence"]] == ["CONTRADICTING", "SUPPORTING"]
    assert detail["evidence"][0]["source_url"] is None

    changed = client.patch(f"{THESIS_URL}/MSFT", json={"signal": "REVIEW_REQUIRED"})
    assert changed.status_code == 200
    reviewed = client.post(f"{THESIS_URL}/MSFT/review", json={"review_due_date": "2026-12-31"})
    assert reviewed.status_code == 200
    assert reviewed.json()["last_reviewed_at"] == "2026-08-07T15:30:00Z"
    assert reviewed.json()["review_due_date"] == "2026-12-31"
    assert reviewed.json()["signal"] == "REVIEW_REQUIRED"
    assert reviewed.json()["conviction"] == created["conviction"]


def test_list_filters_and_deterministic_overdue_order(client: TestClient) -> None:
    create_thesis(client, review_due_date="2026-09-30")
    create_thesis(client, "UBER", title="Mobility scale", summary="Scale supports durable cash generation.", review_due_date="2026-05-01", signal="WEAKENING")
    response = client.get(THESIS_URL)
    assert [item["ticker"] for item in response.json()["theses"]] == ["UBER", "MSFT"]
    assert response.json()["counts"] == {"total": 2, "active": 2, "overdue": 1, "review_required": 0}
    assert [item["ticker"] for item in client.get(THESIS_URL, params={"overdue": "true"}).json()["theses"]] == ["UBER"]
    assert [item["ticker"] for item in client.get(THESIS_URL, params={"signal": "WEAKENING"}).json()["theses"]] == ["UBER"]
    assert [item["ticker"] for item in client.get(THESIS_URL, params={"ticker": "msft"}).json()["theses"]] == ["MSFT"]


def test_evidence_edit_delete_and_belonging_checks(client: TestClient) -> None:
    create_thesis(client)
    create_thesis(client, "UBER", title="Mobility scale", summary="Scale thesis")
    detail = client.post(f"{THESIS_URL}/MSFT/evidence", json=evidence_payload()).json()
    evidence_id = detail["evidence"][0]["id"]
    wrong = client.patch(f"{THESIS_URL}/UBER/evidence/{evidence_id}", json={"title": "Wrong thesis"})
    assert wrong.status_code == 404
    assert wrong.json()["error"]["code"] == "thesis_evidence_not_found"
    edited = client.patch(f"{THESIS_URL}/MSFT/evidence/{evidence_id}", json={"title": "Updated evidence", "source_url": None})
    assert edited.status_code == 200
    assert edited.json()["evidence"][0]["title"] == "Updated evidence"
    deleted = client.delete(f"{THESIS_URL}/MSFT/evidence/{evidence_id}")
    assert deleted.json() == {"evidence_id": evidence_id, "deleted": True}
    assert client.get(f"{THESIS_URL}/MSFT").json()["evidence_counts"]["total"] == 0


@pytest.mark.parametrize("url", ["ftp://example.com", "javascript:alert(1)", "/relative", "https://"])
def test_evidence_rejects_non_http_source_urls(client: TestClient, url: str) -> None:
    create_thesis(client)
    response = client.post(f"{THESIS_URL}/MSFT/evidence", json=evidence_payload(source_url=url))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_missing_resources_and_malformed_enums_have_stable_errors(client: TestClient) -> None:
    missing = client.get(f"{THESIS_URL}/MSFT")
    malformed = client.post(THESIS_URL, json=thesis_payload(status="PUBLISHED"))
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "thesis_not_found"
    assert malformed.status_code == 422
    assert malformed.json()["error"]["code"] == "validation_error"


def test_delete_thesis_cascades_evidence_in_database(client: TestClient, migrated_database_url: str) -> None:
    create_thesis(client)
    client.post(f"{THESIS_URL}/MSFT/evidence", json=evidence_payload())
    deleted = client.delete(f"{THESIS_URL}/MSFT")
    assert deleted.json() == {"ticker": "MSFT", "deleted": True}
    database_path = migrated_database_url.removeprefix("sqlite+aiosqlite:///")
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT count(*) FROM thesis_evidence").fetchone()[0] == 0


def test_thesis_persists_across_application_lifespans(migrated_database_url: str, company_source: CountingCompanySource) -> None:
    del migrated_database_url
    app.dependency_overrides[get_company_service] = lambda: CompanyService(company_source)
    try:
        with TestClient(app) as first:
            create_thesis(first)
        with TestClient(app) as restarted:
            assert restarted.get(f"{THESIS_URL}/MSFT").json()["title"] == "Durable enterprise AI distribution"
    finally:
        app.dependency_overrides.clear()
