"""SQLAlchemy queries for the single-user portfolio ledger."""

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import PortfolioPriceMark, PortfolioTransaction


class PortfolioRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_transactions(
        self,
        ticker: str | None = None,
        *,
        newest_first: bool = False,
    ) -> list[PortfolioTransaction]:
        statement: Select[tuple[PortfolioTransaction]] = select(
            PortfolioTransaction
        )
        if ticker is not None:
            statement = statement.where(PortfolioTransaction.ticker == ticker)

        if newest_first:
            statement = statement.order_by(
                PortfolioTransaction.trade_date.desc(),
                PortfolioTransaction.created_at.desc(),
                PortfolioTransaction.id.desc(),
            )
        else:
            statement = statement.order_by(
                PortfolioTransaction.trade_date.asc(),
                PortfolioTransaction.created_at.asc(),
                PortfolioTransaction.id.asc(),
            )

        result = await self._session.scalars(statement)
        return list(result.all())

    async def get_transaction(
        self,
        transaction_id: int,
    ) -> PortfolioTransaction | None:
        return await self._session.get(PortfolioTransaction, transaction_id)

    async def get_security_transaction(
        self,
        ticker: str,
    ) -> PortfolioTransaction | None:
        return await self._session.scalar(
            select(PortfolioTransaction)
            .where(PortfolioTransaction.ticker == ticker)
            .order_by(PortfolioTransaction.created_at.asc(), PortfolioTransaction.id.asc())
            .limit(1)
        )

    async def add_transaction(
        self,
        transaction: PortfolioTransaction,
    ) -> PortfolioTransaction:
        self._session.add(transaction)
        await self._session.flush()
        await self._session.refresh(transaction)
        return transaction

    async def flush_transaction(
        self,
        transaction: PortfolioTransaction,
    ) -> PortfolioTransaction:
        await self._session.flush()
        await self._session.refresh(transaction)
        return transaction

    async def delete_transaction(self, transaction: PortfolioTransaction) -> None:
        await self._session.delete(transaction)
        await self._session.flush()

    async def list_price_marks(self) -> list[PortfolioPriceMark]:
        result = await self._session.scalars(
            select(PortfolioPriceMark).order_by(PortfolioPriceMark.ticker.asc())
        )
        return list(result.all())

    async def get_price_mark(self, ticker: str) -> PortfolioPriceMark | None:
        return await self._session.scalar(
            select(PortfolioPriceMark).where(PortfolioPriceMark.ticker == ticker)
        )

    async def save_price_mark(
        self,
        mark: PortfolioPriceMark,
    ) -> PortfolioPriceMark:
        self._session.add(mark)
        await self._session.flush()
        await self._session.refresh(mark)
        return mark
