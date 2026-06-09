from pathlib import Path

from fastapi import FastAPI

from agentclaimguard import AgentClaimGuard, Policy
from agentclaimguard.server.schemas import RepairRequest, VerifyRequest


DEFAULT_POLICY_PATH = (
    Path(__file__).resolve().parents[1] / "policies" / "generic_strict.yaml"
)

app = FastAPI(
    title="AgentClaimGuard",
    version="0.4.3",
    description="A framework-agnostic evidence gate for LLM agent claims.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/verify")
def verify(request: VerifyRequest):
    policy = request.policy or Policy.load(DEFAULT_POLICY_PATH)
    guard = AgentClaimGuard(policy=policy)
    return guard.verify(
        claims=request.claims,
        evidence=request.evidence,
        tool_results=request.tool_results,
    )


@app.post("/v1/repair")
def repair(request: RepairRequest):
    policy = request.policy or Policy.load(DEFAULT_POLICY_PATH)
    guard = AgentClaimGuard(policy=policy)
    return guard.repair(
        claims=request.claims,
        evidence=request.evidence,
        tool_results=request.tool_results,
    )
