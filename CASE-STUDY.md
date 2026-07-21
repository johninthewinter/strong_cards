# Case study: removing the LLM orchestrator

## Abstract

This pilot tested a model-placement architecture, not a model beauty contest.
GPT-5.5 at medium effort, through Codex, iteratively developed a ten-card deck;
session metadata corrects the manifest's erroneous `high` effort label. The deck
was hash-frozen before the principal comparison sweeps. A deterministic
shell/Python runner then dispatched cards, ran executable and partial directory
scope gates, allowed one informed retry, and stopped on terminal failure. The
worker LLM chose code and tool actions; no LLM selected routes, retries,
acceptance, or control-plane transitions.

On an M5 Max MacBook Pro with an 18-core CPU and 128 GB of unified memory, local
Qwen3.6 27B and Gemma 4 31B each made the published gates green through Card 9.
Eight hosted configurations reached the same published-gate ceiling. Card 9 was
not a toy: it combined formula
parsing, dependency resolution, rectangular ranges, cycle detection, immutable
input handling, and property tests.

The apparent final result—a GPT-5.5 xhigh pass on Card 10 where smaller models
failed—did not survive audit. The card contained two contract/test
contradictions, and the passing implementation coded around both. The pilot
therefore demonstrates a useful execution pattern through Card 9 while treating
Card 10 as a measurement failure.

## 1. The claim under test

The experiment began with a narrow hypothesis:

> A smaller model can execute complex implementation work if a stronger model
> resolves ambiguity before the run and deterministic software owns runtime
> authority.

This is materially different from claiming that a small model can autonomously
build an arbitrary product. Open-ended assignments force one model to perform
requirements discovery, architecture, planning, coding, tool use, debugging, and
acceptance. When the result fails, the benchmark does not reveal which capability
was missing. When the result looks convincing, it may still be structurally
wrong.

The pilot separated those responsibilities:

- GPT-5.5 iteratively designed the work, then froze it for the measured sweeps;
- a plain controller enforced the execution policy repeatedly;
- worker models performed bounded transformations;
- configured gates, not model confidence, determined progression;
- terminal failures stopped the sequence, while post-hoc audit could invalidate
  a misleading gate result.

The research object was therefore the complete workflow boundary, not a raw
model response.

## 2. Why remove the orchestrator

Multi-agent systems often place a strong model in the most repetitive role: it
routes every task, interprets every failure, decides every retry, and judges every
completion. That can work, but it makes cost and behavior depend on a
probabilistic control plane. It also obscures where intelligence is actually
required.

This pilot reduced runtime control to five artifacts:

1. a frozen manifest;
2. fresh card working directories;
3. a worker adapter;
4. deterministic shell gates;
5. one JSONL file appended within each sweep invocation.

The next state followed directly from observed gate output. Pass advanced to the
next card. A classified, retryable failure produced one fresh attempt with the
failure text attached. A second failure, timeout, observed directory-scope
violation, or source-manifest change stopped the lane. A later audit invalidated
Card 10 without rewriting its recorded result. No language model chose among
those control-plane edges.

This does not make inference deterministic. It makes authority deterministic.

## 3. The Strong Card

Deck development was adaptive: early workers informed later cards. Cards 7 and 9
carry prior failure evidence, and Card 9 gives the worker an explicit
DFS/memoization strategy for dependency evaluation. All ten final artifacts were
recorded with SHA-256 hashes before the principal local and hosted comparison
sweeps. A card contained:

- a single goal;
- the exact public interface;
- one writable solution file;
- readable context files;
- an initial failing stub;
- deterministic examples and, where appropriate, property tests;
- invariants and invalid-input behavior;
- forbidden shortcuts and non-goals;
- the executable acceptance command.

The card was designed so that implementation could vary while the published
gate stayed fixed. Some cards left algorithm choice open; later guided cards
constrained it deliberately. Workers were instructed not to change the question,
tests, or scope. The v1 runner enforced test immutability and some directory
scope, but not a complete filesystem allowlist.

The ten-card sequence moved from stateful containers and interval logic through
an expression parser, a deterministic graph batcher, a small spreadsheet engine,
and finally a custom glob matcher. The intended increase in difficulty was not
perfectly monotonic—two familiar tasks were repeated with denser tests—but the
later cards required more concepts to be composed in one bounded implementation.

