"""Tests for bot runtime timeout configuration."""

from src.bot_runtime.settings import Config
from src.core.timeouts import (
    DEFAULT_BOT_TTS_GENERATION_TIMEOUT_SECONDS,
    DEFAULT_BOT_TTS_PLAYBACK_TIMEOUT_SECONDS,
    DEFAULT_DISCORD_IDLE_DISCONNECT_TIMEOUT_SECONDS,
    DEFAULT_DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS,
)


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


def test_config_requires_database_url_for_postgres_backend(tmp_path):
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
                "REDIS_HOST=redis.local",
                "REDIS_PORT=6380",
                "REDIS_DB=2",
                "REDIS_PASSWORD=secret",
                "REDIS_KEY_PREFIX=discord-tts",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(env_file=env_file)

    assert config.validate() == (True, "")
    assert config.tts_queue_backend == "redis"
    assert config.tts_queue_max_size == 99
    assert config.redis_host == "redis.local"
    assert config.redis_port == 6380
    assert config.redis_db == 2
    assert config.redis_password == "secret"
    assert config.redis_key_prefix == "discord-tts"


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
