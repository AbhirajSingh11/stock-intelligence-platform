"""Dashboard application service."""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.dashboard import DashboardOverview
from app.services.thesis_service import ThesisService


async def get_dashboard_overview(session: AsyncSession) -> DashboardOverview:
    """Return persisted thesis priorities for the portfolio dashboard."""

    service = ThesisService(session)
    return DashboardOverview(
        as_of=datetime.now(timezone.utc),
        thesis_signals=await service.dashboard_theses(limit=5),
    )
