"""Asynchronous client for official SEC EDGAR JSON endpoints."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from time import monotonic
from typing import Any, Protocol, cast

import httpx

from app.cache import TtlCache
from app.config import SecSettings
from app.exceptions import (
    SecMalformedResponseError,
    SecRateLimitError,
    SecTimeoutError,
    SecUpstreamError,
)

COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL_TEMPLATE = (
    "https://data.sec.gov/submissions/CIK{cik}.json"
)
TRANSIENT_STATUS_CODES = frozenset({500, 502, 503, 504})


class RateLimiter(Protocol):
    async def acquire(self) -> None:
        """Wait until one outbound request may start."""


class FixedIntervalRateLimiter:
    """Serialize request starts to a fixed maximum rate."""

    def __init__(
        self,
        requests_per_second: float,
        *,
        clock: Callable[[], float] = monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._interval = 1 / requests_per_second
        self._clock = clock
        self._sleep = sleep
        self._next_request_at = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = self._clock()
            delay = max(0.0, self._next_request_at - now)
            if delay:
                await self._sleep(delay)
                now = self._clock()
            self._next_request_at = max(now, self._next_request_at) + self._interval


def build_sec_http_client(
    settings: SecSettings,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> httpx.AsyncClient:
    """Build one pooled client with SEC-required identity and JSON headers."""

    return httpx.AsyncClient(
        headers={
            "User-Agent": settings.user_agent or "",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        },
        timeout=httpx.Timeout(
            connect=settings.connect_timeout_seconds,
            read=settings.read_timeout_seconds,
            write=settings.read_timeout_seconds,
            pool=settings.connect_timeout_seconds,
        ),
        transport=transport,
        follow_redirects=False,
    )


class SecEdgarClient:
    """Fetch and cache the two official SEC data sources used in Milestone 4."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        settings: SecSettings,
        *,
        rate_limiter: RateLimiter | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._http_client = http_client
        self._max_retries = settings.max_retries
        self._rate_limiter = rate_limiter or FixedIntervalRateLimiter(
            settings.requests_per_second
        )
        self._sleep = sleep
        self._ticker_cache = TtlCache[dict[str, Any]](
            settings.ticker_cache_ttl_seconds
        )
        self._submissions_cache = TtlCache[dict[str, Any]](
            settings.submissions_cache_ttl_seconds
        )
        self._ticker_lock = asyncio.Lock()
        self._submissions_lock = asyncio.Lock()

    async def get_company_tickers(self) -> dict[str, Any]:
        cached = self._ticker_cache.get("company_tickers")
        if cached is not None:
            return cached

        async with self._ticker_lock:
            cached = self._ticker_cache.get("company_tickers")
            if cached is not None:
                return cached

            payload = await self._get_json(COMPANY_TICKERS_URL)
            if not isinstance(payload, dict):
                raise SecMalformedResponseError()
            self._ticker_cache.set("company_tickers", payload)
            return payload

    async def get_company_submissions(self, cik: str | int) -> dict[str, Any]:
        normalized_cik = str(cik).strip().zfill(10)
        if len(normalized_cik) != 10 or not normalized_cik.isdigit():
            raise SecMalformedResponseError()

        cached = self._submissions_cache.get(normalized_cik)
        if cached is not None:
            return cached

        async with self._submissions_lock:
            cached = self._submissions_cache.get(normalized_cik)
            if cached is not None:
                return cached

            payload = await self._get_json(
                SUBMISSIONS_URL_TEMPLATE.format(cik=normalized_cik)
            )
            if not isinstance(payload, dict):
                raise SecMalformedResponseError()
            self._submissions_cache.set(normalized_cik, payload)
            return payload

    async def _get_json(self, url: str) -> dict[str, Any]:
        for attempt in range(self._max_retries + 1):
            await self._rate_limiter.acquire()
            try:
                response = await self._http_client.get(url)
            except httpx.TimeoutException as error:
                if attempt < self._max_retries:
                    await self._backoff(attempt)
                    continue
                raise SecTimeoutError() from error
            except httpx.HTTPError as error:
                raise SecUpstreamError() from error

            if response.status_code == 429:
                if attempt < self._max_retries:
                    await self._backoff(attempt)
                    continue
                raise SecRateLimitError()

            if response.status_code in TRANSIENT_STATUS_CODES:
                if attempt < self._max_retries:
                    await self._backoff(attempt)
                    continue
                raise SecUpstreamError()

            if not response.is_success:
                raise SecUpstreamError()

            try:
                payload = response.json()
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
                raise SecMalformedResponseError() from error

            if not isinstance(payload, dict):
                raise SecMalformedResponseError()
            return cast(dict[str, Any], payload)

        raise SecUpstreamError()

    async def _backoff(self, attempt: int) -> None:
        await self._sleep(0.25 * (2**attempt))
