from typing import ClassVar

from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime


class _FakeStatusCode:
    ERROR = "error"


class _FakeSpanKind:
    SERVER = "server"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class _FakeStatus:
    def __init__(self, code, description):
        self.code = code
        self.description = description


class _FakePropagate:
    def __init__(self):
        self.injected_carriers = []
        self.extracted_carriers = []

    def inject(self, carrier):
        carrier["traceparent"] = "fake-trace"
        self.injected_carriers.append(carrier)

    def extract(self, carrier):
        self.extracted_carriers.append(carrier)
        return {"carrier": carrier}


class _FakeProvider:
    def __init__(self):
        self.calls: list[str] = []

    def force_flush(self):
        self.calls.append("force_flush")

    def shutdown(self):
        self.calls.append("shutdown")


class _FakeResource:
    created_with: ClassVar[list] = []

    @classmethod
    def create(cls, attributes):
        cls.created_with.append(attributes)
        return {"resource": attributes}


class _FakeSpanExporter:
    endpoints: ClassVar[list] = []

    def __init__(self, *, endpoint):
        self.endpoints.append(endpoint)


class _FakeMetricExporter:
    endpoints: ClassVar[list] = []

    def __init__(self, *, endpoint):
        self.endpoints.append(endpoint)


class _FakeSpanProcessor:
    def __init__(self, exporter):
        self.exporter = exporter


class _FakeMetricReader:
    def __init__(self, exporter):
        self.exporter = exporter


class _FakeTracerProvider(_FakeProvider):
    def __init__(self, *, resource):
        super().__init__()
        self.resource = resource
        self.processors = []
        self.tracers = []

    def add_span_processor(self, processor):
        self.processors.append(processor)

    def get_tracer(self, name):
        tracer = _FakeTracer(name)
        self.tracers.append(tracer)
        return tracer


class _FakeMeterProvider(_FakeProvider):
    instances: ClassVar[list] = []

    def __init__(self, *, resource, metric_readers):
        super().__init__()
        self.resource = resource
        self.metric_readers = metric_readers
        self.meters = []
        self.instances.append(self)

    def get_meter(self, name):
        meter = _FakeMeter(name)
        self.meters.append(meter)
        return meter


class _FakeMeter:
    def __init__(self, name):
        self.name = name
        self.histograms = {}
        self.counters = {}

    def create_histogram(self, name, description):
        histogram = _FakeHistogram()
        histogram.description = description
        self.histograms[name] = histogram
        return histogram

    def create_counter(self, name, description):
        counter = _FakeCounter()
        counter.description = description
        self.counters[name] = counter
        return counter


class _FakeTracer:
    def __init__(self, name):
        self.name = name
        self.started_spans = []

    def start_as_current_span(self, name, context, kind):
        started = _FakeStartedSpan(name=name, context=context, kind=kind)
        self.started_spans.append(started)
        return started


class _FakeStartedSpan:
    def __init__(self, *, name, context, kind):
        self.name = name
        self.context = context
        self.kind = kind
        self.span = _FakeSpan()

    def __enter__(self):
        return self.span

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeSpan:
    def __init__(self):
        self.attributes = {}
        self.exceptions = []
        self.status = None

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def record_exception(self, exception):
        self.exceptions.append(exception)

    def set_status(self, status):
        self.status = status


class _FakeCounter:
    def __init__(self):
        self.calls = []

    def add(self, value, attributes):
        self.calls.append((value, attributes))


class _FakeHistogram:
    def __init__(self):
        self.calls = []

    def record(self, value, attributes):
        self.calls.append((value, attributes))


def test_runtime_stays_disabled_when_otel_imports_are_unavailable(monkeypatch):
    def fail_import(name, *args, **kwargs):
        if name == "opentelemetry":
            raise ImportError("missing otel")
        return original_import(name, *args, **kwargs)

    original_import = __import__
    monkeypatch.setattr("builtins.__import__", fail_import)

    runtime = OpenTelemetryRuntime(
        enabled=True,
        service_name="test-service",
        queue_backend="redis",
        otlp_endpoint="http://otel-collector:4318",
    )

    assert runtime.enabled is False


