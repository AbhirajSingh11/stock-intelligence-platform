"""Dashboard API routes."""

from fastapi import APIRouter

from app.schemas.dashboard import DashboardOverview
from app.services.dashboard_service import get_dashboard_overview

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def read_dashboard_overview() -> DashboardOverview:
    """Return the deterministic Milestone 3 dashboard snapshot."""

    return get_dashboard_overview()

