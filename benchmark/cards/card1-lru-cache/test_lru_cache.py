from __future__ import annotations

from collections import OrderedDict

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from lru_cache import LRUCache


def assert_cache_state(
    cache: LRUCache[str, int],
    *,
    mru_to_lru: list[str],
    values: dict[str, int],
) -> None:
    assert len(cache) == len(mru_to_lru)
    assert cache.keys_mru() == mru_to_lru
    for key, value in values.items():
        assert (key in cache) is True
        assert cache.get(key) == value
    for key in set("abcdefghijklmnopqrstuvwxyz") - set(values):
        assert (key in cache) is False


def test_capacity_must_be_positive() -> None:
    with pytest.raises(ValueError, match="capacity"):
        LRUCache[str, int](0)

    with pytest.raises(ValueError, match="capacity"):
        LRUCache[str, int](-3)


def test_warm_up_fills_without_eviction_and_preserves_mru_order() -> None:
    cache = LRUCache[str, int](3)

    cache.put("a", 10)
    assert cache.keys_mru() == ["a"]
    assert len(cache) == 1

    cache.put("b", 20)
    assert cache.keys_mru() == ["b", "a"]
    assert len(cache) == 2

    cache.put("c", 30)
    assert_cache_state(
        cache,
        mru_to_lru=["c", "b", "a"],
        values={"a": 10, "b": 20, "c": 30},
    )


def test_get_hit_refreshes_recency_and_miss_does_not_change_state() -> None:
    cache = LRUCache[str, int](3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)

    assert cache.get("a") == 1
    assert cache.keys_mru() == ["a", "c", "b"]

    assert cache.get("missing") is None
    assert cache.keys_mru() == ["a", "c", "b"]
    assert len(cache) == 3


def test_put_existing_key_updates_value_and_refreshes_without_growing() -> None:
    cache = LRUCache[str, int](2)
    cache.put("a", 1)
    cache.put("b", 2)

    cache.put("a", 99)

    assert len(cache) == 2
    assert cache.keys_mru() == ["a", "b"]
    assert cache.get("a") == 99
    assert cache.get("b") == 2


def test_eviction_removes_exactly_the_least_recently_used_key() -> None:
    cache = LRUCache[str, int](3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    assert cache.get("a") == 1

    cache.put("d", 4)

    assert "b" not in cache
    assert cache.get("b") is None
    assert_cache_state(
        cache,
        mru_to_lru=["d", "a", "c"],
        values={"a": 1, "c": 3, "d": 4},
    )


def test_capacity_one_repeatedly_evicts_previous_key() -> None:
    cache = LRUCache[str, int](1)

    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("b", 22)
    cache.put("c", 3)

    assert cache.keys_mru() == ["c"]
    assert len(cache) == 1
    assert cache.get("a") is None
    assert cache.get("b") is None
    assert cache.get("c") == 3


Operation = tuple[str, str, int]


def apply_model(
    model: OrderedDict[str, int],
    capacity: int,
    op: Operation,
) -> int | None:
    action, key, value = op
    if action == "put":
        if key in model:
            del model[key]
        model[key] = value
        while len(model) > capacity:
            model.popitem(last=False)
        return None

    if key not in model:
        return None
    hit = model.pop(key)
    model[key] = hit
    return hit


def model_keys_mru(model: OrderedDict[str, int]) -> list[str]:
    return list(reversed(model.keys()))


@settings(
    max_examples=200,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    capacity=st.integers(min_value=1, max_value=5),
    operations=st.lists(
        st.tuples(
            st.sampled_from(["get", "put"]),
            st.sampled_from(["a", "b", "c", "d", "e", "f", "g"]),
            st.integers(min_value=-100, max_value=100),
        ),
        min_size=1,
        max_size=80,
    ),
)
def test_property_matches_ordered_dict_lru_model(
    capacity: int,
    operations: list[Operation],
) -> None:
    cache = LRUCache[str, int](capacity)
    model: OrderedDict[str, int] = OrderedDict()

    for op in operations:
        expected = apply_model(model, capacity, op)
        action, key, value = op

        if action == "put":
            assert cache.put(key, value) is None
        else:
            assert cache.get(key) == expected

        assert len(cache) == len(model)
        assert len(cache) <= capacity
        assert cache.keys_mru() == model_keys_mru(model)
        assert len(cache.keys_mru()) == len(set(cache.keys_mru()))

        for model_key, model_value in model.items():
            assert model_key in cache
            assert cache.get(model_key) == model_value
            moved_value = model.pop(model_key)
            model[model_key] = moved_value
            break

        assert cache.keys_mru() == model_keys_mru(model)
