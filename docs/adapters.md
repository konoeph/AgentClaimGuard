# Adapters

AgentClaimGuard adapters keep the core verifier framework-agnostic while making
it easier to embed claim checks inside existing LLM application workflows.

## Runtime Contract

Every adapter follows the same core runtime contract:

```text
claims + evidence + tool_results + policy -> verify -> status + violations + safe fallback
```

## Platform Integration Patterns

Most AgentClaimGuard integrations fit one of three patterns.

### HTTP Tool Pattern

Use this when a workflow platform can call an HTTP endpoint.

```text
Dify / workflow platform -> POST /v1/verify -> guard decision
```

The platform prepares structured `claims`, `evidence`, and `tool_results`.
AgentClaimGuard receives them through the FastAPI server and returns a
verification result.

Use this pattern for Dify-style tools, no-code workflow builders, and services
that can make JSON HTTP requests.

### Evidence Mapping Pattern

Use this when a RAG system already retrieves context chunks.

```text
RAGFlow / RAG system -> Evidence[] -> AgentClaimGuard.verify(...)
```

The RAG system stays responsible for retrieval and ranking. The integration
maps retrieved chunks into AgentClaimGuard `Evidence` records with stable IDs,
source labels, locators, and retrieval metadata.

Use this pattern for RAGFlow-style systems, custom retrievers, and document
pipelines that already produce source chunks.

### Framework Adapter Pattern

Use this when claims should be verified inside an application framework.

```text
LangGraph node / LangChain Runnable -> guard_result -> route or return
```

The framework adapter reads structured claims, evidence, and tool results from
state or Runnable payloads, runs AgentClaimGuard, then writes the verification
result back for routing, repair, retrieval, or human review.

Use this pattern for LangGraph, LangChain, and other code-first agent
frameworks.

## LangGraph

The LangGraph adapter exposes a verification node and a routing helper:

```python
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from agentclaimguard import Policy
from agentclaimguard.core.result import VerificationResult
from agentclaimguard.adapters.langgraph import (
    create_evidence_guard_node,
    route_by_guard_status,
)


class GuardState(TypedDict, total=False):
    claims: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    guard_result: VerificationResult
    final_answer: str


policy = Policy.load_builtin("generic_numeric")
guard_node = create_evidence_guard_node(policy=policy)

builder = StateGraph(GuardState)
builder.add_node("agent", agent_node)
builder.add_node("guard", guard_node)
builder.add_node("repair", repair_node)
builder.add_node("human_review", human_review_node)

builder.add_edge(START, "agent")
builder.add_edge("agent", "guard")
builder.add_conditional_edges(
    "guard",
    route_by_guard_status,
    {
        "passed": END,
        "blocked": "repair",
        "need_check": "human_review",
        "insufficient_evidence": "human_review",
        "conflicting_evidence": "human_review",
    },
)
builder.add_edge("repair", END)
builder.add_edge("human_review", END)
```

The default state shape is intentionally plain:

```python
{
    "claims": [...],
    "evidence": [...],
    "tool_results": [...],
    "guard_result": None,
    "final_answer": "...",
}
```

`create_evidence_guard_node(...)` reads `claims`, `evidence`, and
`tool_results`, then returns a state update containing `guard_result`.
`route_by_guard_status(...)` maps the guard result to one of:

```text
passed
blocked
need_check
insufficient_evidence
conflicting_evidence
```

The top-level `VerificationResult.status` stays `passed` or `blocked`. The
router inspects the first non-passed claim result so graph branches can still
distinguish `insufficient_evidence`, `conflicting_evidence`, and `need_check`.

If your graph uses a different field name, pass the same custom key to both:

```python
guard_node = create_evidence_guard_node(policy=policy, result_key="verification")
route = route_by_guard_status(state, result_key="verification")
```

Run the minimal demo:

```bash
pip install -e ".[dev,server,langgraph]"
python examples/langgraph_guard/demo.py
```

If `langgraph` is not installed, the demo falls back to direct node invocation
so you can still inspect the adapter behavior outside a graph runtime.

## LangChain

The LangChain adapter currently focuses on a Runnable wrapper that runs
AgentClaimGuard after the wrapped Runnable completes.

