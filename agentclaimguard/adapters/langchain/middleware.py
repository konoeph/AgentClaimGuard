"""LangChain middleware adapter for AgentClaimGuard.

Provides a middleware that can be inserted into LangChain agent flows
to automatically verify claims against evidence after each LLM call.

Usage::

    from agentclaimguard.adapters.langchain.middleware import ClaimGuardMiddleware
    from agentclaimguard.core.policy import Policy

    policy = Policy(confidence_threshold=0.8)
    middleware = ClaimGuardMiddleware(policy=policy)

    # Insert into agent flow
    agent = create_agent(..., middleware=[middleware])
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from agentclaimguard.core.policy import Policy
from agentclaimguard.core.result import VerificationResult
from agentclaimguard.core.runtime import AgentClaimGuard

logger = logging.getLogger(__name__)


class ClaimGuardMiddleware:
    """Middleware that verifies agent claims against evidence.

    Intercepts LLM output and runs AgentClaimGuard verification.
    If claims fail verification, the middleware can:
    - Log warnings (default)
    - Append verification result to the output
    - Block the output and request correction (if configured)

    Args:
        policy: Verification policy
        mode: "warn" (log only), "attach" (add result to output), or "block" (reject unverified)
        result_key: Key to attach verification result in output metadata
        max_retries: Max retries when in "block" mode (0 = no retry)
    """

    def __init__(
        self,
        policy: Policy,
        mode: str = "warn",
        result_key: str = "guard_result",
        max_retries: int = 0,
    ):
        if mode not in ("warn", "attach", "block"):
            raise ValueError(f"mode must be 'warn', 'attach', or 'block', got '{mode}'")
        self.policy = policy
        self.mode = mode
        self.result_key = result_key
        self.max_retries = max_retries
        self._guard = AgentClaimGuard(policy=policy)

    def __call__(self, invoke_input: dict[str, Any], config: RunnableConfig) -> dict[str, Any]:
        """Process input through the middleware."""
        # Extract claims and evidence from input
        claims = self._extract_claims(invoke_input)
        evidence = self._extract_evidence(invoke_input)

        if not claims:
            return invoke_input

        # Verify claims
        result = self._guard.verify(
            claims=claims,
            evidence=evidence,
            tool_results=self._extract_tool_results(invoke_input),
        )

        # Handle result based on mode
        if self.mode == "warn":
            if not result.all_verified:
                logger.warning(
                    "ClaimGuard: %d/%d claims failed verification",
                    len(result.failed_claims),
                    len(result.claims),
                )
        elif self.mode == "attach":
            invoke_input[self.result_key] = result
        elif self.mode == "block":
            if not result.all_verified:
                raise ClaimVerificationError(
                    f"ClaimGuard: {len(result.failed_claims)} claims failed verification",
                    result=result,
                )

        return invoke_input

    def _extract_claims(self, data: dict[str, Any]) -> list[dict]:
        """Extract claims from input data."""
        claims = data.get("claims", [])
        if isinstance(claims, list):
            return claims
        return []

    def _extract_evidence(self, data: dict[str, Any]) -> list[dict]:
        """Extract evidence from input data."""
        evidence = data.get("evidence", [])
        if isinstance(evidence, list):
            return evidence
        return []

    def _extract_tool_results(self, data: dict[str, Any]) -> list[dict]:
        """Extract tool results from input data."""
        tool_results = data.get("tool_results", [])
        if isinstance(tool_results, list):
            return tool_results
        return []


class ClaimVerificationError(Exception):
    """Raised when claim verification fails in 'block' mode."""

    def __init__(self, message: str, result: VerificationResult):
        super().__init__(message)
        self.result = result


def create_claim_guard_middleware(
    policy: Policy,
    mode: str = "warn",
    result_key: str = "guard_result",
    max_retries: int = 0,
) -> ClaimGuardMiddleware:
    """Create a ClaimGuardMiddleware instance.

    Args:
        policy: Verification policy
        mode: "warn", "attach", or "block"
        result_key: Key for verification result in output
        max_retries: Max retries in block mode

    Returns:
        ClaimGuardMiddleware instance
    """
    return ClaimGuardMiddleware(
        policy=policy,
        mode=mode,
        result_key=result_key,
        max_retries=max_retries,
    )
