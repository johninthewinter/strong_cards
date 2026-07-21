# Limitations and claim boundary

This is a first instrumented pilot. It establishes feasibility and exposes a
promising architecture; it does not establish causal superiority, general model
rankings, or production reliability.

## Design limitations

- The deck contains ten synthetic Python tasks, not a representative sample of
  software engineering work.
- Card difficulty was designed to rise broadly but was not independently
  calibrated. A C9 published-gate ceiling is specific to this deck.
- There were no repeated trials, randomized seeds, confidence intervals, or
  blinded reviews.
- There was no monolithic-prompt control, frontier-only full-deck baseline, or
  LLM-orchestrator counterfactual.
- The same research process created the contracts and public tests. No hidden
  holdout suite protected against test-specific implementations.
- Deck development was adaptive. Cards 7 and 9 include earlier failure evidence;
  Card 9 also prescribes a memoized DFS/range-expansion strategy. That is
  legitimate guided execution, but it is not a preregistered zero-shot scale.

## Cross-lane limitations

- Local workers used Ollama through a Claude Code-compatible `claude-ollama`
  surface. Hosted workers used the OpenCode CLI with OpenCode Go routes.
  GPT-5.5 xhigh used Codex.
- Timeouts differed across sweeps. Several hosted Card 10 attempts used a
  shorter pre-envelope budget than the dedicated local follow-ups.
- Model tags were recorded, but immutable provider-side weight revisions and
  local Ollama blob digests were not preserved.
- Exact historical versions for Ollama, OpenCode CLI, `claude-ollama`, the host
  operating system, and Python were not captured consistently. Neither were all
  context-window, sampling, and decoding parameters.
- The local machine configuration is reported, but power, thermal state,
  concurrency, token throughput, and background load were not controlled.
- Local and hosted elapsed time is therefore descriptive, not a fair speed
  ranking.

## Evidence limitations

- Qwen3.6 27B's accepted Card 9 rerun is recorded at 2,006 seconds despite a
  nominal 900-second retry budget. The preserved artifact does not explain the
  launch-level timeout overrun.
- The primary hosted sweep file stored 125 objects with literal `\n` separators
  on one physical line and ended with malformed content. Derived rows were
  recovered conservatively and the defect is disclosed.
- Several early hosted Card 10 attempts encountered stale absolute-path prompt
  behavior or returned no edit. They are not clean semantic failures.
- Kimi K2.7 Code's Card 9 tests passed, but the full gate falsely rejected a
  legitimate abstract `NotImplementedError`. Its C8 full-gate ceiling (8/9
  comparative cards) and its test-green C9 result must both be reported.
- V1 used fresh directories and prompt restrictions, not an OS sandbox. Its
  scope gate missed dotfiles, off-tree activity, some deletions, nested changes,
  and changes to copied context other than the test.
- Result files were truncated at sweep start and appended within an invocation;
  they were not durable append-only ledgers across reruns.
- Raw prompts and transcripts are not public because v1 embedded workstation
  paths and provider/session material. De-identified historical runners, public
  contracts, stubs, tests, two accepted C9 artifacts, hashes, and derived ledgers
  are inspectable, but the original run is not fully replayable from this
  repository alone.

## Card 9 is a published-gate result

Both headline local artifacts passed the eleven public C9 tests. Post-hoc probes
then found that Qwen lacked valid multi-letter cell support and that both Qwen
and Gemma accepted booleans and lost precision on large integer division. Gemma
passed the added multi-letter probe. Neither artifact has complete-contract
proof, and the hosted C9 outputs were not subjected to the same post-hoc corpus.

## Card 10 is invalid for comparison

Card 10 contradicts itself about whether `*` may match `/` and about whether one
escaped literal backslash may match two text backslashes. The GPT-5.5 xhigh
reference passed the public suite with a slash hard-code and broadened
backslash behavior.
Consequently:

- the published 7/7 is a gate result, not a validated general solution;
- local and hosted failures do not establish a frontier-only boundary;
- no 10/10 model score is reported as a capability result;
- Card 10 must be repaired and rerun under a new deck version.

## Economic limitations

- No complete cost ledger exists across frontier design, hosted inference,
  subscriptions, local hardware, electricity, operator time, and failed runs.
- “Zero marginal API billing” for a local run is not equivalent to zero cost.
- The pilot did not measure utilization high enough to compare owned hardware
  with elastic hosted capacity.
- No quality-adjusted cost per accepted card was computed across every route.

## Generalization boundary

The evidence supports this statement:

> In this pilot, shell control made routing, retry, published-gate acceptance,
> and stopping decisions without an LLM coordinator. Local Qwen3.6 27B and Gemma
> 4 31B both made the public gates green through Card 9 under guided execution;
> post-hoc probes found additional semantic gaps.

It does not support these statements:

- small models can autonomously build arbitrary systems;
- a Strong Card always makes a weak model sufficient;
- deterministic control guarantees correct specifications or tests;
- Qwen or Gemma is generally better than the hosted models;
- GPT-5.5 alone can solve the tenth task;
- the architecture is cheaper at production scale without total-cost data.

Those are hypotheses for subsequent controlled experiments.
