"""Tests for bot runtime timeout configuration."""

import os

import pytest

from src.bot_runtime.settings import Config
from src.core.timeouts import (
    DEFAULT_BOT_TTS_GENERATION_TIMEOUT_SECONDS,
    DEFAULT_BOT_TTS_PLAYBACK_TIMEOUT_SECONDS,
    DEFAULT_DISCORD_IDLE_DISCONNECT_TIMEOUT_SECONDS,
    DEFAULT_DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS,
)


@pytest.fixture(autouse=True)
def restore_process_environment():
    original_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_env)


def test_config_uses_default_timeout_values(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DISCORD_TOKEN=test-token\n", encoding="utf-8")

    config = Config(env_file=env_file)

    assert config.tts_generation_timeout_seconds == DEFAULT_BOT_TTS_GENERATION_TIMEOUT_SECONDS
    assert config.tts_playback_timeout_seconds == DEFAULT_BOT_TTS_PLAYBACK_TIMEOUT_SECONDS
    assert config.voice_connection_timeout_seconds == DEFAULT_DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS
    assert config.voice_idle_disconnect_timeout_seconds == DEFAULT_DISCORD_IDLE_DISCONNECT_TIMEOUT_SECONDS


def test_config_reads_timeout_overrides_from_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "TTS_GENERATION_TIMEOUT_SECONDS=12.5",
                "TTS_PLAYBACK_TIMEOUT_SECONDS=18",
                "DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS=7",
                "DISCORD_VOICE_IDLE_DISCONNECT_TIMEOUT_SECONDS=90",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.tts_generation_timeout_seconds == 12.5
    assert config.tts_playback_timeout_seconds == 18
    assert config.voice_connection_timeout_seconds == 7
    assert config.voice_idle_disconnect_timeout_seconds == 90


def test_config_exports_dotenv_values_for_process_runtime_checks(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "FFMPEG_PATH=C:/ffmpeg/bin/ffmpeg.exe",
            ]
        ),
        encoding="utf-8",
    )

    Config(env_file=env_file)

    assert os.getenv("FFMPEG_PATH") == "C:/ffmpeg/bin/ffmpeg.exe"


def test_config_requires_database_url_for_postgres_backend(tmp_path):
    previous_env_file = tmp_path / "previous.env"
    previous_env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "CONFIG_STORAGE_BACKEND=json",
                "DATABASE_URL=postgresql://user:pass@localhost:5432/app",
            ]
        ),
        encoding="utf-8",
    )
    Config(env_file=previous_env_file)

    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "CONFIG_STORAGE_BACKEND=postgres",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (
        False,
        "DATABASE_URL not set for CONFIG_STORAGE_BACKEND=postgres",
    )


def test_config_accepts_postgres_backend_when_database_url_is_present(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "CONFIG_STORAGE_BACKEND=postgres",
                "DATABASE_URL=postgresql://user:pass@localhost:5432/app",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (True, "")


def test_config_reads_redis_queue_settings(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "TTS_QUEUE_BACKEND=redis",
                "TTS_QUEUE_MAX_SIZE=99",
                "QUEUE_GUILD_LOCK_TTL_SECONDS=45",
                "QUEUE_GUILD_LOCK_RENEW_INTERVAL_SECONDS=12.5",
                "QUEUE_PROCESSING_LEASE_TTL_SECONDS=75",
                "QUEUE_PROCESSING_LEASE_RENEW_INTERVAL_SECONDS=20",
                "REDIS_HOST=redis.local",
                "REDIS_PORT=6380",
                "REDIS_DB=2",
                "REDIS_PASSWORD=secret",
                "REDIS_KEY_PREFIX=discord-tts",
                "REDIS_COMPLETED_ITEM_TTL_SECONDS=120",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (True, "")
    assert config.tts_queue_backend == "redis"
    assert config.tts_queue_max_size == 99
    assert config.queue_guild_lock_ttl_seconds == 45
    assert config.queue_guild_lock_renew_interval_seconds == 12.5
    assert config.queue_processing_lease_ttl_seconds == 75
    assert config.queue_processing_lease_renew_interval_seconds == 20
    assert config.redis_host == "redis.local"
    assert config.redis_port == 6380
    assert config.redis_db == 2
    assert config.redis_password == "secret"
    assert config.redis_key_prefix == "discord-tts"
    assert config.redis_completed_item_ttl_seconds == 120


def test_config_rejects_unknown_queue_backend(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "TTS_QUEUE_BACKEND=unknown",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (False, "Invalid TTS_QUEUE_BACKEND: unknown")


def test_config_reads_opentelemetry_settings(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "OTEL_ENABLED=true",
                "OTEL_SERVICE_NAME=discord-bot",
                "OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.otel_enabled is True
    assert config.otel_service_name == "discord-bot"
    assert config.otel_exporter_otlp_endpoint == "http://collector:4318"


def test_config_reads_rate_limit_settings(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "BOT_RATE_LIMIT_MAX_REQUESTS=3",
                "BOT_RATE_LIMIT_WINDOW_SECONDS=7.5",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.rate_limit_max_requests == 3
    assert config.rate_limit_window_seconds == 7.5


def test_config_rejects_negative_rate_limit_values(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "BOT_RATE_LIMIT_MAX_REQUESTS=-1",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (
        False,
        "BOT_RATE_LIMIT_MAX_REQUESTS must be greater than or equal to 0",
    )


def test_config_rejects_zero_rate_limit_window_when_limit_is_enabled(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "BOT_RATE_LIMIT_MAX_REQUESTS=3",
                "BOT_RATE_LIMIT_WINDOW_SECONDS=0",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (
        False,
        "BOT_RATE_LIMIT_WINDOW_SECONDS must be greater than 0 when rate limiting is enabled",
    )


def test_config_rejects_negative_rate_limit_window(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "BOT_RATE_LIMIT_MAX_REQUESTS=0",
                "BOT_RATE_LIMIT_WINDOW_SECONDS=-1",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (
        False,
        "BOT_RATE_LIMIT_WINDOW_SECONDS must be greater than or equal to 0",
    )


def test_config_allows_zero_rate_limit_window_when_limit_is_disabled(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "BOT_RATE_LIMIT_MAX_REQUESTS=0",
                "BOT_RATE_LIMIT_WINDOW_SECONDS=0",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (True, "")


def test_config_uses_info_log_level_by_default(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DISCORD_TOKEN=test-token\n", encoding="utf-8")

    config = Config(env_file=env_file)

    assert config.log_level == "INFO"


def test_config_reads_debug_log_level_override(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "LOG_LEVEL=debug",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.log_level == "DEBUG"


def test_config_requires_otlp_endpoint_when_otel_is_enabled(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DISCORD_TOKEN=test-token",
                "TTS_QUEUE_BACKEND=inmemory",
                "OTEL_ENABLED=true",
                "OTEL_EXPORTER_OTLP_ENDPOINT=   ",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (
        False,
        "OTEL_EXPORTER_OTLP_ENDPOINT not set for OTEL_ENABLED=true",
    )
