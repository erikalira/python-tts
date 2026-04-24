from src.core.entities import AudioQueueItem, TTSRequest
from src.infrastructure.runtime_observability import InMemoryBotRuntimeTelemetry


def test_runtime_observability_tracks_percentiles_and_error_rates():
    telemetry = InMemoryBotRuntimeTelemetry()

    request_one = TTSRequest(text="ola", guild_id=1, member_id=10)
    request_two = TTSRequest(text="teste", guild_id=1, member_id=11)
    request_three = TTSRequest(text="falha", guild_id=2, member_id=12)

    telemetry.record_submission_result(
        request=request_one,
        accepted=True,
        code="queued",
        engine="gtts",
    )
    telemetry.record_submission_result(
        request=request_two,
        accepted=True,
        code="queued",
        engine="gtts",
    )
    telemetry.record_submission_result(
        request=request_three,
        accepted=False,
        code="queue_full",
        engine="edge-tts",
    )

    item_one = AudioQueueItem(request=request_one, created_at=10.0)
    item_one.mark_completed()
    item_one.completed_at = 10.100
    telemetry.record_processing_result(item=item_one, success=True, code="ok", engine="gtts")

    item_two = AudioQueueItem(request=request_two, created_at=20.0)
    item_two.mark_failed("boom")
    item_two.completed_at = 20.300
    telemetry.record_processing_result(item=item_two, success=False, code="unknown_error", engine="gtts")

    snapshot = telemetry.snapshot()

    assert snapshot.status == "enabled"
    assert snapshot.total_requests == 3
    assert snapshot.successful_playbacks == 1
    assert snapshot.failed_requests == 2
    assert snapshot.error_rate == 0.6667
    assert snapshot.enqueue_to_playback_sample_count == 1
    assert snapshot.enqueue_to_playback_p95_ms == 100.0
    assert snapshot.enqueue_to_playback_p99_ms == 100.0
    assert snapshot.error_rate_by_guild[0].key == "1"
    assert snapshot.error_rate_by_guild[0].total_requests == 2
    assert snapshot.error_rate_by_guild[0].failed_requests == 1
    assert snapshot.error_rate_by_engine[0].key == "edge-tts"
    assert snapshot.error_rate_by_engine[0].error_rate == 1.0


def test_runtime_observability_snapshot_is_empty_when_no_data_exists():
    telemetry = InMemoryBotRuntimeTelemetry()

    snapshot = telemetry.snapshot()

    assert snapshot.status == "enabled"
    assert snapshot.total_requests == 0
    assert snapshot.failed_requests == 0
    assert snapshot.enqueue_to_playback_p95_ms is None
