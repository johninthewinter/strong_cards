# Placement guide: where smaller and local models add value

The useful question is not whether a small model can replace a frontier model.
It is which stage of a software pipeline actually requires frontier reasoning.

This experiment separates three kinds of authority:

1. **Design authority** reduces ambiguity and belongs to a frontier model or a
   human before execution.
2. **Execution authority** selects states, retries, and acceptance and belongs to
   deterministic code.
3. **Transformation work** produces a candidate change and can often be assigned
   to a smaller, cheaper, or local model.

This is model placement, not model worship. A smaller worker becomes valuable
when the system has already decided what the work means and can independently
detect whether it succeeded.

## Placement map

| Pipeline stage | Best default owner | Why |
|---|---|---|
| Goal clarification and architectural trade-offs | Human plus frontier model | Requirements still have multiple valid interpretations |
| Interface and invariant discovery | Frontier model, grounded in source evidence | Hidden contracts must be surfaced before delegation |
| Strong Card and test design | Frontier model with independent audit | Bad decomposition creates false confidence at every later stage |
| Card ordering, route lookup, timeout, retry, and stop | Shell or Python controller | These are policy decisions, not language tasks |
| Bounded implementation against a frozen interface | Small, local, or economical hosted model | Remaining work is a constrained transformation |
| Scope, anti-stub, unit, property, and regression gates | Deterministic tools | The worker must not certify itself |
| Contradiction or invalid benchmark | Stop, then human or frontier redesign | More execution cannot repair a broken contract |
| Security, irreversible change, or production release | Human authority with independent checks | Passing code tests is insufficient authorization |

## Delegation test

A card is a good candidate for smaller-model execution when all of these are true:

1. **Singular objective**: two competent reviewers would interpret the outcome
   the same way.
2. **Verified interface**: inputs, outputs, dependencies, and relevant invariants
   are known.
3. **Bounded authority**: editable paths and prohibited actions are explicit.
4. **External observability**: success can be measured without trusting the
   model's explanation.
5. **Safe failure**: timeout, refusal, or wrong code can be contained and reset.
6. **Cheap escalation**: a failed card can stop without forcing the worker to
   invent architecture.
7. **Useful repetition**: the transformation occurs often enough that routing
   economics or local control matter.

If the first six are false, the task is not ready for autonomous delegation. A
larger context window or a more confident worker does not repair the missing
contract.

## Why the local result matters

In the pilot, both local workers, Qwen3.6 27B and Gemma 4 31B, made the published
gates green through Card 9. Qwen's ninth card required an extended recorded retry;
Gemma passed it on the first recorded attempt. Several hosted routes reached the
same public-gate ceiling. The later C9 audit found contract gaps in both local
artifacts, so this is operational evidence rather than clean semantic completion.
It remains notable because the workers did not plan the sweep, coordinate agents,
or decide their own acceptance.

Card 10 does not establish a frontier boundary. Its contract and oracle conflict,
and the frontier reference satisfied the published tests with a case-specific
branch. The defensible conclusion is therefore not “small models stop at nine.”
It is “small and local models were credible guided executors through a demanding
C9 published gate in this pilot.”

## Operational value of small and local workers

The experiment directly demonstrates feasibility, not a complete cost or energy
model. In a production pipeline, this placement can create value through:

- **Capacity**: reserve frontier calls for architecture, exceptions, and contract
  repair instead of every mechanical edit.
- **Cost control**: route high-volume bounded transformations to lower-cost
  inference while measuring cost per accepted result.
- **Data locality**: keep eligible source transformations on controlled hardware
  when policy or confidentiality makes hosted inference undesirable.
- **Provider independence**: treat model surfaces as replaceable adapters behind
  one evidence contract.
- **Parallel verification**: spend saved inference budget on retries, independent
  review, mutation tests, or a second worker rather than a single unverified pass.
- **Better system design**: forcing external acceptance exposes missing tests,
  unstable interfaces, and undocumented decisions that were previously hidden in
  human judgment.

These benefits are conditional. Local inference is not automatically faster or
cheaper after hardware, engineering, queueing, and energy are included. Measure
the complete accepted-output cost in the intended deployment.

## Workloads that fit

Strong candidates include:

- implementing a known interface from a frozen stub;
- repetitive schema, API, or configuration migrations with invariant checks;
- test repair where expected behavior is independently specified;
- adapters and serializers with exact input-output contracts;
- bounded bug fixes with a reproducer and regression test;
- mechanical refactors protected by compile, type, and behavior gates;
- read-only diagnosis with a required evidence schema;
- generating candidate implementations for independent comparison.

Poor candidates include:

- open-ended “understand the repository and improve it” requests;
- architecture selection with unresolved product trade-offs;
- cross-cutting refactors whose behavior is poorly observed;
- tasks where the worker must modify the tests that judge it;
- destructive migrations without dry-run and recovery controls;
- acceptance based primarily on aesthetic or rhetorical judgment;
- incident response where changing state precedes understanding the failure.

## Routing policy without a router model

A static table is sufficient for the first useful system:

```text
card_class -> model_route -> adapter -> attempt_1_timeout -> retry_timeout
```

The operator can benchmark routes offline and update that table between protocol
versions. At runtime, ordinary code reads it. This avoids paying an LLM to make a
decision that should be stable, inspectable, and testable.

An adaptive router may become justified at scale, but it should still optimize
within explicit policy boundaries and should not inherit acceptance authority.
The minimal architecture should be the baseline against which added coordination
complexity must prove its value.

## Metrics that matter

Do not optimize for card completion claims. Measure:

- full-gate acceptance rate by attempt;
- time and cost per accepted card;
- retry-assisted versus first-pass acceptance;
- timeout and no-edit rates;
- scope violations and anti-stub failures;
- invalid-card rate in the frontier-authored deck;
- escalation rate and time to repair the contract;
- regression escapes discovered after acceptance;
- total frontier, human, hosted, and local operating cost.

An honest system counts a correct stop as useful behavior and a green but
contradictory benchmark as invalid evidence.

## Deployment rule

Use the smallest model that clears the externally verified contract at the
required reliability and total cost. Keep deterministic code in charge of the
run, keep frontier reasoning focused on ambiguity, and promote a task downward
only after failure is observable and safe.
