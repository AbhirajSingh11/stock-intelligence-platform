"""Shared offline SEC fixtures."""

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures"


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
def anyio_backend() -> str:
    """Run async tests on the asyncio backend already used by FastAPI."""

    return "asyncio"
