from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


EntryKind = Literal["open", "deposit", "withdraw", "transfer_in", "transfer_out"]


class LedgerError(Exception):
    """Base exception for ledger-specific failures."""


class AccountExistsError(LedgerError):
    """Raised when opening an account id that already exists."""


class AccountNotFoundError(LedgerError):
    """Raised when an operation references an unknown account id."""


class OverdraftError(LedgerError):
    """Raised when a debit would cross the configured overdraft limit."""


@dataclass(frozen=True)
class LedgerEntry:
    sequence: int
    account_id: str
    kind: EntryKind
    amount: int
    balance_after: int
    counterparty: str | None = None


class BankLedger:
    def __init__(self, overdraft_limit: int) -> None:
        raise NotImplementedError

    @property
    def overdraft_limit(self) -> int:
        raise NotImplementedError

    def open_account(self, account_id: str, opening_balance: int = 0) -> None:
        raise NotImplementedError

    def deposit(self, account_id: str, amount: int) -> int:
        raise NotImplementedError

    def withdraw(self, account_id: str, amount: int) -> int:
        raise NotImplementedError

    def transfer(self, source_account_id: str, target_account_id: str, amount: int) -> tuple[int, int]:
        raise NotImplementedError

    def balance(self, account_id: str) -> int:
        raise NotImplementedError

    def accounts(self) -> tuple[str, ...]:
        raise NotImplementedError

    def history(self, account_id: str) -> tuple[LedgerEntry, ...]:
        raise NotImplementedError

    def total_cash(self) -> int:
        raise NotImplementedError
