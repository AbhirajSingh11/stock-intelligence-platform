"""Presentation-neutral contracts for normalized SEC Company Facts data."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MetricKey = Literal[
    "revenue",
    "operating_income",
    "net_income",
    "diluted_eps",
    "cash",
    "debt",
    "operating_margin",
    "net_margin",
]
SeriesPeriod = Literal["annual", "quarterly"]
NumericValue = int | float


class FundamentalComponentSource(BaseModel):
    """One source fact used to construct a derived financial value."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_key: str
    value: NumericValue
    unit: str
    taxonomy: str
    source_tag: str
    accession_number: str
    source_filing_url: str


class FundamentalFact(BaseModel):
    """One normalized raw or derived financial observation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_key: MetricKey
    value: NumericValue
    unit: str
    period_start: date | None = None
    period_end: date
    fiscal_year: int
    fiscal_period: str
    form: str
    filed_date: date
    accession_number: str
    frame: str | None = None
    taxonomy: str
    source_tag: str
    is_fallback: bool
    is_derived: bool
    is_restated: bool
    source_filing_url: str
    component_sources: list[FundamentalComponentSource] = Field(
        default_factory=list
    )


class FundamentalMetricSeries(BaseModel):
    """Chronological values for one metric and one period granularity."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_key: MetricKey
    label: str
    unit: str
    period: SeriesPeriod
    facts: list[FundamentalFact]


class LatestFundamentalValue(BaseModel):
    """Most recent available observation for one supported metric."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_key: MetricKey
    label: str
    fact: FundamentalFact


class DataQualityWarning(BaseModel):
    """Non-fatal normalization or coverage warning."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str
    metric_key: MetricKey | None = None


class UnavailableMetric(BaseModel):
    """A supported metric with no defensible value for one period view."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_key: MetricKey
    label: str
    period: SeriesPeriod
    reason: str


class FundamentalsCompanyIdentity(BaseModel):
    """Company identity associated with the normalized facts."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticker: str
    company_name: str
    cik: str = Field(pattern=r"^\d{10}$")


class FundamentalsProvenance(BaseModel):
    """Source resource used for all normalized metrics in the response."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: Literal["SEC EDGAR Company Facts"]
    company_facts_url: str


class CompanyFundamentalsResponse(BaseModel):
    """Complete normalized fundamentals payload for one company."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    company: FundamentalsCompanyIdentity
    data_as_of: datetime
    annual: list[FundamentalMetricSeries]
    quarterly: list[FundamentalMetricSeries]
    latest_values: list[LatestFundamentalValue]
    warnings: list[DataQualityWarning]
    unavailable_metrics: list[UnavailableMetric]
    provenance: FundamentalsProvenance

