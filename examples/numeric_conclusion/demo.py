import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentclaimguard import AgentClaimGuard, Policy  # noqa: E402


def print_summary(name: str, result: Any) -> None:
    claim_result = result.claim_results[0]
    print(f"{name}_status={result.status}")
    print(f"{name}_claim_status={claim_result.status}")
    print(f"{name}_violations={len(claim_result.violations)}")
    print(f"{name}_safe_output={result.safe_output}")


def main() -> None:
    here = Path(__file__).resolve().parent
    policy = Policy.load(here / "policy.yaml")
    blocked_sample = json.loads(
        (here / "sample_blocked.json").read_text(encoding="utf-8")
    )
    passed_sample = json.loads(
        (here / "sample_passed.json").read_text(encoding="utf-8")
    )

    guard = AgentClaimGuard(policy)
    print_summary("blocked", guard.verify(**blocked_sample))
    print_summary("passed", guard.verify(**passed_sample))


if __name__ == "__main__":
    main()
