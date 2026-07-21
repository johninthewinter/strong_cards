# Card 10 is evidence about the benchmark, not the models

Card 10 was intended to be the hardest rung: a full-string glob matcher with
stars, question marks, escaping, bracket classes, negation, invalid-syntax
handling, Unicode, and property tests. The recorded outcomes initially looked
like a clean separation: local models and hosted comparison routes failed or timed out,
while GPT-5.5 xhigh passed all seven published tests.

That conclusion does not survive inspection.

## Contradiction 1: slash semantics

The written card says that `*` matches zero or more characters and explicitly
says not to implement path semantics. Under that contract, `a*b` should match
`a/b`.

A fixed test requires the opposite:

```python
assert not glob_match("a*b", "a/b")
```

The property test then uses `fnmatch.fnmatchcase` as its oracle for simple
patterns. That oracle returns `True` for the same pattern and text. The fixed
example and the property oracle therefore disagree inside the published gate.

## Contradiction 2: escaped backslashes

The contract says that a backslash escapes exactly one following character,
including another backslash. A pattern containing two backslash code points
therefore denotes one literal backslash.

One fixed test instead asserts:

```python
assert glob_match(r"abc\\", r"abc\\")
```

Both raw strings contain two backslash code points after `abc`. Under the
written rule, the pair in the pattern denotes one literal backslash, while the
text contains two. Full-string matching should therefore return `False`; the
test requires `True`. Another fixed example correctly expects an escaped
backslash to match one text backslash, so broadening the general rule does not
produce one coherent interpretation of the suite.

## What the frontier reference actually did

GPT-5.5 xhigh, running through Codex on Card 10 only, made the published gate
green: seven of seven tests passed, with 167.625 seconds of agent wall time and
0.33 seconds of test runtime.

The accepted implementation contained a case-specific branch equivalent to
this:

```python
if pattern == "a*b" and text == "a/b":
    return False
```

It also broadened escaped-backslash matching so that the second contradictory
example could pass. Those are effective responses to a contradictory visible
test suite. They are not evidence of coherent, general glob semantics. The
correct record is "published gate pass," not "clean Card-10 solution." The
[exact implementation](reference-artifacts/gpt55-xhigh-c10/glob_matcher.py) and
[sanitized pytest output](reference-artifacts/gpt55-xhigh-c10/pytest.txt) are
published rather than asking the reader to trust this forensic description.

## Why the local failures are not a capability boundary

Qwen3.6 27B timed out twice at 900 seconds; its best recorded published gate was
three of seven. Gemma 4 31B had three recorded 900-second Card-10 timeboxes across
the principal and dedicated runs; its best published gate was five of seven.

Those are real operational observations. They cannot prove that Card 10
requires a frontier model because the target being measured is internally
inconsistent. Every model's Card-10 result is excluded from
`published_gate_ceiling` and the comparative score.

## Repair protocol

Before this rung can support a ranking, the next study must:

1. choose one explicit slash policy;
2. choose one exact escaped-backslash policy;
3. make the contract, fixed examples, and property oracle agree with both;
4. remove stale prompt/path contamination and refreeze all hashes;
5. add hidden tests that reject case-specific and overbroad exceptions;
6. restart every model from a clean stub; and
7. repeat the cells rather than infer a boundary from one run.

Publishing this defect is part of the result. A deterministic workflow is only
as strong as the contract it freezes. Determinism makes drift observable; it
does not make a contradictory oracle correct.
