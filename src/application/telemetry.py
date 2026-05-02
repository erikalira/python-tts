"""Application-facing runtime telemetry contracts."""

from __future__ import annotations

from typing import Protocol

from src.application.dto import BotRuntimeObservabilityDTO
from src.core.entities import AudioQueueItem, TTSRequest


class BotRuntimeTelemetry(Protocol):
    """Application-facing contract for bot runtime observability."""

    def record_submission_result(
        self,
        *,
        request: TTSRequest,
        accepted: bool,
        code: str,
        engine: str,
    ) -> None:
        """Record the outcome of a speak request submission."""
        ...

    def record_processing_result(
        self,
        *,
        item: AudioQueueItem,
        success: bool,
        code: str,
        engine: str,
    ) -> None:
        """Record the outcome of queued playback processing."""
        ...

    def snapshot(self) -> BotRuntimeObservabilityDTO:
        """Return the current operational snapshot."""
        ...


class NoOpBotRuntimeTelemetry:
    """Safe default telemetry implementation for tests and opt-out runtimes."""

    def record_submission_result(
        self,
        *,
        request: TTSRequest,
        accepted: bool,
        code: str,
        engine: str,
    ) -> None:
        del request, accepted, code, engine

    def record_processing_result(
        self,
        *,
        item: AudioQueueItem,
        success: bool,
        code: str,
        engine: str,
    ) -> None:
        del item, success, code, engine

    def snapshot(self) -> BotRuntimeObservabilityDTO:
        return BotRuntimeObservabilityDTO(
            status="disabled",
            total_requests=0,
            successful_playbacks=0,
            failed_requests=0,
            error_rate=0.0,
            enqueue_to_playback_sample_count=0,
            enqueue_to_playback_p95_ms=None,
            enqueue_to_playback_p99_ms=None,
            error_rate_by_guild=[],
            error_rate_by_engine=[],
        )
