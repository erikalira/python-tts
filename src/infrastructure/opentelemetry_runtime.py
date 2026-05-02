"""Optional OpenTelemetry tracing and metrics for the bot runtime."""

from __future__ import annotations

from contextlib import contextmanager
import logging
from typing import Any
from collections.abc import Mapping

logger = logging.getLogger(__name__)


class _NullSpan:
    def set_attribute(self, key: str, value: Any) -> None:
        del key, value

    def record_exception(self, exception: BaseException) -> None:
        del exception

    def set_status(self, status: object) -> None:
        del status


class OpenTelemetryRuntime:
    """Provide tracing and metrics with a safe no-op fallback."""

    def __init__(
        self,
        *,
        enabled: bool,
        service_name: str,
        queue_backend: str,
        otlp_endpoint: str | None = None,
    ) -> None:
        self._enabled = False
        self._queue_backend = queue_backend
        self._status_factory: Any | None = None
        self._status_code_error: Any | None = None
        self._span_kind: Any | None = None
        self._propagate: Any | None = None
        self._tracer: Any | None = None
        self._tracer_provider: Any | None = None
        self._meter_provider: Any | None = None
        self._queue_depth_histogram: Any | None = None
        self._queue_age_histogram: Any | None = None
        self._queue_item_counter: Any | None = None
        self._queue_lock_loss_counter: Any | None = None
        self._tts_submission_counter: Any | None = None
        self._enqueue_to_playback_histogram: Any | None = None
        if not enabled or not otlp_endpoint:
            return

        try:
            from opentelemetry import propagate
            from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.trace import SpanKind, Status, StatusCode
        except ImportError:
            return

        resource = Resource.create({"service.name": service_name})
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/traces"))
        )
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[
                PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/metrics")
                )
            ],
        )
        meter = meter_provider.get_meter("tts-hotkey-windows.bot-runtime")

        self._enabled = True
        self._status_factory = Status
        self._status_code_error = StatusCode.ERROR
        self._span_kind = SpanKind
        self._propagate = propagate
        self._tracer_provider = tracer_provider
        self._meter_provider = meter_provider
        self._tracer = tracer_provider.get_tracer("tts-hotkey-windows.bot-runtime")
        self._queue_depth_histogram = meter.create_histogram(
            "bot.queue.depth",
            description="Current queue depth sampled by guild",
        )
        self._queue_age_histogram = meter.create_histogram(
            "bot.queue.age.seconds",
            description="Current queue age sampled by guild",
        )
        self._queue_item_counter = meter.create_counter(
            "bot.queue.items.processed",
            description="Queued items processed with outcome attributes",
        )
        self._queue_lock_loss_counter = meter.create_counter(
            "bot.queue.lock_loss",
            description="Guild lock or processing lease loss events in the worker",
        )
        self._tts_submission_counter = meter.create_counter(
            "bot.tts.submissions",
            description="TTS requests submitted to the bot with acceptance and result attributes",
        )
        self._enqueue_to_playback_histogram = meter.create_histogram(
            "bot.tts.enqueue_to_playback.seconds",
            description="Elapsed time from queue enqueue to successful playback completion",
        )

    @property
    def enabled(self) -> bool:
        return self._enabled

    def inject_current_context(self) -> dict[str, str] | None:
        if not self._enabled or self._propagate is None:
            return None
        carrier: dict[str, str] = {}
        self._propagate.inject(carrier)
        return carrier or None

    @contextmanager
    def start_http_span(
        self,
        name: str,
        *,
        headers: Mapping[str, str] | None = None,
        attributes: Mapping[str, Any] | None = None,
    ):
        with self._start_span(
            name,
            carrier=headers,
            kind=self._span_kind.SERVER if self._span_kind is not None else None,
            attributes=attributes,
        ) as span:
            yield span

    @contextmanager
    def start_consumer_span(
        self,
        name: str,
        *,
        carrier: Mapping[str, str] | None = None,
        attributes: Mapping[str, Any] | None = None,
    ):
        with self._start_span(
            name,
            carrier=carrier,
            kind=self._span_kind.CONSUMER if self._span_kind is not None else None,
            attributes=attributes,
        ) as span:
            yield span

    @contextmanager
    def start_internal_span(
        self,
        name: str,
        *,
        attributes: Mapping[str, Any] | None = None,
    ):
        with self._start_span(
            name,
            carrier=None,
            kind=self._span_kind.INTERNAL if self._span_kind is not None else None,
            attributes=attributes,
        ) as span:
            yield span

    def mark_span_error(self, span: Any, exception: BaseException) -> None:
        if not self._enabled or self._status_factory is None or self._status_code_error is None:
            return
        span.record_exception(exception)
        span.set_status(self._status_factory(self._status_code_error, str(exception)))

    def record_queue_depth(self, *, guild_id: int | None, depth: int) -> None:
        if self._queue_depth_histogram is None:
            return
        self._queue_depth_histogram.record(
            depth,
            attributes=self._base_attrs(guild_id=guild_id),
        )

    def record_queue_age(self, *, guild_id: int | None, age_seconds: float) -> None:
        if self._queue_age_histogram is None:
            return
        self._queue_age_histogram.record(
            max(age_seconds, 0.0),
            attributes=self._base_attrs(guild_id=guild_id),
        )

    def record_queue_item_processed(
        self,
        *,
        guild_id: int | None,
        engine: str,
        result_code: str,
        success: bool,
        timeout_flag: bool,
    ) -> None:
        if self._queue_item_counter is None:
            return
        attributes = self._base_attrs(guild_id=guild_id)
        attributes.update(
            {
                "engine": engine,
                "result_code": result_code,
                "success": success,
                "timeout_flag": timeout_flag,
            }
        )
        self._queue_item_counter.add(1, attributes=attributes)

    def record_lock_loss(self, *, guild_id: int | None, lock_kind: str) -> None:
        if self._queue_lock_loss_counter is None:
            return
        attributes = self._base_attrs(guild_id=guild_id)
        attributes["lock_kind"] = lock_kind
        self._queue_lock_loss_counter.add(1, attributes=attributes)

    def record_tts_submission(
        self,
        *,
        guild_id: int | None,
        engine: str,
        result_code: str,
        accepted: bool,
    ) -> None:
        if self._tts_submission_counter is None:
            return
        attributes = self._base_attrs(guild_id=guild_id)
        attributes.update(
            {
                "engine": engine,
                "result_code": result_code,
                "accepted": accepted,
            }
        )
        self._tts_submission_counter.add(1, attributes=attributes)

    def record_enqueue_to_playback_latency(
        self,
        *,
        guild_id: int | None,
        engine: str,
        latency_seconds: float,
    ) -> None:
        if self._enqueue_to_playback_histogram is None:
            return
        attributes = self._base_attrs(guild_id=guild_id)
        attributes["engine"] = engine
        self._enqueue_to_playback_histogram.record(max(latency_seconds, 0.0), attributes=attributes)

    def shutdown(self) -> None:
        if not self._enabled:
            return

        if self._meter_provider is not None:
            force_flush = getattr(self._meter_provider, "force_flush", None)
            if callable(force_flush):
                force_flush()
            shutdown = getattr(self._meter_provider, "shutdown", None)
            if callable(shutdown):
                shutdown()

        if self._tracer_provider is not None:
            force_flush = getattr(self._tracer_provider, "force_flush", None)
            if callable(force_flush):
                force_flush()
            shutdown = getattr(self._tracer_provider, "shutdown", None)
            if callable(shutdown):
                shutdown()

        logger.info("[OTEL] Tracer and meter providers flushed and shut down")

    @contextmanager
    def _start_span(
        self,
        name: str,
        *,
        carrier: Mapping[str, str] | None,
        kind: Any | None,
        attributes: Mapping[str, Any] | None,
    ):
        if not self._enabled or self._tracer is None or self._propagate is None:
            yield _NullSpan()
            return

        parent_context = None if carrier is None else self._propagate.extract(carrier=carrier)
        with self._tracer.start_as_current_span(name, context=parent_context, kind=kind) as span:
            if attributes:
                for key, value in attributes.items():
                    if value is not None:
                        span.set_attribute(key, value)
            yield span

    def _base_attrs(self, *, guild_id: int | None) -> dict[str, Any]:
        return {
            "guild_id": str(guild_id) if guild_id is not None else "unknown",
            "queue_backend": self._queue_backend,
        }
