from __future__ import annotations

from collections.abc import Hashable
from typing import Generic, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    """Fixed-capacity least-recently-used cache.

    Contract summary:
    - ``capacity`` must be a positive integer.
    - ``get(key)`` returns the value for a cache hit, or ``None`` for a miss.
    - Reads and writes both mark an existing key as most recently used.
    - Inserting a new key beyond capacity evicts exactly the least recently used key.
    - ``keys_mru()`` returns keys from most-recently-used to least-recently-used.
    """

    def __init__(self, capacity: int) -> None:
        raise NotImplementedError

    @property
    def capacity(self) -> int:
        raise NotImplementedError

    def get(self, key: K) -> V | None:
        raise NotImplementedError

    def put(self, key: K, value: V) -> None:
        raise NotImplementedError

    def keys_mru(self) -> list[K]:
        raise NotImplementedError

    def __contains__(self, key: object) -> bool:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
