from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime


class _FakeProvider:
    def __init__(self):
        self.calls: list[str] = []

    def force_flush(self):
        self.calls.append("force_flush")

    def shutdown(self):
        self.calls.append("shutdown")


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
