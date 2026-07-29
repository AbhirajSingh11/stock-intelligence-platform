"""Small in-memory TTL cache used for successful SEC responses."""

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic
from typing import Generic, TypeVar

ValueT = TypeVar("ValueT")


@dataclass(frozen=True)
class _CacheEntry(Generic[ValueT]):
    value: ValueT
    expires_at: float


class TtlCache(Generic[ValueT]):
    """Store values until their per-cache time-to-live expires."""

    def __init__(
        self,
        ttl_seconds: float,
        *,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._entries: dict[str, _CacheEntry[ValueT]] = {}

    def get(self, key: str) -> ValueT | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        if entry.expires_at <= self._clock():
            self._entries.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: ValueT) -> None:
        self._entries[key] = _CacheEntry(
            value=value,
            expires_at=self._clock() + self._ttl_seconds,
        )

    def clear(self) -> None:
        self._entries.clear()
