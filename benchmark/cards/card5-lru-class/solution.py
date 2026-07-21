from __future__ import annotations

from typing import Generic, Optional, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    """Finite-capacity least-recently-used cache.

    Contract:
    - capacity must be a positive integer.
    - get(key) returns the stored value, or None if absent.
    - a successful get makes that key most-recently-used.
    - put(key, value) inserts or updates the key and makes it most-recently-used.
    - inserting beyond capacity evicts exactly the least-recently-used key.
    """

    def __init__(self, capacity: int) -> None:
        raise NotImplementedError

    def get(self, key: K) -> Optional[V]:
        raise NotImplementedError

    def put(self, key: K, value: V) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __contains__(self, key: object) -> bool:
        raise NotImplementedError
