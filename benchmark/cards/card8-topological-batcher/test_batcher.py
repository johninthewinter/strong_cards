from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from batcher import DependencyCycleError, build_batches


def flatten(batches: list[list[str]]) -> list[str]:
    return [task for batch in batches for task in batch]


def assert_valid_batches(tasks: dict[str, set[str]], batches: list[list[str]]) -> None:
    flat = flatten(batches)
    assert len(flat) == len(set(flat))
    expected = set(tasks) | {dep for deps in tasks.values() for dep in deps}
    assert set(flat) == expected
    position = {task: index for index, batch in enumerate(batches) for task in batch}
    for task, deps in tasks.items():
        for dep in deps:
            assert position[dep] < position[task]
    for batch in batches:
        assert batch == sorted(batch)
        for task in batch:
            for other in batch:
                assert task == other or task not in tasks.get(other, set())


def test_empty_graph_returns_empty_batches() -> None:
    assert build_batches({}) == []


def test_independent_tasks_share_one_sorted_batch() -> None:
    assert build_batches({"b": set(), "a": set(), "c": set()}) == [["a", "b", "c"]]


def test_dependencies_create_multiple_batches() -> None:
    tasks = {
        "package": {"test"},
        "test": {"build"},
        "lint": {"source"},
        "build": {"source"},
        "source": set(),
    }
    assert build_batches(tasks) == [["source"], ["build", "lint"], ["test"], ["package"]]


def test_implicit_dependency_nodes_are_included() -> None:
    assert build_batches({"deploy": {"package"}, "package": {"test"}}) == [
        ["test"],
        ["package"],
        ["deploy"],
    ]


def test_cycle_is_rejected() -> None:
    with pytest.raises(DependencyCycleError):
        build_batches({"a": {"b"}, "b": {"c"}, "c": {"a"}})


def test_self_cycle_is_rejected() -> None:
    with pytest.raises(DependencyCycleError):
        build_batches({"a": {"a"}})


def test_input_is_not_mutated() -> None:
    tasks = {"b": {"a"}, "a": set()}
    original = {k: set(v) for k, v in tasks.items()}
    build_batches(tasks)
    assert tasks == original


dag_edges = st.lists(
    st.tuples(st.integers(min_value=0, max_value=8), st.integers(min_value=0, max_value=8)),
    max_size=30,
).map(lambda edges: [(a, b) for a, b in edges if a > b])


@given(dag_edges)
@settings(max_examples=250)
def test_property_valid_batches_for_random_dags(edges: list[tuple[int, int]]) -> None:
    names = {f"t{i}" for edge in edges for i in edge}
    tasks = {name: set() for name in names}
    for task, dep in edges:
        tasks[f"t{task}"].add(f"t{dep}")
    batches = build_batches(tasks)
    assert_valid_batches(tasks, batches)


@given(dag_edges)
@settings(max_examples=120)
def test_property_batch_count_is_longest_path_length(edges: list[tuple[int, int]]) -> None:
    names = {f"t{i}" for edge in edges for i in edge}
    tasks = {name: set() for name in names}
    for task, dep in edges:
        tasks[f"t{task}"].add(f"t{dep}")
    batches = build_batches(tasks)
    distance: dict[str, int] = {}

    def depth(task: str) -> int:
        if task not in distance:
            deps = tasks.get(task, set())
            distance[task] = 1 + max((depth(dep) for dep in deps), default=0)
        return distance[task]

    expected = max((depth(task) for task in set(tasks) | {d for ds in tasks.values() for d in ds}), default=0)
    assert len(batches) == expected

