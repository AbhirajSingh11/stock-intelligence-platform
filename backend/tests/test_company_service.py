"""Normalization and ranking tests for the company service."""

from typing import Any

import pytest

from app.exceptions import CompanyNotFoundError, InvalidTickerError
from app.schemas.company import CompanyFilingsParams, CompanySearchParams
from app.services.company_service import (
    CompanyService,
    format_cik,
    normalize_ticker,
)


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


def build_service(
    company_tickers_payload: dict[str, Any],
    msft_submissions_payload: dict[str, Any],
) -> CompanyService:
    return CompanyService(
        FixtureSecClient(
            company_tickers_payload,
            msft_submissions_payload,
        )
    )


def test_ticker_and_cik_normalization() -> None:
    assert normalize_ticker(" msft ") == "MSFT"
    assert normalize_ticker("brk.b") == "BRK.B"
    assert format_cik(789019) == "0000789019"

    with pytest.raises(InvalidTickerError):
        normalize_ticker("../msft")


@pytest.mark.anyio
async def test_search_ranking(
    company_tickers_payload: dict[str, Any],
    msft_submissions_payload: dict[str, Any],
) -> None:
    service = build_service(company_tickers_payload, msft_submissions_payload)

    response = await service.search_companies(
        CompanySearchParams(query="msft", limit=8)
    )

    assert [result.ticker for result in response.results] == ["MSFT", "XMSFT"]
    assert response.results[0].cik == "0000789019"


@pytest.mark.anyio
async def test_company_profile_is_normalized(
    company_tickers_payload: dict[str, Any],
    msft_submissions_payload: dict[str, Any],
) -> None:
    service = build_service(company_tickers_payload, msft_submissions_payload)

    company = await service.get_company_profile("msft")

    assert company.ticker == "MSFT"
    assert company.company_name == "MICROSOFT CORP"
    assert company.cik == "0000789019"
    assert company.sic_code == "7372"
    assert company.exchanges == ["Nasdaq"]
    assert company.business_address is not None
    assert company.business_address.city == "REDMOND"
    assert company.former_names[0].name == "MICROSOFT INC"
    assert company.sec_company_url.startswith("https://www.sec.gov/")


@pytest.mark.anyio
async def test_filings_are_filtered_limited_and_linked(
    company_tickers_payload: dict[str, Any],
    msft_submissions_payload: dict[str, Any],
) -> None:
    service = build_service(company_tickers_payload, msft_submissions_payload)

    response = await service.get_company_filings(
        "MSFT",
        CompanyFilingsParams(forms=("10-Q", "8-K", "10-K"), limit=2),
    )

    assert [filing.form for filing in response.filings] == ["10-Q", "8-K"]
    assert len(response.filings) == 2
    first = response.filings[0]
    assert "/789019/000095017025100001/" in first.filing_detail_url
    assert first.filing_detail_url.endswith(
        "/0000950170-25-100001-index.html"
    )
    assert first.primary_document_url.endswith("/msft-20250630.htm")
    assert first.filing_detail_url.startswith("https://www.sec.gov/")


@pytest.mark.anyio
async def test_unknown_ticker_is_not_found(
    company_tickers_payload: dict[str, Any],
    msft_submissions_payload: dict[str, Any],
) -> None:
    service = build_service(company_tickers_payload, msft_submissions_payload)

    with pytest.raises(CompanyNotFoundError):
        await service.get_company_profile("ZZZZ")
