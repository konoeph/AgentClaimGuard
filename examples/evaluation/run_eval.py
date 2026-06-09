import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentclaimguard import AgentClaimGuard, Policy  # noqa: E402


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            cases.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc
    return cases


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    policy_name = case["policy"]
    policy = Policy.load_builtin(policy_name)
    result = AgentClaimGuard(policy).verify(
        claims=case["claims"],
        evidence=case.get("evidence", []),
        tool_results=case.get("tool_results", []),
    )

    claim_result = result.claim_results[0]
    violation_types = [violation.type for violation in claim_result.violations]
    expected = case["expected"]

    checks = [
        result.status == expected["status"],
        claim_result.status == expected["claim_status"],
    ]
    expected_violation = expected.get("violation_type")
    if expected_violation is None:
        checks.append(violation_types == [])
    else:
        checks.append(expected_violation in violation_types)

    return {
        "case_id": case["case_id"],
        "ok": all(checks),
        "expected_status": expected["status"],
        "actual_status": result.status,
        "expected_claim_status": expected["claim_status"],
        "actual_claim_status": claim_result.status,
        "expected_violation": expected_violation,
        "actual_violations": violation_types,
    }


def print_table(rows: list[dict[str, Any]]) -> None:
    headers = [
        "case_id",
        "ok",
        "status",
        "claim_status",
        "expected_violation",
        "actual_violations",
    ]
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        print(
            " | ".join(
                [
                    row["case_id"],
                    "yes" if row["ok"] else "no",
                    row["actual_status"],
                    row["actual_claim_status"],
                    str(row["expected_violation"]),
                    ",".join(row["actual_violations"]) or "-",
                ]
            )
        )


def main() -> int:
    cases_path = Path(__file__).resolve().parent / "cases.jsonl"
    cases = load_cases(cases_path)
    rows = [run_case(case) for case in cases]

    print_table(rows)

    total = len(rows)
    failed = [row for row in rows if not row["ok"]]
    status_counts = Counter(row["actual_status"] for row in rows)
    violation_counts = Counter(
        violation
        for row in rows
        for violation in row["actual_violations"]
    )

    print()
    print(f"total_cases={total}")
    print(f"passed_cases={total - len(failed)}")
    print(f"failed_cases={len(failed)}")
    print(f"blocked_count={status_counts.get('blocked', 0)}")
    print(f"passed_count={status_counts.get('passed', 0)}")
    print(
        "violation_categories="
        + json.dumps(dict(sorted(violation_counts.items())), sort_keys=True)
    )

    if failed:
        print()
        print("failed_case_ids=" + ",".join(row["case_id"] for row in failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
