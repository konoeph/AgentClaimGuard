"""Tests for LangChain middleware adapter."""

from unittest.mock import MagicMock, patch

import pytest

from agentclaimguard.adapters.langchain.middleware import (
    ClaimGuardMiddleware,
    ClaimVerificationError,
    create_claim_guard_middleware,
)
from agentclaimguard.core.policy import Policy
from agentclaimguard.core.result import VerificationResult


@pytest.fixture
def policy():
    return Policy(confidence_threshold=0.8)


@pytest.fixture
def sample_input():
    return {
        "claims": [{"text": "The sky is blue", "confidence": 0.9}],
        "evidence": [{"text": "Observation confirms blue sky", "source": "visual"}],
        "tool_results": [],
    }


class TestClaimGuardMiddleware:
    def test_warn_mode_passes_through(self, policy, sample_input):
        """Warn mode should always pass through input unchanged."""
        middleware = ClaimGuardMiddleware(policy=policy, mode="warn")
        result = middleware(sample_input, config={})
        assert result == sample_input
        assert "guard_result" not in result

    def test_attach_mode_adds_result(self, policy, sample_input):
        """Attach mode should add verification result to input."""
        middleware = ClaimGuardMiddleware(policy=policy, mode="attach")
        result = middleware(sample_input, config={})
        assert "guard_result" in result
        assert isinstance(result["guard_result"], VerificationResult)

    def test_block_mode_raises_on_failure(self, policy):
        """Block mode should raise ClaimVerificationError on failed claims."""
        middleware = ClaimGuardMiddleware(policy=policy, mode="block")
        bad_input = {
            "claims": [{"text": "False claim", "confidence": 0.1}],
            "evidence": [],
            "tool_results": [],
        }
        with pytest.raises(ClaimVerificationError):
            middleware(bad_input, config={})

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
