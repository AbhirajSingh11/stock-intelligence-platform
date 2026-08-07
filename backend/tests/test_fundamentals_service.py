"""Offline financial normalization tests using a captured SEC-shaped fixture."""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest

from app.services.company_service import CompanyService
from app.services.fundamentals_service import FundamentalsService

FIXED_NOW = datetime(2025, 5, 1, 12, 0, tzinfo=timezone.utc)


class FixtureSecClient:
    def __init__(
        self,
        tickers: dict[str, Any],
        company_facts: dict[str, Any],
    ) -> None:
        self.tickers = tickers
        self.company_facts = company_facts
        self.company_facts_requests = 0

    async def get_company_tickers(self) -> dict[str, Any]:
        return self.tickers

    async def get_company_facts(self, _cik: str | int) -> dict[str, Any]:
        self.company_facts_requests += 1
        return self.company_facts

    async def get_company_submissions(self, _cik: str | int) -> dict[str, Any]:
        raise AssertionError("Fundamentals must not request submissions data.")


def build_service(
    tickers: dict[str, Any],
    company_facts: dict[str, Any],
) -> tuple[FundamentalsService, FixtureSecClient]:
    client = FixtureSecClient(tickers, company_facts)
    company_service = CompanyService(client)
    return (
        FundamentalsService(client, company_service, now=lambda: FIXED_NOW),
        client,
    )


def series_by_key(response: Any, period: str) -> dict[str, Any]:
    return {series.metric_key: series for series in getattr(response, period)}


@pytest.mark.anyio
async def test_normalizes_raw_fallback_and_derived_series(
    company_tickers_payload: dict[str, Any],
    msft_company_facts_payload: dict[str, Any],
) -> None:
    service, client = build_service(
        company_tickers_payload,
        msft_company_facts_payload,
    )

    response = await service.get_company_fundamentals("msft")
    annual = series_by_key(response, "annual")
    quarterly = series_by_key(response, "quarterly")

    assert client.company_facts_requests == 1
    assert response.company.ticker == "MSFT"
    assert response.company.cik == "0000789019"
    assert response.data_as_of == datetime(
        2025,
        4,
        30,
        tzinfo=timezone.utc,
    )
    assert len(response.annual) == 8
    assert len(response.quarterly) == 8

    assert [fact.value for fact in annual["revenue"].facts] == [
        211_915_000_000,
        245_122_000_001,
    ]
    assert annual["revenue"].facts[0].source_tag == "Revenues"
    assert annual["revenue"].facts[0].is_fallback is True
    assert annual["revenue"].facts[1].is_restated is True

    assert [fact.value for fact in quarterly["revenue"].facts] == [
        65_585_000_000,
        69_632_000_000,
        70_066_000_000,
    ]
    assert all(
        fact.period_start is not None for fact in quarterly["revenue"].facts
    )
    assert quarterly["revenue"].facts[1].value != 135_217_000_000

    derived_debt = annual["debt"].facts[0]
    assert derived_debt.value == 47_237_000_000
    assert derived_debt.is_derived is True
    assert derived_debt.is_fallback is True
    assert len(derived_debt.component_sources) == 2

    annual_margin = annual["operating_margin"].facts[-1]
    assert annual_margin.value == pytest.approx(
        109_433_000_000 / 245_122_000_001
    )
    assert annual_margin.unit == "pure"
    assert annual_margin.is_derived is True
    assert len(annual_margin.component_sources) == 2
    assert annual_margin.source_filing_url.startswith("https://www.sec.gov/")
    assert all(
        source.source_filing_url.startswith("https://www.sec.gov/")
        for source in annual_margin.component_sources
    )


@pytest.mark.anyio
async def test_incompatible_ratio_provenance_creates_gap_and_warning(
    company_tickers_payload: dict[str, Any],
    msft_company_facts_payload: dict[str, Any],
) -> None:
    payload = deepcopy(msft_company_facts_payload)
    operating_facts = payload["facts"]["us-gaap"]["OperatingIncomeLoss"][
        "units"
    ]["USD"]
    for fact in operating_facts:
        if fact["end"] == "2024-06-30":
            fact["start"] = "2023-07-02"

    service, _client = build_service(company_tickers_payload, payload)
    response = await service.get_company_fundamentals("MSFT")
    annual = series_by_key(response, "annual")

    assert [fact.period_end.isoformat() for fact in annual["operating_margin"].facts] == [
        "2023-06-30"
    ]
    assert any(
        warning.code == "incompatible_ratio_components"
        and warning.metric_key == "operating_margin"
        for warning in response.warnings
    )


