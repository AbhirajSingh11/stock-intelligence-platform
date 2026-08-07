"""Dashboard API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.dashboard import DashboardOverview
from app.services.dashboard_service import get_dashboard_overview

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
async def read_dashboard_overview(
    session: AsyncSession = Depends(get_db_session),
) -> DashboardOverview:
    """Return the persisted Milestone 8 thesis snapshot."""

    return await get_dashboard_overview(session)
