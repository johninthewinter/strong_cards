from __future__ import annotations


class DependencyCycleError(ValueError):
    pass


def build_batches(tasks: dict[str, set[str]]) -> list[list[str]]:
    raise NotImplementedError

