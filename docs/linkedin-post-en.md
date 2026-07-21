# LinkedIn post in English

A local 27-billion-parameter model just reached the ninth step of a progressive engineering benchmark on my M5 Max MacBook Pro.

Not nine variations of a toy prompt.

C1: an LRU cache.
C3: a bank ledger with atomicity and invariants.
C7: an expression parser without `eval`.
C8: dependency graphs with cycle detection.
C9: a small spreadsheet engine that parses formulas, resolves forward references, expands rectangular ranges, and detects cycles.

Local Gemma 4 31B cleared C1 through C9 on first attempts.
Local Qwen3.6 27B cleared C1 through C8, then passed C9 after an extended retry.
Eight hosted routes across GLM, MiMo, Qwen, MiniMax, and DeepSeek also reached C9.

The important result is not that a small model “replaced” a frontier model.

It never had to become the architect.

GPT-5.5 had compiled every step into a Strong Card: a frozen contract containing the objective, interface, writable scope, invariants, tests, budget, retry rules, and stop conditions.

Then it left the loop.

A shell/Python controller selected the card, launched the worker, ran the gates, allowed or denied the retry, and stopped the run. Zero LLM control-plane decisions. Claude Code was the harness for local models, OpenCode for hosted routes, and Codex for the GPT reference run.

Frontier intelligence was spent before execution. Authority stayed in deterministic code. Cheaper models absorbed the bounded implementation work.

The audit also broke my own result. C9 had coverage gaps. C10 contradicted itself across contract and tests. Even GPT-5.5 xhigh reached 7/7 by coding around an invalid benchmark.

That is exactly why this experiment matters to me.

I am not asking whether a small model can improvise an application from an ambiguous brief. I am asking where it belongs in a real architecture so it can be useful, verifiable, and replaceable without receiving authority over the system.

I published the full card-by-card, model-by-model leaderboard, including failures, retries, gate false positives, accepted artifacts, runners, and limitations.

First pilot. The next protocol is already being designed.
