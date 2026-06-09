# Policy Reference

AgentClaimGuard policies are YAML files that define claim-level evidence and
tool-result contracts.

## Top-Level Fields

```yaml
name: generic_numeric
version: "0.1"

claim_types: {}

default_fallback:
  verdict: need_check
  reason: The claim could not be verified by the active policy.

metadata: {}
```

Fields:

- `name`: policy name
- `version`: policy version string
- `claim_types`: mapping from claim type to claim-type policy
- `default_fallback`: fallback used when a claim type has no fallback
- `metadata`: optional policy metadata

## Claim-Type Fields

```yaml
claim_types:
  numeric_conclusion:
    required_evidence:
      - type: source_fact
        min_count: 2
    required_tool_results:
      - calculator
    forbidden:
      - numeric_claim_without_tool
    fallback:
      verdict: insufficient_evidence
      reason: Numeric conclusions require source facts and calculation results.
    metadata: {}
```

Fields:

- `required_evidence`: evidence type/count requirements
- `required_tool_results`: tool-result requirements
- `forbidden`: named forbidden patterns checked by built-in validators
- `fallback`: safe verdict and reason for blocked claims of this type
- `metadata`: optional claim-type policy metadata

## required_evidence

Each evidence requirement has:

```yaml
type: source_fact
min_count: 2
```

`min_count` defaults to `1`.

The verifier counts referenced evidence records of the required `type`.

## required_tool_results

Tool requirements can be written as a string:

```yaml
required_tool_results:
  - calculator
```

Or as an object:

```yaml
required_tool_results:
  - tool_name: calculator
    min_count: 1
```

`min_count` defaults to `1`.

The verifier counts successful referenced tool results with the required
`tool_name`.

## fallback

Fallback rules define the safe verdict returned when a claim is blocked:

```yaml
fallback:
  verdict: insufficient_evidence
  reason: Numeric conclusions require source facts and calculation results.
```

Fallbacks do not prove an alternative answer. They provide a conservative
application-level routing signal.

## Numeric Example

```yaml
name: generic_numeric
version: "0.1"

claim_types:
  numeric_conclusion:
    required_evidence:
      - type: source_fact
        min_count: 2
    required_tool_results:
      - calculator
    forbidden:
      - numeric_claim_without_tool
    fallback:
      verdict: insufficient_evidence
      reason: Numeric conclusions require source facts and calculation results.
```

This policy blocks a numeric conclusion when source facts exist but a successful
calculator result is missing.

## Compliance Example

```yaml
name: generic_compliance
version: "0.1"

claim_types:
  compliance_judgement:
    required_evidence:
      - type: regulation
        min_count: 1
      - type: source_fact
        min_count: 1
    forbidden:
      - use_model_memory_as_authority
      - unsupported_pass_fail
    fallback:
      verdict: need_check
      reason: Compliance judgments require rule evidence and source facts.
```

This policy blocks a compliance judgment when it lacks either regulation
evidence or source facts.

## Current Limits

Policies currently express deterministic structural checks. They do not perform
semantic entailment, source-quality scoring, or LLM-based truth judgment by
default.
