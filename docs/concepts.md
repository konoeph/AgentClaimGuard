# Concepts

AgentClaimGuard verifies structured claim records against evidence, tool
results, and policy rules.

## Claim

A `Claim` is a structured statement that may be returned by an LLM, RAG system,
agent, or workflow.

Core fields:

- `id`: stable claim ID
- `text`: the claim text
- `type`: policy key such as `numeric_conclusion` or `compliance_judgement`
- `verdict`: optional upstream verdict
- `evidence_refs`: evidence IDs the claim depends on
- `tool_result_refs`: tool result IDs the claim depends on
- `confidence`: optional upstream confidence between `0.0` and `1.0`
- `metadata`: extra workflow-specific fields

## Evidence

`Evidence` is a structured source record used by policy checks.

Core fields:

- `id`: stable evidence ID
- `type`: evidence type such as `source_fact` or `regulation`
- `source`: optional source label
- `locator`: optional page, URL, chunk, or record locator
- `content`: evidence text or serialized content
- `metadata`: extra fields such as retrieval score, document ID, or conflict tags

Evidence presence does not automatically prove semantic support. The current
runtime checks references, types, counts, and explicit conflict metadata.

## ToolResult

`ToolResult` records the output of a tool call.

Core fields:

- `id`: stable tool result ID
- `tool_name`: tool name such as `calculator`
- `status`: `success`, `error`, or `skipped`
- `input`: tool input payload
- `output`: tool output payload
- `evidence_refs`: evidence IDs used by the tool
- `metadata`: extra tool-specific fields

Policies can require successful tool results before a claim is allowed.

## Policy

A `Policy` defines the evidence and tool-result contract for each claim type.

It can specify:

- `required_evidence`
- `required_tool_results`
- `forbidden`
- `fallback`
- `default_fallback`
- `metadata`

See [policy.md](policy.md) for the YAML format.

## VerificationResult

`VerificationResult` is the top-level result returned by the verifier.

Core fields:

- `status`: `passed` or `blocked`
- `claim_results`: per-claim results
- `violations`: flattened policy violations
- `safe_output`: structured fallback output for blocked claims

## Violation

A `Violation` explains why a claim failed a policy check.

Core fields:

- `claim_id`
- `type`
- `message`
- `required`
- `found`
- `refs`
- `details`

Common violation types include:

- `missing_required_evidence`
- `missing_required_tool_result`
- `required_tool_error`
- `invalid_evidence_ref`
- `missing_citation`
- `conflicting_evidence`

## safe_output

`safe_output` is a conservative structured fallback produced when claims are
blocked.

Current shape:

```python
{
    "blocked_claims": [
        {
            "claim_id": "claim_1",
            "safe_verdict": "insufficient_evidence",
            "reason": "Numeric conclusions require source facts and calculation results.",
            "status": "tool_required",
        }
    ]
}
```

Applications can use `safe_output` to route blocked claims to repair, retrieval,
or human review.
