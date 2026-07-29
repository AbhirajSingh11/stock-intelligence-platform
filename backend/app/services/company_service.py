"""Company search, profile, and filing normalization services."""

import re
from typing import Any, Protocol
from urllib.parse import quote

from pydantic import ValidationError

from app.exceptions import (
    CompanyNotFoundError,
    InvalidFilingsQueryError,
    InvalidTickerError,
    SecMalformedResponseError,
)
from app.schemas.company import (
    CompanyAddress,
    CompanyFilingsParams,
    CompanyFilingsResponse,
    CompanyProfileResponse,
    CompanySearchParams,
    CompanySearchResponse,
    CompanySearchResult,
    FilingRecord,
    FormerCompanyName,
)

DEFAULT_FILING_FORMS = ("10-K", "10-Q", "8-K")
TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.-]{0,9}$")
FORM_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9/-]{0,19}$")
SEC_ARCHIVES_BASE_URL = "https://www.sec.gov/Archives/edgar/data"
SEC_COMPANY_BASE_URL = "https://www.sec.gov/edgar/browse/"


class CompanyDataSource(Protocol):
    async def get_company_tickers(self) -> dict[str, Any]:
        """Return the official SEC ticker mapping."""

    async def get_company_submissions(self, cik: str | int) -> dict[str, Any]:
        """Return official SEC submissions for one CIK."""


def normalize_ticker(ticker: str) -> str:
    normalized = ticker.strip().upper()
    if not TICKER_PATTERN.fullmatch(normalized):
        raise InvalidTickerError()
    return normalized


def format_cik(cik: str | int) -> str:
    raw_cik = str(cik).strip()
    if not raw_cik.isdigit() or len(raw_cik) > 10:
        raise SecMalformedResponseError()
    return raw_cik.zfill(10)


def parse_filing_forms(raw_forms: str | None) -> tuple[str, ...]:
    if raw_forms is None:
        return DEFAULT_FILING_FORMS

    forms = tuple(
        form.strip().upper()
        for form in raw_forms.split(",")
        if form.strip()
    )
    if (
        not forms
        or len(forms) > 10
        or len(set(forms)) != len(forms)
        or any(not FORM_PATTERN.fullmatch(form) for form in forms)
    ):
        raise InvalidFilingsQueryError(
            "Forms must be a comma-separated list of up to 10 unique SEC form names."
        )
    return forms