@pytest.mark.anyio
async def test_primary_tag_wins_over_fallback_for_the_same_period(
    company_tickers_payload: dict[str, Any],
    msft_company_facts_payload: dict[str, Any],
) -> None:
    payload = deepcopy(msft_company_facts_payload)
    payload["facts"]["us-gaap"]["Revenues"]["units"]["USD"].append(
        {
            "start": "2023-07-01",
            "end": "2024-06-30",
            "val": 999,
            "accn": "0000000000-24-999999",
            "fy": 2024,
            "fp": "FY",
            "form": "10-K/A",
            "filed": "2024-09-01",
            "frame": "CY2023",
        }
    )
    service, _client = build_service(company_tickers_payload, payload)

    response = await service.get_company_fundamentals("MSFT")
    revenue = series_by_key(response, "annual")["revenue"].facts[-1]

    assert revenue.value == 245_122_000_001
    assert revenue.source_tag == (
        "RevenueFromContractWithCustomerExcludingAssessedTax"
    )
    assert revenue.is_fallback is False


@pytest.mark.anyio
async def test_incompatible_units_and_malformed_concepts_are_nonfatal(
    company_tickers_payload: dict[str, Any],
    msft_company_facts_payload: dict[str, Any],
) -> None:
    payload = deepcopy(msft_company_facts_payload)
    payload["facts"]["us-gaap"]["EarningsPerShareDiluted"]["units"] = {
        "shares": [{"val": 3.5}]
    }
    payload["facts"]["us-gaap"]["CashAndCashEquivalentsAtCarryingValue"] = []
    service, _client = build_service(company_tickers_payload, payload)

    response = await service.get_company_fundamentals("MSFT")

    assert any(series.facts for series in response.annual)
    assert any(
        warning.code == "incompatible_unit"
        and warning.metric_key == "diluted_eps"
        for warning in response.warnings
    )
    assert any(
        warning.code == "malformed_concept" and warning.metric_key == "cash"
        for warning in response.warnings
    )
    assert {item.metric_key for item in response.unavailable_metrics} >= {
        "diluted_eps",
        "cash",
    }


@pytest.mark.anyio
async def test_missing_debt_components_do_not_invent_a_value(
    company_tickers_payload: dict[str, Any],
    msft_company_facts_payload: dict[str, Any],
) -> None:
    payload = deepcopy(msft_company_facts_payload)
    concepts = payload["facts"]["us-gaap"]
    del concepts["LongTermDebt"]
    del concepts["LongTermDebtCurrent"]
    del concepts["LongTermDebtNoncurrent"]
    service, _client = build_service(company_tickers_payload, payload)

    response = await service.get_company_fundamentals("MSFT")

    assert {
        (item.metric_key, item.period) for item in response.unavailable_metrics
    } >= {("debt", "annual"), ("debt", "quarterly")}
    assert any(
        warning.code == "metric_unavailable" and warning.metric_key == "debt"
        for warning in response.warnings
    )


@pytest.mark.anyio
async def test_missing_concept_is_partial_success_with_unavailable_metric(
    company_tickers_payload: dict[str, Any],
    msft_company_facts_payload: dict[str, Any],
) -> None:
    payload = deepcopy(msft_company_facts_payload)
    del payload["facts"]["us-gaap"]["EarningsPerShareDiluted"]
    service, _client = build_service(company_tickers_payload, payload)

    response = await service.get_company_fundamentals("MSFT")

    assert response.company.ticker == "MSFT"
    assert any(series.facts for series in response.annual)
    assert {
        (item.metric_key, item.period) for item in response.unavailable_metrics
    } >= {("diluted_eps", "annual"), ("diluted_eps", "quarterly")}


@pytest.mark.anyio
async def test_series_limits_keep_most_recent_periods(
    company_tickers_payload: dict[str, Any],
    msft_company_facts_payload: dict[str, Any],
) -> None:
    payload = deepcopy(msft_company_facts_payload)
    revenue = payload["facts"]["us-gaap"][
        "RevenueFromContractWithCustomerExcludingAssessedTax"
    ]["units"]["USD"]
    revenue.extend(
        {
            "start": f"{year - 1}-01-01",
            "end": f"{year - 1}-12-31",
            "val": year,
            "accn": f"0000000001-{str(year)[-2:]}-000001",
            "fy": year,
            "fp": "FY",
            "form": "10-K",
            "filed": f"{year}-02-01",
            "frame": f"CY{year - 1}",
        }
        for year in range(2015, 2023)
    )
    revenue.extend(
        {
            "start": f"{year}-01-01",
            "end": f"{year}-03-31",
            "val": year,
            "accn": f"0000000001-{str(year)[-2:]}-000002",
            "fy": year,
            "fp": "Q1",
            "form": "10-Q",
            "filed": f"{year}-04-30",
            "frame": f"CY{year}Q1",
        }
        for year in range(2014, 2024)
    )
    service, _client = build_service(company_tickers_payload, payload)

    response = await service.get_company_fundamentals("MSFT")
    annual = series_by_key(response, "annual")["revenue"].facts
    quarterly = series_by_key(response, "quarterly")["revenue"].facts

    assert len(annual) == 5
    assert len(quarterly) == 8
    assert annual == sorted(annual, key=lambda fact: fact.period_end)
    assert quarterly == sorted(quarterly, key=lambda fact: fact.period_end)
