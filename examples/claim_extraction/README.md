# Claim Extraction Helper Example

This example shows the optional claim extraction helper.

The helper is deterministic. It does not call an LLM and does not verify truth.
It only converts user-provided claim-like items into structured
AgentClaimGuard `Claim` objects.

```text
LLM/RAG answer -> claim candidates -> AgentClaimGuard.verify(...)
```

## Run

```bash
python examples/claim_extraction/demo.py
```

## Expected Output

```text
extracted_claims=1
skipped_items=1
guard_status=blocked
claim_status=tool_required
safe_verdict=insufficient_evidence
```

## Boundary

Extraction is not verification.

Use `ClaimExtractionTemplate.default()` when you want to ask your own LLM to
produce claim candidates. AgentClaimGuard still verifies those claims against
evidence, tool results, and policies afterwards.

## Behavior Notes

- `create_claims_from_items(...)` accepts strings, dictionaries,
  `ClaimCandidate` objects, and existing `Claim` objects.
- Dictionaries may use either `type` or `claim_type`; if both are present,
  `type` wins.
- Invalid items are collected in `skipped_items`, with matching messages in
  `warnings`.
- Invalid confidence values are skipped in batch extraction instead of stopping
  the whole batch.
- `ClaimExtractionTemplate.default()` only returns a prompt template. It does
  not call a model.
