# Results

## Reading the scores

For the fastest visual comparison, open the
[card-by-card completion leaderboard](leaderboard.md). It shows every local,
hosted, and reference configuration across the full progressive ladder.

Card 10 is invalid for comparative inference. The primary score in this report is
therefore **published-gate cards passed among C1-C9**, not a semantic capability
score out of ten.

“Accepted” means the complete recorded v1 gate passed. It is stricter than tests
alone because anti-stub, test-integrity, and visible top-level directory checks
could reject a test-green implementation. It is weaker than full contract proof
or hermetic scope enforcement. These distinctions explain both the Kimi K2.7
Code result and the Card 9 post-hoc findings.

The experiment used different execution surfaces and some different budgets
across local and hosted lanes. Compare operational ceilings, not raw elapsed
time, as if this were a controlled speed leaderboard.

## Headline result

- Local Qwen3.6 27B made the C1-C9 published gates green, with Card 9 requiring a
  timeout followed by an extended informed rerun; it later failed a multi-letter
  contract probe.
- Local Gemma 4 31B made the C1-C9 published gates green on first attempts and
  passed the added multi-letter probe; other post-hoc gaps remained.
- Eight of thirteen hosted configurations made the published gates green through
  C9.
- Kimi K2.7 Code was test-green on Card 9 twice but rejected by a defective
  anti-stub rule, leaving its full-gate score at eight.
- Card 10 cannot support “only GPT-5.5 could solve it”; its contract and tests
  conflict, and the GPT reference hard-coded the conflicting example.

## Local lane

| Model tag | Published gates passed | First-pass gates | Published-gate ceiling | Card 9 result | Card 10 diagnostic |
|---|---:|---:|---:|---|---|
| `qwen3.6:27b-mtp-q8_0` | 9/9 | 8/9 | C9 | 900 s timeout, then 11/11 on rerun at 2,006 s; multi-letter probe failed | Two 900 s timeouts |
| `gemma4:31b-coding-mtp-bf16` | 9/9 | 9/9 | C9 | First-attempt 11/11 in 804 s; multi-letter probe passed | Three 900 s timeboxes across main and focused runs; best focused attempt reached 5/7 tests |
| `qwen3.6:35b-a3b-mtp-q8_0` | 8/9 | 8/9 | C8 | Two recorded timeouts, 953 s and 901 s | Skipped after C9 stop |

All three used local Ollama inference behind a Claude Code-compatible
`claude-ollama` execution surface. The machine was an Apple M5 Max MacBook Pro,
18-core CPU, 128 GB unified memory.

### Worker-invocation timing

| Model | C1-C8 worker wall | C9 attempts counted | Worker wall to accepted ceiling | Worker wall through terminal break |
|---|---:|---|---:|---:|
| Qwen3.6 27B | 1,533 s | 900 s timeout + 2,006 s accepted rerun | 4,439 s through C9 | same |
| Gemma 4 31B | 2,272 s | 804 s first-attempt pass | 3,076 s through C9 | same |
| Qwen3.6 35B | 929 s | 953 s timeout + 901 s timeout | 929 s through C8 | 2,783 s through terminal C9 failure |

These are sums of worker-CLI wall fields. They exclude warm/smoke preflight,
pytest and other post-worker gates, and controller overhead; they are not
end-to-end or token-generation benchmarks. Qwen3.6 27B's 2,006-second record exceeds the nominal
900-second retry policy. The result ledger supports the gate pass but does not
preserve enough launch telemetry to explain the budget overrun.

### Local attempt detail

| Card | Qwen3.6 27B | Gemma 4 31B | Qwen3.6 35B |
|---:|---:|---:|---:|
| C1 | pass, 171 s | pass, 229 s | pass, 66 s |
| C2 | pass, 201 s | pass, 501 s | pass, 98 s |
| C3 | pass, 211 s | pass, 270 s | pass, 80 s |
| C4 | pass, 145 s | pass, 201 s | pass, 50 s |
| C5 | pass, 134 s | pass, 227 s | pass, 44 s |
| C6 | pass, 239 s | pass, 280 s | pass, 62 s |
| C7 | pass, 303 s | pass, 235 s | pass, 451 s |
| C8 | pass, 129 s | pass, 329 s | pass, 78 s |
| C9 | timeout 900 s; retry pass 2,006 s | pass, 804 s | timeout 953 s; retry timeout 901 s |
| C10, excluded | timeout 900 s at 3/7; retry timeout 900 s at 0/7 | three 900 s timeboxes across the sweep and a focused follow-up; best 5/7 | not run; the run ended at the C9 break |

The Card 10 row is diagnostic only. The card is invalid for comparative
inference, so no outcome in it affects a ceiling or a rank.

The complete attempt rows, including Card 10 diagnostics, are in
[`evidence/local-attempts.csv`](../evidence/local-attempts.csv).

## Hosted OpenCode CLI lane

The execution surface was the OpenCode CLI; `opencode-go/...` is the provider and
model-route namespace.

