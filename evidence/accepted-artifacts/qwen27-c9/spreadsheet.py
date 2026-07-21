from __future__ import annotations

import re
import math
from typing import Any

CELL_RE = re.compile(r"([A-Z]+)(\d+)")


class SpreadsheetError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Parser  (returns a small AST as nested tuples)
# ---------------------------------------------------------------------------

def _parse(tokens: list[str]) -> tuple[str, ...]:
    pos = [0]

    def _peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def _eat(expected: str | None = None):
        t = tokens[pos[0]]
        if expected and t != expected:
            raise SpreadsheetError(f"expected {expected}, got {t}")
        pos[0] += 1
        return t

    def _add():
        left = _term()
        while _peek() in ("+", "-"):
            op = tokens[pos[0]]; pos[0] += 1
            right = _term()
            left = (op, left, right)
        return left

    def _term():
        left = _factor()
        while _peek() in ("*", "/"):
            op = tokens[pos[0]]; pos[0] += 1
            right = _factor()
            left = (op, left, right)
        return left

    def _factor():
        t = _peek()
        if t is None:
            raise SpreadsheetError("unexpected end of formula")
        if t in ("+", "-"):
            pos[0] += 1
            return ("u" + t, _factor())
        if t == "(":
            pos[0] += 1
            node = _add()
            _eat(")")
            return node
        if t == "SUM":
            pos[0] += 1  # SUM
            _eat("(")
            c1 = _cell_name()
            _eat(":")
            c2 = _cell_name()
            _eat(")")
            return ("SUM", c1, c2)
        t = _eat()
        if t.lstrip("-").isdigit():
            return ("NUM", int(t))
        if CELL_RE.fullmatch(t):
            return ("CELL", t)
        raise SpreadsheetError(f"unexpected token: {t}")

    def _cell_name():
        t = _eat()
        if not CELL_RE.fullmatch(t):
            raise SpreadsheetError(f"expected cell name, got {t}")
        return t

    ast = _add()
    if pos[0] != len(tokens):
        raise SpreadsheetError(f"unexpected token: {tokens[pos[0]]}")
    return ast


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def _tokenize(formula: str) -> list[str]:
    toks: list[str] = []
    i = 0
    while i < len(formula):
        if formula[i].isspace():
            i += 1; continue
        if formula[i].isdigit() or (formula[i] == "-" and toks and toks[-1] not in (":", "(", "+", "-", "*", "/")):
            j = i + 1
            while j < len(formula) and formula[j].isdigit():
                j += 1
            toks.append(formula[i:j]); i = j; continue
        if formula[i:i+3] == "SUM":
            toks.append("SUM"); i += 3; continue
        if CELL_RE.fullmatch(formula[i:i+2]) and (i + 2 >= len(formula) or not formula[i+2].isalpha()):
            # could be multi-letter col — grab all letters then digits
            j = i
            while j < len(formula) and formula[j].isupper():
                j += 1
            k = j
            while k < len(formula) and formula[k].isdigit():
                k += 1
            if k > j:
                toks.append(formula[i:k]); i = k; continue
        c = formula[i]
        if c in "+-*/():".replace(" ", ""):
            toks.append(c); i += 1; continue
        raise SpreadsheetError(f"unexpected character: {c}")
    return toks


# ---------------------------------------------------------------------------
# AST evaluator
# ---------------------------------------------------------------------------

def _eval_ast(node: Any, cells: dict, memo: dict, visiting: set) -> int:
    op = node[0]
    if op == "NUM":
        return node[1]
    if op == "CELL":
        return _get_cell(node[1], cells, memo, visiting)
    if op == "+":
        return _eval_ast(node[1], cells, memo, visiting) + _eval_ast(node[2], cells, memo, visiting)
    if op == "-":
        return _eval_ast(node[1], cells, memo, visiting) - _eval_ast(node[2], cells, memo, visiting)
    if op == "*":
        return _eval_ast(node[1], cells, memo, visiting) * _eval_ast(node[2], cells, memo, visiting)
    if op == "/":
        d = _eval_ast(node[2], cells, memo, visiting)
        if d == 0:
            raise SpreadsheetError("division by zero")
        return int(_eval_ast(node[1], cells, memo, visiting) / d)  # trunc toward zero
    if op == "u+":
        return _eval_ast(node[1], cells, memo, visiting)
    if op == "u-":
        return -_eval_ast(node[1], cells, memo, visiting)
    if op == "SUM":
        return _expand_sum(node[1], node[2], cells, memo, visiting)
    raise SpreadsheetError(f"unknown opcode: {op}")


def _get_cell(name: str, cells: dict, memo: dict, visiting: set) -> int:
    if name not in cells:
        raise SpreadsheetError(f"unknown cell: {name}")
    if name in memo:
        return memo[name]
    if name in visiting:
        raise SpreadsheetError("cycle detected")
    visiting.add(name)
    raw = cells[name]
    val = raw if isinstance(raw, int) else _eval_formula(raw, cells, memo, visiting)
    memo[name] = val
    visiting.discard(name)
    return val


def _eval_formula(formula: str, cells: dict, memo: dict, visiting: set) -> int:
    if not formula.startswith("="):
        raise SpreadsheetError("formula must start with =")
    tokens = _tokenize(formula[1:])
    if not tokens:
        raise SpreadsheetError("empty formula")
    ast = _parse(tokens)
    return _eval_ast(ast, cells, memo, visiting)


# ---------------------------------------------------------------------------
# SUM range expansion
# ---------------------------------------------------------------------------

def _cell_coords(name: str) -> tuple[int, int]:
    m = CELL_RE.fullmatch(name)
    if not m:
        raise SpreadsheetError(f"invalid cell name: {name}")
    col = ord(m.group(1).upper()) - ord("A")
    row = int(m.group(2))
    if row < 1:
        raise SpreadsheetError(f"invalid row: {row}")
    return (col, row)


def _expand_sum(c1: str, c2: str, cells: dict, memo: dict, visiting: set) -> int:
    (cc1, cr1) = _cell_coords(c1)
    (cc2, cr2) = _cell_coords(c2)
    if cc1 > cc2 or cr1 > cr2:
        raise SpreadsheetError(f"invalid range: {c1}:{c2}")
    lo_c, hi_c = cc1, cc2
    lo_r, hi_r = cr1, cr2
    total = 0
    for c in range(lo_c, hi_c + 1):
        for r in range(lo_r, hi_r + 1):
            name = f"{chr(c + ord('A'))}{r}"
            if name not in cells:
                raise SpreadsheetError(f"unknown cell in range: {name}")
            total += _get_cell(name, cells, memo, visiting)
    return total


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def evaluate_workbook(cells: dict[str, int | str]) -> dict[str, int]:
    # Validate all cell names first
    for name in cells:
        m = CELL_RE.fullmatch(name)
        if not m or int(m.group(2)) < 1:
            raise SpreadsheetError(f"invalid cell name: {name}")

    safe = dict(cells)  # don't mutate input
    memo: dict[str, int] = {}
    visiting: set[str] = set()

    result = {}
    for name in cells:
        result[name] = _get_cell(name, safe, memo, visiting)
    return result

