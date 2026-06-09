# RAGFlow-Style Evidence Mapping Example

This example shows how to map RAGFlow-style retrieved chunks into
AgentClaimGuard `Evidence` records.

It is not a RAGFlow adapter or plugin and does not perform retrieval, vector
search, ranking, or answer generation. It only demonstrates the evidence
mapping boundary:

```text
RAGFlow / RAG system retrieves chunks
        -> map chunks to Evidence
        -> AgentClaimGuard.verify(...)
```

## What It Demonstrates

- retrieved chunks become structured `Evidence`
- chunk IDs and document IDs are preserved in `locator` and `metadata`
- source text is kept in `content`
- AgentClaimGuard still blocks a numeric claim without a calculator tool result

## Run

From a local clone:

```bash
python examples/ragflow_evidence/demo.py
```

Expected high-level result:

```text
retrieved_chunks=2
mapped_evidence=2
first_locator=finance_report_2026_q1#chunk_1
guard_status=blocked
claim_status=tool_required
safe_verdict=insufficient_evidence
```

## Mapping Pattern

The example maps a retrieved chunk like this:

```json
{
  "id": "chunk_1",
  "document_id": "finance_report_2026_q1",
  "document_name": "Finance Report 2026 Q1",
  "content": "Revenue was 115 million USD in Q1 2026.",
  "score": 0.91,
  "page": 4
}
```

Into an AgentClaimGuard evidence record:

```json
{
  "id": "ev_chunk_1",
  "type": "source_fact",
  "source": "Finance Report 2026 Q1",
  "locator": "finance_report_2026_q1#chunk_1",
  "content": "Revenue was 115 million USD in Q1 2026.",
  "metadata": {
    "provider": "ragflow",
    "chunk_id": "chunk_1",
    "document_id": "finance_report_2026_q1",
    "score": 0.91,
    "page": 4
  }
}
```

## Boundary

RAGFlow or another RAG system is responsible for retrieval.

AgentClaimGuard is responsible for checking whether claims are allowed to be
returned under the active evidence, tool-result, and policy constraints.
