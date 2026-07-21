# Proof index

## Purpose

This index separates what the pilot **shows**, what can be **replayed**, what is
**derived**, and what remains **qualified**. It is the shortest path from a public
claim to the artifact that supports or limits it.

The repository is a first-test research record, not a claim that every historical
event can be reconstructed from public raw transcripts. The exact evidentiary
boundary is part of the result.

## Evidence classes

| Class | Meaning | Permitted claim strength |
|---|---|---|
| A: executable primary evidence | Public code, frozen inputs, hashes, gate output, or a check that can be rerun | Directly inspectable or replayable within the documented environment |
| B: normalized record | Hash-bound CSV, JSON, or sanitized historical runner derived from retained source material | Supports aggregate and process claims when transformation and limits are disclosed |
| C: retained source record | Private sanitized session, operator artifact, machine record, or supplied source retained locally and represented publicly by original digest or provenance note | Supports attribution and audit continuity, but not public transcript-level replay |
| D: interpretation | Analysis that follows from A-C plus stated assumptions | Hypothesis, design inference, or placement recommendation rather than direct measurement |

No claim is upgraded by persuasive wording. Where a Class A artifact contradicts
a headline interpretation, the artifact controls.

## Claim-to-proof map

| Claim | Class | Canonical proof | Independent check | Status and boundary |
|---|---|---|---|---|
| GPT-5.5 at medium effort authored the final ten-card deck through Codex | C and B | [`study.json`](evidence/study.json), [`provenance.md`](evidence/provenance.md) | Compare the declared attribution source with the recorded manifest metadata error | Supported attribution; raw authoring transcript is retained privately, not published |
| All ten final card artifacts were frozen before the principal comparison sweeps | A and B | [`card-catalog.csv`](evidence/card-catalog.csv), [`benchmark/cards/`](benchmark/cards/), [`study.json`](evidence/study.json) | `python3 scripts/verify.py` recomputes card, stub, and test hashes | Supported for the four published artifact classes; v1 did not bind every route and policy field |
| The runtime comparison used no LLM orchestrator or coordinator for control-plane decisions | A and B | [`runner/archive/`](runner/archive/), [`runner-artifacts.csv`](evidence/runner-artifacts.csv), [`method.md`](docs/method.md) | Inspect hard-coded card order, retry branch, gates, and stop flag; run `bash -n` through the verifier | Supported for the published historical runners; worker models still chose code and tool actions |
| Local inference ran on an Apple M5 Max MacBook Pro with 18 CPU cores and 128 GB unified memory | C and B | [`study.json`](evidence/study.json), [`local-attempts.csv`](evidence/local-attempts.csv) | Cross-check every local attempt's hardware field with the canonical study record | Operator-recorded environment; not an independently reproduced hardware benchmark |
| Local Qwen3.6 27B made the published gates green through C9 | A and B | [`qwen27-c9/spreadsheet.py`](evidence/accepted-artifacts/qwen27-c9/spreadsheet.py), [`qwen27-c9/pytest.txt`](evidence/accepted-artifacts/qwen27-c9/pytest.txt), [`metadata.json`](evidence/accepted-artifacts/metadata.json), [`local-attempts.csv`](evidence/local-attempts.csv) | `python3 scripts/verify.py` checks hashes and post-hoc behavior; `python3 scripts/verify_red_gates.py` replays relevant public suites | Supported as a retry-assisted published-gate result; first C9 attempt timed out at 900 s and accepted rerun records 2,006 s |
| Local Gemma 4 31B made the published gates green through C9 on first attempts | A and B | [`gemma4-c9/spreadsheet.py`](evidence/accepted-artifacts/gemma4-c9/spreadsheet.py), [`gemma4-c9/pytest.txt`](evidence/accepted-artifacts/gemma4-c9/pytest.txt), [`metadata.json`](evidence/accepted-artifacts/metadata.json), [`local-attempts.csv`](evidence/local-attempts.csv) | `python3 scripts/verify.py` recomputes the attempt sequence, hashes, and probes | Supported for the published v1 gates; C9 recorded 804 s |
| Eight of thirteen hosted OpenCode Go routes reached the C9 published-gate ceiling | B | [`hosted-results.csv`](evidence/hosted-results.csv), [`model-summary.csv`](evidence/model-summary.csv) | `python3 scripts/verify.py` recomputes contiguous ceilings and requires exactly eight | Supported as a normalized route record; heterogeneous hosted services and budgets prevent a clean speed ranking |
| The public leaderboard shows every tested configuration and its exact card breakpoint | B derived from A and B | [`card-matrix.csv`](evidence/card-matrix.csv), [`leaderboard.md`](docs/leaderboard.md) | `python3 scripts/verify.py` reconstructs every local and hosted cell from the attempt ledgers and validates competition ranks | Completion ranking only; C10 is displayed as an excluded diagnostic and timing does not break ties |
| Kimi K2.7 Code had green C9 tests but was rejected by the anti-stub gate | B and A | [`hosted-results.csv`](evidence/hosted-results.csv), [`model-summary.csv`](evidence/model-summary.csv), historical anti-stub logic in [`runner/archive/`](runner/archive/) | Inspect the lexical `NotImplementedError` rule and the normalized C9 notes | Supported as a gate defect finding; full-gate comparative ceiling remains C8 |
| C9 public gates did not prove the whole written contract | A | [`card9-posthoc-audit.md`](evidence/card9-posthoc-audit.md), accepted [`metadata.json`](evidence/accepted-artifacts/metadata.json), both accepted implementations | `python3 scripts/verify.py` reruns multi-letter, boolean, and large-integer probes | Directly reproduced; both artifacts fail at least two uncovered clauses |
| C10 is invalid for comparative inference | A | [`card10-audit.json`](evidence/card10-audit.json), [`card10-audit.md`](evidence/card10-audit.md), frozen [`CARD.md`](benchmark/cards/card10-master-coder/CARD.md), and public test | Inspect the slash and escaped-backslash contradictions; verifier checks the audit state | Supported benchmark-validity finding; all C10 model outcomes are excluded from ranking |
| GPT-5.5 xhigh passed the seven published C10 tests but did not provide clean semantic proof | A | exact [`glob_matcher.py`](evidence/reference-artifacts/gpt55-xhigh-c10/glob_matcher.py), [`pytest.txt`](evidence/reference-artifacts/gpt55-xhigh-c10/pytest.txt), and [`metadata.json`](evidence/reference-artifacts/metadata.json) | `python3 scripts/verify_red_gates.py` replays 7/7; `verify.py` reproduces the pair-specific slash branch and broadened backslash behavior | Direct published-gate proof, explicitly excluded from comparative ranking |
| Every published benchmark stub starts red | A | [`benchmark/cards/`](benchmark/cards/), [`card-catalog.csv`](evidence/card-catalog.csv) | `python3 scripts/verify_red_gates.py` executes all ten suites and requires failure | Replayable with the pinned development dependencies and declared Hypothesis seed |
| The v1 controller was deterministic but not hermetic | A and B | [`runner/archive/`](runner/archive/), [`controller-policy.md`](protocol/controller-policy.md), [`limitations.md`](docs/limitations.md) | Inspect the working-directory scope checks and absence of OS sandbox enforcement | Supported and explicitly limited: dotfiles, nested changes, deletions, and off-tree access were not fully observed |
| Strong Cards are a useful placement boundary for smaller models | D grounded in A-C | [`strong-card-concept.md`](docs/strong-card-concept.md), [`placement-guide.md`](docs/placement-guide.md), and the result artifacts above | Replicate the repaired design in [`next-experiment.md`](docs/next-experiment.md) | Promising first-test inference, not a causal or universal conclusion |

