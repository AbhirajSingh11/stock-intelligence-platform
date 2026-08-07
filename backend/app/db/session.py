"""Async SQLAlchemy engine lifecycle and request-scoped sessions."""

from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import Request
from sqlalchemy import event
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def prepare_database_directory(database_url: str) -> None:
    url = make_url(database_url)
    if not url.drivername.startswith("sqlite") or not url.database:
        return
    if url.database == ":memory:" or url.database.startswith("file:"):
        return

    Path(url.database).expanduser().resolve().parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def _enable_sqlite_foreign_keys(engine: AsyncEngine) -> None:
    if not engine.url.drivername.startswith("sqlite"):
        return

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: object, _record: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()


class Database:
    """Own the async engine and session factory for one application lifespan."""

    def __init__(self, database_url: str) -> None:
        prepare_database_directory(database_url)
        self.engine = create_async_engine(database_url, pool_pre_ping=True)
        _enable_sqlite_foreign_keys(self.engine)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """Release pooled connections when the application shuts down."""

        await self.engine.dispose()


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield one session per request without implicitly committing writes."""

    database: Database = request.app.state.database
    async with database.session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
