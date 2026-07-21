from __future__ import annotations

import re

import pytest
from hypothesis import given, settings, strategies as st

from spreadsheet import SpreadsheetError, evaluate_workbook


def test_literals_and_simple_formulas() -> None:
    cells = {"A1": 2, "A2": 3, "B1": "=A1 + A2 * 4", "B2": "=(A1 + A2) * 4"}
    assert evaluate_workbook(cells) == {"A1": 2, "A2": 3, "B1": 14, "B2": 20}


def test_dependency_order_does_not_depend_on_input_order() -> None:
    cells = {
        "C1": "=B1 + B2",
        "B2": "=A2 * 10",
        "A2": 4,
        "B1": "=A1 + 7",
        "A1": 5,
    }
    assert evaluate_workbook(cells)["C1"] == 52


def test_sum_range_supports_rectangles_and_single_cells() -> None:
    cells = {
        "A1": 1,
        "A2": 2,
        "B1": 10,
        "B2": 20,
        "C1": "=SUM(A1:B2)",
        "C2": "=SUM(B2:B2) + SUM(A1:A2)",
    }
    assert evaluate_workbook(cells)["C1"] == 33
    assert evaluate_workbook(cells)["C2"] == 23


def test_forward_references_inside_sum_range() -> None:
    cells = {"A1": "=SUM(A2:A4)", "A2": 1, "A3": "=A2 + 2", "A4": "=A3 + 3"}
    assert evaluate_workbook(cells)["A1"] == 10


def test_unknown_cell_is_rejected() -> None:
    with pytest.raises(SpreadsheetError):
        evaluate_workbook({"A1": "=A2 + 1"})


def test_cycles_are_rejected() -> None:
    with pytest.raises(SpreadsheetError):
        evaluate_workbook({"A1": "=A2 + 1", "A2": "=A1 + 1"})


def test_self_cycle_through_sum_range_is_rejected() -> None:
    with pytest.raises(SpreadsheetError):
        evaluate_workbook({"A1": "=SUM(A1:A2)", "A2": 1})


def test_invalid_cell_names_and_formulas_are_rejected() -> None:
    bad_inputs = [
        {"AA0": 1},
        {"1A": 1},
        {"A1": "=1 +"},
        {"A1": "=SUM(A2)"},
        {"A1": "=SUM(B2:A1)", "A2": 1, "B1": 2, "B2": 3},
        {"A1": "=A2 / 0", "A2": 1},
        {"A1": "=A2 ** 2", "A2": 1},
    ]
    for cells in bad_inputs:
        with pytest.raises(SpreadsheetError):
            evaluate_workbook(cells)


def test_input_is_not_mutated() -> None:
    cells: dict[str, int | str] = {"A1": 1, "A2": "=A1 + 2"}
    original = dict(cells)
    evaluate_workbook(cells)
    assert cells == original


cell_name = st.builds(
    lambda col, row: f"{col}{row}",
    st.sampled_from(["A", "B", "C", "D"]),
    st.integers(min_value=1, max_value=6),
)


@given(st.lists(st.integers(min_value=-20, max_value=20), min_size=1, max_size=12))
@settings(max_examples=120)
def test_property_chain_of_formulas_matches_running_sum(values: list[int]) -> None:
    cells: dict[str, int | str] = {"A1": values[0]}
    expected = values[0]
    for index, value in enumerate(values[1:], start=2):
        cells[f"A{index}"] = f"=A{index - 1} + {value}"
        expected += value
    result = evaluate_workbook(cells)
    assert result[f"A{len(values)}"] == expected


@given(st.dictionaries(cell_name, st.integers(min_value=-10, max_value=10), min_size=1, max_size=15))
@settings(max_examples=120)
def test_property_sum_of_literal_range_matches_manual_total(cells: dict[str, int]) -> None:
    names = sorted(cells)
    first = names[0]
    last = names[-1]
    match_first = re.fullmatch(r"([A-D])([1-6])", first)
    match_last = re.fullmatch(r"([A-D])([1-6])", last)
    assert match_first and match_last
    col1, row1 = match_first.group(1), int(match_first.group(2))
    col2, row2 = match_last.group(1), int(match_last.group(2))
    if col1 > col2 or row1 > row2:
        return
    expected = 0
    complete = True
    for col_code in range(ord(col1), ord(col2) + 1):
        for row in range(row1, row2 + 1):
            name = f"{chr(col_code)}{row}"
            if name not in cells:
                complete = False
            else:
                expected += cells[name]
    if not complete:
        return
    workbook: dict[str, int | str] = dict(cells)
    workbook["Z9"] = f"=SUM({first}:{last})"
    assert evaluate_workbook(workbook)["Z9"] == expected

