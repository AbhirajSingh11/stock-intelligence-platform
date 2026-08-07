"""Public contracts for portfolio transactions, marks, and accounting."""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    field_validator,
    model_validator,
)

TransactionSide = Literal["BUY", "SELL"]
PriceMarkSource = Literal["MANUAL"]
PositiveDecimal = Annotated[
    Decimal,
    Field(gt=0, max_digits=24, decimal_places=8),
    PlainSerializer(lambda value: format(value, "f"), return_type=str),
]
NonnegativeDecimal = Annotated[
    Decimal,
    Field(ge=0, max_digits=24, decimal_places=8),
    PlainSerializer(lambda value: format(value, "f"), return_type=str),
]
DecimalString = Annotated[
    Decimal,
    PlainSerializer(lambda value: format(value, "f"), return_type=str),
]


def _validate_trade_date(value: date) -> date:
    if value > datetime.now(timezone.utc).date():
        raise ValueError("trade_date cannot be in the future")
    return value


def _normalize_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_notes(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class PortfolioTransactionCreate(BaseModel):
    """A user-entered buy or sell transaction."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    ticker: str = Field(min_length=1, max_length=10)
    side: TransactionSide
    trade_date: date
    quantity: PositiveDecimal
    price_per_share: PositiveDecimal
    fees: NonnegativeDecimal = Decimal("0")
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("trade_date", mode="after")
    @classmethod
    def trade_date_is_not_future(cls, value: date) -> date:
        return _validate_trade_date(value)

    @field_validator("notes", mode="after")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_notes(value)


class PortfolioTransactionUpdate(BaseModel):
    """Editable fields on an existing transaction."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    side: TransactionSide | None = None
    trade_date: date | None = None
    quantity: PositiveDecimal | None = None
    price_per_share: PositiveDecimal | None = None
    fees: NonnegativeDecimal | None = None
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("trade_date", mode="after")
    @classmethod
    def trade_date_is_not_future(cls, value: date | None) -> date | None:
        return _validate_trade_date(value) if value is not None else None

    @field_validator("notes", mode="after")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_notes(value)

    @model_validator(mode="after")
    def require_valid_change(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one editable field is required.")
        nullable_fields = {"notes"}
        for field_name in self.model_fields_set - nullable_fields:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class PortfolioTransactionResponse(BaseModel):
    """One stored ledger event plus its exact gross amount."""

    model_config = ConfigDict(extra="forbid", frozen=True, from_attributes=True)

    id: int
    ticker: str
    cik: str = Field(pattern=r"^\d{10}$")
    company_name: str
    side: TransactionSide
    trade_date: date
    quantity: DecimalString
    price_per_share: DecimalString
    fees: DecimalString
    gross_amount: DecimalString
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", mode="after")
    @classmethod
    def ensure_utc(cls, value: datetime) -> datetime:
        return _normalize_utc(value)


class PortfolioTransactionsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    transactions: list[PortfolioTransactionResponse]


class PortfolioTransactionDeleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    transaction_id: int
    deleted: bool = True


class PortfolioPriceMarkUpdate(BaseModel):
    """A manually supplied current price and optional observation time."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    price: PositiveDecimal
    as_of: datetime | None = None

    @field_validator("as_of", mode="after")
    @classmethod
    def supplied_timestamp_requires_timezone(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("as_of must include a UTC offset or timezone")
        return value.astimezone(timezone.utc)


class PortfolioPriceMarkResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, from_attributes=True)

    id: int
    ticker: str
    price: DecimalString
    as_of: datetime
    source: PriceMarkSource
    created_at: datetime
    updated_at: datetime

    @field_validator("as_of", "created_at", "updated_at", mode="after")
    @classmethod
    def ensure_utc(cls, value: datetime) -> datetime:
        return _normalize_utc(value)


class PortfolioPosition(BaseModel):
    """Calculated current state for one open security."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticker: str
    cik: str = Field(pattern=r"^\d{10}$")
    company_name: str
    quantity: DecimalString
    average_cost: DecimalString
    open_cost_basis: DecimalString
    realized_gain_loss: DecimalString
    manual_price: DecimalString | None
    price_as_of: datetime | None
    price_source: PriceMarkSource | None
    market_value: DecimalString | None
    unrealized_gain_loss: DecimalString | None
    unrealized_return_percent: DecimalString | None

    @field_validator("price_as_of", mode="after")
    @classmethod
    def ensure_price_timestamp_utc(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        return _normalize_utc(value) if value is not None else None


class PortfolioTotals(BaseModel):
    """Portfolio-wide totals with explicit manual-price completeness."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    open_cost_basis: DecimalString
    realized_gain_loss: DecimalString
    market_value: DecimalString | None
    marked_market_value: DecimalString
    unrealized_gain_loss: DecimalString | None
    marked_unrealized_gain_loss: DecimalString
    open_position_count: int = Field(ge=0)
    transaction_count: int = Field(ge=0)
    marked_position_count: int = Field(ge=0)
    unmarked_position_count: int = Field(ge=0)
    manual_price_coverage_percent: DecimalString | None
    market_values_complete: bool


class PortfolioOverviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    as_of: datetime
    currency: Literal["USD"] = "USD"
    totals: PortfolioTotals
    positions: list[PortfolioPosition]


class PortfolioSecurityIdentity(BaseModel):
    """Internal official identity reused after the first SEC validation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticker: str
    cik: str
    company_name: str
