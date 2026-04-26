from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime


class _FakeProvider:
    def __init__(self):
        self.calls: list[str] = []

    def force_flush(self):
        self.calls.append("force_flush")

    def shutdown(self):
        self.calls.append("shutdown")


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
