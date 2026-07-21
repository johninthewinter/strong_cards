# The Strong Card concept

## Definition

A **Strong Card** is a versioned, hash-bound execution contract that converts a
piece of already-decided system design into a bounded transformation a worker can
perform and an external controller can accept without interpreting the worker's
prose.

It is the intermediate representation between reasoning and execution:

```text
problem facts -> architectural judgment -> Strong Card -> worker attempt -> external gates -> evidence
```

A prompt asks a model to do something. A ticket records intended work. A test
checks selected behavior. A Strong Card binds all three to an authority boundary:
what the worker may change, what it must produce, what it must not decide, how
failure is handled, and which observations cause the controller to advance.

The word **strong** does not describe length or tone. It describes closure. A card
is strong only when success is externally observable, failure is safe, and the
worker does not need to invent missing architecture to proceed.

## Formal object

For protocol purposes, represent a card as:

```text
SC = (I, O, S, B, G, R, E)
```

where:

- `I` is immutable identity: card ID, version, dependencies, and frozen hashes;
- `O` is one externally observable objective;
- `S` is the change surface: readable, writable, creatable, and deletable paths;
- `B` is the behavioral contract: interface, invariants, edge cases, and non-goals;
- `G` is an ordered set of independently executable gates;
- `R` is the runtime policy: budget, retry packet, stop states, and escalation;
- `E` is the evidence schema emitted for every attempt and terminal decision.

Given a frozen card, route, policy version, and observed gate vector, the next
controller state must be a pure policy decision:

```text
transition(manifest, attempt, observations) -> ACCEPT | RETRY | STOP | INVALID_CARD
```

The candidate implementation may vary because inference is probabilistic. The
authority path does not: the model cannot select the next card, grant itself a
retry, waive a failed gate, redefine success, or decide that the run is complete.

## Required properties

### 1. Identity is immutable

The card, prompt envelope, starting artifacts, tests, ordered gates, budgets,
route, and adapter configuration are versioned and digest-bound. A material
change creates a new card or run version; it never silently changes an existing
result.

### 2. The objective is singular

One card produces one bounded semantic outcome. If independent architectural
choices or unrelated writable surfaces remain, the unit must be decomposed or
returned for design.

### 3. Authority is explicit

The card defines exact read, write, create, and delete permissions. Everything
not granted is forbidden. The worker owns implementation choices inside that
cell, not requirements, orchestration, acceptance, publication, or exception
policy.

### 4. The contract is executable

Every acceptance-relevant clause maps to a gate, oracle, invariant review, or
explicitly declared untested assumption. Worker self-report is diagnostic output,
never acceptance evidence.

### 5. Failure is a designed state

Timeout, environment failure, frozen-input drift, scope violation, exhausted
attempts, and contract-oracle contradiction have distinct terminal records. A
worker is allowed to fail; it is not allowed to widen the task to escape failure.

### 6. Evidence is attempt-scoped

Every invocation records input identity, model route, adapter, timing, process
status, changed paths, gate observations, retry lineage, and final controller
state. Failures and retries remain visible rather than being collapsed into a
single final score.

## Division of labor

| Layer | Owns | Must not own |
|---|---|---|
| Human or frontier design phase | ambiguity reduction, architecture, decomposition, oracle design, exception policy | runtime self-approval |
| Strong Card | frozen execution contract and authority boundary | adaptive judgment |
| Deterministic controller | ordering, dispatch, budgets, gates, retry, stopping, evidence | implementation semantics beyond declared gates |
| Worker model | bounded code and tool choices inside the card | routing, acceptance, policy changes, task expansion |
| Human or frontier escalation | invalid contracts, unresolved architecture, consequential exceptions | rewriting a measured run in place |

This is why a smaller model can be valuable without being treated as a smaller
architect. The system spends expensive judgment before the loop, then uses a
replaceable worker where the remaining decision surface is narrow and externally
testable.

## Authoring and execution lifecycle

1. **Discover:** establish repository facts, dependencies, constraints, and the
   intended outcome.
2. **Decide:** resolve product and architecture choices outside the worker loop.
3. **Compile:** author the card, starting artifact, interface, invariants, tests,
   scope, budgets, and evidence schema.
4. **Audit:** check that prose, examples, tests, properties, and stop rules entail
   the same contract.
5. **Verify red:** prove that the frozen starting state fails at least one
   mandatory functional gate for the intended reason.
6. **Freeze:** version and hash all execution-relevant inputs and policy.
7. **Dispatch:** give one materialized card to one configured worker route.
8. **Gate:** evaluate the candidate outside the worker in the declared order.
9. **Transition:** accept, issue one mechanical failure packet, stop, or mark the
   card invalid according to fixed predicates.
10. **Seal:** append the complete attempt record and bind accepted artifacts to
    their hashes.

## Readiness test

A card is ready to freeze only if all of these questions have objective answers:

1. What single observable fact becomes true?
2. Which exact artifacts may change?
3. Which decisions have already been made for the worker?
4. Which behaviors and invariants are mandatory?
5. Which executable observation covers each mandatory clause?
6. What proves the initial state is meaningfully red?
7. What evidence distinguishes semantic failure, harness failure, timeout, and
   scope violation?
8. What exact observation permits retry, acceptance, stop, or invalidation?
9. Can a failed worker leave the system in a safe, inspectable state?
10. Can another controller replay the decision without reading model prose?

If any answer requires open-ended interpretation at runtime, the card is not yet
strong. It returns to design rather than delegating architecture to the worker.

## What a Strong Card is not

- It is not a large prompt padded with explanations.
- It is not a chain-of-thought request or a way to imitate frontier reasoning.
- It is not an autonomous-agent plan with a model acting as router and judge.
- It is not a public-test score presented as complete semantic correctness.
- It is not a substitute for sandboxing, provenance, hidden tests, mutation
  testing, or human approval where consequences require them.
- It is not evidence that every real project can be decomposed this way.

## Lessons from the pilot

Card 9 demonstrated why a green public suite and a written contract are different
claims. Both accepted local artifacts cleared the published gate; post-hoc probes
found uncovered boolean and large-integer behavior, and the Qwen artifact also
failed valid multi-letter cells. A hardened card must map every important clause
to an oracle or declare the gap.

Card 10 demonstrated a more fundamental failure: the prose, fixed example, and
property oracle contradicted one another. GPT-5.5 xhigh made the seven published
tests green with case-specific behavior, but there was no coherent contract to
solve. A correct controller state is therefore `INVALID_CARD`, not worker failure
or frontier victory.

The historical v1 cards and runners are research artifacts; they do not all meet
this full definition. The [canonical template](../protocol/strong-card-template.md),
[controller policy](../protocol/controller-policy.md), and
[minimal loop](../protocol/minimal-loop.md) define the hardened target for the
next experiment.
