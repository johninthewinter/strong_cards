# Card 6 - Interval Merge

## Goal

Implement a pure-Python interval merge algorithm with edge-by-edge correctness over dense overlapping, nested, duplicate, zero-length, negative, and unsorted closed intervals.

## Contract

```python
def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping closed intervals into sorted, disjoint ranges.

    Args:
        intervals: A list of closed [start, end] integer intervals. Valid input
            intervals satisfy start <= end.

    Returns:
        The minimum set of sorted, non-overlapping closed intervals covering the
        same union as the input intervals.

    Raises:
        ValueError: if any interval has start > end.
    """
```

Intervals that share an endpoint overlap because the intervals are closed. For example, `(1, 2)` and `(2, 3)` merge to `(1, 3)`.

Required edge cases:

- Empty list.
- Single interval.
- Already-disjoint intervals.
- All-overlapping intervals.
- Unsorted input.
- Nested intervals.
- Duplicate intervals.
- Zero-length intervals.
- Negative coordinates.

## Acceptance

Run:

```bash
.venv/bin/python -m pytest -q
```

All tests in `test_solution.py` must pass.

The acceptance suite includes deterministic edge-case tests and a Hypothesis property test that checks:

- output is sorted,
- output intervals are disjoint,
- output covers the same union as the input,
- output contains exactly one interval for each maximal connected covered range.

The initial `solution.py` is a contract stub and must fail the tests until implemented.

## Scope

files_write = [`solution.py`]

files_read = [`solution.py`, `test_solution.py`, `CARD.md`, `CODER_PROMPT.txt`]

## Non-goals

- No interval tree, segment tree, balanced tree, or advanced data structure.
- No CLI, stdin/stdout protocol, file I/O, network access, database access, or environment-variable integration.
- No floating-point interval support.
- No custom interval class or extra public API beyond `merge_intervals`.
- No mutation requirement for the input list; callers must not rely on in-place behavior.

