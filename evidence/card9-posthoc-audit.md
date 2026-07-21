# Card 9 post-hoc contract probe

Both local headline artifacts made the eleven published Card 9 tests green. The
accepted solution files and literal pytest outputs are published under
`evidence/accepted-artifacts/`.

Inspection found multiple uncovered contract clauses. The targeted probes below
are not an exhaustive hidden suite; they demonstrate why a public-gate pass must
not be relabelled as complete contract proof.

### Multi-letter cells

The card permits cell names with one or more uppercase letters followed by a
positive row number. The public property generator covers columns A through D,
and the fixed invalid-name test checks `AA0`, but no public test uses a valid
multi-letter column such as `AA1`.

A post-hoc probe evaluated this workbook:

```python
{
    "AA1": 2,
    "AB1": "=AA1 + 3",
    "AC1": "=SUM(AA1:AB1)",
}
```

Expected `AC1` was 7.

- Gemma 4 31B returned the expected workbook.
- Qwen3.6 27B raised `SpreadsheetError` while tokenizing the multi-letter
  reference.

This does not erase Qwen's recorded 11/11 published-gate result. It changes its
interpretation: Qwen reached a test-green Card 9 after an extended informed
rerun, but did not satisfy the complete written contract under this post-hoc
probe. Gemma passed the published gate and this added probe.

### Boolean values

The card permits integer literals or formula strings and explicitly excludes
booleans. Both artifacts accept `{"A1": True}` because Python treats `bool` as a
subclass of `int`. Both therefore fail this contract probe.

### Unbounded integer division

The card defines integer arithmetic without a magnitude cap. Both artifacts
implement truncation with an intermediate float conversion. For
`100000000000000000000 / 3`, both return `33333333333333331968`; exact truncation
is `33333333333333333333`. Both fail this probe as well.

Neither local artifact has full-contract proof. Gemma has the stronger observed
C9 result—first-attempt public-gate pass plus multi-letter support—but the added
probes still found shared semantic gaps.

The finding reinforces the central systems lesson. A deterministic controller
can remove an LLM judge, but it cannot make an incomplete oracle complete. The
next deck must include multi-letter properties and hidden contract-entailment
tests before freeze.
