"""Typed request and response contracts for thesis persistence."""

from datetime import date, datetime, timezone
import re
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ThesisStatus = Literal["DRAFT", "ACTIVE", "INVALIDATED", "ARCHIVED"]
ThesisConviction = Literal["LOW", "MEDIUM", "HIGH"]
ThesisSignal = Literal["STRENGTHENING", "STABLE", "WEAKENING", "REVIEW_REQUIRED"]
EvidenceStance = Literal["SUPPORTING", "CONTRADICTING", "NEUTRAL"]
EvidenceCategory = Literal[
    "FINANCIAL", "COMPETITIVE", "MANAGEMENT", "VALUATION",
    "CATALYST", "RISK", "FILING", "OTHER",
]

RequiredText = Annotated[str, Field(min_length=1)]
OptionalText = str | None


def _strip_required(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("value must not be blank")
    return stripped


def _strip_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class ThesisFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    summary: RequiredText
    bull_case: OptionalText = None
    bear_case: OptionalText = None
    invalidation_criteria: OptionalText = None
    status: ThesisStatus = "DRAFT"
    conviction: ThesisConviction = "MEDIUM"
    signal: ThesisSignal = "STABLE"
    review_due_date: date | None = None

    @field_validator("title", "summary", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return _strip_required(value)

    @field_validator("bull_case", "bear_case", "invalidation_criteria", mode="before")
    @classmethod
    def blank_optional_text_is_null(cls, value: str | None) -> str | None:
        return _strip_optional(value)


class ThesisCreate(ThesisFields):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ticker: str = Field(min_length=1, max_length=10)

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker_shape(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not re.fullmatch(r"[A-Z0-9.-]{1,10}", normalized):
            raise ValueError("ticker has an invalid format")
        return normalized


class ThesisUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = Field(default=None, min_length=1)
    bull_case: OptionalText = None
    bear_case: OptionalText = None
    invalidation_criteria: OptionalText = None
    status: ThesisStatus | None = None
    conviction: ThesisConviction | None = None
    signal: ThesisSignal | None = None
    review_due_date: date | None = None

    @field_validator("title", "summary", mode="before")
    @classmethod
    def strip_required_updates(cls, value: str | None) -> str | None:
        return _strip_required(value) if value is not None else None

    @field_validator("bull_case", "bear_case", "invalidation_criteria", mode="before")
    @classmethod
    def blank_optional_updates_are_null(cls, value: str | None) -> str | None:
        return _strip_optional(value)

    @model_validator(mode="after")
    def require_a_change(self) -> "ThesisUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        return self


class ThesisReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    review_due_date: date | None = None


class EvidenceFields(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stance: EvidenceStance
    category: EvidenceCategory
    title: str = Field(min_length=1, max_length=200)
    description: RequiredText
    source_url: str | None = Field(default=None, max_length=2048)
    observed_on: date

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_evidence_text(cls, value: str) -> str:
        return _strip_required(value)

    @field_validator("source_url", mode="before")
    @classmethod
    def validate_source_url(cls, value: str | None) -> str | None:
        normalized = _strip_optional(value)
        if normalized is None:
            return None
        parsed = urlsplit(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("source_url must be an absolute HTTP or HTTPS URL")
        return normalized


class EvidenceCreate(EvidenceFields):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EvidenceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    stance: EvidenceStance | None = None
    category: EvidenceCategory | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    source_url: str | None = Field(default=None, max_length=2048)
    observed_on: date | None = None

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_evidence_updates(cls, value: str | None) -> str | None:
        return _strip_required(value) if value is not None else None

    @field_validator("source_url", mode="before")
    @classmethod
    def validate_source_url(cls, value: str | None) -> str | None:
        return EvidenceFields.validate_source_url(value)

    @model_validator(mode="after")
    def require_a_change(self) -> "EvidenceUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        return self


class EvidenceCounts(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    supporting: int = Field(ge=0)
    contradicting: int = Field(ge=0)
    neutral: int = Field(ge=0)
    total: int = Field(ge=0)


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, from_attributes=True)
    id: int
    thesis_id: int
    stance: EvidenceStance
    category: EvidenceCategory
    title: str
    description: str
    source_url: str | None
    observed_on: date
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", mode="after")
    @classmethod
    def timestamps_are_utc(cls, value: datetime) -> datetime:
        return _normalize_timestamp(value)


class ThesisSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: int
    ticker: str
    cik: str
    company_name: str
    title: str
    summary: str
    status: ThesisStatus
    conviction: ThesisConviction
    signal: ThesisSignal
    review_due_date: date | None
    last_reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    is_overdue: bool
    evidence_counts: EvidenceCounts

    @field_validator("last_reviewed_at", "created_at", "updated_at", mode="after")
    @classmethod
    def optional_timestamps_are_utc(cls, value: datetime | None) -> datetime | None:
        return _normalize_timestamp(value) if value is not None else None


class ThesisDetail(ThesisSummary):
    bull_case: str | None
    bear_case: str | None
    invalidation_criteria: str | None
    evidence: list[EvidenceResponse]


class ThesisJournalCounts(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    total: int = Field(ge=0)
    active: int = Field(ge=0)
    overdue: int = Field(ge=0)
    review_required: int = Field(ge=0)


class ThesisListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    theses: list[ThesisSummary]
    counts: ThesisJournalCounts


class ThesisDeleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ticker: str
    deleted: bool = True


class EvidenceDeleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    evidence_id: int
    deleted: bool = True
