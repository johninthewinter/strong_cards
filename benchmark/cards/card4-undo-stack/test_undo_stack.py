from __future__ import annotations

from dataclasses import FrozenInstanceError

from hypothesis import given
from hypothesis import strategies as st

from undo_stack import UndoStack, history, push, redo, undo


def test_push_records_current_and_clears_redo_branch() -> None:
    stack = UndoStack("draft-0")

    stack = push(stack, "draft-1")
    stack = push(stack, "draft-2")
    stack = undo(stack)

    assert stack.current == "draft-1"
    assert stack.past == ("draft-0",)
    assert stack.future == ("draft-2",)

    branched = push(stack, "draft-1b")

    assert branched.current == "draft-1b"
    assert branched.past == ("draft-0", "draft-1")
    assert branched.future == ()
    assert history(branched) == ("draft-0", "draft-1", "draft-1b")


def test_undo_and_redo_are_exact_round_trips() -> None:
    stack = UndoStack(0)
    for value in (1, 2, 3):
        stack = push(stack, value)

    before = stack
    undone_once = undo(stack)
    redone_once = redo(undone_once)

    assert undone_once.current == 2
    assert undone_once.past == (0, 1)
    assert undone_once.future == (3,)
    assert redone_once == before

    redone_first = redo(stack)
    undone_after_empty_redo = undo(redone_first)

    assert redone_first == stack
    assert redo(undo(redone_first)) == redone_first
    assert redo(undone_after_empty_redo) == redone_first


def test_history_ordering_through_multiple_undos_and_redos() -> None:
    stack = UndoStack("a")
    for value in ("b", "c", "d", "e"):
        stack = push(stack, value)

    stack = undo(undo(stack))

    assert stack.current == "c"
    assert stack.past == ("a", "b")
    assert stack.future == ("d", "e")
    assert history(stack) == ("a", "b", "c", "d", "e")

    stack = redo(stack)

    assert stack.current == "d"
    assert stack.past == ("a", "b", "c")
    assert stack.future == ("e",)
    assert history(stack) == ("a", "b", "c", "d", "e")


def test_boundaries_are_no_ops_and_state_is_immutable() -> None:
    stack = UndoStack("only")

    assert undo(stack) == stack
    assert redo(stack) == stack
    assert history(stack) == ("only",)

    try:
        stack.current = "mutated"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("UndoStack must be immutable")


Operation = tuple[str, int | None]


def apply_to_model(values: list[int], index: int, operation: Operation) -> tuple[list[int], int]:
    op_name, maybe_value = operation
    if op_name == "push":
        assert maybe_value is not None
        return values[: index + 1] + [maybe_value], index + 1
    if op_name == "undo":
        return values, max(0, index - 1)
    if op_name == "redo":
        return values, min(len(values) - 1, index + 1)
    raise AssertionError(f"unknown operation: {op_name}")


operation_strategy = st.one_of(
    st.tuples(st.just("push"), st.integers(min_value=-100, max_value=100)),
    st.tuples(st.just("undo"), st.none()),
    st.tuples(st.just("redo"), st.none()),
)


@given(initial=st.integers(min_value=-100, max_value=100), operations=st.lists(operation_strategy, max_size=80))
def test_property_round_trips_and_history_ordering(initial: int, operations: list[Operation]) -> None:
    stack = UndoStack(initial)
    model_values = [initial]
    model_index = 0

    for operation in operations:
        before_stack = stack
        before_values = list(model_values)
        before_index = model_index

        op_name, maybe_value = operation
        if op_name == "push":
            assert maybe_value is not None
            stack = push(stack, maybe_value)
        elif op_name == "undo":
            stack = undo(stack)
        elif op_name == "redo":
            stack = redo(stack)
        else:
            raise AssertionError(f"unknown operation: {op_name}")

        model_values, model_index = apply_to_model(model_values, model_index, operation)

        assert stack.current == model_values[model_index]
        assert stack.past == tuple(model_values[:model_index])
        assert stack.future == tuple(model_values[model_index + 1 :])
        assert history(stack) == tuple(model_values)

        if before_index > 0:
            assert redo(undo(before_stack)) == before_stack
        if before_index < len(before_values) - 1:
            assert undo(redo(before_stack)) == before_stack
