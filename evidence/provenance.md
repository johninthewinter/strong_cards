# Provenance, normalization, and limits

## Source precedence

Conflicts were resolved in this order:

1. Frozen card content and its manifest hashes
2. Literal runner result lines and gate output
3. Structured JSONL run records
4. Codex session metadata for card authoring and the isolated GPT reference
5. Contemporary benchmark reports
6. Retrospective narrative

This order changes an early interpretation of Card 10. Its published gate did
turn green for GPT-5.5 xhigh, but the frozen contract, tests, and implementation
show that the benchmark itself is internally inconsistent. The result is
therefore recorded without using it as capability evidence.

## Source artifacts

The derived tables were reconstructed from these private raw artifacts and
artifact classes:

- `frozen-card-manifest.json`, the ten card contracts, solution stubs, and tests;
- Codex session metadata and the contemporary authoring handoff that identify
  GPT-5.5 at medium reasoning effort as the card author;
- `18-opencode-go-sweep-results.jsonl` and
  `19-opencode-go-addon-sweep-results.jsonl` for hosted models;
- `20-claude-ollama-local-sweep-results.jsonl`,
  `22-qwen27-claude-ollama-force-card10-results.jsonl`, and
  `23-gemma-card10-only-results.jsonl` for local models;
- the isolated Codex session used for the GPT-5.5 xhigh Card-10 reference;
- the matching controller scripts and
  `21-PRELIMINARY-MODEL-BENCH-REPORT.md`.

Raw streams are not published because they contain workstation paths, complete
model transcripts, tool traces, and disposable run directories. The frozen
content hashes needed to identify the card deck are published in
`card-catalog.csv`. Sanitized historical controller scripts are published under
`runner/archive/`; `runner-artifacts.csv` binds them to their private source
hashes and records the limited parameterization applied for publication.

The frozen manifest's `author_effort: high` field is a provenance error. Codex
turn metadata consistently records GPT-5.5 at medium reasoning effort, and the
contemporary handoff agrees. The public record uses the session evidence rather
than repeating the incorrect manifest label.

## Deck chronology

The deck was developed adaptively rather than preregistered before every worker
interaction. Cards 7-9 were developed after earlier worker runs. Cards 7 and 9
include prior failure evidence, and Card 9 explicitly supplies a memoized
depth-first-search and range-expansion implementation strategy. The comparison
therefore measures frontier-guided implementation, not zero-shot worker
reasoning.

All ten final card artifacts were hash-frozen before the principal hosted and
local comparison sweeps. The chronology supports a two-stage claim: frontier
reasoning compressed observed ambiguity into fixed execution contracts, then a
deterministic controller ran the comparative deck without runtime replanning.

Cards 1-9 are published byte-for-byte with their frozen contract, stub, and test
digests. In the excluded Card 10 test only, literal Unicode pictographs were
rewritten as equivalent Python `\U0001F642` and `\U0001F643` escapes to honor the
publication's no-pictograph style rule without changing runtime strings. The
original frozen C10 test SHA-256 is
`a9a1ba2a63b713b9e22c0862901b9743ea0156405f90e62cb34e9fe40cca3383`; the
published normalized file digest is recorded in `card-catalog.csv`.

One primary hosted stream stores escaped record separators and has a malformed
tail. Its valid records were normalized through the final complete DeepSeek V4
Flash row and cross-checked against the contemporary report. The separate add-on
stream for Kimi K2.7 Code and DeepSeek V4 Pro is valid JSONL. No missing or
malformed tail data is presented as a measured result.

Earlier direct-Ollama baseline rows are not mixed into the principal comparison.
They used a materially different tool envelope and included no-write artifacts.
The published local rows use the Claude Code-compatible headless harness and
preserve their exact Ollama model tags.

## Architecture evidence

GPT-5.5 authored the cards, interfaces, invariants, tests, and final manifest
through Codex. During the principal sweeps, plain shell/Python control selected
the next fixed card, invoked the configured adapter, ran the fixed v1 gates,
allowed only the configured retry transition, and stopped or continued from
explicit verdicts. No LLM made a runtime control-plane decision about card
order, routing, retry eligibility, acceptance, or stopping.

The worker still reasoned, selected tools, and edited code inside its assigned
working directory. This is not a claim that the task loop contained no model
decisions; it is a claim that those decisions did not control workflow topology
or override acceptance policy.

The historical v1 controller provided a fresh working directory and prompt
instructions, not an operating-system sandbox. The local worker had Bash access
under bypassed permission checks. The runner reverified the source manifest
before and after execution, diffed the copied test, scanned for unremoved stubs,
and rejected unexpected visible top-level names. It did not completely observe
dotfiles, off-tree reads or writes, deletions, nested changes, or modifications
to every copied context file. Consequently, `scope` in the tables means the v1
visible-directory gate, not hermetic write confinement.

Each sweep truncated its result file when that invocation began and appended an
event row as work progressed. The files are append-only within an invocation;
they are not durable append-only ledgers across reruns.

