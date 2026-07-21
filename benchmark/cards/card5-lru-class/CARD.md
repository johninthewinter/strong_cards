# Card 5 — Generic LRUCache

## Goal

Implement a pure-Python finite-capacity least-recently-used cache.

The cache stores key/value pairs, returns `None` for missing keys, refreshes recency on successful reads and writes, and evicts exactly the least-recently-used key when a new insertion exceeds capacity.

## Contract

```python
class LRUCache(Generic[K, V]):
    def __init__(self, capacity: int) -> None:
        """Create an empty cache with positive finite capacity.

        Raises:
            ValueError: if capacity <= 0.
        """

    def get(self, key: K) -> Optional[V]:
        """Return the value for key, or None if absent.

        A successful get makes key the most-recently-used entry.
        A miss must not change the cache contents.
        """

    def put(self, key: K, value: V) -> None:
        """Insert or update key with value.

        The written key becomes most-recently-used. Updating an existing key must
        not grow the cache. Inserting a new key beyond capacity evicts exactly
        the least-recently-used key.
        """

    def __len__(self) -> int:
        """Return the number of stored entries."""

    def __contains__(self, key: object) -> bool:
        """Return whether key is currently stored without changing recency."""
```

## Acceptance

Run:

```bash
.venv/bin/python -m pytest -q
```

All tests in `test_solution.py` must pass.

The acceptance suite includes deterministic behavioral tests and a Hypothesis model test that checks:

- capacity invariant after random operation sequences,
- correct least-recently-used eviction order,
- key existence invariant via `key in cache`.

The initial `solution.py` is a contract stub and must fail the tests until implemented.

## Scope

files_write = [`solution.py`]

files_read = [`solution.py`, `test_solution.py`, `CARD.md`, `CODER_PROMPT.txt`]

## Non-goals

- No thread-safety or async behavior.
- No TTL, expiry, persistence, serialization, or metrics.
- No CLI, filesystem, network, database, or environment-variable integration.
- No extra public cache API beyond the contract above.
