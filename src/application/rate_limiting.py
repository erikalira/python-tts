"""Shared rate limiting contracts for runtime entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


RATE_LIMIT_REASON_TOO_MANY_REQUESTS = "too_many_requests"


@dataclass(frozen=True, slots=True)
class RateLimitRequest:
    """Input used by runtimes to check a caller-specific rate limit."""

    scope: str
    limit: int
    window_seconds: float


@dataclass(frozen=True, slots=True)
class RateLimitResult:
    """Typed result for rate limit decisions."""

    allowed: bool
    scope: str
    reason: str | None = None
    retry_after_seconds: float | None = None


class RateLimiter(Protocol):
    """Contract implemented by runtime-specific rate limit adapters."""

    def check(self, request: RateLimitRequest) -> RateLimitResult: ...