## Repository classification

The project is ordered by function rather than chronology:

| Path | Classification | Contents and authority |
|---|---|---|
| `README.md`, `CASE-STUDY.md` | Public synthesis | Entry point and complete research narrative; neither overrides evidence artifacts |
| `PROOF-INDEX.md` | Public claim map | Maps statements to evidence, replay checks, and limitations |
| `docs/` | Public analysis | Method, results, limitations, placement, next study, public posts, and the formal concept |
| `protocol/` | Normative v2 design | Hardened Strong Card template and deterministic controller contract; not a claim that v1 already implemented every control |
| `benchmark/` | Frozen public inputs | Ten cards, starting stubs, and normalized public tests; C10 retained but excluded |
| `evidence/` | Public proof package | Canonical machine-readable records, accepted local C9 artifacts, audits, reference C10 artifact, hashes, and provenance |
| `runner/archive/` | Historical mechanism | Sanitized v1 shell runners with source/public digests and disclosed control gaps |
| `scripts/` | Public verification | Consistency, hash, hygiene, link, probe, red-gate, and reference replay checks |
| `.github/`, `Makefile`, dependency files | Reproduction infrastructure | Continuous verification and pinned developer test environment |
| `.private-inputs/` | Sanitized retained source archive, gitignored | 147 retained source files classified by cards, consults, contracts, model-placement records, orchestration, supplied requests, runs, and excluded side material; credentials, identity-bearing paths, emails, machine identifiers, and generated caches have been removed or redacted |
| `.git/` | Revision proof | Repository history and the sealed public snapshot |

## Reproduction order

For the fastest independent audit:

1. Read [`evidence/study.json`](evidence/study.json) for the declared design and
   claim boundary.
2. Run `make verify` to recompute hashes, totals, public-artifact probes, links,
   runner syntax, and publication hygiene.
3. Install `requirements-dev.txt` and run `make verify-red` to execute every red
   starting gate and replay the excluded GPT C10 reference against the normalized
   public test.
4. Inspect [`local-attempts.csv`](evidence/local-attempts.csv) and
   [`hosted-results.csv`](evidence/hosted-results.csv) instead of relying on the
   headline table.
5. Read the C9 and C10 audits before drawing capability conclusions.
6. Inspect the historical runners to verify that control decisions are ordinary
   shell/Python transitions rather than model judgments.

## Public versus retained proof

The public Git history intentionally excludes raw sessions, machine identifiers,
unredacted paths, unrelated source material, and credentials. The complete owner
copy retains sanitized versions of those inputs under `.private-inputs/` for
continued research. Original attachment digests remain in its private inventory,
but sensitive plaintext is not retained in this project. That folder is an audit
source, not a public reproducibility dependency and must remain gitignored before
any push.

This boundary makes two things true at once: the public repository is safe and
reviewable, while the owner retains the complete source record needed to extend,
challenge, or repeat the study.