## 4. Runtime controls

For every model/card pair, the runner:

1. verified the source-deck hashes;
2. copied the card into a fresh run directory;
3. invoked the configured execution adapter;
4. ran pytest outside the model process;
5. verified the copied test had not changed;
6. rejected unexpected visible top-level names;
7. scanned the solution for unresolved implementation stubs;
8. recorded timing, exit state, gate state, and retry disposition;
9. either advanced, retried once, or stopped.

The v1 run directory and prompt were not an OS sandbox. Dotfiles, off-tree reads
or writes, deletions, and every copied-context modification were not fully
observed. The event file was truncated at invocation start, then appended per
event. Those limitations are visible in the published historical scripts.

The harness distinction matters. Local inference used Ollama through
`claude-ollama`, a Claude Code-compatible headless surface. Hosted workers used
the OpenCode CLI with OpenCode Go routes. The isolated GPT-5.5 xhigh reference
used Codex. These tools gave models access to the card and file operations; the
outer state machine retained control.

Earlier direct local runs made capable models appear to fail because the harness
did not reliably convert intent into file writes. The improved headless tool loop
moved Gemma 4 31B and Qwen3.6 35B well beyond those apparent ceilings. That is an
important methodological result: an agent benchmark measures model, prompt,
tool schema, adapter, permissions, time budget, and gate together.

## 5. Observed results

### 5.1 Local models

Gemma 4 31B made the C1-C9 published gates green on its first recorded attempt
for each card. Card 9 took 804 seconds. It then exhausted three recorded
900-second Card 10
timeboxes across the main sweep and a dedicated follow-up; the final dedicated
attempt improved from zero to five of seven tests but did not pass.

Qwen3.6 27B passed the C1-C8 gates on first attempts. Its first Card 9 attempt
timed out at 900 seconds with nine of eleven tests passing. An informed rerun was
recorded as accepted after 2,006 seconds with all eleven tests passing. That
duration exceeds the nominal 900-second retry budget, and the preserved records
do not explain why the launcher allowed it. The published-gate pass is present
in the result artifact; timeout-policy conformance is not established.

The accepted C9 code is now public. Added probes found that Qwen cannot parse a
valid multi-letter cell, both artifacts accept booleans despite the non-goal, and
both lose precision when large integer division converts through float.
Gemma passed the added multi-letter probe. Neither artifact has full-contract
proof.

Qwen then timed out on both Card 10 attempts. Qwen3.6 35B reached Card 8 and
timed out twice on Card 9.

The local result is impressive for capability, not throughput. The models were
slower than the fastest hosted configurations, but they performed a nontrivial
composition task with no per-token API charge and without sending inference to a
hosted provider.

### 5.2 Hosted models

Eight of thirteen hosted configurations made the published gates green through
Card 9:

- GLM-5.2;
- MiMo-V2.5-Pro;
- Qwen3.7 Max;
- Qwen3.7 Plus;
- Qwen3.6 Plus;
- MiniMax M3;
- DeepSeek V4 Flash;
- DeepSeek V4 Pro.

MiMo-V2.5 reached Card 7, MiniMax M2.7 reached Card 6, Kimi K2.6 received a 1/9
comparative scope-gated score, and GLM-5.1 stopped at Card 1 under the recorded timeout
policy.

Kimi K2.7 Code is the instructive exception. Its Card 9 test suite was green on
both attempts, but the anti-stub gate rejected a legitimate abstract
`raise NotImplementedError`. Its published full-gate ceiling is therefore C8,
while the evidence also records functional test success on Card 9. A gate is part
of the system and can be wrong just as a model can.

These runs are useful placement observations, not a cross-provider ranking.
Budgets and execution surfaces differed, some Card 10 prompts were affected by a
stale-path envelope, and the principal sweep file required repair before it could
be parsed as JSONL.

### 5.3 What Card 9 established

Card 9 required the worker to implement a spreadsheet evaluator supporting:

- integer literals and arithmetic formulas;
- forward cell references;
- rectangular `SUM` ranges;
- deterministic dependency resolution;
- unknown-reference errors;
- direct and indirect cycle detection;
- input non-mutation;
- property checks over formula chains and range totals.

