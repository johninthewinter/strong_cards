# Card 9 — Spreadsheet Engine

## Goal

Implement a tiny spreadsheet evaluator with dependency resolution, formulas, rectangular ranges, and cycle detection.

## Contract

Edit only `spreadsheet.py`.

Expose:

- `class SpreadsheetError(ValueError)`
- `def evaluate_workbook(cells: dict[str, int | str]) -> dict[str, int]`

Cell names are one or more uppercase letters followed by a positive row number, for example `A1`, `B12`, `Z9`. Values are either integer literals or formula strings beginning with `=`.

Supported formula syntax:

- integer literals
- cell references
- binary `+`, `-`, `*`, `/`
- unary `+` and `-`
- parentheses
- `SUM(A1:B3)` rectangular ranges

Division is integer division truncated toward zero. Unknown cells, invalid syntax, invalid cell names, invalid ranges, division by zero, and cycles must raise `SpreadsheetError`. The input must not be mutated.

## Acceptance

`test_spreadsheet.py` must pass, including property tests for formula chains and rectangular sums.

## Scope

Files write: `spreadsheet.py`

Files read: `test_spreadsheet.py`, `CARD.md`, `CODER_PROMPT.txt`

## Non-goals

- Do not use `eval` or `exec`.
- Do not support floats, strings, booleans, multiple sheets, assignments, functions other than `SUM`, open-ended ranges, or relative references.
- Do not change tests.

