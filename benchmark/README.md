# Published benchmark artifacts

This directory contains the ten contracts, initial implementation stubs, and
public test suites used by the pilot. The files are published in their red-gate
state: every implementation is deliberately incomplete.

| Card | Subject | Principal capability |
|---:|---|---|
| 1 | LRU cache | Mutable state, recency, property-model agreement |
| 2 | Interval merge | Edge semantics, normalization, non-mutation |
| 3 | Bank ledger | Stateful invariants and atomic transfer |
| 4 | Undo stack | Immutable transitions and branch history |
| 5 | Generic LRU class | Familiar API under a denser test surface |
| 6 | Rich interval merge | Negative, nested, duplicate, and boundary cases |
| 7 | Expression evaluator | Parsing, precedence, variables, error handling |
| 8 | Topological batcher | Graph ordering, implicit nodes, cycle rejection |
| 9 | Spreadsheet engine | Parser, dependency graph, ranges, cycles, state |
| 10 | Glob matcher | Custom parser and matcher; invalid as a comparison gate in v1 |

The SHA-256 values for each published contract, stub, and test file are recorded in
[`evidence/card-catalog.csv`](../evidence/card-catalog.csv). The public verifier
recomputes them.

## Why the raw coder prompts are absent

The v1 prompt envelopes embedded workstation paths and, on some later cards,
failure context from informed retries. Publishing a cosmetically sanitized
version as though it were the original would create false reproducibility.

The research archive retains those source prompts. This public release instead
publishes the invariant experimental objects—the contract, stub, and tests—and
states the prompt-envelope limitation explicitly. The next experiment will
freeze path-independent prompts before the first run and publish their hashes and
content verbatim.

One source-only normalization was made to the excluded Card 10 test file: two
literal pictographs were rewritten as equivalent Python Unicode escapes. Runtime
string values and test behavior are unchanged. The original frozen test digest
is retained in the provenance note; Cards 1-9 are byte-identical to the frozen
comparative artifacts.

## Inspect the red gates

With Python 3.14 and the development dependencies installed:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q benchmark/cards/card1-lru-cache
```

The command must fail because the implementation is still a stub. The original
manifest recorded the same expected red state for all ten cards. A v1 worker run
copied one card into a fresh directory, instructed the worker to change only its
solution file, and applied the recorded gates outside the model process. The
[runner archive](../runner/README.md) documents why that was not a complete
filesystem sandbox.

To check every published red gate in one command:

```bash
make verify-red
```

This also replays the published, excluded GPT-5.5 xhigh reference against the
public Card 10 suite so its forensic 7/7 record is executable. The verifier uses
the declared public replay seed `20260721`; the original historical Hypothesis
seed was not retained.

Card 10 is included for auditability, not as a valid capability test. Its
contract/test contradiction is documented in
[`evidence/card10-audit.md`](../evidence/card10-audit.md).
