# Limitations

AgentClaimGuard is a lightweight claim-level evidence and policy gate.

It checks whether structured claims are allowed under explicit evidence,
tool-result, and policy contracts. It does not prove factual truth by itself.

## What AgentClaimGuard Checks

AgentClaimGuard currently checks structural and policy-level conditions:

- whether a claim references required evidence
- whether referenced evidence IDs exist
- whether required evidence types and counts are present
- whether required tool results are present and successful
- whether a claim violates configured forbidden patterns
- whether evidence records are explicitly marked as conflicting
- whether citations and tool-result references are bound to known records

These checks are deterministic and policy-driven.

## What AgentClaimGuard Does Not Guarantee

AgentClaimGuard does not guarantee that:

- a claim is factually true
- a retrieved passage semantically entails the claim
- every hallucination is detected
- a source document is authoritative or current
- a tool result was computed correctly outside the recorded result
- an LLM used the evidence correctly
- a workflow is safe for all production use cases

It is not a full factuality verifier, hallucination detector, semantic
entailment engine, legal reviewer, compliance authority, or mature production
guardrail framework.

## Current Support Model

The current verifier assumes claims, evidence, and tool results are already
structured.

For example, a `numeric_conclusion` policy can require:

```text
- two source_fact evidence records
- one successful calculator tool result
```

If the calculator result is missing, AgentClaimGuard can block the claim. It
does not independently recalculate the business metric unless a calculator tool
result is provided and referenced.

## Future Direction

Optional semantic support checking is planned as a separate extension point.
That future layer should be explicit, configurable, and optional. It should not
turn the core verifier into a hidden LLM judge.

See [support_checkers.md](support_checkers.md) for the v0.5 design note.
