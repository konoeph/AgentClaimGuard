# Example Outputs

These are the expected high-level outcomes from the bundled demos.

## Integration Pattern Map

Use the examples by integration pattern:

```text
HTTP tool          examples/dify_http_tool
Evidence mapping  examples/ragflow_evidence
Framework adapter examples/langgraph_guard, examples/langchain_guard
Claim preparation examples/claim_extraction
Evaluation        examples/evaluation
Core runtime       examples/numeric_conclusion, examples/rag_citation
```

## Numeric Conclusion

```text
$ python examples/numeric_conclusion/demo.py
blocked_status=blocked
blocked_claim_status=tool_required
blocked_violations=2
blocked_safe_output={'blocked_claims': [{'claim_id': 'claim_1', 'safe_verdict': 'insufficient_evidence', 'reason': 'Numeric conclusions require source facts and calculation results.', 'status': 'tool_required'}]}
passed_status=passed
passed_claim_status=passed
passed_violations=0
passed_safe_output={'blocked_claims': []}
```

## Compliance Judgment

```text
$ python examples/compliance_judgement/demo.py
{
  "status": "blocked",
  "claim_results": [
    {
      "claim_id": "claim_2",
      "status": "insufficient_evidence",
      "safe_verdict": "need_check"
    }
  ]
}
```

## RAG Citation

```text
$ python examples/rag_citation/demo.py
{
  "status": "blocked",
  "claim_results": [
    {
      "claim_id": "claim_3",
      "status": "insufficient_evidence",
      "safe_verdict": "insufficient_evidence"
    }
  ]
}
```

## LangGraph Guard

The LangGraph demo runs through a real `StateGraph` when `langgraph` is
installed. Without it, the example falls back to direct node invocation and
prints the same routing outcome.

```text
$ python examples/langgraph_guard/demo.py
guard_status=blocked
claim_status=tool_required
route=blocked
final_answer=Need calculator result before returning numeric conclusion.
```

## LangChain Guard

```text
$ python examples/langchain_guard/demo.py
sync_final_answer=Revenue increased by 15%.
sync_guard_status=blocked
sync_claim_status=tool_required
async_final_answer=Revenue increased by 15%.
async_guard_status=blocked
async_claim_status=tool_required
```

## Dify HTTP Tool

The Dify HTTP tool example calls the existing FastAPI server with structured
claims, evidence, and tool results.

```text
$ curl -X POST http://localhost:8000/v1/verify \
  -H "Content-Type: application/json" \
  --data @examples/dify_http_tool/request.json
{
  "status": "blocked",
  "claim_results": [
    {
      "claim_id": "claim_dify_1",
      "status": "tool_required",
      "safe_verdict": "insufficient_evidence"
    }
  ]
}
```

## Claim Extraction Helper

The claim extraction helper converts user-provided claim-like items into
structured `Claim` objects before verification.

```text
$ python examples/claim_extraction/demo.py
extracted_claims=1
skipped_items=1
guard_status=blocked
claim_status=tool_required
safe_verdict=insufficient_evidence
```

Extraction is not verification. The helper does not call an LLM and does not
decide whether claims are true.

Invalid claim-like items are collected in `skipped_items` with corresponding
`warnings`, so users can inspect extraction failures without stopping an entire
batch.

## RAGFlow-Style Evidence Mapping

The RAGFlow-style evidence mapping example maps retrieved chunks into
AgentClaimGuard `Evidence` records before verification.

```text
$ python examples/ragflow_evidence/demo.py
retrieved_chunks=2
mapped_evidence=2
first_locator=finance_report_2026_q1#chunk_1
guard_status=blocked
claim_status=tool_required
safe_verdict=insufficient_evidence
```

This is a mapping example, not a RAGFlow adapter or plugin. Retrieval, ranking,
and answer generation stay in the RAG system; AgentClaimGuard verifies
structured claims against evidence, tool results, and policy.
