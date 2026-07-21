# Related work and primary documentation

This pilot sits between model routing, repository-level coding evaluation, and
workflow engineering. It does not claim to introduce model cascades or software
agent benchmarks. Its narrower contribution is to move ambiguity reduction
before execution, then replace a runtime LLM coordinator with a small,
deterministic state machine around frozen task contracts.

## Model routing and cost

- Chen, Zaharia, and Zou,
  [FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance](https://arxiv.org/abs/2305.05176),
  2023. Describes cascades that select among LLMs to improve the
  cost/quality trade-off.
- Ong et al.,
  [RouteLLM: Learning to Route LLMs with Preference Data](https://arxiv.org/abs/2406.18665),
  2024. Learns routing policies between stronger and weaker models.

Strong Cards takes a more static first step. Routing happens after a task has
been compiled into a hash-bound execution contract, and the initial route table
is plain configuration rather than an LLM or learned service. The experiment
asks whether better task construction can make a cheaper worker operationally
acceptable before adaptive routing is added.

## Software-agent evaluation

- Jimenez et al.,
  [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770),
  ICLR 2024. Evaluates end-to-end resolution of repository issues.

SWE-bench measures a model or agent against real issue-level work. This pilot
instead studies deliberately bounded implementation cells with frozen scope and
visible proof obligations. That sacrifices ecological breadth to make control
flow, retries, scope violations, and oracle defects easier to inspect.

## Execution surfaces and model sources

- [OpenCode Go documentation](https://dev.opencode.ai/docs/go/) documents the
  hosted execution surface and its model routes.
- [Claude Code CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-usage)
  documents headless print mode, the interface shape used by the compatible
  local wrapper. The local attempts did not use Anthropic inference.
- [Qwen3.6 repository](https://github.com/QwenLM/Qwen3.6/blob/main/README.md) and
  [Qwen3.6 27B model files](https://huggingface.co/Qwen/Qwen3.6-27B/tree/main)
  identify the open model family used by the local lane.
- [Gemma 4 model documentation](https://deepmind.google/models/gemma/gemma-4/)
  identifies the Gemma family used by the local lane.
- [MiMo-V2.5 release documentation](https://mimo.mi.com/docs/en-US/news/latest/v2.5-open-sourced)
  provides primary model-family context for the hosted MiMo routes.

The route names in the evidence tables are preserved as observed. A product
page or model-family document does not establish the immutable provider-side
weight revision used in a historical hosted call; that missing provenance is
listed as a limitation.
