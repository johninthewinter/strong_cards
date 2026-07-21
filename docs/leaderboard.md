# Strong Cards completion leaderboard

## What is being ranked

This is a **progressive implementation ladder**, not ten unrelated prompts. Each
card adds another kind of engineering pressure while keeping the worker inside a
frozen contract.

| Card | Task | What becomes harder |
|---|---|---|
| C1 | LRU cache | Mutable state, recency, eviction, property-model agreement |
| C2 | Interval merge | Boundary semantics, ordering, non-mutation |
| C3 | Bank ledger | Atomic state transitions, invariants, history |
| C4 | Undo stack | Undo, redo, immutable snapshots, branch invalidation |
| C5 | Generic LRU class | Typed reusable API plus stateful recency |
| C6 | Rich interval merge | Negative ranges, containment, duplicates, dense overlap |
| C7 | Expression evaluator | Custom parser, precedence, variables, syntax rejection |
| C8 | Topological batcher | Dependency graph, cycles, stable deterministic ordering |
| C9 | Spreadsheet engine | Formula parser, forward references, rectangular ranges, dependency evaluation, cycles |
| C10 | Glob matcher | Wildcards, escaping, character classes, Unicode; **excluded because its contract and tests contradict each other** |

The comparative score stops at C9. Rank is based only on the number of contiguous
full-gate acceptances from C1. Ties share a rank. Timing does not break ties
because local and hosted routes used different infrastructure and budgets.

## Every tested configuration, card by card

Legend: `P` accepted on first attempt; `R` accepted after informed retry; `G`
functional tests passed but another gate rejected the artifact; `F` terminal
failure or timeout; `-` not run; `X/...` C10 diagnostic excluded from ranking.

| Rank | Model configuration | Route | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | Score | C10, excluded |
|---:|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---:|---|
| 1 | Gemma 4 31B coding BF16 | Local Ollama, Claude Code-compatible harness | P | P | P | P | P | P | P | P | P | 9/9 | X/timeout, best 5/7 |
| 1 | GLM-5.2 | OpenCode CLI | P | P | P | P | P | P | P | P | P | 9/9 | X/fail |
| 1 | Qwen3.7 Max | OpenCode CLI | P | P | P | P | P | P | P | P | P | 9/9 | X/fail |
| 1 | MiniMax M3 | OpenCode CLI | P | P | P | P | P | P | P | P | P | 9/9 | X/fail |
| 1 | DeepSeek V4 Flash | OpenCode CLI | P | P | P | P | P | P | P | P | P | 9/9 | X/contaminated fail |
| 1 | DeepSeek V4 Pro | OpenCode CLI | P | P | P | P | P | P | P | P | P | 9/9 | X/timeout |
| 1 | Qwen3.6 27B Q8 | Local Ollama, Claude Code-compatible harness | P | P | P | P | P | P | P | P | R | 9/9 | X/timeout, best 3/7 |
| 1 | MiMo-V2.5-Pro | OpenCode CLI | P | R | P | P | P | P | P | P | P | 9/9 | X/fail |
| 1 | Qwen3.7 Plus | OpenCode CLI | P | R | P | P | P | P | P | P | P | 9/9 | X/timeout |
| 1 | Qwen3.6 Plus | OpenCode CLI | P | P | P | P | P | P | R | P | R | 9/9 | X/fail |
| 11 | Kimi K2.7 Code | OpenCode CLI | P | P | P | P | P | P | P | P | G | 8/9 | - |
| 11 | Qwen3.6 35B A3B Q8 | Local Ollama, Claude Code-compatible harness | P | P | P | P | P | P | P | P | F | 8/9 | - |
| 13 | MiMo-V2.5 | OpenCode CLI | P | P | P | P | P | P | P | F | - | 7/9 | - |
| 14 | MiniMax M2.7 | OpenCode CLI | P | P | P | P | P | P | F | - | - | 6/9 | - |
| 15 | Kimi K2.6 | OpenCode CLI | P | G | - | - | - | - | - | - | - | 1/9 | - |
| 16 | GLM-5.1 | OpenCode CLI | F | - | - | - | - | - | - | - | - | 0/9 | - |
| - | GPT-5.5 xhigh reference | Codex, isolated C10 only | - | - | - | - | - | - | - | - | - | Not ranked | X/pass 7/7 |

## The result visible in one line

```text
stateful components -> transactional invariants -> parsers -> dependency graphs -> spreadsheet engine
       C1-C6                    C3-C6             C7              C8                    C9
```

Ten configurations cleared the entire valid ladder: two local models and eight
hosted routes. Six did so without an accepted retry. Qwen3.6 27B needed an
extended retry on the spreadsheet engine. Kimi K2.7 Code produced green C9 tests
twice but lost the card to a defective anti-stub gate, which is why `G` is not
counted as acceptance.

## What the table does not say

This is a completion leaderboard, not a universal intelligence or speed ranking.
The harnesses, inference locations, and budgets were heterogeneous. C9 also had
public-test gaps discovered after the run. C10 is displayed only because hiding
an invalid final card would make the record less useful; none of its outcomes
affect rank.

The canonical machine-readable form is
[`evidence/card-matrix.csv`](../evidence/card-matrix.csv). Attempt-level evidence
remains in [`local-attempts.csv`](../evidence/local-attempts.csv) and
[`hosted-results.csv`](../evidence/hosted-results.csv).
