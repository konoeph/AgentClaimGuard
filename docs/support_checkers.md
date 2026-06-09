# Support Checkers Design Note

This is a v0.5 design note. It is not implemented in the core runtime.

## Goal

Add an optional semantic support-checking extension point without turning
AgentClaimGuard into a hidden LLM judge.

The core verifier should remain deterministic and policy-driven. Semantic
support checks should be explicit, configurable, and optional.

## Proposed Types

```python
class SupportCheckResult(BaseModel):
    claim_id: str
    status: Literal["supported", "unsupported", "contradicted", "unknown"]
    confidence: float | None = None
    reason: str | None = None
    evidence_refs: list[str] = []
    metadata: dict[str, Any] = {}


class SupportChecker(Protocol):
    def check(
        self,
        claim: Claim,
        evidence: list[Evidence],
        policy: Policy,
    ) -> SupportCheckResult:
        ...
```

## Possible Backends

- deterministic custom checker
- LLM-based checker
- NLI model checker
- domain-specific rule checker
- external service checker

## Runtime Boundary

Support checkers should be opt-in:

```text
core policy checks -> optional SupportChecker -> combined verification result
```

The default AgentClaimGuard runtime should not call an LLM, network service, or
semantic model.

## Policy Boundary

Policies may later include optional semantic support settings, for example:

```yaml
claim_types:
  factual_claim:
    required_evidence:
      - type: source_fact
        min_count: 1
    support_check:
      enabled: true
      backend: custom
      min_confidence: 0.8
```

This should remain a future extension. It should not change the meaning of
existing deterministic policy fields.

## Non-Goals

- no mandatory LLM dependency
- no built-in universal factuality verifier
- no hidden model calls in the core verifier
- no claim extraction inside support checking
- no replacement for evidence and tool-result contracts

## Design Principle

Semantic support checking can add evidence-quality signals, but it should not
erase the current contract:

```text
Claim -> Evidence -> Tool -> Policy -> Verify
```

If a workflow needs semantic entailment, it should opt into a support checker
and treat the result as one additional verification signal.