That is a better signal than “make a website” because success is judged by
executable behavior rather than appearance or persuasion. The post-hoc audit
also demonstrates the boundary: a public test suite can be objective and still
fail to entail every written requirement.

That the local models reached this card is evidence that their useful
operational ceiling can be much higher than casual, open-prompt demos suggest.

## 6. The Card 10 audit

The initial story appeared clean: smaller models stopped at Card 10, while the
GPT-5.5 xhigh reference passed seven of seven public tests. The Codex session took
approximately 167.6 seconds; pytest itself reported roughly one third of a
second.

Inspection invalidated the inference.

The card defines `*` as matching zero or more characters and says not to
implement filesystem path semantics. Under that contract, `a*b` must match
`a/b`. One deterministic test asserted the opposite, while a property test used
Python behavior that permits the match. The contract also says a backslash
escapes exactly one following character, but a test expects one escaped
backslash to match two text backslashes. The accepted GPT implementation added a
literal slash special case and broadened escaped-backslash matching to satisfy
the second contradiction.

Consequently:

- GPT-5.5 xhigh passed the published gate;
- the gate did not consistently represent the contract;
- the passing code is not evidence of a general solution;
- Card 10 cannot establish a frontier-only boundary;
- every Card 10 comparison is diagnostic, not rankable.

This correction strengthens the architecture thesis. Deterministic gates remove
an LLM judge from the loop, but they do not remove the need for good specification
engineering, test entailment, hidden tests, and benchmark audit.

## 7. Interpretation: where smaller models create value

The pilot does not recommend replacing frontier models. It recommends placing
them where new judgment has the highest leverage.

Frontier models are valuable when the system must discover repository contracts,
resolve ambiguity, choose architecture, construct adversarial tests, or adjudicate
an exception. Smaller models become valuable after those decisions, where the
remaining work is bounded, repeatable, and externally falsifiable.

Good worker placements include:

- mechanical migrations with conservation checks;
- target-file refactors under frozen interfaces;
- adapter and serializer implementations;
- schema, fixture, and configuration transformations;
- parser or algorithm cells with strong properties;
- repetitive remediation cards generated from an audit;
- parallel implementation variants evaluated by the same gate.

Poor placements include unresolved product requirements, cross-cutting design,
tasks without an external oracle, high-impact changes with unobservable failure,
and any situation where “try something plausible” can silently redefine success.

The economic argument is not “small is always cheaper.” It is that frontier
reasoning can be amortized. Spend it once to reduce the decision surface, then
route repeatable execution to the least expensive worker that reliably clears the
gate.

## 8. What this first pilot does not establish

The study has no repeated trials, randomized model order, common adapter across
lanes, total-cost accounting, hidden test suite, or open raw prompt corpus. Card
difficulty was not psychometrically calibrated. The deck was developed
adaptively; later prompts contained prior failure evidence and explicit
algorithmic guidance. V1 isolation and scope observation were incomplete, and
its ledgers were invocation-scoped. The local Qwen timeout anomaly is unresolved.
Card 9 has known public-test coverage gaps, and Card 10 is invalid for comparison.
Raw hosted output also contains format and stale-path defects documented in the
evidence package.

Therefore, C9 is not a universal ability score or complete semantic proof. It is
the highest contiguous published-gate point observed in this specific pilot.

## 9. Next experiment

The next run will:

1. repair Card 10 from the contract outward;
2. add hidden, adversarial, and metamorphic tests;
3. freeze path-independent prompt envelopes and all environment versions;
4. use one adapter policy and one time-budget policy across models;
5. repeat every model/card condition;
6. separate semantic failure, scope failure, tool failure, and timeout;
7. record launch, process, and gate clocks independently;
8. report total cost per accepted card, including frontier preparation and human
   intervention.
9. enforce a complete filesystem allowlist and preserve a durable append-only
   event ledger.

That will test causality and reliability. This pilot established that the
architecture is worth testing.

## Conclusion

The strongest result is not a winning model. It is a division of cognitive
labor:

- frontier intelligence converts ambiguity into a frozen contract;
- deterministic software controls progression and authority;
- smaller models execute bounded transformations;
- humans or frontier systems return only when the contract itself breaks.

The local Qwen and Gemma results show that this worker tier can be far more
capable than superficial demos imply. The Card 9 and Card 10 audits show why
capability must be measured by audited systems, not green checkmarks alone.
