# Interval Merge

## Goal

Implement a pure-Python interval merge function for closed integer intervals.

## Contract

- Public API: `merge_intervals(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]`
- Input intervals are closed integer pairs `(start, end)`.
- Valid intervals satisfy `start <= end`.
- Overlapping intervals merge when they share at least one integer point.
- Touching closed intervals merge: `(1, 3)` and `(3, 5)` become `(1, 5)`.
- Return intervals sorted by ascending start, then ascending end.
- Return a canonical result with no two output intervals overlapping or touching.
- Accept any iterable input.
- Do not mutate caller-owned input containers.
- Raise `ValueError` for any reversed interval where `start > end`.

## Acceptance

- `pytest test_interval_merge.py` passes from this directory.
- At least one Hypothesis property test passes.
- The stub implementation must fail before coding, because `merge_intervals` raises `NotImplementedError`.
- The implementation remains pure Python and self-contained.

## Scope

### files_write

- `interval_merge.py`

### files_read

- `interval_merge.py`
- `test_interval_merge.py`
- `CARD.md`
- `CODER_PROMPT.txt`

## Non-goals

- Do not support floating-point intervals.
- Do not support half-open or open interval semantics.
- Do not add dependencies beyond the test dependency on Hypothesis.
- Do not create a CLI, service, package, or persistent storage.
