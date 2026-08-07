"""SQLAlchemy queries specific to the watchlist aggregate."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.watchlist import WatchlistEntry


class WatchlistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_entries(self) -> list[WatchlistEntry]:
        result = await self._session.scalars(
            select(WatchlistEntry).order_by(WatchlistEntry.ticker.asc())
        )
        return list(result.all())

    async def get_by_ticker(self, ticker: str) -> WatchlistEntry | None:
        return await self._session.scalar(
            select(WatchlistEntry).where(WatchlistEntry.ticker == ticker)
        )

    async def add(self, entry: WatchlistEntry) -> WatchlistEntry:
        self._session.add(entry)
        await self._session.flush()
        await self._session.refresh(entry)
        return entry

    async def delete(self, entry: WatchlistEntry) -> None:
        await self._session.delete(entry)
        await self._session.flush()
