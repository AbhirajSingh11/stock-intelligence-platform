"""Versioned company fundamentals API route."""

from fastapi import APIRouter, Depends, Request

from app.api.routes.companies import ERROR_RESPONSES
from app.exceptions import SecConfigurationError
from app.schemas.company import ErrorResponse
from app.schemas.fundamentals import CompanyFundamentalsResponse
from app.services.fundamentals_service import FundamentalsService

router = APIRouter(prefix="/companies", tags=["companies"])


def get_fundamentals_service(request: Request) -> FundamentalsService:
    service = getattr(request.app.state, "fundamentals_service", None)
    if service is None:
        raise SecConfigurationError()
    return service


@router.get(
    "/{ticker}/fundamentals",
    response_model=CompanyFundamentalsResponse,
    responses={404: {"model": ErrorResponse}, **ERROR_RESPONSES},
)
async def read_company_fundamentals(
    ticker: str,
    service: FundamentalsService = Depends(get_fundamentals_service),
) -> CompanyFundamentalsResponse:
    """Return normalized annual and discrete-quarter SEC financial facts."""

    return await service.get_company_fundamentals(ticker)
