# Evidence package

This directory contains the public evidence for a first deterministic
Strong-Card benchmark. The comparative result is deliberately limited to Cards
1-9. Card 10 is retained only as an audit finding because its contract, fixed
tests, and property oracle contain two contradictions.

| File | Purpose |
|---|---|
| `study.json` | Canonical experiment definition, architecture, hardware, and claim boundaries |
| `card-catalog.csv` | Frozen card catalog, red-gate counts, and SHA-256 identifiers |
| `model-summary.csv` | One conservative comparison row per model configuration |
| `card-matrix.csv` | Complete C1-C9 outcome matrix for every configuration, plus excluded C10 diagnostics |
| `local-attempts.csv` | Every recorded local-run event, including retries, timeouts, and one skip event |
| `hosted-results.csv` | Per-card outcomes from the OpenCode CLI using OpenCode Go model routes |
| `runner-artifacts.csv` | Source and public SHA-256 identifiers for the historical v1 runners |
| `accepted-artifacts/metadata.json` | Hashes, gate output, and post-hoc probe outcomes for the accepted local Card 9 artifacts |
| `reference-artifacts/metadata.json` | Hashes and forensic findings for the excluded GPT-5.5 xhigh Card 10 reference |
| `card9-posthoc-audit.md` | Targeted contract probes applied after both local Card 9 public-gate passes |
| `card10-audit.json` | Machine-readable statement of the Card 10 benchmark defect |
| `card10-audit.md` | Human-readable Card 10 forensic note |
| `provenance.md` | Source hierarchy, transformations, exclusions, and limitations |

## How to read the result

- `published_gate_cards_passed` and `published_gate_ceiling` use the nine
  comparative cards, C1-C9. They do not mean that every clause of each written
  contract has been independently proven.
- A card counts only when the historical runner accepted every configured v1
  gate: process outcome, published tests, anti-stub check, copied-test
  immutability, and its visible top-level scope check.
- A retry is visible rather than collapsed. Its wall time remains part of the
  worker-invocation time to reach the accepted ceiling.
- Worker wall time measures the coding-model CLI invocation only. It excludes
  warm-up or smoke work, pytest and other gates, and controller overhead.
- Harness and inference are separate fields. A Claude Code-compatible local
  harness does not imply that Claude performed the inference.
- Hosted inference used the OpenCode CLI; identifiers beginning with
  `opencode-go/` are OpenCode Go model routes, not a separate controller.
- Card 10 outcomes must not be used to rank capability. GPT-5.5 xhigh passed the
  published seven-test gate, but its solution hardcoded one contradictory case
  and broadened behavior to satisfy another. That is a gate pass, not a clean
  semantic result. The exact [reference implementation](reference-artifacts/gpt55-xhigh-c10/glob_matcher.py)
  and its sanitized gate output are published for inspection.

## What was deterministic

GPT-5.5 at medium reasoning effort authored the ten Strong Cards through Codex.
Deck construction was adaptive: Cards 7-9 were developed after earlier worker
runs, Cards 7 and 9 carry prior failure evidence, and Card 9 prescribes an
implementation strategy. All ten final artifacts were then hash-frozen before
the principal hosted and local comparison sweeps.

During those sweeps, no LLM made control-plane decisions. Shell and Python fixed
card order, route selection, retry eligibility, acceptance, and stopping. A
worker model still chose code and tool actions inside its assigned card; the
claim is zero runtime LLM control-plane decisions, not zero model agency.

The historical v1 controls were narrower than a hermetic sandbox. They used a
fresh working directory plus prompt constraints, and their scope checks did not
observe every dotfile, nested change, deletion, off-tree read, or off-tree write.
Result files were truncated when a sweep invocation started and then appended
per event, so they are invocation-scoped ledgers rather than durable append-only
logs across reruns.

The headline observation is narrow but useful: with planning moved before
execution and runtime control reduced to a deterministic state machine, a local
Qwen3.6 27B configuration and a local Gemma 4 31B configuration each made the
published gates green through Card 9. The accepted files are published. Post-hoc
probes found that Qwen did not support valid multi-letter cells and that both
local artifacts accepted booleans and lost precision on large integer division;
neither result is full-contract proof. This is a first test, not evidence that
small models can solve arbitrary software projects or that the result
generalizes beyond this card deck.
