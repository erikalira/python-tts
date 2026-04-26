"""In-memory rate limiting adapter for runtime entrypoints."""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable

from src.application.rate_limiting import (
    RATE_LIMIT_REASON_TOO_MANY_REQUESTS,
    RateLimiter,
    RateLimitRequest,
    RateLimitResult,
)


class InMemoryRateLimiter(RateLimiter):
    """Sliding-window in-memory rate limiter.

    This adapter is intentionally process-local. It protects a single bot
    runtime without adding Redis coupling to the shared application contract.
    """

    def __init__(self, clock: Callable[[], float] | None = None):
        self._clock = clock or time.monotonic
        self._hits_by_scope: dict[str, deque[float]] = {}

    def check(self, request: RateLimitRequest) -> RateLimitResult:
        if request.limit <= 0 or request.window_seconds <= 0:
            return RateLimitResult(allowed=True, scope=request.scope)

        now = self._clock()
        window_started_at = now - request.window_seconds
        self._prune_expired_scopes(window_started_at)
        hits = self._hits_by_scope.setdefault(request.scope, deque())

        if len(hits) >= request.limit:
            retry_after = max(hits[0] + request.window_seconds - now, 0.0)
            return RateLimitResult(
                allowed=False,
                scope=request.scope,
                reason=RATE_LIMIT_REASON_TOO_MANY_REQUESTS,
                retry_after_seconds=retry_after,
            )

        hits.append(now)
        return RateLimitResult(allowed=True, scope=request.scope)

    def _prune_expired_scopes(self, window_started_at: float) -> None:
        for scope, hits in list(self._hits_by_scope.items()):
            while hits and hits[0] <= window_started_at:
                hits.popleft()

            if not hits:
                del self._hits_by_scope[scope]
