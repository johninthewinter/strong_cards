# Card 8 — Topological Batcher

## Goal

Implement deterministic dependency batching for tasks that can run in parallel once their dependencies are complete.

## Contract

Edit only `batcher.py`.

Expose:

- `class DependencyCycleError(ValueError)`
- `def build_batches(tasks: dict[str, set[str]]) -> list[list[str]]`

The input maps each task to the set of tasks it depends on. Dependencies may be implicit nodes that do not appear as top-level keys. Return a list of batches. Every task in a batch may run in parallel. A task must appear in a strictly later batch than all of its dependencies. Each batch must be sorted lexicographically for deterministic output.

Cycle or self-cycle must raise `DependencyCycleError`. The function must not mutate the input mapping or dependency sets.

## Acceptance

`test_batcher.py` must pass, including property tests for random DAGs and minimal batch count.

## Scope

Files write: `batcher.py`

Files read: `test_batcher.py`, `CARD.md`, `CODER_PROMPT.txt`

## Non-goals

- Do not execute tasks.
- Do not add weights, priorities, retries, or concurrency limits.
- Do not change tests.

