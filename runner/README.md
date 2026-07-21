# Historical v1 runner archive

These six shell scripts are the de-identified control programs used by the v1
sweeps and focused follow-ups. They are published so the central architectural
claim can be inspected in code rather than inferred from a diagram.

The control path is visible directly:

- model and card routes are static arrays;
- card order is a shell loop;
- the adapter is invoked once per attempt;
- pytest, anti-stub, and directory-scope gates are ordinary commands;
- the retry is constructed mechanically from recorded failure output;
- a second failed attempt sets `broken=1` and later cards are skipped;
- no LLM chooses a route, adjudicates a gate, or selects the next transition.

## Files

| Public artifact | Historical role |
|---|---|
| `archive/v1-hosted-run-cell.sh` | One hosted OpenCode CLI cell; byte-identical to the archived source |
| `archive/v1-hosted-sweep.sh` | Main OpenCode CLI sweep over OpenCode Go model routes |
| `archive/v1-hosted-addon-sweep.sh` | Kimi K2.7 Code and DeepSeek V4 Pro add-on sweep |
| `archive/v1-local-sweep.sh` | Main local Ollama sweep through the Claude Code-compatible wrapper |
| `archive/v1-qwen27-followup.sh` | Qwen3.6 27B focused rerun with forced Card 10 |
| `archive/v1-gemma-card10-followup.sh` | Gemma 4 focused Card 10 follow-up |

Source and public SHA-256 values are in
[`evidence/runner-artifacts.csv`](../evidence/runner-artifacts.csv). The only
source transformations were replacing the workstation root with required
`PIPELINE_ROOT` configuration and replacing one private executable path with the
`claude-ollama` command name. The single-cell hosted runner required neither
change and retains its original digest.

## Important v1 limitations visible in the code

This archive is evidence of a deterministic control plane. It is not evidence
of a hardened sandbox.

- Isolation was a fresh working directory plus explicit prompt instructions,
  not an operating-system boundary.
- The local adapter granted shell tools with bypassed interactive permissions.
- The v1 scope gate compared the test file and looked for unexpected visible
  top-level names. It did not inventory dotfiles, off-tree writes, reads,
  deletions, nested changes, or modifications to every copied context file.
- Rechecking the frozen manifest protected the source deck, not every byte in
  the materialized worker directory.
- Result files were truncated at the start of each sweep invocation, then
  appended once per event. They were invocation-scoped ledgers, not durable
  append-only logs across reruns.
- The scripts expect unpublished v1 prompt envelopes and a private manifest
  under `PIPELINE_ROOT`; they are archival control code, not a turnkey replay
  from this public repository.

Those limitations do not introduce an LLM coordinator. They narrow the claim:
v1 proved that routing, retry, gating, and stopping can be encoded without one;
it did not yet prove hermetic containment or replay-complete provenance.

The hardened target policy in [`protocol/controller-policy.md`](../protocol/controller-policy.md)
closes these gaps by requiring content-addressed materialization, complete change
inventory, durable event storage, and versioned route and timeout policy.
