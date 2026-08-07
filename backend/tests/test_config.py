"""Tests for environment-driven application configuration."""

import pytest

from app.config import (
    DEFAULT_CORS_ORIGINS,
    MAX_SEC_REQUESTS_PER_SECOND,
    get_cors_origins,
    get_sec_settings,
)


def test_cors_origins_use_safe_local_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    assert get_cors_origins() == list(DEFAULT_CORS_ORIGINS)


def test_cors_origins_accept_explicit_comma_separated_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://research.example.com, http://localhost:3000/",
    )

    assert get_cors_origins() == [
        "https://research.example.com",
        "http://localhost:3000",
    ]


def test_cors_origins_reject_wildcard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "*")

    with pytest.raises(ValueError, match="explicit origins"):
        get_cors_origins()


def test_sec_settings_use_safe_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "SEC_USER_AGENT",
        "SEC_RATE_LIMIT_PER_SECOND",
        "SEC_CONNECT_TIMEOUT_SECONDS",
        "SEC_READ_TIMEOUT_SECONDS",
        "SEC_TICKER_CACHE_TTL_SECONDS",
        "SEC_SUBMISSIONS_CACHE_TTL_SECONDS",
        "SEC_COMPANY_FACTS_CACHE_TTL_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = get_sec_settings()

    assert settings.user_agent is None
    assert settings.requests_per_second == MAX_SEC_REQUESTS_PER_SECOND
    assert settings.ticker_cache_ttl_seconds == 86_400
    assert settings.submissions_cache_ttl_seconds == 900
    assert settings.company_facts_cache_ttl_seconds == 900


def test_sec_settings_reject_rate_above_application_maximum(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SEC_RATE_LIMIT_PER_SECOND", "5.1")

    with pytest.raises(ValueError, match="cannot exceed"):
        get_sec_settings()
