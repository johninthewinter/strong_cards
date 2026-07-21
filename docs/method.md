# Method

## Research question

This pilot tested a placement hypothesis:

> After a frontier model has converted a programming problem into frozen,
> externally testable units, can smaller or local models execute those units
> under a deterministic control loop with no runtime LLM coordinator?

The experiment was not designed to rank general intelligence. It tested whether
model capability becomes operationally useful when the surrounding system
removes unresolved decisions and refuses to trust self-reported completion.

## Experimental object

The benchmark was a synthetic ladder of ten coding cards:

1. LRU cache
2. interval merge
3. bank ledger
4. undo stack
5. generic LRU class
6. richer interval merge
7. expression evaluator
8. topological batcher
9. spreadsheet engine
10. glob matcher

Each card supplied a bounded implementation target, a starting stub, tests,
scope rules, and a timeout. Later cards generally required more state, edge-case
handling, or interacting invariants. The ladder is a first test, not a calibrated
measure of task complexity across domains.

## Phase 1: adaptive deck development, then freeze

GPT-5.5 at medium reasoning effort, through Codex, designed the deck and its
execution contracts. Codex session metadata and the contemporary handoff recover
that attribution; the frozen manifest's `high` effort field is a provenance
error.

The deck was developed adaptively rather than preregistered before all worker
activity. Earlier worker runs informed later artifacts. Cards 7 and 9 include
prior failure evidence, and the Card 9 prompt explicitly prescribes a memoized
DFS dependency evaluator with rectangular range expansion. This was deliberate
guided implementation, not zero-shot algorithm discovery. The authoring phase:

- define the behavioral interfaces and invariants;
- decompose the ladder into bounded Strong Cards;
- write starting stubs and acceptance tests;
- specify allowed paths, non-goals, budgets, and stop conditions;
- verify that the initial artifacts failed their gates;
- write SHA-256 digests for the card, prompt, stub, and tests into a frozen
  manifest.

Once all ten artifacts were frozen, the deck became the fixed input to the
principal local and hosted comparison sweeps. No planner or coordinator model
rewrote a card within those measured routes.

## Phase 2: deterministic execution

A shell/Python runner owned the runtime state machine. For each fixed model route
it:

1. materialized a fresh working-directory copy of the starting artifact;
2. iterated through a hard-coded ordered card array, with a `broken` flag that
   skipped all later cards after a terminal two-attempt failure;
3. invoked the configured adapter with the frozen prompt;
4. captured exit status, timeout, output, worker-invocation duration, and
   selected directory observations;
5. ran test immutability, visible top-level scope, anti-stub, and functional
   gates outside the model;
6. accepted the card, supplied one bounded failure packet for an informed retry,
   or stopped according to fixed policy;
7. appended the attempt record within that sweep invocation.

There was no runtime prompt asking a stronger model what to run next, whether to
retry, or whether a candidate was good enough. Those decisions were encoded in
ordinary control flow. The [historical runners](../runner/README.md) are public.
The [minimal loop](../protocol/minimal-loop.md) and
[controller policy](../protocol/controller-policy.md) specify the hardened
follow-up rather than pretending v1 already had those controls.

## Execution surfaces were adapters

Different model families required different launch surfaces:

| Route type | Execution surface | Inference location | Runtime authority |
|---|---|---|---|
| Qwen3.6 27B and Gemma 4 31B | Claude Code-compatible `claude-ollama` headless interface | Local Ollama on the test workstation | None beyond worker invocation |
| Hosted comparison models | OpenCode CLI | Hosted OpenCode Go model routes | No control-plane authority |
| GPT frontier reference on Card 10 | Codex | Hosted | None beyond worker invocation |

The surface translated a fixed request into the worker's CLI contract and
returned observable process data. The worker decided code and tool actions, but
the surface did not choose card order, retry count, gate verdict, or the next
controller transition. Calling the surface a harness does not make it the
workflow controller.

## Hardware context

The local routes ran on a MacBook Pro with an Apple M5 Max, 18 CPU cores, and
128 GB of unified memory. This identifies the environment in which local
feasibility and elapsed times were observed. It is not a hardware benchmark:
throughput, power, temperature, and alternative quantizations were not controlled.

## Gate contract

A card counted as accepted by the v1 runner only when its recorded gates passed:

- the frozen source deck still matched the manifest before and after the attempt;
- the copied test file remained unchanged;
- no unexpected visible top-level name was observed in the run directory;
- prohibited `NotImplementedError`, `TODO`, `FIXME`, and standalone-ellipsis
  patterns were absent from the solution;
- the exact acceptance suite exited successfully;
- the wrapper did not classify the attempt as a timeout.

This was not complete write-scope enforcement. V1 did not observe dotfiles,
off-tree reads or writes, all deletions, nested changes, or modifications to
every copied context file. The local worker also had shell tools with interactive
permissions bypassed. Isolation was therefore cwd plus instructions, not an OS
sandbox.

