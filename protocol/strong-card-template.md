# Strong Card contract

> Reusable protocol target derived from the pilot. The published v1 cards are
> historical artifacts and do not all satisfy every authoring rule below; Card
> 10 is the documented counterexample.

A Strong Card is a frozen unit of execution authority. It tells a worker exactly
what may change, what must remain true, how success will be measured, and when it
must stop. It is authored before the run and referenced by hash from the run
manifest. The runtime controller does not ask another model to reinterpret it.

The card is intentionally narrower than a conventional implementation ticket.
Architecture and product choices have already been made. The worker owns a
bounded transformation, not the surrounding decisions.

## Canonical template

```markdown
# CARD <id>: <title>

## Identity

- Card ID: `<stable identifier>`
- Card version: `<integer>`
- Depends on: `<card IDs or none>`
- Manifest hash: `<computed during freeze>`

## Objective

One externally observable outcome, stated without prescribing unrelated work.

## Starting contract

- Starting artifact: `<path to the worker-editable stub or fixture>`
- Required interface: `<exact callable, command, or data shape>`
- Preconditions: `<facts already verified by the deck author>`

## Allowed change surface

### May modify

- `<path>`

### May create

- `<path or none>`

### May delete

- `<path or none>`

Every unlisted path is read-only.

## Behavioral contract

1. `<required behavior>`
2. `<invariant>`
3. `<edge case>`

## Acceptance gates

Run in this order:

1. Scope: `<command or controller check>`
2. Anti-stub: `<command or controller check>`
3. Functional: `<exact test command>`
4. Optional static check: `<exact command or none>`

Acceptance requires every mandatory gate to exit successfully. Worker prose and
completion messages are not acceptance evidence.

## Non-goals

- Do not edit tests, fixtures, or the manifest.
- Do not refactor neighboring code.
- Do not add dependencies unless explicitly allowed above.
- Do not weaken, skip, replace, or special-case an acceptance assertion.
- Do not publish, push, rewrite history, or perform destructive cleanup.

## Execution budget

- Maximum attempts: `2`
- Attempt 1 timebox: `<seconds>`
- Informed retry timebox: `<seconds>`
- Maximum changed lines or bytes: `<limit or none>`

## Retry input

On a retry, append only the controller-produced failure packet:

- attempted card ID and hash;
- failed gate name;
- process exit status or timeout status;
- bounded stdout and stderr excerpts;
- changed-path report;
- instruction to repair the same contract without widening scope.

## Stop conditions

Stop the card when any of the following is true:

- every gate passes;
- the second attempt fails;
- a frozen input fails its hash check;
- the specification and acceptance suite contradict each other;
- the required change exceeds the allowed surface;
- the environment cannot execute a mandatory gate.
```

## What is frozen

The pilot manifest bound these artifacts by SHA-256 digest:

- the card text;
- the worker prompt envelope;
- the starting stub or fixture;
- the public acceptance tests.

A hardened follow-up should also bind:

- the ordered gate commands;
- the attempt and timeout policy;
- the model route and adapter configuration used for that run.

A changed artifact or policy produces a new deck or run version. It must not be
silently substituted into an existing result.

## Card-authoring rules

1. One card should have one semantic objective.
2. Every requirement must map to an external gate or a named invariant.
3. The editable surface should be smaller than the readable context.
4. Tests and oracles must agree with the written contract.
5. The initial stub must fail at least one mandatory functional gate before the
   deck is frozen.
6. A legal refusal or escalation must be representable without editing code.
7. A retry may repair an implementation; it may not repair the benchmark.
8. Any architectural choice left to the worker is evidence that the card is not
   ready to freeze.

## Why the completion message is omitted

Models can state that a task is complete while tests fail, scope has widened, or
the intended behavior has not been implemented. The controller therefore records
only observable process and gate results. Natural-language output remains useful
diagnostic material, but it has no authority in the state machine.

## The Card 10 lesson

The pilot's tenth card violated the authoring rules: the prose denied path
semantics, one example treated `/` specially, and a property oracle implied the
opposite result. A frontier reference run made the published tests green with a
case-specific branch. That is a gate pass, not a valid capability result.

The correct protocol response is `INVALID_CARD`: preserve the record, exclude
the card from comparative conclusions, repair and re-audit the contract, assign
a new hash, and rerun it as a new benchmark version.
