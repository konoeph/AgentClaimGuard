# Evaluation

AgentClaimGuard includes a small deterministic evaluation suite under
`examples/evaluation/`.

The suite shows which structured claim patterns are blocked or passed under the
current evidence, tool-result, and policy contracts.

## What It Measures

The evaluation suite measures deterministic verifier behavior:

- numeric claims missing required calculator results
- numeric claims with required calculator results
- claims missing required evidence
- claims with invalid `evidence_refs`
- compliance claims missing required regulation evidence
- claims citing explicitly conflicting evidence
- RAG-style answers missing required citations

Each case declares:

- `case_id`
- `description`
- `claims`
- `evidence`
- `tool_results`
- `policy`
- expected top-level status
- expected claim status
- expected violation type when blocked

Some cases produce more than one violation. The runner treats a blocked case as
passing when the expected violation type is present in the actual violation
list.

## What It Does Not Measure

This is not a factuality benchmark.

It does not measure:

- whether claims are true in the real world
- whether evidence semantically entails a claim
- whether every hallucination is detected
- retrieval quality
- ranking quality
- source authority
- LLM judgment quality

The current suite only evaluates deterministic policy/evidence/tool contracts.

## Run

From a local clone:

```bash
python examples/evaluation/run_eval.py
```

Expected summary:

```text
total_cases=7
passed_cases=7
failed_cases=0
blocked_count=6
passed_count=1
```

The command exits with a non-zero status if any case fails.

## Case File

Cases live in:

```text
examples/evaluation/cases.jsonl
```

Each line is one JSON object. Use JSONL so new cases can be added without
editing a single large JSON array.

Minimal shape:

```json
{
  "case_id": "numeric_missing_calculator",
  "description": "Numeric claim has required source facts but no calculator result.",
  "policy": "generic_numeric",
  "claims": [],
  "evidence": [],
  "tool_results": [],
  "expected": {
    "status": "blocked",
    "claim_status": "tool_required",
    "violation_type": "missing_required_tool_result"
  }
}
```

For passing cases, set:

```json
{
  "expected": {
    "status": "passed",
    "claim_status": "passed",
    "violation_type": null
  }
}
```

## Add A New Case

1. Pick a built-in policy such as `generic_numeric`, `generic_compliance`, or
   `generic_rag`.
2. Add one JSONL line to `examples/evaluation/cases.jsonl`.
3. Include structured claims, evidence, and tool results.
4. Set expected top-level status, claim status, and violation type.
5. Run:

```bash
python examples/evaluation/run_eval.py
```

Do not use this suite to hide semantic assumptions. If a case requires semantic
entailment or LLM judgment, document that as a future support-checker case
rather than adding a misleading deterministic expectation.
