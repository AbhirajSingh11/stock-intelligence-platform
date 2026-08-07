"""Transactional application service for the persisted watchlist."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import WatchlistEntryExistsError, WatchlistEntryNotFoundError
from app.models.watchlist import WatchlistEntry
from app.repositories.watchlist_repository import WatchlistRepository
from app.schemas.watchlist import (
    WatchlistDeleteResponse,
    WatchlistEntryResponse,
    WatchlistResponse,
)
from app.services.company_service import CompanyService, normalize_ticker


class WatchlistService:
    """Coordinate SEC validation with atomic local persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = WatchlistRepository(session)

    async def list_entries(self) -> WatchlistResponse:
        entries = await self._repository.list_entries()
        return WatchlistResponse(
            entries=[WatchlistEntryResponse.model_validate(entry) for entry in entries]
        )

    async def add_entry(
        self,
        ticker: str,
        company_service: CompanyService,
    ) -> WatchlistEntryResponse:
        company = await company_service.resolve_company(ticker)
        entry = WatchlistEntry(
            ticker=company.ticker.upper(),
            cik=company.cik,
            company_name=company.company_name,
        )

        try:
            async with self._session.begin():
                existing = await self._repository.get_by_ticker(entry.ticker)
                if existing is not None:
                    raise WatchlistEntryExistsError()
                await self._repository.add(entry)
        except IntegrityError as error:
            await self._session.rollback()
            raise WatchlistEntryExistsError() from error

        return WatchlistEntryResponse.model_validate(entry)

    async def delete_entry(self, ticker: str) -> WatchlistDeleteResponse:
        normalized_ticker = normalize_ticker(ticker)
        async with self._session.begin():
            entry = await self._repository.get_by_ticker(normalized_ticker)
            if entry is None:
                raise WatchlistEntryNotFoundError()
            await self._repository.delete(entry)

        return WatchlistDeleteResponse(ticker=normalized_ticker)
