from unittest.mock import Mock

import pytest

from src.bot_runtime.readiness import BotReadinessProbe


def _config(*, storage_backend: str = "json", queue_backend: str = "inmemory") -> Mock:
    config = Mock()
    config.config_storage_backend = storage_backend
    config.tts_queue_backend = queue_backend
    return config


@pytest.mark.asyncio
@pytest.mark.chaos
async def test_readiness_reports_not_ready_when_postgres_is_unavailable():
    storage = Mock()
    storage._connect.side_effect = TimeoutError("postgres unavailable")
    config_repository = Mock()
    config_repository._storage = storage
    probe = BotReadinessProbe(
        config=_config(storage_backend="postgres"),
        discord_client=Mock(is_ready=Mock(return_value=True)),
        queue_worker=Mock(is_running=Mock(return_value=True)),
        config_repository=config_repository,
        audio_queue=Mock(),
    )

    payload = await probe.payload()

    assert payload["status"] == "not_ready"
    postgres = _dependency(payload, "postgres")
    assert postgres["status"] == "not_ready"
    assert "postgres unavailable" in postgres["detail"]


@pytest.mark.asyncio
@pytest.mark.chaos
async def test_readiness_reports_not_ready_when_postgres_connect_method_is_missing():
    config_repository = Mock()
    config_repository._storage = object()
    probe = BotReadinessProbe(
        config=_config(storage_backend="postgres"),
        discord_client=Mock(is_ready=Mock(return_value=True)),
        queue_worker=Mock(is_running=Mock(return_value=True)),
        config_repository=config_repository,
        audio_queue=Mock(),
    )

    payload = await probe.payload()

    assert payload["status"] == "not_ready"
    postgres = _dependency(payload, "postgres")
    assert postgres["status"] == "not_ready"
    assert postgres["detail"] == "connect method unavailable"


@pytest.mark.asyncio
@pytest.mark.chaos
async def test_readiness_reports_not_ready_when_redis_ping_raises():
    redis_client = Mock()
    redis_client.ping.side_effect = ConnectionError("redis unavailable")
    audio_queue = Mock()
    audio_queue._redis = redis_client
    probe = BotReadinessProbe(
        config=_config(queue_backend="redis"),
        discord_client=Mock(is_ready=Mock(return_value=True)),
        queue_worker=Mock(is_running=Mock(return_value=True)),
        config_repository=Mock(),
        audio_queue=audio_queue,
    )

    payload = await probe.payload()

    assert payload["status"] == "not_ready"
    redis = _dependency(payload, "redis")
    assert redis["status"] == "not_ready"
    assert "redis unavailable" in redis["detail"]


@pytest.mark.asyncio
@pytest.mark.chaos
async def test_readiness_reports_not_ready_when_queue_worker_is_stopped():
    probe = BotReadinessProbe(
        config=_config(),
        discord_client=Mock(is_ready=Mock(return_value=True)),
        queue_worker=Mock(is_running=Mock(return_value=False)),
        config_repository=Mock(),
        audio_queue=Mock(),
    )

    payload = await probe.payload()

    assert payload["status"] == "not_ready"
    queue_worker = _dependency(payload, "queue_worker")
    assert queue_worker["status"] == "not_ready"
    assert queue_worker["detail"] == "worker not running"


def _dependency(payload: dict[str, object], name: str) -> dict[str, object]:
    dependencies = payload["dependencies"]
    assert isinstance(dependencies, list)
    for dependency in dependencies:
        if dependency["name"] == name:
            return dependency
    raise AssertionError(f"dependency {name!r} not found in {dependencies!r}")