## Harness is not inference

- Local Qwen3.6 and Gemma 4 inference ran through Ollama on a MacBook Pro with
  M5 Max, 18 reported cores, and 128 GB unified memory. A Claude
  Code-compatible `claude-ollama` headless wrapper supplied the coding harness.
  No Anthropic model performed those local attempts.
- Hosted comparison models ran through the OpenCode CLI using OpenCode Go model
  routes. OpenCode was the execution surface; each named route supplied
  inference.
- GPT-5.5 xhigh ran through Codex for one isolated Card-10 reference only.

These surfaces have different transport, startup, and tool overhead. Recorded
worker wall seconds measure only the coding-model CLI invocation. They exclude
warm-up or smoke work, pytest and other acceptance gates, and controller
overhead. They are useful operational observations, not a controlled
inference-speed benchmark across providers.

The historical archive preserves route names and local model tags, not an exact
runtime lock. It lacks immutable hosted weight revisions, local Ollama blob
digests, complete decoding/context parameters, and consistent version records
for Ollama, OpenCode CLI, `claude-ollama`, the host operating system, and Python.
That prevents bit-for-bit environment reconstruction and is a required fix for
protocol v2.

The historical Hypothesis seed was also not retained. The public executable
checks declare seed `20260721` only to make CI replay stable; it is a publication
seed, not reconstructed historical provenance.

## Normalization rules

- `PASS` means tests, anti-stub, and scope gates all passed.
- `PASS_ON_RETRY` means the same gates passed after one recorded informed retry.
- A green test gate with a failed scope or anti-stub gate remains a failure.
- `published_gate_ceiling` is the last contiguous runner-accepted card among
  Cards 1-9. It is not a claim of complete written-contract satisfaction.
- `worker_wall_seconds_to_published_gate_ceiling` sums worker CLI invocations for
  accepted cards and failed attempts for a card that later passed. It excludes
  work on the subsequent breakpoint and all non-worker gate/controller time.
- Worker wall seconds are kept as integers exactly as emitted, except for the
  isolated GPT reference whose session and pytest timings retain decimals.
- The exact timeout cap applied to Qwen3.6 27B Card 9 attempt 2 is not present in
  the normalized result row. The row proves an extended run lasting 2,006
  seconds with an informed prompt, not the configured cap itself.
- Local hardware values are operator-reported configuration facts; unique host
  identifiers were neither retained nor published.

## Card 9 artifact audit

The accepted Qwen3.6 27B and Gemma 4 31B Card 9 implementations, their literal
pytest output, and their hashes are published under `accepted-artifacts/`. Both
made all eleven published tests green. Qwen did so after a 900-second timeout at
9/11 and an informed extended rerun recorded at 2,006 seconds; Gemma did so on
its first attempt in 804 seconds.

Post-hoc probes found coverage gaps. Qwen rejected a valid workbook using
`AA1`, `AB1`, and `AC1`, while Gemma evaluated it correctly. Both implementations
accepted boolean values even though the card excludes them, and both lost
precision when dividing `100000000000000000000` by `3`. These findings preserve
the published-gate outcomes while preventing them from being overstated as
full-contract proof.

## Card 10 reference artifact

The exact GPT-5.5 xhigh Card 10 reference implementation is published under
`reference-artifacts/` with a sanitized copy of its final pytest output and a
hash-bound metadata record. The private Codex session is not published because
it contains workstation paths, task identifiers, telemetry, instructions, and
encrypted reasoning data; its SHA-256 digest binds the public metadata to the
retained source record. The implementation itself contains no private paths or
credentials.

## What the evidence supports

It supports feasibility of a narrow placement strategy: precompute ambiguity
with a frontier model, then use smaller or cheaper models for bounded
implementation cells controlled by deterministic code. It also shows that the
local 27B and 31B configurations reached the same nine-card published-gate
ceiling as eight hosted routes under their respective harnesses. This result is
about placement inside a constrained pipeline, not replacement of frontier
reasoning.

## What it does not support

- It is not a statistically powered model benchmark; most cells are single
  observations with at most one informed retry.
- It does not show that a small model can plan or complete an arbitrary project
  without decomposition.
- It does not establish a frontier-only Card-10 boundary.
- It does not compare inference speed or cost on equal infrastructure.
- It has no hidden-test set, repeated seeds, confidence intervals, or
  independent reproduction yet.
- It does not prove semantic correctness beyond the published gates. The Card 9
  probes and Card 10 defects demonstrate why that distinction matters.
- It is artifact-auditable but not replay-complete: private raw transcripts and
  path-bearing event streams are not included, and the historical environment
  was not hermetic.

The next experiment should repair and refreeze Card 10, add hidden tests, repeat
each model/card cell, add complete filesystem observation or an actual sandbox,
use a durable append-only event ledger, preserve exact timeout configuration in
every event, and publish a clean replayable runner.
