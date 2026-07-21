# Undo/Redo Stack

## Goal

Implement a tiny immutable undo/redo stack for editor-like state snapshots.

The challenge is the shared-state interplay between `undo` and `redo`: each move must preserve chronological ordering while transferring exactly one value between the past/current/future regions. A new `push` after undoing must create a branch by clearing redo history.

## Contract

Expose the API already declared in `undo_stack.py`.

- `UndoStack(current: T, past: tuple[T, ...] = (), future: tuple[T, ...] = ())` stores the current value, older values in chronological order, and redo values in chronological order.
- `push(stack: UndoStack[T], value: T) -> UndoStack[T]` returns a new stack where `value` is current, the previous current is appended to `past`, and `future` is cleared.
- `undo(stack: UndoStack[T]) -> UndoStack[T]` returns a new stack moved one step backward when `past` is non-empty.
- `redo(stack: UndoStack[T]) -> UndoStack[T]` returns a new stack moved one step forward when `future` is non-empty.
- `history(stack: UndoStack[T]) -> tuple[T, ...]` returns all known values in chronological order: `past`, then `current`, then `future`.

Boundary behavior:

- Undo with empty `past` is a no-op and returns an equal stack.
- Redo with empty `future` is a no-op and returns an equal stack.
- The stack must be immutable; operations return new values instead of mutating the input.

## Acceptance

Run:

```bash
.venv/bin/python -m pytest test_undo_stack.py
```

All tests must pass, including the Hypothesis property test. That property test uses an independent list-and-index model as an oracle and verifies after generated sequences that:

- `undo` followed by `redo` round-trips when undo is available,
- `redo` followed by `undo` round-trips when redo is available,
- `push` clears redo history after a branch,
- `past`, `current`, `future`, and `history()` preserve chronological ordering.

The provided stub must fail these tests with `NotImplementedError`.

## Scope

files_write:

- `undo_stack.py`

files_read:

- `undo_stack.py`
- `test_undo_stack.py`
- `CARD.md`
- `CODER_PROMPT.txt`

## Non-goals

- Do not implement persistence, file I/O, databases, network calls, or external processes.
- Do not add editor commands, diffing, patch formats, timestamps, branching trees, or merge behavior.
- Do not mutate `UndoStack` instances in place.
- Do not change public function names, signatures, dataclass fields, or test expectations.