class CompanyService:
    """Application service over normalized SEC EDGAR data."""

    def __init__(self, sec_client: CompanyDataSource) -> None:
        self._sec_client = sec_client

    async def search_companies(
        self,
        params: CompanySearchParams,
    ) -> CompanySearchResponse:
        query = params.query.upper()
        records = await self._ticker_records()

        ranked: list[tuple[int, str, CompanySearchResult]] = []
        for record in records:
            ticker = record.ticker.upper()
            company_name = record.company_name.upper()
            rank: int | None = None
            if ticker == query:
                rank = 0
            elif ticker.startswith(query):
                rank = 1
            elif company_name.startswith(query):
                rank = 2
            elif query in ticker:
                rank = 3
            elif query in company_name:
                rank = 4

            if rank is not None:
                ranked.append((rank, ticker, record))

        ranked.sort(key=lambda item: (item[0], item[1]))
        return CompanySearchResponse(
            query=params.query,
            results=[item[2] for item in ranked[: params.limit]],
        )

    async def get_company_profile(self, ticker: str) -> CompanyProfileResponse:
        normalized_ticker = normalize_ticker(ticker)
        mapping = await self._find_company(normalized_ticker)
        submissions = await self._sec_client.get_company_submissions(mapping.cik)

        try:
            company_name = _required_string(submissions, "name")
            cik = format_cik(submissions.get("cik", mapping.cik))
            addresses = submissions.get("addresses", {})
            if not isinstance(addresses, dict):
                raise SecMalformedResponseError()

            return CompanyProfileResponse(
                ticker=normalized_ticker,
                company_name=company_name,
                cik=cik,
                sic_code=_optional_string(submissions.get("sic")),
                sic_description=_optional_string(submissions.get("sicDescription")),
                exchanges=_string_list(submissions.get("exchanges")),
                fiscal_year_end=_optional_string(submissions.get("fiscalYearEnd")),
                state_of_incorporation=_optional_string(
                    submissions.get("stateOfIncorporationDescription")
                    or submissions.get("stateOfIncorporation")
                ),
                business_address=_normalize_address(addresses.get("business")),
                mailing_address=_normalize_address(addresses.get("mailing")),
                former_names=_normalize_former_names(
                    submissions.get("formerNames")
                ),
                sec_company_url=(
                    f"{SEC_COMPANY_BASE_URL}?CIK={cik}&owner=exclude"
                ),
            )
        except (KeyError, TypeError, ValidationError) as error:
            raise SecMalformedResponseError() from error

    async def get_company_filings(
        self,
        ticker: str,
        params: CompanyFilingsParams,
    ) -> CompanyFilingsResponse:
        normalized_ticker = normalize_ticker(ticker)
        mapping = await self._find_company(normalized_ticker)
        submissions = await self._sec_client.get_company_submissions(mapping.cik)
        cik = format_cik(submissions.get("cik", mapping.cik))

        filings_container = submissions.get("filings")
        if not isinstance(filings_container, dict):
            raise SecMalformedResponseError()
        recent = filings_container.get("recent")
        if not isinstance(recent, dict):
            raise SecMalformedResponseError()

        accession_numbers = recent.get("accessionNumber")
        if not isinstance(accession_numbers, list):
            raise SecMalformedResponseError()

        filings: list[FilingRecord] = []
        for index, accession_value in enumerate(accession_numbers):
            form = _parallel_string(recent, "form", index, required=True)
            if form not in params.forms:
                continue

            accession_number = _as_nonempty_string(accession_value)
            filing_date = _parallel_string(
                recent,
                "filingDate",
                index,
                required=True,
            )
            primary_document = _parallel_string(
                recent,
                "primaryDocument",
                index,
                required=True,
            )
            accession_path = accession_number.replace("-", "")
            cik_path = str(int(cik))
            encoded_document = quote(primary_document, safe="._-")
            archive_directory = (
                f"{SEC_ARCHIVES_BASE_URL}/{cik_path}/{accession_path}"
            )

            try:
                record = FilingRecord(
                    accession_number=accession_number,
                    form=form,
                    filing_date=filing_date,
                    report_date=_parallel_string(
                        recent,
                        "reportDate",
                        index,
                    ),
                    acceptance_timestamp=_parallel_string(
                        recent,
                        "acceptanceDateTime",
                        index,
                    ),
                    primary_document=primary_document,
                    filing_detail_url=(
                        f"{archive_directory}/{accession_number}-index.html"
                    ),
                    primary_document_url=(
                        f"{archive_directory}/{encoded_document}"
                    ),
                    description=_parallel_string(
                        recent,
                        "primaryDocDescription",
                        index,
                    ),
                    items=_parallel_string(recent, "items", index),
                )
            except ValidationError as error:
                raise SecMalformedResponseError() from error

            filings.append(record)
            if len(filings) == params.limit:
                break

        return CompanyFilingsResponse(
            ticker=normalized_ticker,
            cik=cik,
            forms=list(params.forms),
            filings=filings,
        )

    async def _find_company(self, ticker: str) -> CompanySearchResult:
        records = await self._ticker_records()
        for record in records:
            if record.ticker == ticker:
                return record
        raise CompanyNotFoundError()

    async def _ticker_records(self) -> list[CompanySearchResult]:
        payload = await self._sec_client.get_company_tickers()
        records: list[CompanySearchResult] = []

        try:
            for raw_record in payload.values():
                if not isinstance(raw_record, dict):
                    raise SecMalformedResponseError()
                records.append(
                    CompanySearchResult(
                        ticker=_required_string(raw_record, "ticker").upper(),
                        company_name=_required_string(raw_record, "title"),
                        cik=format_cik(raw_record["cik_str"]),
                    )
                )
        except (KeyError, TypeError, ValidationError) as error:
            raise SecMalformedResponseError() from error

        return records


def _required_string(payload: dict[str, Any], key: str) -> str:
    return _as_nonempty_string(payload[key])


def _as_nonempty_string(value: Any) -> str:
    if not isinstance(value, (str, int)):
        raise SecMalformedResponseError()
    normalized = str(value).strip()
    if not normalized:
        raise SecMalformedResponseError()
    return normalized


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise SecMalformedResponseError()
    return [
        normalized
        for item in value
        if (normalized := _optional_string(item)) is not None
    ]


def _normalize_address(value: Any) -> CompanyAddress | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise SecMalformedResponseError()

    address = CompanyAddress(
        street1=_optional_string(value.get("street1")),
        street2=_optional_string(value.get("street2")),
        city=_optional_string(value.get("city")),
        state_or_country=_optional_string(value.get("stateOrCountry")),
        state_or_country_description=_optional_string(
            value.get("stateOrCountryDescription")
        ),
        postal_code=_optional_string(value.get("zipCode")),
    )
    return address if any(address.model_dump().values()) else None


def _normalize_former_names(value: Any) -> list[FormerCompanyName]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise SecMalformedResponseError()

    former_names: list[FormerCompanyName] = []
    try:
        for former_name in value:
            if not isinstance(former_name, dict):
                raise SecMalformedResponseError()
            former_names.append(
                FormerCompanyName(
                    name=_required_string(former_name, "name"),
                    from_date=_optional_string(former_name.get("from")),
                    to_date=_optional_string(former_name.get("to")),
                )
            )
    except ValidationError as error:
        raise SecMalformedResponseError() from error
    return former_names


def _parallel_string(
    payload: dict[str, Any],
    key: str,
    index: int,
    *,
    required: bool = False,
) -> str | None:
    values = payload.get(key)
    if not isinstance(values, list) or index >= len(values):
        if required:
            raise SecMalformedResponseError()
        return None

    value = _optional_string(values[index])
    if required and value is None:
        raise SecMalformedResponseError()
    return value