```python
from langchain_core.runnables import RunnableLambda

from agentclaimguard import Policy
from agentclaimguard.adapters.langchain import create_guarded_runnable

chain = RunnableLambda(lambda payload: {
    "final_answer": payload["question"],
    "claims": payload["claims"],
    "evidence": payload["evidence"],
    "tool_results": payload["tool_results"],
})

guarded = create_guarded_runnable(
    runnable=chain,
    policy=Policy.load_builtin("generic_numeric"),
)

result = guarded.invoke(input_data)
```

The wrapped Runnable should expose structured `claims`, `evidence`, and
`tool_results` in its output or input payload. By default, the adapter looks for
those field names in the Runnable output first, then in the original input.

When your chain uses different keys, provide a `field_map`:

```python
guarded = create_guarded_runnable(
    runnable=chain,
    policy=policy,
    field_map={
        "claims": "structured_claims",
        "evidence": "supporting_evidence",
        "tool_results": "calculator_runs",
    },
    result_key="verification",
)
```

### LangChain field resolution

For string-based `field_map` entries, AgentClaimGuard resolves fields in this
order:

1. Runnable output
2. Runnable input

This means a chain can return `claims`, `evidence`, and `tool_results` itself,
or pass them through from the original input payload.

For callable extractors, the callable receives both `input` and `output` and
fully controls extraction.

Resolved values must be lists or `None`. Missing values are treated as empty
lists.

Async chains can use the same wrapper API:

```python
result = await guarded.ainvoke(input_data)
```

If the wrapped Runnable returns a mapping, the adapter appends `guard_result`
under the configured `result_key`. If it returns a non-mapping value, the
adapter wraps it into:

```python
{
    "output": original_output,
    "guard_result": verification_result,
}
```

If the wrapped Runnable already returns the configured `result_key`, the adapter
raises `ValueError` by default. Use `overwrite_result=True` only when that
replacement is intentional.

Run the minimal demo:

```bash
pip install -e ".[dev,server,langchain]"
python examples/langchain_guard/demo.py
```

## Dify HTTP Tool

The Dify integration path uses the existing FastAPI server as an HTTP tool.
This keeps the adapter boundary simple: Dify prepares structured claims,
evidence, and tool results, then AgentClaimGuard verifies them.

```text
Dify workflow -> HTTP tool -> POST /v1/verify -> status + claim_results
```

Start the AgentClaimGuard API:

```bash
pip install "agentclaimguard[server]"
uvicorn agentclaimguard.server.main:app --host 0.0.0.0 --port 8000
```

Configure the Dify HTTP tool with:

```text
Method: POST
URL: http://<agentclaimguard-host>:8000/v1/verify
Header: Content-Type: application/json
Body: claims, evidence, and tool_results JSON
```

The example request in `examples/dify_http_tool/request.json` produces a
blocked result because the numeric claim has source evidence but no calculator
tool result.

Route the returned `status` in Dify:

```text
passed  -> return answer
blocked -> repair, retrieve more evidence, or human review
```

This is not a full Dify plugin package. It is a minimal HTTP tool integration
example that reuses the server API.

## RAGFlow-Style Evidence Mapping

The RAGFlow-style evidence mapping example maps retrieved chunks into AgentClaimGuard
`Evidence` records. This keeps retrieval in the RAG system and verification in
AgentClaimGuard:

```text
RAGFlow / RAG system retrieves chunks
        -> map chunks to Evidence
        -> AgentClaimGuard.verify(...)
```

A retrieved chunk can become an evidence record by preserving:

- the chunk text as `content`
- the source document name as `source`
- the document/chunk pointer as `locator`
- retrieval metadata such as chunk ID, document ID, score, and page in
  `metadata`

See `examples/ragflow_evidence/` for a copyable mapping example.

This is not a RAGFlow adapter, plugin, vector search implementation, ranking
layer, or answer-generation layer. It is an evidence mapping example for
workflows that already have retrieved chunks.

## Planned Adapters

- LangChain middleware hook
  - Add a deeper integration path after the Runnable wrapper API settles.
- DSPy module wrapper
  - Expose policy-backed assertions as reusable pipeline checks.
- Dify plugin package
  - Extend the HTTP tool pattern into a packaged integration if there is demand.
- Possible RAGFlow plugin package
  - Future work only. Current support is a RAGFlow-style evidence mapping
    example, not a RAGFlow adapter or plugin.

## Design Goal

Adapters should be thin. The core logic stays in the SDK, and each adapter only
translates its host framework into the shared AgentClaimGuard schema.
