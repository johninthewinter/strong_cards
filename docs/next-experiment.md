# Next experiment: protocol v2

The first pilot established that the architecture is worth studying. Protocol v2
is designed to test reliability, causality, and economics rather than produce a
larger anecdotal model table.

## Primary questions

1. Does Strong Card decomposition improve accepted-output rate for the same
   worker relative to a monolithic assignment?
2. Does a deterministic controller match or outperform an LLM coordinator when
   the cards and gates are identical?
3. Which local and hosted routes minimize total cost and elapsed time per
   accepted card at a required reliability level?
4. At what contract complexity should the system escalate instead of retrying a
   smaller worker?

## Repair before rerun

Card 10 will not be patched in place. It will receive a new identifier and hash
after these changes:

- choose and state slash semantics consistently;
- remove the contradictory deterministic assertion;
- replace the inconsistent property oracle;
- add hidden tests for escape behavior, ranges, negation, Unicode, and
  adversarial backtracking cases;
- mutation-test the suite against plausible shortcuts and the published GPT
  hard-code;
- have an independent reviewer check that every test is entailed by the prose.

Cards with informed-retry text in their base prompt will also be rebuilt so the
base and retry envelopes are separate, versioned objects.

## Experimental conditions

Use a crossover design in which each model receives the same underlying task
under three conditions:

| Condition | Planning input | Runtime control | Purpose |
|---|---|---|---|
| A: monolithic | One complete task description | Fixed timeout and final gates | Baseline for open-ended execution |
| B: Strong Cards | Frozen decomposed cards | Deterministic controller | Test the proposed architecture |
| C: coordinated | The same frozen cards | LLM coordinator under a fixed policy | Measure whether runtime reasoning adds value |

Condition C is a counterfactual, not a requirement for the production design.
It exists to test whether removing the coordinator loses measurable capability.

Run every eligible model/condition pair at least five times. Randomize model and
condition order while keeping dependency order inside a deck. Start each run from
an identical content-addressed environment.

## Frozen environment

The versioned manifest must bind:

- repository or fixture digest;
- card, base prompt, retry prompt, stub, public tests, and hidden-test digest;
- ordered gate commands and gate implementation version;
- runner commit and adapter version;
- exact model route, quantization, context window, and decoding parameters;
- container or environment lock;
- first-attempt and retry timeouts;
- dependency graph and stop policy;
- hardware class and concurrency setting.

Any change creates a new protocol version. Results from incompatible versions
must not be merged into one score.

## Containment and evidence hardening

Run each attempt inside an OS-enforced sandbox or disposable container with an
explicit read and write allowlist. Capture a complete before/after inventory,
including dotfiles, nested paths, creations, modifications, and deletions. Deny
off-tree writes at the boundary instead of trying to infer them later, and log
permitted reads when source confidentiality is part of the claim.

Write events to a durable, append-only run ledger keyed by experiment, route,
replication, card, and attempt. A new sweep may append a new run; it may never
truncate or reuse a prior result destination. Seal stdout, stderr, diffs, gate
outputs, and accepted artifacts by digest before the next controller transition.

The Card 9 suite must add the clauses missed by the public v1 oracle: valid
multi-letter columns, explicit boolean rejection, and exact large-integer
division. Apply the same post-hoc corpus to every local and hosted accepted
artifact, then keep it as a hidden holdout for the next independently authored
deck.

## Telemetry contract

Record separate clocks for adapter launch, model generation, tool execution,
functional tests, and all-gate completion. Every attempt should include:

```json
{
  "experiment_id": "v2",
  "replication": 1,
  "condition": "strong_cards_deterministic",
  "card_id": "C09-v2",
  "attempt": 1,
  "model_route": "provider/model@revision",
  "adapter_version": "commit-or-version",
  "runner_commit": "full-git-sha",
  "input_digest": "sha256",
  "prompt_digest": "sha256",
  "timeout_seconds": 900,
  "process_status": "exit|timeout|launch_error",
  "semantic_tests_passed": false,
  "scope_gate_passed": false,
  "anti_stub_gate_passed": false,
  "hidden_tests_passed": false,
  "controller_state": "ACCEPTED|RETRY_PENDING|FAILED|INVALID_CARD",
  "wall_seconds": 0,
  "energy_wh": null,
  "provider_cost_usd": null,
  "human_intervention_seconds": 0
}
```

Preserve stdout, stderr, changed-path inventory, diff, gate output, and controller
transition as content-addressed attachments. Never replace a failed attempt with
the eventual successful retry.

## Primary metrics

- full-deck completion rate;
- first-attempt and retry-assisted acceptance rate;
- semantic-test and full-gate acceptance rate;
- hidden-test survival rate;
- timeout, no-edit, scope-violation, and false-positive gate rate;
- invalid-card rate from the frontier authoring phase;
- frontier and human intervention per accepted card;
- total elapsed time and total cost per accepted card;
- local energy per accepted card where measurement is available;
- regression escapes found after acceptance.

## Decision rules

A smaller-model route is operationally viable for a card class only when it:

1. clears the full gate in at least four of five replications;
2. produces no uncontained scope violation;
3. survives the hidden suite;
4. has a lower total accepted-output cost than the frontier baseline;
5. remains within the workflow's latency objective;
6. escalates contract defects instead of silently redefining them.

The deterministic design earns promotion only if Condition B is non-inferior to
Condition C on accepted-output reliability while reducing frontier runtime cost
or control variance.

## Expected outcome

The next study should produce routing thresholds, not a winner. The useful output
is a versioned table mapping task class and contract complexity to the least
expensive route that meets a reliability target, plus an explicit frontier
escalation boundary.
