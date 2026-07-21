# Minimal no-orchestrator loop

> Reference design for protocol v2. It intentionally closes gaps found in the
> historical v1 scripts; it is not a byte-for-byte description of their scope
> checks, isolation, or invocation-scoped result files.

The runtime needs four components:

1. a frozen manifest;
2. a deterministic controller;
3. thin execution adapters;
4. external gates plus an append-only ledger.

It does not need an LLM router, planner, supervisor, critic, or coordinator.

## Control flow

```text
frontier authoring, before the run
    |
    v
frozen manifest and Strong Cards
    |
    v
deterministic controller
    |
    +--> adapter --> probabilistic worker --> candidate diff
    |                                      |
    +<------------- process result --------+
    |
    v
ordered external gates
    |
    +--> pass --------------------------> accept and advance
    +--> first contract-preserving fail -> one informed retry
    +--> second fail -------------------> stop and record
    +--> contradictory benchmark ------> invalidate and record
```

The frontier model leaves the control path before the manifest is frozen. It may
return only after a run terminates, to help design a new protocol version.

## Reference pseudocode

```python
manifest = load_manifest("manifest.json")
verify_all_hashes(manifest)
routes = load_static_routes(manifest)

for card in stable_manifest_order(manifest):
    if not dependencies_accepted(card):
        append_state(card, "SKIPPED_DEPENDENCY")
        continue

    if card.audit_status != "VALID":
        append_state(card, "INVALID_CARD")
        continue

    accepted = False

    for attempt in (1, 2):
        workspace = materialize_isolated_start(card)
        prompt = frozen_prompt(card)

        if attempt == 2:
            prompt += deterministic_failure_packet(previous_attempt)

        route = routes[card.route_id]
        process = route.adapter.invoke(
            model=route.model,
            prompt=prompt,
            cwd=workspace,
            timeout=route.timeout_for(attempt),
        )

        gates = run_ordered_gates(card, workspace, process)
        state = transition(process, gates, attempt)
        append_attempt(card, route, attempt, process, gates, state)

        if state == "ACCEPTED":
            seal_accepted_artifact(card, workspace)
            accepted = True
            break

        if state != "RETRY_PENDING":
            break

    if not accepted and manifest.stop_route_on_failure:
        mark_remaining_according_to_dependencies()
        break
```

`transition()` is a table lookup over gate booleans, attempt number, and explicit
error classes. It does not contain a model call. `audit_status` is a versioned
input produced before the run, or a post-run correction that invalidates the
comparison without rewriting the original attempt record.

## Minimal adapter interface

```python
class Adapter:
    def invoke(self, *, model, prompt, cwd, timeout) -> ProcessResult:
        """Launch one worker and return observable process data."""
```

`ProcessResult` should contain process status, elapsed time, captured output
digests, and any provider-supplied identifiers. The controller, not the adapter,
runs repository gates and assigns the card state.

## Reproducibility requirements

- Materialize the same frozen starting artifact for every model route.
- Verify hashes before each attempt, not only when the deck is created.
- Keep card order, retry count, gate order, and stop policy in the manifest.
- Record timeouts as outcomes; do not convert them into silent reruns.
- Keep failed attempts after a retry passes.
- Version any test, timeout, prompt, or route-policy change.
- Re-run a repaired invalid card under a new deck identifier.

The loop is deliberately small. Most of the intelligence lives in authoring a
good card and a trustworthy acceptance boundary before execution begins.
