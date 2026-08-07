"""Migration lifecycle and database resource tests."""

import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from app.db.session import Database

BACKEND_DIRECTORY = Path(__file__).parents[1]


def _table_names(database_url: str) -> set[str]:
    database_path = database_url.removeprefix("sqlite+aiosqlite:///")
    with sqlite3.connect(database_path) as connection:
        return {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }


def test_initial_migration_upgrade_downgrade_upgrade(
    isolated_database_url: str,
) -> None:
    config = Config(str(BACKEND_DIRECTORY / "alembic.ini"))

    command.upgrade(config, "head")
    assert "watchlist_entries" in _table_names(isolated_database_url)

    command.downgrade(config, "base")
    assert "watchlist_entries" not in _table_names(isolated_database_url)

    command.upgrade(config, "head")
    assert "watchlist_entries" in _table_names(isolated_database_url)


@pytest.mark.anyio
async def test_database_disposal_releases_sqlite_file(
    isolated_database_url: str,
) -> None:
    database = Database(isolated_database_url)
    async with database.engine.connect() as connection:
        await connection.exec_driver_sql("SELECT 1")

    await database.dispose()
    database_path = Path(
        isolated_database_url.removeprefix("sqlite+aiosqlite:///")
    )
    database_path.unlink()
    assert not database_path.exists()
