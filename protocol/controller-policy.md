# Deterministic controller policy

> Protocol v2 target. This is the hardened controller contract derived from the
> pilot, not a claim that the historical v1 runner already enforced every item
> below. See the [v1 runner archive](../runner/README.md) for the exact controls
> and their limits.

The controller is ordinary shell or Python code. It does not reason about the
task, choose the next action through an LLM, or delegate to an agent coordinator.
Its authority is limited to reading frozen configuration, launching an adapter,
running gates, applying a fixed transition table, and appending evidence.

This is the central separation in the experiment:

- model inference is nondeterministic;
- execution control is deterministic;
- acceptance is based on external observations;
- architectural revision occurs outside the runtime loop.

## Inputs

The controller accepts only versioned inputs:

- a hash-bound card manifest;
- a stable card order and dependency list;
- a static model-to-adapter route table;
- isolated starting artifacts;
- ordered gate commands;
- attempt and timeout limits;
- a durable append-only result destination.

There is no prompt such as “decide what to do next.” The next eligible card is
the first pending card in manifest order whose dependencies are accepted.

## Card state machine

```text
PENDING
  |
  | dependencies accepted and hashes valid
  v
ELIGIBLE -> DISPATCHED -> GATING -> ACCEPTED
                           |
                           +-> RETRY_PENDING -> DISPATCHED
                           |
                           +-> FAILED
                           |
                           +-> INVALID_CARD
                           |
                           +-> ENVIRONMENT_ERROR

PENDING -> SKIPPED_DEPENDENCY when an upstream card is not accepted
```

Every edge is selected from recorded predicates. No transition depends on a
model's explanation, confidence, or completion claim.

## Ordered gates

After an adapter returns or times out, the controller evaluates gates in a fixed
order:

1. **Input integrity**: frozen artifacts still match their manifest hashes.
2. **Process status**: the adapter produced a classifiable exit or timeout.
3. **Change scope**: every changed, created, and deleted path is allowed.
4. **Anti-stub**: prohibited placeholders, disabled tests, and known benchmark
   exploits are absent.
5. **Functional acceptance**: the controller executes the card's exact tests.
6. **Optional static gates**: only commands already named in the manifest.

The result is accepted only if all mandatory gates pass. A green functional test
cannot override a scope failure or invalid frozen input.

## Fixed transition table

| Observed result | Attempts used | Next state |
|---|---:|---|
| All mandatory gates pass | any | `ACCEPTED` |
| Implementation, timeout, or scope gate fails | 1 | `RETRY_PENDING` |
| Same classes of failure persist | 2 | `FAILED` |
| Versioned preflight or post-run audit marks the card contradictory | any | `INVALID_CARD` |
| Mandatory gate cannot run for environmental reasons | any | `ENVIRONMENT_ERROR` |
| Upstream card is not accepted | n/a | `SKIPPED_DEPENDENCY` |

The failure class is derived from process and gate outputs. Card invalidation is
supplied by an explicit audit result outside the worker loop; the controller does
not pretend that shell code can infer every semantic contradiction. A model does
not classify its own failure.

## One informed retry

The single retry is not a second planning cycle. The controller preserves the
same objective, scope, tests, and starting contract, then adds a bounded failure
packet generated from attempt 1. The retry packet may contain:

- the failing gate name;
- exit code or timeout;
- a fixed-size output excerpt;
- the list of changed paths;
- the instruction to repair only the frozen card.

If the timeout or any other budget changes, that change must be explicit in the
route policy or recorded as a new protocol version. It cannot be hidden inside a
successful aggregate score. In the pilot, Qwen3.6 27B's Card 9 result is labelled
retry-assisted because acceptance followed a timed-out attempt and an extended,
recorded follow-up.

## Stop and escalation

`FAILED`, `INVALID_CARD`, and `ENVIRONMENT_ERROR` are terminal states for the
current run. An invalidation discovered after execution supersedes the card's
comparative interpretation without deleting its recorded gate result. The
controller may skip dependent cards, end the route, or continue only where the
frozen dependency graph permits it.

Escalation is an output artifact, not an LLM call inside the loop. A human or a
frontier model may later inspect the evidence and author a new card version. That
new version receives new hashes and starts a new run. The old record remains
unchanged.

## Append-only evidence

Write one machine-readable record per attempt before the next transition. A
minimal record contains:

```json
{
  "run_id": "stable run identifier",
  "deck_version": "version identifier",
  "card_id": "C01",
  "card_hash": "sha256",
  "route": "model and adapter identifier",
  "attempt": 1,
  "started_at": "UTC timestamp",
  "duration_ms": 0,
  "process_status": "exit | timeout | launch_error",
  "changed_paths": [],
  "gates": [],
  "state": "ACCEPTED | RETRY_PENDING | FAILED | INVALID_CARD",
  "stdout_digest": "sha256",
  "stderr_digest": "sha256"
}
```

Provider telemetry may be added, but it must not replace controller observations.
Do not rewrite a failed attempt after a later retry succeeds.

## Adapter boundary

An adapter translates the controller's fixed request into the CLI or API shape a
model surface expects. It may launch OpenCode, a Claude Code-compatible local
surface, Codex, or another worker interface. It may normalize exit status and
capture output.

An adapter may not:

- select a card;
- alter the prompt contract;
- decide whether a failure deserves another attempt;
- waive a gate;
- edit tests or manifests;
- summarize evidence into a pass;
- call another model to coordinate the worker.

Changing execution surfaces therefore does not change who controls the run. The
adapter is a replaceable transport edge, not an orchestrator.

## Meaning of deterministic

This protocol does not promise identical model output, identical latency, or an
identical diff across runs. It promises that, for the same manifest and observed
gate results, ordinary code chooses the same allowed transition. The auditable
object is the control path, not the token stream.
