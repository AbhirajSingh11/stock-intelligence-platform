"""Transactional portfolio service and Decimal-based overview assembly."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    PortfolioLedgerConflictError,
    PortfolioSecurityNotFoundError,
    PortfolioTransactionNotFoundError,
)
from app.models.portfolio import PortfolioPriceMark, PortfolioTransaction
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.portfolio import (
    PortfolioOverviewResponse,
    PortfolioPosition,
    PortfolioPriceMarkResponse,
    PortfolioPriceMarkUpdate,
    PortfolioSecurityIdentity,
    PortfolioTotals,
    PortfolioTransactionCreate,
    PortfolioTransactionDeleteResponse,
    PortfolioTransactionResponse,
    PortfolioTransactionsResponse,
    PortfolioTransactionUpdate,
)
from app.services.company_service import CompanyService, normalize_ticker
from app.services.portfolio_accounting import (
    LedgerEntry,
    LedgerViolation,
    PERCENT_QUANTUM,
    ZERO,
    quantize_money,
    quantize_percent,
    replay_ledger,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PortfolioService:
    """Coordinate official identities, ledger validation, and persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = PortfolioRepository(session)

    @staticmethod
    def _ledger_entry(transaction: PortfolioTransaction) -> LedgerEntry:
        created_at = transaction.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return LedgerEntry(
            id=transaction.id,
            ticker=transaction.ticker,
            company_name=transaction.company_name,
            cik=transaction.cik,
            side=transaction.side,
            trade_date=transaction.trade_date,
            quantity=transaction.quantity,
            price_per_share=transaction.price_per_share,
            fees=transaction.fees,
            created_at=created_at,
        )

    @staticmethod
    def _transaction_response(
        transaction: PortfolioTransaction,
    ) -> PortfolioTransactionResponse:
        return PortfolioTransactionResponse(
            id=transaction.id,
            ticker=transaction.ticker,
            cik=transaction.cik,
            company_name=transaction.company_name,
            side=transaction.side,
            trade_date=transaction.trade_date,
            quantity=transaction.quantity,
            price_per_share=transaction.price_per_share,
            fees=transaction.fees,
            gross_amount=quantize_money(
                transaction.quantity * transaction.price_per_share
            ),
            notes=transaction.notes,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
        )

    async def _validate_ticker_ledger(self, ticker: str) -> None:
        transactions = await self._repository.list_transactions(ticker)
        replay_ledger([self._ledger_entry(item) for item in transactions])

    async def get_overview(self) -> PortfolioOverviewResponse:
        transactions = await self._repository.list_transactions()
        ledger = replay_ledger(
            [self._ledger_entry(transaction) for transaction in transactions]
        )
        marks = {
            mark.ticker: mark for mark in await self._repository.list_price_marks()
        }

        positions: list[PortfolioPosition] = []
        total_cost_basis = ZERO
        marked_market_value = ZERO
        marked_unrealized = ZERO
        marked_count = 0

        for ticker in sorted(ledger.positions):
            accounted = ledger.positions[ticker]
            if accounted.quantity <= ZERO:
                continue

            total_cost_basis = quantize_money(
                total_cost_basis + accounted.open_cost_basis
            )
            mark = marks.get(ticker)
            market_value: Decimal | None = None
            unrealized: Decimal | None = None
            unrealized_percent: Decimal | None = None

            if mark is not None:
                marked_count += 1
                market_value = quantize_money(accounted.quantity * mark.price)
                unrealized = quantize_money(
                    market_value - accounted.open_cost_basis
                )
                unrealized_percent = quantize_percent(
                    unrealized / accounted.open_cost_basis * Decimal("100")
                )
                marked_market_value = quantize_money(
                    marked_market_value + market_value
                )
                marked_unrealized = quantize_money(
                    marked_unrealized + unrealized
                )

            positions.append(
                PortfolioPosition(
                    ticker=ticker,
                    cik=accounted.cik,
                    company_name=accounted.company_name,
                    quantity=accounted.quantity,
                    average_cost=accounted.average_cost,
                    open_cost_basis=accounted.open_cost_basis,
                    realized_gain_loss=quantize_money(
                        accounted.realized_gain_loss
                    ),
                    manual_price=mark.price if mark is not None else None,
                    price_as_of=mark.as_of if mark is not None else None,
                    price_source="MANUAL" if mark is not None else None,
                    market_value=market_value,
                    unrealized_gain_loss=unrealized,
                    unrealized_return_percent=unrealized_percent,
                )
            )

        open_count = len(positions)
        unmarked_count = open_count - marked_count
        values_complete = unmarked_count == 0
        coverage = (
            quantize_percent(
                Decimal(marked_count) / Decimal(open_count) * Decimal("100")
            )
            if open_count > 0
            else None
        )

        return PortfolioOverviewResponse(
            as_of=utc_now(),
            currency="USD",
            totals=PortfolioTotals(
                open_cost_basis=quantize_money(total_cost_basis),
                realized_gain_loss=quantize_money(ledger.realized_gain_loss),
                market_value=(
                    quantize_money(marked_market_value)
                    if values_complete
                    else None
                ),
                marked_market_value=quantize_money(marked_market_value),
                unrealized_gain_loss=(
                    quantize_money(marked_unrealized)
                    if values_complete
                    else None
                ),
                marked_unrealized_gain_loss=quantize_money(marked_unrealized),
                open_position_count=open_count,
                transaction_count=len(transactions),
                marked_position_count=marked_count,
                unmarked_position_count=unmarked_count,
                manual_price_coverage_percent=(
                    coverage.quantize(PERCENT_QUANTUM) if coverage is not None else None
                ),
                market_values_complete=values_complete,
            ),
            positions=positions,
        )

    async def get_transactions(
        self,
        ticker: str | None = None,
    ) -> PortfolioTransactionsResponse:
        normalized_ticker = normalize_ticker(ticker) if ticker is not None else None
        transactions = await self._repository.list_transactions(
            normalized_ticker,
            newest_first=True,
        )
        return PortfolioTransactionsResponse(
            transactions=[
                self._transaction_response(transaction)
                for transaction in transactions
            ]
        )

    async def create_transaction(
        self,
        payload: PortfolioTransactionCreate,
        company_service: CompanyService,
    ) -> PortfolioTransactionResponse:
        requested_ticker = normalize_ticker(payload.ticker)
        existing = await self._repository.get_security_transaction(requested_ticker)
        await self._session.rollback()

        resolved_identity: PortfolioSecurityIdentity | None = None
        if existing is None:
            company = await company_service.resolve_company(requested_ticker)
            resolved_identity = PortfolioSecurityIdentity(
                ticker=company.ticker.upper(),
                cik=company.cik,
                company_name=company.company_name,
            )

        try:
            async with self._session.begin():
                existing = await self._repository.get_security_transaction(
                    requested_ticker
                )
                identity = (
                    PortfolioSecurityIdentity(
                        ticker=existing.ticker,
                        cik=existing.cik,
                        company_name=existing.company_name,
                    )
                    if existing is not None
                    else resolved_identity
                )
                if identity is None:
                    raise PortfolioSecurityNotFoundError()

                transaction = PortfolioTransaction(
                    ticker=identity.ticker,
                    cik=identity.cik,
                    company_name=identity.company_name,
                    side=payload.side,
                    trade_date=payload.trade_date,
                    quantity=payload.quantity,
                    price_per_share=payload.price_per_share,
                    fees=payload.fees,
                    notes=payload.notes,
                )
                await self._repository.add_transaction(transaction)
                await self._validate_ticker_ledger(identity.ticker)
        except LedgerViolation as error:
            raise PortfolioLedgerConflictError() from error

        return self._transaction_response(transaction)

    async def update_transaction(
        self,
        transaction_id: int,
        payload: PortfolioTransactionUpdate,
    ) -> PortfolioTransactionResponse:
        try:
            async with self._session.begin():
                transaction = await self._repository.get_transaction(transaction_id)
                if transaction is None:
                    raise PortfolioTransactionNotFoundError()

                changes = payload.model_dump(exclude_unset=True)
                for field_name, value in changes.items():
                    setattr(transaction, field_name, value)
                transaction.updated_at = utc_now()
                await self._repository.flush_transaction(transaction)
                await self._validate_ticker_ledger(transaction.ticker)
        except LedgerViolation as error:
            raise PortfolioLedgerConflictError() from error

        return self._transaction_response(transaction)

    async def delete_transaction(
        self,
        transaction_id: int,
    ) -> PortfolioTransactionDeleteResponse:
        try:
            async with self._session.begin():
                transaction = await self._repository.get_transaction(transaction_id)
                if transaction is None:
                    raise PortfolioTransactionNotFoundError()
                ticker = transaction.ticker
                await self._repository.delete_transaction(transaction)
                await self._validate_ticker_ledger(ticker)
        except LedgerViolation as error:
            raise PortfolioLedgerConflictError() from error

        return PortfolioTransactionDeleteResponse(transaction_id=transaction_id)

    async def set_price_mark(
        self,
        ticker: str,
        payload: PortfolioPriceMarkUpdate,
    ) -> PortfolioPriceMarkResponse:
        normalized_ticker = normalize_ticker(ticker)
        async with self._session.begin():
            security = await self._repository.get_security_transaction(
                normalized_ticker
            )
            if security is None:
                raise PortfolioSecurityNotFoundError()

            mark = await self._repository.get_price_mark(normalized_ticker)
            observed_at = payload.as_of or utc_now()
            if mark is None:
                mark = PortfolioPriceMark(
                    ticker=normalized_ticker,
                    price=payload.price,
                    as_of=observed_at,
                    source="MANUAL",
                )
            else:
                mark.price = payload.price
                mark.as_of = observed_at
                mark.source = "MANUAL"
                mark.updated_at = utc_now()
            await self._repository.save_price_mark(mark)

        return PortfolioPriceMarkResponse.model_validate(mark)
