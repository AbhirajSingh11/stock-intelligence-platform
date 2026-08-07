"""Dashboard API response contracts."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PerformancePeriod = Literal["1M", "3M", "6M", "1Y", "ALL"]
SignalTone = Literal["positive", "warning", "neutral"]
ThesisState = Literal["Strengthening", "Review required", "Stable"]


class PortfolioSummary(BaseModel):
    """Portfolio-level values returned as unformatted domain numbers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total_value: float
    total_gain: float
    total_return_percent: float
    today_change: float
    today_change_percent: float
    position_count: int = Field(ge=0)


class PerformancePoint(BaseModel):
    """Portfolio value observed on one ISO calendar date."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    date: date
    value: float


class PerformanceSeries(BaseModel):
    """One selectable dashboard chart period."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    period: PerformancePeriod
    start_date: date
    end_date: date
    change_percent: float
    points: list[PerformancePoint] = Field(min_length=1)


class ThesisSignal(BaseModel):
    """Latest thesis state for one followed company."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticker: str
    company: str
    state: ThesisState
    tone: SignalTone
    last_reviewed: date


class DashboardOverview(BaseModel):
    """Complete dashboard snapshot returned by the versioned endpoint."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    as_of: datetime
    currency: Literal["USD"]
    portfolio_summary: PortfolioSummary
    performance: list[PerformanceSeries] = Field(min_length=5, max_length=5)
    thesis_signals: list[ThesisSignal]
