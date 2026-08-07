"""Dashboard API response contracts."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.thesis import ThesisSummary


class DashboardOverview(BaseModel):
    """Complete dashboard snapshot returned by the versioned endpoint."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    as_of: datetime
    thesis_signals: list[ThesisSummary]
