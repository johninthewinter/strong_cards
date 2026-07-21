from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from solution import merge_intervals


def test_empty_input_returns_empty_list() -> None:
    assert merge_intervals([]) == []


def test_single_interval_returns_same_interval() -> None:
    assert merge_intervals([(3, 7)]) == [(3, 7)]


def test_already_disjoint_intervals_are_sorted_without_merging() -> None:
    assert merge_intervals([(10, 12), (-5, -3), (2, 4)]) == [
        (-5, -3),
        (2, 4),
        (10, 12),
    ]


def test_overlapping_chain_collapses_to_one_interval() -> None:
    assert merge_intervals([(1, 4), (3, 8), (8, 10), (0, 2)]) == [(0, 10)]


def test_all_overlapping_unsorted_intervals_merge_to_minimum_cover() -> None:
    assert merge_intervals([(7, 9), (1, 3), (2, 8), (0, 10), (4, 6)]) == [(0, 10)]


def test_nested_intervals_do_not_split_the_outer_interval() -> None:
    assert merge_intervals([(0, 20), (2, 5), (6, 6), (10, 19), (1, 3)]) == [(0, 20)]


def test_shared_endpoint_counts_as_overlap_for_closed_intervals() -> None:
    assert merge_intervals([(1, 2), (2, 3), (5, 5), (3, 5)]) == [(1, 5)]


def test_duplicate_and_zero_length_intervals_merge_correctly() -> None:
    assert merge_intervals([(4, 4), (4, 4), (1, 1), (1, 2), (2, 2)]) == [(1, 2), (4, 4)]


def test_negative_coordinates_and_gap_boundaries_are_preserved() -> None:
    assert merge_intervals([(-10, -4), (-7, -2), (0, 0), (1, 3), (3, 4)]) == [
        (-10, -2),
        (0, 0),
        (1, 4),
    ]


@pytest.mark.parametrize(
    "intervals",
    [
        [(5, 1)],
        [(0, 2), (3, 1)],
    ],
)
def test_invalid_interval_with_start_after_end_raises_value_error(
    intervals: list[tuple[int, int]],
) -> None:
    with pytest.raises(ValueError):
        merge_intervals(intervals)


interval_strategy = st.builds(
    lambda start, end: (min(start, end), max(start, end)),
    st.integers(min_value=-40, max_value=40),
    st.integers(min_value=-40, max_value=40),
)


def _member_points(intervals: list[tuple[int, int]]) -> set[float]:
    points: set[float] = set()
    for start, end in intervals:
        points.add(float(start))
        points.add(float(end))
        for integer_point in range(start, end):
            points.add(float(integer_point))
            points.add(integer_point + 0.5)
    return points


def _is_covered(point: float, intervals: list[tuple[int, int]]) -> bool:
    return any(start <= point <= end for start, end in intervals)


def _component_count(intervals: list[tuple[int, int]]) -> int:
    if not intervals:
        return 0

    sorted_intervals = sorted(intervals)
    count = 0
    current_end: int | None = None

    for start, end in sorted_intervals:
        if current_end is None or start > current_end:
            count += 1
            current_end = end
        else:
            current_end = max(current_end, end)

    return count


@given(st.lists(interval_strategy, max_size=80))
@settings(max_examples=400)
def test_property_merged_output_is_sorted_disjoint_maximal_and_preserves_union(
    intervals: list[tuple[int, int]],
) -> None:
    merged = merge_intervals(intervals)

    assert merged == sorted(merged)
    assert all(start <= end for start, end in merged)
    assert all(
        left_end < right_start
        for (_, left_end), (right_start, _) in zip(merged, merged[1:])
    )

    witness_points = _member_points(intervals) | _member_points(merged)
    for point in witness_points:
        assert _is_covered(point, merged) == _is_covered(point, intervals)

    assert len(merged) == _component_count(intervals)

