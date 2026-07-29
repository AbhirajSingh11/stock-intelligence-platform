"""Dashboard application service."""

from app.data.mock_dashboard import MOCK_DASHBOARD_OVERVIEW
from app.schemas.dashboard import DashboardOverview


def get_dashboard_overview() -> DashboardOverview:
    """Validate and return the backend-owned dashboard snapshot."""

    return DashboardOverview.model_validate(MOCK_DASHBOARD_OVERVIEW)

