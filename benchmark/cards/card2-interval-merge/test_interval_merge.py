import pytest
from hypothesis import given
from hypothesis import strategies as st

from interval_merge import merge_intervals


raw_interval = st.tuples(st.integers(-50, 50), st.integers(-50, 50))
intervals = st.lists(raw_interval, max_size=30)


def normalize(interval):
    start, end = interval
    return (min(start, end), max(start, end))


def covered_points(intervals):
    points = set()
    for start, end in intervals:
        points.update(range(start, end + 1))
    return points


def assert_valid_merged(intervals):
    assert intervals == sorted(intervals)
    for start, end in intervals:
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert start <= end
    for left, right in zip(intervals, intervals[1:]):
        assert left[1] < right[0]


def test_empty_input_returns_empty_list():
    assert merge_intervals([]) == []


def test_merges_unsorted_overlapping_intervals():
    assert merge_intervals([(5, 8), (1, 3), (2, 6), (10, 12)]) == [(1, 8), (10, 12)]


def test_merges_touching_closed_intervals():
    assert merge_intervals([(1, 3), (3, 5), (8, 10), (10, 10)]) == [(1, 5), (8, 10)]


def test_handles_containment_duplicates_and_negatives():
    assert merge_intervals([(0, 10), (-5, -2), (2, 3), (0, 10), (-4, 1)]) == [(-5, 10)]


def test_accepts_any_iterable_without_mutating_source_list():
    source = [(4, 4), (1, 2), (2, 3)]
    assert merge_intervals(iter(source)) == [(1, 4)]
    assert source == [(4, 4), (1, 2), (2, 3)]


def test_rejects_reversed_intervals():
    with pytest.raises(ValueError):
        merge_intervals([(3, 1)])


@given(intervals)
def test_property_preserves_integer_coverage_and_canonical_shape(raw_intervals):
    normalized = [normalize(interval) for interval in raw_intervals]

    merged = merge_intervals(normalized)

    assert_valid_merged(merged)
    assert covered_points(merged) == covered_points(normalized)
