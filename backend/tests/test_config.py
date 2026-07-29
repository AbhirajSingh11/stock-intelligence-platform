"""Tests for environment-driven application configuration."""

import pytest

from app.config import DEFAULT_CORS_ORIGINS, get_cors_origins


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

