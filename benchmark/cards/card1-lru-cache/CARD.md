# LRU Cache

## Goal

Implement a small, self-contained, pure-Python `LRUCache` class with fixed capacity, warm-up behavior, recency refresh on hits and updates, and exact least-recently-used eviction once full.

## Contract

- Public module: `lru_cache.py`.
- Public class: `LRUCache[K, V]`.
- Constructor: `LRUCache(capacity: int)`.
- `capacity` must be a positive integer; invalid capacity raises `ValueError` mentioning `capacity`.
- `get(key: K) -> V | None` returns the cached value on hit and `None` on miss.
- `put(key: K, value: V) -> None` inserts or updates a value.
- Warm-up: before the cache reaches capacity, inserts must not evict anything.
- Recency invariant: successful `get` and every `put` of an existing key make that key most recently used.
- Eviction invariant: inserting a new key when already at capacity evicts exactly the least recently used key.
- `keys_mru() -> list[K]` returns keys from most-recently-used to least-recently-used.
- `len(cache)` returns the current number of entries.
- `key in cache` reflects current membership.

## Acceptance

- `pytest test_lru_cache.py` passes from this directory.
- The stub must fail immediately until `lru_cache.py` is implemented.
- Tests include deterministic scenarios for validation, warm-up, recency refresh, updates, capacity-one behavior, and exact eviction.
- Tests include a Hypothesis property test comparing the implementation against an `OrderedDict` reference model over randomized operation sequences.

## Scope

files_write:

- `lru_cache.py`

files_read:

- `test_lru_cache.py`
- `CARD.md`
- `CODER_PROMPT.txt`

## Non-goals

- Do not implement decorators, TTL expiration, async behavior, persistence, metrics, or thread safety.
- Do not add dependencies, packaging metadata, command-line interfaces, or files outside this card directory.
- Do not change the public API to mimic `functools.lru_cache`.
- Do not optimize beyond clear constant-time or near-constant-time cache operations.
