"""Public request and response contracts for the persisted watchlist."""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WatchlistCreate(BaseModel):
    """Ticker supplied by a client when following a company."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    ticker: str = Field(min_length=1, max_length=10)


class WatchlistEntryResponse(BaseModel):
    """Persisted SEC identity metadata for one followed company."""

    model_config = ConfigDict(extra="forbid", frozen=True, from_attributes=True)

    id: int
    ticker: str
    cik: str = Field(pattern=r"^\d{10}$")
    company_name: str
    added_at: datetime
    updated_at: datetime

    @field_validator("added_at", "updated_at", mode="after")
    @classmethod
    def ensure_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class WatchlistResponse(BaseModel):
    """Alphabetically ordered local watchlist."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    entries: list[WatchlistEntryResponse]


class WatchlistDeleteResponse(BaseModel):
    """Confirmation that one ticker was deliberately removed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticker: str
    deleted: bool = True
