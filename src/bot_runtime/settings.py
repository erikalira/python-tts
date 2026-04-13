"""Configuration management using environment variables."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.core.entities import TTSConfig
from src.core.timeouts import (
    DEFAULT_BOT_TTS_GENERATION_TIMEOUT_SECONDS,
    DEFAULT_BOT_TTS_PLAYBACK_TIMEOUT_SECONDS,
    DEFAULT_DISCORD_IDLE_DISCONNECT_TIMEOUT_SECONDS,
    DEFAULT_DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS,
)


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

        # Load environment variables
        load_dotenv(env_file, override=True)

        # Discord settings
        self.discord_token = os.getenv("DISCORD_TOKEN")

        # HTTP settings shared by the bot runtime and Desktop App client.
        self.http_port = int(os.getenv("PORT", os.getenv("DISCORD_BOT_PORT", "10000")))
        self.discord_bot_port = self.http_port
        self.http_host = os.getenv("DISCORD_BOT_HOST", os.getenv("HOST", "127.0.0.1"))
        self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", os.getenv("TTS_MAX_TEXT_LENGTH", "500")))
        self.tts_generation_timeout_seconds = float(
            os.getenv("TTS_GENERATION_TIMEOUT_SECONDS", str(DEFAULT_BOT_TTS_GENERATION_TIMEOUT_SECONDS))
        )
        self.tts_playback_timeout_seconds = float(
            os.getenv("TTS_PLAYBACK_TIMEOUT_SECONDS", str(DEFAULT_BOT_TTS_PLAYBACK_TIMEOUT_SECONDS))
        )
        self.voice_connection_timeout_seconds = float(
            os.getenv("DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS", str(DEFAULT_DISCORD_VOICE_CONNECTION_TIMEOUT_SECONDS))
        )
        self.voice_idle_disconnect_timeout_seconds = float(
            os.getenv(
                "DISCORD_VOICE_IDLE_DISCONNECT_TIMEOUT_SECONDS",
                str(DEFAULT_DISCORD_IDLE_DISCONNECT_TIMEOUT_SECONDS),
            )
        )

        # TTS settings
        self.tts_config = TTSConfig(
            engine=os.getenv("TTS_ENGINE", "gtts").lower(),
            language=os.getenv("TTS_LANGUAGE", "pt"),
            voice_id=os.getenv("TTS_VOICE_ID", "roa/pt-br"),
            rate=int(os.getenv("TTS_RATE", "180")),
        )
        self.config_storage_backend = os.getenv("CONFIG_STORAGE_BACKEND", "json").strip().lower() or "json"
        self.config_storage_dir = os.getenv("CONFIG_STORAGE_DIR", "configs")
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")

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

        return True, ""
