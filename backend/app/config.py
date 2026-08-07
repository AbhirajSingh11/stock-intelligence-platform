"""Application configuration read from environment variables."""

import os
from dataclasses import dataclass

DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)
MAX_SEC_REQUESTS_PER_SECOND = 5.0


@dataclass(frozen=True)
class SecSettings:
    """Validated SEC EDGAR transport and cache settings."""

    user_agent: str | None
    requests_per_second: float
    connect_timeout_seconds: float
    read_timeout_seconds: float
    ticker_cache_ttl_seconds: float
    submissions_cache_ttl_seconds: float
    company_facts_cache_ttl_seconds: float
    max_retries: int = 2


def get_cors_origins() -> list[str]:
    """Return configured CORS origins or safe local-development defaults."""

    raw_origins = os.getenv("CORS_ORIGINS")
    if not raw_origins:
        return list(DEFAULT_CORS_ORIGINS)

    origins: list[str] = []
    for value in raw_origins.split(","):
        origin = value.strip().rstrip("/")
        if not origin:
            continue
        if origin == "*":
            raise ValueError("CORS_ORIGINS must list explicit origins, not '*'.")
        if not origin.startswith(("http://", "https://")):
            raise ValueError(
                f"CORS origin must start with http:// or https://: {origin}"
            )
        if origin not in origins:
            origins.append(origin)

    return origins or list(DEFAULT_CORS_ORIGINS)


def _positive_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        value = float(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} must be a number.") from error

    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return value


def get_sec_settings() -> SecSettings:
    """Return SEC configuration with conservative local defaults."""

    user_agent = os.getenv("SEC_USER_AGENT")
    if user_agent is not None:
        user_agent = user_agent.strip() or None

    requests_per_second = _positive_float(
        "SEC_RATE_LIMIT_PER_SECOND",
        MAX_SEC_REQUESTS_PER_SECOND,
    )
    if requests_per_second > MAX_SEC_REQUESTS_PER_SECOND:
        raise ValueError(
            "SEC_RATE_LIMIT_PER_SECOND cannot exceed the application maximum "
            f"of {MAX_SEC_REQUESTS_PER_SECOND:g}."
        )

    return SecSettings(
        user_agent=user_agent,
        requests_per_second=requests_per_second,
        connect_timeout_seconds=_positive_float(
            "SEC_CONNECT_TIMEOUT_SECONDS",
            5.0,
        ),
        read_timeout_seconds=_positive_float(
            "SEC_READ_TIMEOUT_SECONDS",
            15.0,
        ),
        ticker_cache_ttl_seconds=_positive_float(
            "SEC_TICKER_CACHE_TTL_SECONDS",
            86_400.0,
        ),
        submissions_cache_ttl_seconds=_positive_float(
            "SEC_SUBMISSIONS_CACHE_TTL_SECONDS",
            900.0,
        ),
        company_facts_cache_ttl_seconds=_positive_float(
            "SEC_COMPANY_FACTS_CACHE_TTL_SECONDS",
            900.0,
        ),
    )
