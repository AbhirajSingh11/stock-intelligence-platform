"""Versioned API routes for portfolio transactions and accounting."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.companies import ERROR_RESPONSES, get_company_service
from app.db.session import get_db_session
from app.schemas.company import ErrorResponse
from app.schemas.portfolio import (
    PortfolioOverviewResponse,
    PortfolioPriceMarkResponse,
    PortfolioPriceMarkUpdate,
    PortfolioTransactionCreate,
    PortfolioTransactionDeleteResponse,
    PortfolioTransactionResponse,
    PortfolioTransactionsResponse,
    PortfolioTransactionUpdate,
)
from app.services.company_service import CompanyService
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
PORTFOLIO_ERROR_RESPONSES = {
    404: {"model": ErrorResponse},
    409: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
}


def get_portfolio_service(
    session: AsyncSession = Depends(get_db_session),
) -> PortfolioService:
    return PortfolioService(session)


@router.get("/overview", response_model=PortfolioOverviewResponse)
async def read_portfolio_overview(
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioOverviewResponse:
    return await service.get_overview()


@router.get(
    "/transactions",
    response_model=PortfolioTransactionsResponse,
    responses={422: {"model": ErrorResponse}},
)
async def read_portfolio_transactions(
    ticker: str | None = Query(default=None, max_length=10),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioTransactionsResponse:
    return await service.get_transactions(ticker)


@router.post(
    "/transactions",
    response_model=PortfolioTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**PORTFOLIO_ERROR_RESPONSES, **ERROR_RESPONSES},
)
async def create_portfolio_transaction(
    payload: PortfolioTransactionCreate,
    service: PortfolioService = Depends(get_portfolio_service),
    company_service: CompanyService = Depends(get_company_service),
) -> PortfolioTransactionResponse:
    return await service.create_transaction(payload, company_service)


@router.patch(
    "/transactions/{transaction_id}",
    response_model=PortfolioTransactionResponse,
    responses=PORTFOLIO_ERROR_RESPONSES,
)
async def update_portfolio_transaction(
    transaction_id: int,
    payload: PortfolioTransactionUpdate,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioTransactionResponse:
    return await service.update_transaction(transaction_id, payload)


@router.delete(
    "/transactions/{transaction_id}",
    response_model=PortfolioTransactionDeleteResponse,
    responses=PORTFOLIO_ERROR_RESPONSES,
)
async def delete_portfolio_transaction(
    transaction_id: int,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioTransactionDeleteResponse:
    return await service.delete_transaction(transaction_id)


@router.put(
    "/marks/{ticker}",
    response_model=PortfolioPriceMarkResponse,
    responses=PORTFOLIO_ERROR_RESPONSES,
)
async def update_portfolio_price_mark(
    ticker: str,
    payload: PortfolioPriceMarkUpdate,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioPriceMarkResponse:
    return await service.set_price_mark(ticker, payload)
