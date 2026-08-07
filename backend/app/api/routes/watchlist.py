"""Versioned API routes for the persisted local watchlist."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.companies import ERROR_RESPONSES, get_company_service
from app.db.session import get_db_session
from app.schemas.company import ErrorResponse
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistDeleteResponse,
    WatchlistEntryResponse,
    WatchlistResponse,
)
from app.services.company_service import CompanyService
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


def get_watchlist_service(
    session: AsyncSession = Depends(get_db_session),
) -> WatchlistService:
    return WatchlistService(session)


@router.get("", response_model=WatchlistResponse)
async def read_watchlist(
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistResponse:
    return await service.list_entries()


@router.post(
    "",
    response_model=WatchlistEntryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        **ERROR_RESPONSES,
    },
)
async def create_watchlist_entry(
    request: WatchlistCreate,
    service: WatchlistService = Depends(get_watchlist_service),
    company_service: CompanyService = Depends(get_company_service),
) -> WatchlistEntryResponse:
    return await service.add_entry(request.ticker, company_service)


@router.delete(
    "/{ticker}",
    response_model=WatchlistDeleteResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def delete_watchlist_entry(
    ticker: str,
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistDeleteResponse:
    return await service.delete_entry(ticker)
