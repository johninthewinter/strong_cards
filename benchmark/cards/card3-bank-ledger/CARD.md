# Bank Ledger With Overdraft Limit

## Goal

Implement a small in-memory bank ledger that tracks accounts, integer-cent balances, immutable ledger entries, total cash, and an account-level overdraft limit.

The challenge is not CRUD. The implementation must behave like a tiny state machine: every accepted debit mutates exactly once, every rejected debit leaves state unchanged, transfers are atomic, and no account balance may ever cross below `-overdraft_limit`.

## Contract

Expose the API already declared in `bank_ledger.py`.

- `BankLedger(overdraft_limit: int)` creates an empty ledger. Negative limits are invalid.
- `open_account(account_id: str, opening_balance: int = 0) -> None` creates a unique account. Empty ids and negative opening balances are invalid.
- `deposit(account_id: str, amount: int) -> int` adds a positive amount and returns the new balance.
- `withdraw(account_id: str, amount: int) -> int` subtracts a positive amount and returns the new balance unless it would cross the overdraft limit.
- `transfer(source_account_id: str, target_account_id: str, amount: int) -> tuple[int, int]` atomically debits source and credits target, returning `(source_balance, target_balance)`.
- `balance(account_id: str) -> int` returns the current balance.
- `accounts() -> tuple[str, ...]` returns sorted account ids.
- `history(account_id: str) -> tuple[LedgerEntry, ...]` returns immutable per-account history in sequence order.
- `total_cash() -> int` returns the sum of all balances.

Expected exceptions:

- `ValueError` for invalid construction, empty account ids, non-positive transaction amounts, negative opening balances, and self-transfers.
- `AccountExistsError` for duplicate account creation.
- `AccountNotFoundError` for unknown accounts.
- `OverdraftError` when a debit or transfer would push the source below `-overdraft_limit`.

## Acceptance

Run:

```bash
.venv/bin/python -m pytest test_bank_ledger.py
```

All tests must pass, including the Hypothesis state-machine property test. That property test uses an independent dict model as an oracle and verifies after every generated operation that:

- ledger balances match the model,
- rejected overdrafts do not mutate state,
- transfers are atomic,
- total cash matches the sum of model balances,
- no modeled balance ever crosses below `-overdraft_limit`.

The provided stub must fail these tests with `NotImplementedError`.

## Scope

files_write:

- `bank_ledger.py`

files_read:

- `bank_ledger.py`
- `test_bank_ledger.py`
- `CARD.md`
- `CODER_PROMPT.txt`

## Non-goals

- Do not persist data to disk, databases, network services, or external processes.
- Do not implement interest, fees, currencies, timestamps, authentication, or concurrency controls.
- Do not use floats or `Decimal`; amounts are already integer cents.
- Do not change public signatures, exception class names, or test expectations.
