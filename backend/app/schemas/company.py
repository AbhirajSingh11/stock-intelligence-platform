"""Public request and response contracts for SEC company research."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompanySearchParams(BaseModel):
    """Validated company-search query parameters."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    query: str = Field(min_length=2, max_length=100)
    limit: int = Field(default=8, ge=1, le=20)


class CompanyFilingsParams(BaseModel):
    """Validated filing-filter query parameters."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    forms: tuple[str, ...] = Field(min_length=1, max_length=10)
    limit: int = Field(default=20, ge=1, le=100)

    @field_validator("forms")
    @classmethod
    def forms_must_be_unique(cls, forms: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(forms)) != len(forms):
            raise ValueError("forms must not contain duplicates")
        return forms


class ErrorDetail(BaseModel):
    """Stable error information safe to expose to API consumers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Envelope used by predictable application errors."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    error: ErrorDetail


class CompanySearchResult(BaseModel):
    """Normalized SEC ticker mapping entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticker: str
    company_name: str
    cik: str = Field(pattern=r"^\d{10}$")


class CompanySearchResponse(BaseModel):
    """Ranked company-search results."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    query: str
    results: list[CompanySearchResult]


class CompanyAddress(BaseModel):
    """Normalized SEC business or mailing address."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    street1: str | None = None
    street2: str | None = None
    city: str | None = None
    state_or_country: str | None = None
    state_or_country_description: str | None = None
    postal_code: str | None = None


class FormerCompanyName(BaseModel):
    """A former registrant name and the period in which it applied."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    from_date: date | None = None
    to_date: date | None = None


class CompanyProfileResponse(BaseModel):
    """Normalized SEC company submissions metadata."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticker: str
    company_name: str
    cik: str = Field(pattern=r"^\d{10}$")
    sic_code: str | None = None
    sic_description: str | None = None
    exchanges: list[str]
    fiscal_year_end: str | None = None
    state_of_incorporation: str | None = None
    business_address: CompanyAddress | None = None
    mailing_address: CompanyAddress | None = None
    former_names: list[FormerCompanyName]
    sec_company_url: str


class FilingRecord(BaseModel):
    """One normalized recent filing from SEC submissions data."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    accession_number: str
    form: str
    filing_date: date
    report_date: date | None = None
    acceptance_timestamp: datetime | None = None
    primary_document: str
    filing_detail_url: str
    primary_document_url: str
    description: str | None = None
    items: str | None = None


class CompanyFilingsResponse(BaseModel):
    """Recent filings for one company and the applied form filters."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticker: str
    cik: str = Field(pattern=r"^\d{10}$")
    forms: list[str]
    filings: list[FilingRecord]
