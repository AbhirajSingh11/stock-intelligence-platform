"""Offline transport tests for the SEC EDGAR client."""

import asyncio
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from app.clients.sec_edgar import (
    COMPANY_TICKERS_URL,
    FixedIntervalRateLimiter,
    SecEdgarClient,
    build_sec_http_client,
)
from app.config import SecSettings
from app.exceptions import (
    SecMalformedResponseError,
    SecRateLimitError,
    SecTimeoutError,
    SecUpstreamError,
)


class NoopRateLimiter:
    async def acquire(self) -> None:
        return None


async def no_sleep(_seconds: float) -> None:
    return None


def sec_settings() -> SecSettings:
    return SecSettings(
        user_agent="Stock Intelligence Platform tests@example.com",
        requests_per_second=5,
        connect_timeout_seconds=1,
        read_timeout_seconds=1,
        ticker_cache_ttl_seconds=86_400,
        submissions_cache_ttl_seconds=900,
        max_retries=2,
    )


async def build_client(
    handler: Callable[[httpx.Request], httpx.Response],
) -> tuple[SecEdgarClient, httpx.AsyncClient]:
    transport = httpx.MockTransport(handler)
    http_client = build_sec_http_client(sec_settings(), transport=transport)
    return (
        SecEdgarClient(
            http_client,
            sec_settings(),
            rate_limiter=NoopRateLimiter(),
            sleep=no_sleep,
        ),
        http_client,
    )


@pytest.mark.anyio
async def test_required_headers_cik_padding_and_cache(
    company_tickers_payload: dict[str, Any],
    msft_submissions_payload: dict[str, Any],
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        payload = (
            company_tickers_payload
            if str(request.url) == COMPANY_TICKERS_URL
            else msft_submissions_payload
        )
        return httpx.Response(200, json=payload)

    client, http_client = await build_client(handler)
    try:
        await client.get_company_tickers()
        await client.get_company_tickers()
        await client.get_company_submissions(789019)
        await client.get_company_submissions("0000789019")
    finally:
        await http_client.aclose()

    assert len(requests) == 2
    assert requests[0].headers["user-agent"] == (
        "Stock Intelligence Platform tests@example.com"
    )
    assert requests[0].headers["accept"] == "application/json"
    assert requests[0].headers["accept-encoding"] == "gzip, deflate"
    assert str(requests[1].url).endswith("/submissions/CIK0000789019.json")


@pytest.mark.anyio
async def test_concurrent_cache_misses_share_one_request(
    company_tickers_payload: dict[str, Any],
) -> None:
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, json=company_tickers_payload)

    client, http_client = await build_client(handler)
    try:
        first, second = await asyncio.gather(
            client.get_company_tickers(),
            client.get_company_tickers(),
        )
    finally:
        await http_client.aclose()

    assert first == second
    assert call_count == 1


@pytest.mark.anyio
async def test_rate_limiter_spaces_requests_at_five_per_second() -> None:
    current_time = 0.0
    delays: list[float] = []

    def clock() -> float:
        return current_time

    async def advance_clock(delay: float) -> None:
        nonlocal current_time
        delays.append(delay)
        current_time += delay

    limiter = FixedIntervalRateLimiter(
        5,
        clock=clock,
        sleep=advance_clock,
    )

    await limiter.acquire()
    await limiter.acquire()
    await limiter.acquire()

    assert delays == pytest.approx([0.2, 0.2])


@pytest.mark.anyio
@pytest.mark.parametrize("transient_status", [429, 503])
async def test_transient_responses_are_retried(
    transient_status: int,
    company_tickers_payload: dict[str, Any],
) -> None:
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return httpx.Response(transient_status)
        return httpx.Response(200, json=company_tickers_payload)

    client, http_client = await build_client(handler)
    try:
        payload = await client.get_company_tickers()
    finally:
        await http_client.aclose()

    assert payload == company_tickers_payload
    assert call_count == 3


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (429, SecRateLimitError),
        (503, SecUpstreamError),
    ],
)
async def test_exhausted_transient_responses_are_translated(
    status_code: int,
    expected_error: type[Exception],
) -> None:
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(status_code)

    client, http_client = await build_client(handler)
    try:
        with pytest.raises(expected_error):
            await client.get_company_tickers()
    finally:
        await http_client.aclose()

    assert call_count == 3


@pytest.mark.anyio
async def test_timeout_is_retried_then_translated() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        raise httpx.ReadTimeout("timed out", request=request)

    client, http_client = await build_client(handler)
    try:
        with pytest.raises(SecTimeoutError):
            await client.get_company_tickers()
    finally:
        await http_client.aclose()

    assert call_count == 3


@pytest.mark.anyio
async def test_malformed_json_is_rejected() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )

    client, http_client = await build_client(handler)
    try:
        with pytest.raises(SecMalformedResponseError):
            await client.get_company_tickers()
    finally:
        await http_client.aclose()
