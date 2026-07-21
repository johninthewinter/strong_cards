# Contributing

This repository is an evidence-backed pilot, not a leaderboard. Useful
contributions improve the protocol, challenge a claim, repair or mutation-test
a card, add an independently reproducible run, or strengthen the evidence
validator.

For a new experiment, preserve the distinction between worker output,
deterministic controller state, semantic test status, and full-gate status.
Report failures, retries, invalid cards, and human interventions. Do not collapse
them into a single success number.

Changing a card, prompt, test, timeout, adapter, or gate creates a new protocol
version. Never overwrite the original attempt ledger after a successful retry.

Run `make verify` before opening a pull request.
