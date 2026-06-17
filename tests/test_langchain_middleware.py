"""Tests for LangChain middleware adapter."""

import pytest

from agentclaimguard.adapters.langchain.middleware import (
    ClaimGuardMiddleware,
    ClaimVerificationError,
    create_claim_guard_middleware,
)
from agentclaimguard.core.policy import Policy
from agentclaimguard.core.result import VerificationResult


@pytest.fixture
def policy() -> Policy:
    return Policy.load_builtin("generic_numeric")


@pytest.fixture
def sample_input() -> dict:
    return _passed_numeric_input()


def _passed_numeric_input() -> dict:
    return {
        "claims": [
            {
                "id": "claim_1",
                "type": "numeric_conclusion",
                "text": "Revenue increased by 15%.",
                "evidence_refs": ["ev_1", "ev_2"],
                "tool_result_refs": ["tool_1"],
            }
        ],
        "evidence": [
            {
                "id": "ev_1",
                "type": "source_fact",
                "content": "Revenue was 115.",
            },
            {
                "id": "ev_2",
                "type": "source_fact",
                "content": "Revenue was 100.",
            },
        ],
        "tool_results": [
            {
                "id": "tool_1",
                "tool_name": "calculator",
                "status": "success",
                "output": {"growth_rate": "15%"},
            }
        ],
    }


def _blocked_numeric_input() -> dict:
    return {
        "claims": [
            {
                "id": "claim_1",
                "type": "numeric_conclusion",
                "text": "Revenue increased by 15%.",
                "evidence_refs": ["ev_1", "ev_2"],
                "tool_result_refs": [],
            }
        ],
        "evidence": [
            {
                "id": "ev_1",
                "type": "source_fact",
                "content": "Revenue was 115.",
            },
            {
                "id": "ev_2",
                "type": "source_fact",
                "content": "Revenue was 100.",
            },
        ],
        "tool_results": [],
    }


class TestClaimGuardMiddleware:
    def test_warn_mode_passes_through(self, policy, sample_input):
        """Warn mode should always pass through input unchanged."""
        middleware = ClaimGuardMiddleware(policy=policy, mode="warn")
        result = middleware(sample_input, config={})
        assert result is sample_input
        assert "guard_result" not in result

    def test_warn_mode_logs_failed_claim(self, policy, caplog):
        """Warn mode should log blocked structured claims without raising."""
        middleware = ClaimGuardMiddleware(policy=policy, mode="warn")
        blocked_input = _blocked_numeric_input()

        result = middleware(blocked_input, config={})

        assert result is blocked_input
        assert "ClaimGuard: 1/1 claims failed verification" in caplog.text

    def test_attach_mode_adds_result(self, policy, sample_input):
        """Attach mode should add verification result to input."""
        middleware = ClaimGuardMiddleware(policy=policy, mode="attach")
        result = middleware(sample_input, config={})
        assert "guard_result" in result
        assert isinstance(result["guard_result"], VerificationResult)
        assert result["guard_result"].status == "passed"

    def test_block_mode_raises_on_failure(self, policy):
        """Block mode should raise ClaimVerificationError on failed claims."""
        middleware = ClaimGuardMiddleware(policy=policy, mode="block")
        with pytest.raises(ClaimVerificationError) as exc_info:
            middleware(_blocked_numeric_input(), config={})

        assert exc_info.value.result.status == "blocked"
        assert exc_info.value.result.claim_results[0].status == "tool_required"

    def test_no_claims_passes_through(self, policy):
        """Input without claims should pass through unchanged."""
        middleware = ClaimGuardMiddleware(policy=policy, mode="block")
        no_claims = {"messages": ["hello"]}
        result = middleware(no_claims, config={})
        assert result == no_claims

    def test_invalid_mode_raises(self, policy):
        """Invalid mode should raise ValueError."""
        with pytest.raises(ValueError, match="mode must be"):
            ClaimGuardMiddleware(policy=policy, mode="invalid")

    def test_custom_result_key(self, policy, sample_input):
        """Custom result_key should be used."""
        middleware = ClaimGuardMiddleware(
            policy=policy, mode="attach", result_key="verification"
        )
        result = middleware(sample_input, config={})
        assert "verification" in result
        assert result["verification"].status == "passed"
        assert "guard_result" not in result


class TestCreateClaimGuardMiddleware:
    def test_create_middleware(self, policy):
        """Factory function should create middleware correctly."""
        middleware = create_claim_guard_middleware(
            policy=policy, mode="attach", result_key="test"
        )
        assert isinstance(middleware, ClaimGuardMiddleware)
        assert middleware.mode == "attach"
        assert middleware.result_key == "test"
