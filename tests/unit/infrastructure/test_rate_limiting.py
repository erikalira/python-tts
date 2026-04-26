"""Tests for in-memory rate limiting adapter."""

from src.application.rate_limiting import RATE_LIMIT_REASON_TOO_MANY_REQUESTS, RateLimitRequest
from src.infrastructure.rate_limiting import InMemoryRateLimiter


def test_in_memory_rate_limiter_allows_requests_under_limit():
    now = 100.0
    limiter = InMemoryRateLimiter(clock=lambda: now)

    first = limiter.check(RateLimitRequest(scope="discord:speak:guild:1:user:2", limit=2, window_seconds=10))
    second = limiter.check(RateLimitRequest(scope="discord:speak:guild:1:user:2", limit=2, window_seconds=10))

    assert first.allowed is True
    assert second.allowed is True


def test_in_memory_rate_limiter_blocks_requests_over_limit():
    now = 100.0
    limiter = InMemoryRateLimiter(clock=lambda: now)
    request = RateLimitRequest(scope="discord:speak:guild:1:user:2", limit=1, window_seconds=10)

    limiter.check(request)
    result = limiter.check(request)

    assert result.allowed is False
    assert result.reason == RATE_LIMIT_REASON_TOO_MANY_REQUESTS
    assert result.retry_after_seconds == 10


def test_in_memory_rate_limiter_isolates_scopes():
    now = 100.0
    limiter = InMemoryRateLimiter(clock=lambda: now)

    limiter.check(RateLimitRequest(scope="discord:speak:guild:1:user:2", limit=1, window_seconds=10))
    result = limiter.check(RateLimitRequest(scope="discord:speak:guild:1:user:3", limit=1, window_seconds=10))

    assert result.allowed is True


def test_in_memory_rate_limiter_reopens_scope_after_window():
    current_time = 100.0

    def clock() -> float:
        return current_time

    limiter = InMemoryRateLimiter(clock=clock)
    request = RateLimitRequest(scope="http:speak:guild:1:member:2", limit=1, window_seconds=10)

    limiter.check(request)
    current_time = 111.0
    result = limiter.check(request)

    assert result.allowed is True

