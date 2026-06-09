# Numeric Conclusion Example

This example shows both sides of the numeric policy contract.

Claim:

```text
Revenue increased by 15%.
```

Policy rule:

```text
numeric_conclusion requires:
- at least two source_fact evidence records
- at least one successful calculator tool result
```

## Blocked Case

`sample_blocked.json` includes the source facts but omits the calculator result.

Expected result:

```text
blocked_status=blocked
blocked_claim_status=tool_required
blocked_violations=2
```

## Passed Case

`sample_passed.json` includes the same source facts plus a successful
`calculator` result referenced by the claim.

Expected result:

```text
passed_status=passed
passed_claim_status=passed
passed_violations=0
```

## Run

```bash
python examples/numeric_conclusion/demo.py
```

AgentClaimGuard checks the evidence and tool-result contract. It does not prove
that the underlying business fact is true by itself.
