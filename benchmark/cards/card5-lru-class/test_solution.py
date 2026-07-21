from __future__ import annotations

from collections import OrderedDict

import pytest
from hypothesis import given, settings, strategies as st

from solution import LRUCache


def test_put_then_get_returns_value_and_len_tracks_entries() -> None:
    cache: LRUCache[str, int] = LRUCache(2)

    cache.put("alpha", 10)

    assert cache.get("alpha") == 10
    assert "alpha" in cache
    assert len(cache) == 1


def test_missing_key_returns_none_and_does_not_grow_cache() -> None:
    cache: LRUCache[str, int] = LRUCache(2)

    assert cache.get("missing") is None
    assert "missing" not in cache
    assert len(cache) == 0


def test_put_over_capacity_evicts_least_recently_used_key() -> None:
    cache: LRUCache[str, int] = LRUCache(2)

    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)

    assert "a" not in cache
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3
    assert len(cache) == 2


def test_get_refreshes_recency_before_next_eviction() -> None:
    cache: LRUCache[str, int] = LRUCache(2)

    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)

    assert "b" not in cache
    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3


def test_updating_existing_key_refreshes_recency_without_growing() -> None:
    cache: LRUCache[str, int] = LRUCache(2)

    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 100)
    cache.put("c", 3)

    assert len(cache) == 2
    assert "b" not in cache
    assert cache.get("a") == 100
    assert cache.get("c") == 3


@pytest.mark.parametrize("capacity", [0, -1, -5])
def test_capacity_must_be_positive(capacity: int) -> None:
    with pytest.raises(ValueError):
        LRUCache(capacity)


Operation = tuple[str, int, int]


operation_strategy = st.lists(
    st.tuples(
        st.sampled_from(["put", "get"]),
        st.integers(min_value=0, max_value=5),
        st.integers(min_value=-100, max_value=100),
    ),
    min_size=1,
    max_size=80,
)


@given(capacity=st.integers(min_value=1, max_value=5), operations=operation_strategy)
@settings(max_examples=250)
def test_lru_matches_ordered_dict_model_under_random_operations(
    capacity: int, operations: list[Operation]
) -> None:
    cache: LRUCache[int, int] = LRUCache(capacity)
    oracle: OrderedDict[int, int] = OrderedDict()
    key_universe = range(6)

    for op, key, value in operations:
        if op == "put":
            cache.put(key, value)
            if key in oracle:
                oracle.move_to_end(key)
            oracle[key] = value
            if len(oracle) > capacity:
                oracle.popitem(last=False)
        else:
            observed = cache.get(key)
            if key in oracle:
                oracle.move_to_end(key)
                assert observed == oracle[key]
            else:
                assert observed is None

        assert len(cache) == len(oracle)
        assert len(cache) <= capacity

        for candidate in key_universe:
            assert (candidate in cache) == (candidate in oracle)

    for key, expected_value in list(oracle.items()):
        assert cache.get(key) == expected_value
