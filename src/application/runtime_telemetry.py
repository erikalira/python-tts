"""Shared observability contracts for application and presentation layers."""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Protocol
from collections.abc import Mapping


class RuntimeSpan(Protocol):
    def set_attribute(self, key: str, value: Any) -> None: ...


class RuntimeTelemetry(Protocol):
    def inject_current_context(self) -> dict[str, str] | None: ...

    def start_http_span(
        self,
        name: str,
        *,
        headers: Mapping[str, str] | None = None,
        attributes: Mapping[str, Any] | None = None,
    ) -> AbstractContextManager[RuntimeSpan]: ...

    def start_consumer_span(
        self,
        name: str,
        *,
        carrier: Mapping[str, str] | None = None,
        attributes: Mapping[str, Any] | None = None,
    ) -> AbstractContextManager[RuntimeSpan]: ...

    def start_internal_span(
        self,
        name: str,
        *,
        attributes: Mapping[str, Any] | None = None,
    ) -> AbstractContextManager[RuntimeSpan]: ...

    def mark_span_error(self, span: object, exception: BaseException) -> None: ...

    def record_queue_depth(self, *, guild_id: int | None, depth: int) -> None: ...

    def record_queue_age(self, *, guild_id: int | None, age_seconds: float) -> None: ...

    def record_queue_item_processed(
        self,
        *,
        guild_id: int | None,
        engine: str,
        result_code: str,
        success: bool,
        timeout_flag: bool,
    ) -> None: ...

    def record_lock_loss(self, *, guild_id: int | None, lock_kind: str) -> None: ...

    def record_tts_submission(
        self,
        *,
        guild_id: int | None,
        engine: str,
        result_code: str,
        accepted: bool,
    ) -> None: ...

    def record_enqueue_to_playback_latency(
        self,
        *,
        guild_id: int | None,
        engine: str,
        latency_seconds: float,
    ) -> None: ...


class NullRuntimeSpan:
    def set_attribute(self, key: str, value: Any) -> None:
        del key, value


class NullRuntimeSpanContext(AbstractContextManager[RuntimeSpan]):
    def __enter__(self) -> RuntimeSpan:
        return NullRuntimeSpan()

    def __exit__(self, exc_type, exc, tb) -> bool:
        del exc_type, exc, tb
        return False