| Model route | Published gates passed | Full-gate ceiling | Material qualification |
|---|---:|---:|---|
| `opencode-go/glm-5.2` | 9/9 | C9 | C10 affected by pre-envelope/stale-path behavior |
| `opencode-go/glm-5.1` | 0/9 | none | C1 retry timed out although post-timeout tests were green |
| `opencode-go/kimi-k2.6` | 1/9 | C1 | C2 tests passed; rejected for an out-of-scope `venv` directory |
| `opencode-go/kimi-k2.7-code` | 8/9 | C8 | C9 tests green twice; anti-stub false positive |
| `opencode-go/mimo-v2.5-pro` | 9/9 | C9 | C2 required one retry |
| `opencode-go/mimo-v2.5` | 7/9 | C7 | C8 remained stubbed after retry |
| `opencode-go/qwen3.7-max` | 9/9 | C9 | C10 returned no valid edit |
| `opencode-go/qwen3.7-plus` | 9/9 | C9 | C10 timed out twice at 300 s |
| `opencode-go/qwen3.6-plus` | 9/9 | C9 | Retries required on C7 and C9 |
| `opencode-go/minimax-m3` | 9/9 | C9 | Fastest recorded accepted path through C9 in this lane |
| `opencode-go/minimax-m2.7` | 6/9 | C6 | C7 remained stubbed after retry |
| `opencode-go/deepseek-v4-flash` | 9/9 | C9 | C10 contaminated by prompt/path or no-edit behavior |
| `opencode-go/deepseek-v4-pro` | 9/9 | C9 | C10 timeout records include 300 s and anomalous 1,880 s entries |

Eight hosted configurations received a 9/9 published-gate score. Kimi
K2.7 Code makes a ninth route with semantic tests green through C9, but not a
ninth full-gate pass.

### Recorded worker wall through accepted C9

For the eight hosted 9/9 routes, summing the recorded whole-second attempts
through the accepted Card 9 gives:

| Model route | Recorded seconds through C9, including failed retries |
|---|---:|
| MiniMax M3 | 332 |
| DeepSeek V4 Pro | 607 |
| Qwen3.7 Max | 640 |
| DeepSeek V4 Flash | 640 |
| Qwen3.7 Plus | 799 |
| MiMo-V2.5-Pro | 841 |
| GLM-5.2 | 908 |
| Qwen3.6 Plus | 963 |

This table is descriptive only. It mixes provider routes, possible queue time,
adapter behavior, and different model architectures. It should not be read as a
tokens-per-second or hardware comparison.

The normalized rows and qualifications are in
[`evidence/hosted-results.csv`](../evidence/hosted-results.csv).

## Harness sensitivity

Earlier direct-Ollama baselines made Qwen3.6 35B and Gemma 4 31B appear to stop
at Card 2 because the loop often narrated instead of writing the solution file.
Under the Claude Code-compatible local tool surface, Qwen3.6 35B reached C8 and
Gemma reached C9.

That difference is too large to treat “model” as the only independent variable.
Operational capability is a property of at least:

```text
weights × quantization × prompt × adapter × tools × permissions × budget × gates
```

A model result without its harness is incomplete evidence.

## Why Card 9 matters

The ninth card implemented a small spreadsheet engine. Passing required all of
the following under one public contract:

- tokenize and parse arithmetic formulas without `eval`;
- resolve forward cell references independently of input order;
- expand rectangular `SUM(A1:B3)` ranges;
- reject unknown cells and malformed names;
- detect direct and indirect dependency cycles;
- preserve the caller's input;
- satisfy deterministic examples and property tests.

This is the pilot's strongest published-gate capability signal. It is complex
enough to require composition, but the post-hoc audit found that its public
oracle did not cover the full contract: Qwen failed valid multi-letter cells,
and both local artifacts accepted booleans and lost precision on large integer
division. See the [accepted code and probe record](../evidence/card9-posthoc-audit.md).

## Card 10: recorded outcome versus valid inference

| Route | Recorded outcome | Valid interpretation |
|---|---|---|
| GPT-5.5 xhigh via Codex | 7/7 public tests; approximately 167.6 s agent wall | Published-gate pass only; solution hard-coded a contradictory case |
| Qwen3.6 27B local | Two 900 s timeouts | Diagnostic execution evidence only |
| Gemma 4 31B local | Three 900 s timeboxes; focused retry improved to 5/7 | Diagnostic execution evidence only |
| Hosted routes | Mixed no-edit, failure, and timeout outcomes | Confounded by invalid card and some prompt-envelope defects |

The conflict is specific. The prose says `*` matches zero or more characters and
forbids path semantics. A deterministic assertion requires `a*b` not to match
`a/b`, while the property oracle implies the match is valid. A second assertion
also contradicts exact one-character backslash escaping. The GPT solution
special-cased exactly `pattern == "a*b" and text == "a/b"` and broadened escaped
backslash matching.

The correct research result is not “GPT won.” It is “the benchmark failed its
own entailment audit.” See [`evidence/card10-audit.md`](../evidence/card10-audit.md).

## What the result means

The observed evidence supports placement, not replacement:

- frontier reasoning is high leverage before execution, while requirements and
  invariants can still be made explicit;
- deterministic code can hold retry, acceptance, and stop authority;
- smaller workers can own substantial bounded transformations;
- local workers can reach useful capability even when they are slower;
- gates must themselves be audited and tested.

The result does not establish general software-engineering autonomy or a stable
frontier boundary. It establishes a credible reason to build protocol v2.
