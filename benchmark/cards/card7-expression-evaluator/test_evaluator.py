from __future__ import annotations

import ast
import operator

import pytest
from hypothesis import given, settings, strategies as st

from evaluator import ExpressionError, evaluate


def test_integer_literals_and_whitespace() -> None:
    assert evaluate("  42 ") == 42
    assert evaluate("-7") == -7
    assert evaluate("--7") == 7


def test_precedence_and_parentheses() -> None:
    assert evaluate("2 + 3 * 4") == 14
    assert evaluate("(2 + 3) * 4") == 20
    assert evaluate("18 / 3 / 2") == 3
    assert evaluate("2 * -3 + 10") == 4


def test_variables_are_resolved_from_mapping() -> None:
    assert evaluate("a * (b + 3) - c", {"a": 4, "b": 2, "c": 5}) == 15


def test_unknown_variable_is_rejected() -> None:
    with pytest.raises(ExpressionError):
        evaluate("known + missing", {"known": 1})


def test_invalid_syntax_and_trailing_tokens_are_rejected() -> None:
    for expr in ["", "1 +", "1 2", "(1 + 2", "1 + * 2", "foo()"]:
        with pytest.raises(ExpressionError):
            evaluate(expr, {"foo": 1})


def test_division_by_zero_is_rejected() -> None:
    with pytest.raises(ExpressionError):
        evaluate("4 / (2 - 2)")


def test_float_and_unsupported_operators_are_rejected() -> None:
    for expr in ["1.5 + 2", "2 ** 3", "7 % 3", "[1][0]"]:
        with pytest.raises(ExpressionError):
            evaluate(expr)


def _safe_eval(expr: str, variables: dict[str, int]) -> int:
    tree = ast.parse(expr, mode="eval")

    def walk(node: ast.AST) -> int:
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return node.value
        if isinstance(node, ast.Name):
            return variables[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -walk(node.operand)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return walk(node.operand)
        if isinstance(node, ast.BinOp):
            left = walk(node.left)
            right = walk(node.right)
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
            }
            for kind, fn in ops.items():
                if isinstance(node.op, kind):
                    return fn(left, right)
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError
                return int(left / right)
        raise AssertionError(ast.dump(node))

    return walk(tree)


atoms = st.one_of(
    st.integers(min_value=-20, max_value=20).map(str),
    st.sampled_from(["a", "b", "c"]),
)


@st.composite
def expressions(draw: st.DrawFn, depth: int = 0) -> str:
    if depth >= 3:
        return draw(atoms)
    choice = draw(st.integers(min_value=0, max_value=4))
    if choice == 0:
        return draw(atoms)
    if choice == 1:
        return f"({draw(expressions(depth + 1))})"
    if choice == 2:
        return f"-{draw(expressions(depth + 1))}"
    left = draw(expressions(depth + 1))
    right = draw(expressions(depth + 1))
    op = draw(st.sampled_from(["+", "-", "*"]))
    return f"{left} {op} {right}"


@given(expressions(), st.dictionaries(st.sampled_from(["a", "b", "c"]), st.integers(-10, 10), min_size=3, max_size=3))
@settings(max_examples=250)
def test_property_matches_reference_for_supported_expressions(
    expr: str, variables: dict[str, int]
) -> None:
    assert evaluate(expr, variables) == _safe_eval(expr, variables)

