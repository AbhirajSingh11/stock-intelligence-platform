"""Dashboard API response contracts."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

SignalTone = Literal["positive", "warning", "neutral"]
ThesisState = Literal["Strengthening", "Review required", "Stable"]


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
    thesis_signals: list[ThesisSignal]
