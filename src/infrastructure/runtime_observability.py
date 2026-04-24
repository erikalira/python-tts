"""In-memory operational metrics for the Discord bot runtime."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict
from threading import Lock

from src.application.dto import (
    BotRuntimeErrorRateDTO,
    BotRuntimeObservabilityDTO,
)
from src.core.entities import AudioQueueItem, TTSRequest


class InMemoryBotRuntimeTelemetry:
    """Track a compact rolling baseline of bot runtime metrics."""

    def __init__(self, latency_window_size: int = 500):
        self._lock = Lock()
        self._latency_ms = deque(maxlen=latency_window_size)
        self._total_requests = 0
        self._successful_playbacks = 0
        self._failed_requests = 0
        self._total_by_guild: dict[str, int] = defaultdict(int)
        self._failed_by_guild: dict[str, int] = defaultdict(int)
        self._total_by_engine: dict[str, int] = defaultdict(int)
        self._failed_by_engine: dict[str, int] = defaultdict(int)

    def record_submission_result(
        self,
        *,
        request: TTSRequest,
        accepted: bool,
        code: str,
        engine: str,
    ) -> None:
        del code
        guild_key = self._guild_key(request.guild_id)
        with self._lock:
            self._total_requests += 1
            self._total_by_guild[guild_key] += 1
            self._total_by_engine[engine] += 1
            if not accepted:
                self._failed_requests += 1
                self._failed_by_guild[guild_key] += 1
                self._failed_by_engine[engine] += 1

    def record_processing_result(
        self,
        *,
        item: AudioQueueItem,
        success: bool,
        code: str,
        engine: str,
    ) -> None:
        del code
        guild_key = self._guild_key(item.request.guild_id)
        with self._lock:
            if success:
                self._successful_playbacks += 1
                if item.completed_at is not None:
                    self._latency_ms.append(round((item.completed_at - item.created_at) * 1000, 2))
                return

            self._failed_requests += 1
            self._failed_by_guild[guild_key] += 1
            self._failed_by_engine[engine] += 1

    def snapshot(self) -> BotRuntimeObservabilityDTO:
        with self._lock:
            return BotRuntimeObservabilityDTO(
                status="enabled",
                total_requests=self._total_requests,
                successful_playbacks=self._successful_playbacks,
                failed_requests=self._failed_requests,
                error_rate=self._rate(self._failed_requests, self._total_requests),
                enqueue_to_playback_sample_count=len(self._latency_ms),
                enqueue_to_playback_p95_ms=self._percentile(self._latency_ms, 0.95),
                enqueue_to_playback_p99_ms=self._percentile(self._latency_ms, 0.99),
                error_rate_by_guild=self._build_breakdown(self._total_by_guild, self._failed_by_guild),
                error_rate_by_engine=self._build_breakdown(self._total_by_engine, self._failed_by_engine),
            )

    def snapshot_payload(self) -> dict[str, object]:
        return asdict(self.snapshot())

    def _build_breakdown(
        self,
        total_map: dict[str, int],
        failed_map: dict[str, int],
    ) -> list[BotRuntimeErrorRateDTO]:
        buckets = []
        for key in sorted(total_map):
            total_requests = total_map[key]
            failed_requests = failed_map.get(key, 0)
            buckets.append(
                BotRuntimeErrorRateDTO(
                    key=key,
                    total_requests=total_requests,
                    failed_requests=failed_requests,
                    error_rate=self._rate(failed_requests, total_requests),
                )
            )
        return buckets

    def _guild_key(self, guild_id: int | None) -> str:
        return str(guild_id) if guild_id is not None else "unknown"

    def _rate(self, failed_requests: int, total_requests: int) -> float:
        if total_requests <= 0:
            return 0.0
        return round(failed_requests / total_requests, 4)

    def _percentile(self, values: deque[float], percentile: float) -> float | None:
        if not values:
            return None
        sorted_values = sorted(values)
        index = int(round((len(sorted_values) - 1) * percentile))
        return sorted_values[index]
