from __future__ import annotations


class ExpressionError(ValueError):
    pass


def evaluate(expression: str, variables: dict[str, int] | None = None) -> int:
    raise NotImplementedError

