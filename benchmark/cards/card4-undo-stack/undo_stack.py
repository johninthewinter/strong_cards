from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class UndoStack(Generic[T]):
    """Immutable undo/redo state for one current value."""

    current: T
    past: tuple[T, ...] = ()
    future: tuple[T, ...] = ()


def push(stack: UndoStack[T], value: T) -> UndoStack[T]:
    """Record a new current value and clear redo history."""
    raise NotImplementedError


def undo(stack: UndoStack[T]) -> UndoStack[T]:
    """Move one step backward if possible; otherwise return the unchanged stack."""
    raise NotImplementedError


def redo(stack: UndoStack[T]) -> UndoStack[T]:
    """Move one step forward if possible; otherwise return the unchanged stack."""
    raise NotImplementedError


def history(stack: UndoStack[T]) -> tuple[T, ...]:
    """Return chronological history: past values, current value, then redo values."""
    raise NotImplementedError