def test_runtime_wires_enabled_otel_providers_and_records_runtime_metrics(monkeypatch):
    fake_propagate = _FakePropagate()
    monkeypatch.setattr("opentelemetry.propagate.inject", fake_propagate.inject)
    monkeypatch.setattr("opentelemetry.propagate.extract", fake_propagate.extract)
    monkeypatch.setattr("opentelemetry.exporter.otlp.proto.http.metric_exporter.OTLPMetricExporter", _FakeMetricExporter)
    monkeypatch.setattr("opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter", _FakeSpanExporter)
    monkeypatch.setattr("opentelemetry.sdk.metrics.MeterProvider", _FakeMeterProvider)
    monkeypatch.setattr("opentelemetry.sdk.metrics.export.PeriodicExportingMetricReader", _FakeMetricReader)
    monkeypatch.setattr("opentelemetry.sdk.resources.Resource", _FakeResource)
    monkeypatch.setattr("opentelemetry.sdk.trace.TracerProvider", _FakeTracerProvider)
    monkeypatch.setattr("opentelemetry.sdk.trace.export.BatchSpanProcessor", _FakeSpanProcessor)
    monkeypatch.setattr("opentelemetry.trace.SpanKind", _FakeSpanKind)
    monkeypatch.setattr("opentelemetry.trace.Status", _FakeStatus)
    monkeypatch.setattr("opentelemetry.trace.StatusCode", _FakeStatusCode)

    runtime = OpenTelemetryRuntime(
        enabled=True,
        service_name="test-service",
        queue_backend="redis",
        otlp_endpoint="http://otel-collector:4318/",
    )

    assert runtime.enabled is True
    assert runtime.inject_current_context() == {"traceparent": "fake-trace"}

    with runtime.start_http_span(
        "http.request",
        headers={"traceparent": "incoming"},
        attributes={"guild_id": "123", "ignored": None},
    ) as span:
        span.set_attribute("result_code", "ok")

    runtime.record_queue_depth(guild_id=123, depth=4)
    runtime.record_queue_age(guild_id=None, age_seconds=-2)
    runtime.record_queue_item_processed(
        guild_id=123,
        engine="gtts",
        result_code="ok",
        success=True,
        timeout_flag=False,
    )
    runtime.record_lock_loss(guild_id=None, lock_kind="guild_lock")
    runtime.record_tts_submission(
        guild_id=123,
        engine="gtts",
        result_code="queued",
        accepted=True,
    )
    runtime.record_enqueue_to_playback_latency(
        guild_id=None,
        engine="gtts",
        latency_seconds=-1,
    )

    meter = _FakeMeterProvider.instances[-1].meters[-1]
    assert _FakeSpanExporter.endpoints[-1] == "http://otel-collector:4318/v1/traces"
    assert _FakeMetricExporter.endpoints[-1] == "http://otel-collector:4318/v1/metrics"
    assert meter.histograms["bot.queue.depth"].calls == [
        (4, {"guild_id": "123", "queue_backend": "redis"})
    ]
    assert meter.histograms["bot.queue.age.seconds"].calls == [
        (0.0, {"guild_id": "unknown", "queue_backend": "redis"})
    ]
    assert meter.counters["bot.queue.items.processed"].calls == [
        (
            1,
            {
                "guild_id": "123",
                "queue_backend": "redis",
                "engine": "gtts",
                "result_code": "ok",
                "success": True,
                "timeout_flag": False,
            },
        )
    ]
    assert meter.counters["bot.queue.lock_loss"].calls == [
        (
            1,
            {
                "guild_id": "unknown",
                "queue_backend": "redis",
                "lock_kind": "guild_lock",
            },
        )
    ]
    assert meter.counters["bot.tts.submissions"].calls[-1][1]["accepted"] is True
    assert meter.histograms["bot.tts.enqueue_to_playback.seconds"].calls == [
        (
            0.0,
            {
                "guild_id": "unknown",
                "queue_backend": "redis",
                "engine": "gtts",
            },
        )
    ]