Worker prose had no effect on the result. A timeout remained in the ledger even
if a later attempt passed. Qwen3.6 27B's Card 9 acceptance, for example, is
reported as retry-assisted after a 900-second timeout and a longer recorded
follow-up, not as a first-pass success.

The v1 runner's recorded order was process outcome, functional tests,
anti-stub, test immutability/top-level directory scope, then final verdict. The reusable controller policy in
this repository hardens the next version by checking frozen-input integrity and
scope earlier. That normative ordering is not retroactively presented as the v1
implementation.

## Threat model

| Failure mode | External control | Residual risk exposed by the pilot |
|---|---|---|
| Worker claims completion without working code | Ignore prose; rerun tests outside the worker | Public tests may still be incomplete |
| Worker changes the question | Verify the source manifest and copied test | Other copied context and off-tree changes were not fully observed |
| Worker widens scope | Reject unexpected visible top-level names | Kimi K2.6 was caught, but v1 was not a complete filesystem allowlist |
| Worker leaves a placeholder | Anti-stub scan | Kimi K2.7 showed that a broad lexical rule can reject legitimate abstraction |
| Worker consumes unbounded time | Process timebox and terminal timeout state | Qwen C9 exposed incomplete launch-level timeout telemetry |
| Harness fails to produce edits | Separate no-edit/tool failure from semantic failure | Early direct-Ollama baselines understated capability |
| Acceptance oracle contradicts the contract | Pre-run entailment review and post-run benchmark audit | Card 10 showed that green tests can encode the wrong target |
| Controller silently changes policy | Version route, budget, gate order, and runner | v1 did not bind every one of these fields in its manifest |

The controller reduces the worker's authority; it does not make every external
oracle correct. That distinction is why invalid-card state is part of the
protocol rather than being collapsed into model failure.

## Measurements

The useful unit is the attempt, not the model's final message. The runner captured:

- model route and adapter;
- deck, card, prompt, stub, and test identity;
- attempt number;
- start and end time plus worker-CLI wall time;
- exit, timeout, or launch status;
- changed-path and anti-stub results;
- test result and gate output;
- terminal controller state;
- whether acceptance required a retry.

The published wall totals sum worker invocation only. They exclude warm/smoke
preflight, pytest and other post-worker gates, and controller overhead. They are
not end-to-end run time.

Comparisons should distinguish semantic test success from full-gate success. For
example, a model can produce working behavior but fail the scope gate by creating
an unapproved file. Both facts belong in the record.

## What “deterministic” means

The models remain probabilistic. Repeating a run may change tokens, latency, or
the candidate implementation. Determinism applies to execution authority:

- the source deck and route are frozen for the principal sweep;
- the next card is selected by a fixed order;
- gates run in a fixed order;
- a pass, retry, stop, or invalidation follows explicit predicates;
- no model judges its own output;
- preserved attempts remain auditable within the available invocation files.

For the same manifest and observed gate results, the controller takes the same
transition. That is a deterministic workflow around nondeterministic inference.

## Card 10 validity failure

Card 10 cannot support a clean model-capability comparison. Its written contract
said that `*` matched zero or more characters and explicitly rejected path
semantics. One example nevertheless required `a*b` not to match `a/b`, while the
property oracle based on `fnmatch.fnmatchcase` implied that it should match. A
second public test also expected one escaped literal backslash in the pattern to
match two backslashes in the text, contradicting the written escape rule.

The GPT frontier reference cleared the seven published tests, but inspection of
the implementation found a branch for the slash contradiction and broadened
backslash behavior for the second. The observable
statement is therefore narrow: the run passed the published gate. It is not
evidence of a general glob implementation or of a frontier-only capability wall.

The protocol marks Card 10 `INVALID_CARD` for comparative interpretation. Its
attempts and timeouts remain useful operational evidence, but headline completion
claims should use Cards 1 through 9 until a corrected card is audited, refrozen,
and rerun with stronger hidden or mutation-tested acceptance.

## Inference boundary

The pilot supports a feasibility claim: local Qwen3.6 27B and Gemma 4 31B both
made the published gates green through Card 9 under guided execution, alongside
several hosted model routes. Post-hoc probes found that Qwen lacked multi-letter
cell support and that both local artifacts accepted booleans and lost precision
on large integer division. The result is operational gate evidence, not complete
contract proof. It also demonstrates that retry budget can determine whether a
test-green implementation becomes observable as a pass.

It does not establish causal superiority over an orchestrated workflow, generalize
to arbitrary repositories, or prove that every task can be compressed into a
Strong Card. The study has limited repetitions, a synthetic ladder, heterogeneous
routes, and a defective tenth card. Its value is architectural: it identifies a
small, testable runtime design and provides evidence strong enough to justify a
more controlled second experiment.
