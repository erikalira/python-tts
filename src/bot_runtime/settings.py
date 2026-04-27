"""Configuration management using environment variables."""

import logging
import os
from pathlib import Path
from typing import Mapping, Optional

from dotenv import dotenv_values, load_dotenv

from src.core.entities import TTSConfig
from src.core.timeouts import (
    DEFAULT_BOT_TTS_GENERATION_TIMEOUT_SECONDS,
    DEFAULT_BOT_TTS_PLAYBACK_TIMEOUT_SECONDS,
    DEFAULT_DISCORD_IDLE_DISCONNECT_TIMEOUT_SECONDS,
    DEFAULT_DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS,
)

_LOADED_DOTENV_VALUES: dict[str, str] = {}


def _load_environment_snapshot(env_file: Path) -> dict[str, str]:
    """Load dotenv values and return the effective environment snapshot."""

    env_values = _read_dotenv_values(env_file)
    _clear_stale_dotenv_values(env_values)

    # Export .env values for process-level runtime helpers that read directly
    # from os.environ, such as Discord voice FFmpeg checks.
    load_dotenv(env_file, override=True)

    _LOADED_DOTENV_VALUES.clear()
    _LOADED_DOTENV_VALUES.update(env_values)
    return dict(os.environ)


def _read_dotenv_values(env_file: Path) -> dict[str, str]:
    return {
        key: value
        for key, value in dotenv_values(env_file).items()
        if value is not None
    }


def _clear_stale_dotenv_values(next_values: Mapping[str, str]) -> None:
    stale_loaded_keys = set(_LOADED_DOTENV_VALUES) - set(next_values)
    for key in stale_loaded_keys:
        if os.environ.get(key) == _LOADED_DOTENV_VALUES.get(key):
            os.environ.pop(key, None)