def test_runtime_marks_enabled_spans_as_errors(monkeypatch):
    fake_propagate = _FakePropagate()
    monkeypatch.setattr("opentelemetry.propagate.inject", fake_propagate.inject)
    monkeypatch.setattr("opentelemetry.propagate.extract", fake_propagate.extract)
    monkeypatch.setattr("opentelemetry.exporter.otlp.proto.http.metric_exporter.OTLPMetricExporter", _FakeMetricExporter)
    monkeypatch.setattr("opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter", _FakeSpanExporter)
    monkeypatch.setattr("opentelemetry.sdk.metrics.MeterProvider", _FakeMeterProvider)
    monkeypatch.setattr("opentelemetry.sdk.metrics.export.PeriodicExportingMetricReader", _FakeMetricReader)
    monkeypatch.setattr("opentelemetry.sdk.resources.Resource", _FakeResource)
    monkeypatch.setattr("opentelemetry.sdk.trace.TracerProvider", _FakeTracerProvider)
    monkeypatch.setattr("opentelemetry.sdk.trace.export.BatchSpanProcessor", _FakeSpanProcessor)
    monkeypatch.setattr("opentelemetry.trace.SpanKind", _FakeSpanKind)
    monkeypatch.setattr("opentelemetry.trace.Status", _FakeStatus)
    monkeypatch.setattr("opentelemetry.trace.StatusCode", _FakeStatusCode)
    runtime = OpenTelemetryRuntime(
        enabled=True,
        service_name="test-service",
        queue_backend="memory",
        otlp_endpoint="http://otel-collector:4318",
    )
    exception = RuntimeError("boom")

    with runtime.start_internal_span("internal") as span:
        runtime.mark_span_error(span, exception)

    assert span.exceptions == [exception]
    assert span.status.code == "error"
    assert span.status.description == "boom"


def test_disabled_runtime_span_contexts_are_noops():
    runtime = OpenTelemetryRuntime(
        enabled=False,
        service_name="test-service",
        queue_backend="memory",
    )

    with runtime.start_http_span("http") as http_span:
        http_span.set_attribute("ignored", "value")
    with runtime.start_consumer_span("consumer") as consumer_span:
        consumer_span.set_attribute("ignored", "value")
    with runtime.start_internal_span("internal") as internal_span:
        internal_span.set_attribute("ignored", "value")

    runtime.mark_span_error(internal_span, RuntimeError("ignored"))
    assert runtime.inject_current_context() is None


def test_shutdown_flushes_meter_and_tracer_providers():
    runtime = OpenTelemetryRuntime(
        enabled=False,
        service_name="test-service",
        queue_backend="redis",
    )
    tracer_provider = _FakeProvider()
    meter_provider = _FakeProvider()
    runtime._enabled = True
    runtime._tracer_provider = tracer_provider
    runtime._meter_provider = meter_provider

    runtime.shutdown()

    assert meter_provider.calls == ["force_flush", "shutdown"]
    assert tracer_provider.calls == ["force_flush", "shutdown"]


def test_runtime_records_tts_submission_and_latency_metrics():
    runtime = OpenTelemetryRuntime(
        enabled=False,
        service_name="test-service",
        queue_backend="redis",
    )
    submission_counter = _FakeCounter()
    latency_histogram = _FakeHistogram()
    runtime._tts_submission_counter = submission_counter
    runtime._enqueue_to_playback_histogram = latency_histogram

    runtime.record_tts_submission(
        guild_id=123,
        engine="gtts",
        result_code="queued",
        accepted=True,
    )
    runtime.record_enqueue_to_playback_latency(
        guild_id=123,
        engine="gtts",
        latency_seconds=-1.5,
    )

    assert submission_counter.calls == [
        (
            1,
            {
                "guild_id": "123",
                "queue_backend": "redis",
                "engine": "gtts",
                "result_code": "queued",
                "accepted": True,
            },
        )
    ]
    assert latency_histogram.calls == [
        (
            0.0,
            {
                "guild_id": "123",
                "queue_backend": "redis",
                "engine": "gtts",
            },
        )
    ]
# pyright: reportAttributeAccessIssue=false
