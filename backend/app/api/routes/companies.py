"""Versioned company research API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from pydantic import ValidationError

from app.exceptions import (
    InvalidFilingsQueryError,
    InvalidQueryError,
    SecConfigurationError,
)
from app.schemas.company import (
    CompanyFilingsParams,
    CompanyFilingsResponse,
    CompanyProfileResponse,
    CompanySearchParams,
    CompanySearchResponse,
    ErrorResponse,
)
from app.services.company_service import CompanyService, parse_filing_forms

router = APIRouter(prefix="/companies", tags=["companies"])
ERROR_RESPONSES = {
    422: {"model": ErrorResponse},
    429: {"model": ErrorResponse},
    502: {"model": ErrorResponse},
    503: {"model": ErrorResponse},
    504: {"model": ErrorResponse},
}


def get_company_service(request: Request) -> CompanyService:
    service = getattr(request.app.state, "company_service", None)
    if service is None:
        raise SecConfigurationError()
    return service


@router.get(
    "/search",
    response_model=CompanySearchResponse,
    responses=ERROR_RESPONSES,
)
async def search_companies(
    query: Annotated[str, Query(max_length=100)] = "",
    limit: Annotated[int, Query(ge=1, le=20)] = 8,
    service: CompanyService = Depends(get_company_service),
) -> CompanySearchResponse:
    """Return ranked ticker and company-name matches."""

    try:
        params = CompanySearchParams(query=query, limit=limit)
    except ValidationError as error:
        raise InvalidQueryError() from error
    return await service.search_companies(params)


@router.get(
    "/{ticker}",
    response_model=CompanyProfileResponse,
    responses={404: {"model": ErrorResponse}, **ERROR_RESPONSES},
)
async def read_company(
    ticker: str,
    service: CompanyService = Depends(get_company_service),
) -> CompanyProfileResponse:
    """Return normalized SEC submissions metadata for one ticker."""

    return await service.get_company_profile(ticker)


@router.get(
    "/{ticker}/filings",
    response_model=CompanyFilingsResponse,
    responses={404: {"model": ErrorResponse}, **ERROR_RESPONSES},
)
async def read_company_filings(
    ticker: str,
    forms: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    service: CompanyService = Depends(get_company_service),
) -> CompanyFilingsResponse:
    """Return recent filings filtered to requested SEC form types."""

    parsed_forms = parse_filing_forms(forms)
    try:
        params = CompanyFilingsParams(forms=parsed_forms, limit=limit)
    except ValidationError as error:
        raise InvalidFilingsQueryError() from error
    return await service.get_company_filings(ticker, params)