class Config:
    """Application configuration.

    Follows Single Responsibility: only handles configuration loading.
    """

    def __init__(self, env_file: Path | None = None):
        """Initialize configuration.

        Args:
            env_file: Path to .env file or None to use default
        """
        if env_file is None:
            env_file = Path(__file__).resolve().parents[2] / ".env"

        self._env = _load_environment_snapshot(env_file)

        # Discord settings
        self.discord_token = self._getenv("DISCORD_TOKEN")

        # HTTP settings shared by the bot runtime and Desktop App client.
        self.http_port = int(self._getenv("PORT", self._getenv("DISCORD_BOT_PORT", "10000")))
        self.discord_bot_port = self.http_port
        self.http_host = self._getenv("DISCORD_BOT_HOST", self._getenv("HOST", "127.0.0.1"))
        self.http_cors_allowed_origins = self._parse_csv(self._getenv("BOT_HTTP_CORS_ALLOWED_ORIGINS", ""))
        self.max_text_length = int(self._getenv("MAX_TEXT_LENGTH", self._getenv("TTS_MAX_TEXT_LENGTH", "500")))
        self.rate_limit_max_requests = int(self._getenv("BOT_RATE_LIMIT_MAX_REQUESTS", "8"))
        self.rate_limit_window_seconds = float(self._getenv("BOT_RATE_LIMIT_WINDOW_SECONDS", "10"))
        self.tts_generation_timeout_seconds = float(
            self._getenv("TTS_GENERATION_TIMEOUT_SECONDS", str(DEFAULT_BOT_TTS_GENERATION_TIMEOUT_SECONDS))
        )
        self.tts_playback_timeout_seconds = float(
            self._getenv("TTS_PLAYBACK_TIMEOUT_SECONDS", str(DEFAULT_BOT_TTS_PLAYBACK_TIMEOUT_SECONDS))
        )
        self.voice_connection_timeout_seconds = float(
            self._getenv(
                "DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS",
                str(DEFAULT_DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS),
            )
        )
        self.voice_idle_disconnect_timeout_seconds = float(
            self._getenv(
                "DISCORD_VOICE_IDLE_DISCONNECT_TIMEOUT_SECONDS",
                str(DEFAULT_DISCORD_IDLE_DISCONNECT_TIMEOUT_SECONDS),
            )
        )
        self.tts_queue_backend = self._getenv("TTS_QUEUE_BACKEND", "inmemory").strip().lower() or "inmemory"
        self.tts_queue_max_size = int(self._getenv("TTS_QUEUE_MAX_SIZE", "50"))
        self.queue_guild_lock_ttl_seconds = int(self._getenv("QUEUE_GUILD_LOCK_TTL_SECONDS", "30"))
        guild_lock_renew = self._getenv("QUEUE_GUILD_LOCK_RENEW_INTERVAL_SECONDS")
        self.queue_guild_lock_renew_interval_seconds = (
            float(guild_lock_renew.strip()) if guild_lock_renew and guild_lock_renew.strip() else None
        )
        self.queue_processing_lease_ttl_seconds = int(
            self._getenv("QUEUE_PROCESSING_LEASE_TTL_SECONDS", str(self.queue_guild_lock_ttl_seconds))
        )
        processing_lease_renew = self._getenv("QUEUE_PROCESSING_LEASE_RENEW_INTERVAL_SECONDS")
        self.queue_processing_lease_renew_interval_seconds = (
            float(processing_lease_renew.strip())
            if processing_lease_renew and processing_lease_renew.strip()
            else None
        )
        self.redis_host = self._getenv("REDIS_HOST", "127.0.0.1")
        self.redis_port = int(self._getenv("REDIS_PORT", "6379"))
        self.redis_db = int(self._getenv("REDIS_DB", "0"))
        self.redis_password: Optional[str] = self._getenv("REDIS_PASSWORD")
        self.redis_key_prefix = self._getenv("REDIS_KEY_PREFIX", "tts").strip() or "tts"
        self.redis_completed_item_ttl_seconds = int(self._getenv("REDIS_COMPLETED_ITEM_TTL_SECONDS", "900"))
        self.otel_enabled = self._getenv("OTEL_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}
        self.otel_service_name = (
            self._getenv("OTEL_SERVICE_NAME", "tts-hotkey-windows-bot").strip() or "tts-hotkey-windows-bot"
        )
        otlp_endpoint = self._getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        self.otel_exporter_otlp_endpoint: Optional[str] = otlp_endpoint.strip() if otlp_endpoint else None
        self.log_level = self._parse_log_level(self._getenv("LOG_LEVEL", "INFO"))

        # TTS settings
        self.tts_config = TTSConfig(
            engine=self._getenv("TTS_ENGINE", "gtts").lower(),
            language=self._getenv("TTS_LANGUAGE", "pt"),
            voice_id=self._getenv("TTS_VOICE_ID", "roa/pt-br"),
            rate=int(self._getenv("TTS_RATE", "180")),
        )
        self.config_storage_backend = self._getenv("CONFIG_STORAGE_BACKEND", "json").strip().lower() or "json"
        self.config_storage_dir = self._getenv("CONFIG_STORAGE_DIR", "configs")
        self.database_url: Optional[str] = self._getenv("DATABASE_URL")

    def validate(self) -> tuple[bool, str]:
        """Validate required configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.discord_token:
            return False, "DISCORD_TOKEN not set"

        if self.tts_config.engine not in ["gtts", "pyttsx3", "edge-tts"]:
            return False, f"Invalid TTS_ENGINE: {self.tts_config.engine}"

        if self.config_storage_backend not in ["json", "postgres"]:
            return False, f"Invalid CONFIG_STORAGE_BACKEND: {self.config_storage_backend}"

        if self.config_storage_backend == "postgres" and not self.database_url:
            return False, "DATABASE_URL not set for CONFIG_STORAGE_BACKEND=postgres"

        if self.tts_queue_backend not in ["inmemory", "redis"]:
            return False, f"Invalid TTS_QUEUE_BACKEND: {self.tts_queue_backend}"

        if self.rate_limit_max_requests < 0:
            return False, "BOT_RATE_LIMIT_MAX_REQUESTS must be greater than or equal to 0"

        if self.rate_limit_window_seconds < 0:
            return False, "BOT_RATE_LIMIT_WINDOW_SECONDS must be greater than or equal to 0"

        if self.rate_limit_max_requests > 0 and self.rate_limit_window_seconds == 0:
            return False, "BOT_RATE_LIMIT_WINDOW_SECONDS must be greater than 0 when rate limiting is enabled"

        if "*" in self.http_cors_allowed_origins:
            return False, "BOT_HTTP_CORS_ALLOWED_ORIGINS must list explicit origins, not *"

        if self.otel_enabled and not self.otel_exporter_otlp_endpoint:
            return False, "OTEL_EXPORTER_OTLP_ENDPOINT not set for OTEL_ENABLED=true"

        return True, ""

    def _parse_log_level(self, raw_level: str | None) -> str:
        normalized = (raw_level or "INFO").strip().upper() or "INFO"
        if normalized in logging.getLevelNamesMapping():
            return normalized
        return "INFO"

    def _getenv(self, key: str, default: str | None = None) -> str | None:
        return self._env.get(key, default)

    def _parse_csv(self, raw_value: str | None) -> tuple[str, ...]:
        if not raw_value:
            return ()
        return tuple(value.strip() for value in raw_value.split(",") if value.strip())
