"""Application configuration read from environment variables."""

import os

DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


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

