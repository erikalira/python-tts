from unittest.mock import Mock

import pytest

from src.bot_runtime.container import Container
from src.infrastructure.audio_queue import InMemoryAudioQueue, RedisAudioQueue
from src.infrastructure.persistence.config_storage import JSONConfigStorage
from src.infrastructure.persistence.postgres_storage import PostgreSQLConfigStorage


def _build_config(backend: str):
    config = Mock()
    config.config_storage_backend = backend
    config.config_storage_dir = "configs-test"
    config.database_url = "postgresql://user:pass@localhost/db"
    config.tts_queue_backend = "inmemory"
    config.tts_queue_max_size = 50
    config.redis_host = "127.0.0.1"
    config.redis_port = 6379
    config.redis_db = 0
    config.redis_password = None
    config.redis_key_prefix = "tts"
    return config


def test_container_uses_json_storage_when_configured():
    container = Container.__new__(Container)

    storage = container._build_config_storage(_build_config("json"))

    assert isinstance(storage, JSONConfigStorage)
    assert str(storage.storage_dir).endswith("configs-test")


def test_container_uses_postgres_storage_when_configured():
    container = Container.__new__(Container)

    storage = container._build_config_storage(_build_config("postgres"))

    assert isinstance(storage, PostgreSQLConfigStorage)


def test_container_uses_inmemory_audio_queue_by_default():
    container = Container.__new__(Container)

    queue = container._build_audio_queue(_build_config("json"))

    assert isinstance(queue, InMemoryAudioQueue)


def test_container_uses_redis_audio_queue_when_configured(monkeypatch):
    container = Container.__new__(Container)
    config = _build_config("json")
    config.tts_queue_backend = "redis"

    class FakeRedisClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr("src.bot_runtime.container.Redis", FakeRedisClient)

    queue = container._build_audio_queue(config)

    assert isinstance(queue, RedisAudioQueue)


def test_container_requires_redis_dependency_for_redis_backend(monkeypatch):
    container = Container.__new__(Container)
    config = _build_config("json")
    config.tts_queue_backend = "redis"
    monkeypatch.setattr("src.bot_runtime.container.Redis", None)

    with pytest.raises(RuntimeError, match="redis package is required"):
        container._build_audio_queue(config)
