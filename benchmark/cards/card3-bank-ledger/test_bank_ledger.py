from __future__ import annotations

import pytest
from hypothesis import assume
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from bank_ledger import (
    AccountExistsError,
    AccountNotFoundError,
    BankLedger,
    LedgerEntry,
    OverdraftError,
)


def test_open_deposit_withdraw_history_and_totals() -> None:
    ledger = BankLedger(overdraft_limit=50)

    ledger.open_account("checking", opening_balance=25)
    assert ledger.accounts() == ("checking",)
    assert ledger.balance("checking") == 25
    assert ledger.total_cash() == 25

    assert ledger.deposit("checking", 40) == 65
    assert ledger.withdraw("checking", 90) == -25
    assert ledger.balance("checking") == -25
    assert ledger.total_cash() == -25

    history = ledger.history("checking")
    assert isinstance(history, tuple)
    assert [entry.kind for entry in history] == ["open", "deposit", "withdraw"]
    assert [entry.amount for entry in history] == [25, 40, 90]
    assert [entry.balance_after for entry in history] == [25, 65, -25]
    assert all(isinstance(entry, LedgerEntry) for entry in history)
    assert [entry.sequence for entry in history] == sorted(entry.sequence for entry in history)


def test_overdraft_rejection_is_exact_and_does_not_mutate_state() -> None:
    ledger = BankLedger(overdraft_limit=30)
    ledger.open_account("ops", opening_balance=10)
    ledger.deposit("ops", 5)
    before_history = ledger.history("ops")

    with pytest.raises(OverdraftError):
        ledger.withdraw("ops", 46)

    assert ledger.balance("ops") == 15
    assert ledger.total_cash() == 15
    assert ledger.history("ops") == before_history


def test_transfer_is_atomic_and_preserves_total_cash() -> None:
    ledger = BankLedger(overdraft_limit=20)
    ledger.open_account("source", opening_balance=10)
    ledger.open_account("target", opening_balance=7)

    assert ledger.transfer("source", "target", 25) == (-15, 32)
    assert ledger.balance("source") == -15
    assert ledger.balance("target") == 32
    assert ledger.total_cash() == 17

    source_before = ledger.history("source")
    target_before = ledger.history("target")
    with pytest.raises(OverdraftError):
        ledger.transfer("source", "target", 6)

    assert ledger.balance("source") == -15
    assert ledger.balance("target") == 32
    assert ledger.total_cash() == 17
    assert ledger.history("source") == source_before
    assert ledger.history("target") == target_before


def test_validation_and_unknown_accounts() -> None:
    ledger = BankLedger(overdraft_limit=0)
    ledger.open_account("a")

    with pytest.raises(AccountExistsError):
        ledger.open_account("a")

    for bad_amount in (0, -1):
        with pytest.raises(ValueError):
            ledger.deposit("a", bad_amount)
        with pytest.raises(ValueError):
            ledger.withdraw("a", bad_amount)

    with pytest.raises(ValueError):
        ledger.open_account("")
    with pytest.raises(ValueError):
        BankLedger(overdraft_limit=-1)
    with pytest.raises(AccountNotFoundError):
        ledger.balance("missing")
    with pytest.raises(AccountNotFoundError):
        ledger.deposit("missing", 1)


def test_self_transfer_is_rejected_without_changing_state() -> None:
    ledger = BankLedger(overdraft_limit=100)
    ledger.open_account("a", opening_balance=10)
    before = ledger.history("a")

    with pytest.raises(ValueError):
        ledger.transfer("a", "a", 5)

    assert ledger.balance("a") == 10
    assert ledger.total_cash() == 10
    assert ledger.history("a") == before


class LedgerStateMachine(RuleBasedStateMachine):
    account_ids = ("a", "b", "c")

    def __init__(self) -> None:
        super().__init__()
        self.limit = 75
        self.ledger = BankLedger(overdraft_limit=self.limit)
        self.model: dict[str, int] = {}

    @rule(account=st.sampled_from(account_ids), opening_balance=st.integers(min_value=0, max_value=150))
    def open_account(self, account: str, opening_balance: int) -> None:
        if account in self.model:
            with pytest.raises(AccountExistsError):
                self.ledger.open_account(account, opening_balance)
            return

        self.ledger.open_account(account, opening_balance)
        self.model[account] = opening_balance
        assert self.ledger.balance(account) == self.model[account]

    @rule(account=st.sampled_from(account_ids), amount=st.integers(min_value=1, max_value=125))
    def deposit(self, account: str, amount: int) -> None:
        if account not in self.model:
            with pytest.raises(AccountNotFoundError):
                self.ledger.deposit(account, amount)
            return

        expected = self.model[account] + amount
        assert self.ledger.deposit(account, amount) == expected
        self.model[account] = expected

    @rule(account=st.sampled_from(account_ids), amount=st.integers(min_value=1, max_value=125))
    def withdraw(self, account: str, amount: int) -> None:
        if account not in self.model:
            with pytest.raises(AccountNotFoundError):
                self.ledger.withdraw(account, amount)
            return

        projected = self.model[account] - amount
        before = dict(self.model)
        if projected < -self.limit:
            with pytest.raises(OverdraftError):
                self.ledger.withdraw(account, amount)
            assert self.model == before
            assert self.ledger.balance(account) == before[account]
            return

        assert self.ledger.withdraw(account, amount) == projected
        self.model[account] = projected

    @rule(
        source=st.sampled_from(account_ids),
        dest=st.sampled_from(account_ids),
        amount=st.integers(min_value=1, max_value=125),
    )
    def transfer(self, source: str, dest: str, amount: int) -> None:
        assume(source != dest)

        if source not in self.model or dest not in self.model:
            with pytest.raises(AccountNotFoundError):
                self.ledger.transfer(source, dest, amount)
            return

        projected_source = self.model[source] - amount
        before = dict(self.model)
        if projected_source < -self.limit:
            with pytest.raises(OverdraftError):
                self.ledger.transfer(source, dest, amount)
            assert self.model == before
            assert self.ledger.balance(source) == before[source]
            assert self.ledger.balance(dest) == before[dest]
            return

        expected_dest = self.model[dest] + amount
        assert self.ledger.transfer(source, dest, amount) == (projected_source, expected_dest)
        self.model[source] = projected_source
        self.model[dest] = expected_dest

    @invariant()
    def balances_match_model_and_never_cross_overdraft_limit(self) -> None:
        for account, expected_balance in self.model.items():
            assert self.ledger.balance(account) == expected_balance
            assert expected_balance >= -self.limit
        assert self.ledger.total_cash() == sum(self.model.values())
        assert self.ledger.accounts() == tuple(sorted(self.model))


TestLedgerStateMachine = LedgerStateMachine.TestCase
