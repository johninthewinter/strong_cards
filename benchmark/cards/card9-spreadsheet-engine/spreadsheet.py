from __future__ import annotations


class SpreadsheetError(ValueError):
    pass


def evaluate_workbook(cells: dict[str, int | str]) -> dict[str, int]:
    raise NotImplementedError

