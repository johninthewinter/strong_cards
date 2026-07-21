"""Merge closed integer intervals."""

from collections.abc import Iterable

Interval = tuple[int, int]


def merge_intervals(intervals: Iterable[Interval]) -> list[Interval]:
    """Return sorted, non-overlapping closed intervals covering the input.

    Each interval is a ``(start, end)`` pair with ``start <= end``. Intervals
    overlap when they share at least one integer point, so ``(1, 3)`` and
    ``(3, 5)`` merge into ``(1, 5)``.
    """
    raise NotImplementedError
