# Card 7 — Expression Evaluator

## Goal

Implement a small integer expression evaluator with variables, precedence, parentheses, unary signs, and clear errors.

## Contract

Edit only `evaluator.py`.

Expose:

- `class ExpressionError(ValueError)`
- `def evaluate(expression: str, variables: dict[str, int] | None = None) -> int`

Supported syntax:

- integer literals
- variable names made of Python identifiers
- binary `+`, `-`, `*`, `/`
- unary `+` and `-`
- parentheses
- whitespace anywhere between tokens

Division is integer division truncated toward zero. Invalid syntax, unknown variables, division by zero, unsupported operators, floats, calls, indexing, and trailing tokens must raise `ExpressionError`.

## Acceptance

`test_evaluator.py` must pass, including the Hypothesis property test against the reference evaluator.

## Scope

Files write: `evaluator.py`

Files read: `test_evaluator.py`, `CARD.md`, `CODER_PROMPT.txt`

## Non-goals

- Do not use `eval` or `exec`.
- Do not support floats, exponentiation, modulo, functions, lists, attributes, assignment, or mutation.
- Do not change tests.

