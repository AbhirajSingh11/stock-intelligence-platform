"""Shared offline SEC fixtures."""

import json
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config

FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures"
BACKEND_DIRECTORY = Path(__file__).parents[1]


@pytest.fixture(autouse=True)
def isolated_database_url(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    """Keep every test process away from the developer's local database."""

    database_path = (tmp_path / "test.db").as_posix()
    database_url = f"sqlite+aiosqlite:///{database_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    return database_url


@pytest.fixture
def migrated_database_url(isolated_database_url: str) -> str:
    """Upgrade an isolated SQLite file through the real Alembic environment."""

    config = Config(str(BACKEND_DIRECTORY / "alembic.ini"))
    command.upgrade(config, "head")
    return isolated_database_url


@pytest.fixture
def company_tickers_payload() -> dict[str, Any]:
    return json.loads(
        (FIXTURE_DIRECTORY / "company_tickers.json").read_text(encoding="utf-8")
    )


@pytest.fixture
def msft_submissions_payload() -> dict[str, Any]:
    return json.loads(
        (FIXTURE_DIRECTORY / "submissions_msft.json").read_text(encoding="utf-8")
    )


@pytest.fixture
def msft_company_facts_payload() -> dict[str, Any]:
    return json.loads(
        (FIXTURE_DIRECTORY / "company_facts_msft.json").read_text(
            encoding="utf-8"
        )
    )


@pytest.fixture
def anyio_backend() -> str:
    """Run async tests on the asyncio backend already used by FastAPI."""

    return "asyncio"
