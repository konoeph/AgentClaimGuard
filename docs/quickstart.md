# Quickstart

Install AgentClaimGuard in editable mode while developing:

```bash
pip install -e ".[dev,server]"
```

Run a demo:

```bash
python examples/numeric_conclusion/demo.py
```

Start the OpenAPI server:

```bash
uvicorn agentclaimguard.server.main:app --reload
```

Submit a verification request:

```bash
curl -X POST http://127.0.0.1:8000/v1/verify \
  -H "Content-Type: application/json" \
  -d @examples/numeric_conclusion/sample_blocked.json
```

See [examples.md](examples.md) for expected outputs from the bundled demos.

Run the LangGraph adapter demo:

```bash
pip install -e ".[dev,server,langgraph]"
python examples/langgraph_guard/demo.py
```

See [../examples/langgraph_guard/README.md](../examples/langgraph_guard/README.md)
for the state shape, routing behavior, and expected output.

Run the LangChain adapter demo:

```bash
pip install -e ".[dev,server,langchain]"
python examples/langchain_guard/demo.py
```
