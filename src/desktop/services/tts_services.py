#!/usr/bin/env python3
"""
TTS Services Module - Clean Architecture
Provides Desktop App TTS engines and orchestration helpers.
"""

import logging
import threading
from abc import ABC, abstractmethod
from typing import Optional, Protocol

from src.application.tts_routing import TTSFallbackChain, build_tts_engine_chain
from src.application.tts_text import prepare_tts_text
from src.infrastructure.tts.pyttsx3_support import configure_pyttsx3_engine

from ..adapters.keyboard_backend import KeyboardHookBackend
from ..adapters.local_tts import Pyttsx3Adapter, is_pyttsx3_available
from ..config.desktop_config import DesktopAppConfig
from .discord_bot_client import DiscordBotClient, HttpDiscordBotClient

logger = logging.getLogger(__name__)


class AudioDevice(Protocol):
    """Protocol for audio device selection."""

    def set_output_device(self, device_name: str) -> bool:
        """Set the output device for audio playback."""
        ...


class TTSEngine(ABC):
    """Abstract base class for TTS engines."""

    @abstractmethod
    def speak(self, text: str) -> bool:
        """Speak the given text. Returns True if successful."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the TTS engine is available."""
        pass


class LocalPyTTSX3Engine(TTSEngine):
    """Local TTS engine using pyttsx3."""

    def __init__(self, config: DesktopAppConfig, adapter: Optional[Pyttsx3Adapter] = None):
        self._config = config
        self._adapter = adapter or Pyttsx3Adapter()
        self._engine: Optional[object] = None
        self._lock = threading.Lock()

    def _initialize_engine(self) -> bool:
        """Initialize the pyttsx3 engine."""
        if not self._adapter.is_available():
            return False

        try:
            if self._engine is None:
                self._engine = self._adapter.create_engine()
                configure_pyttsx3_engine(self._engine, self._config.tts, logger)

            return True
        except Exception as exc:
            logger.error("[TTS] Erro ao inicializar pyttsx3: %s", exc)
            return False

    def speak(self, text: str) -> bool:
        """Speak text using pyttsx3."""
        with self._lock:
            if not self._initialize_engine():
                return False

            try:
                self._engine.say(text)
                self._engine.runAndWait()
                return True
            except Exception as exc:
                logger.error("[TTS] Erro ao reproduzir com pyttsx3: %s", exc)
                return False

    def is_available(self) -> bool:
        """Check if pyttsx3 is available."""
        return self._adapter.is_available()


class DiscordTTSService(TTSEngine):
    """TTS service that sends text to the Discord bot."""

    def __init__(self, config: DesktopAppConfig, bot_client: Optional[DiscordBotClient] = None):
        self._config = config
        self._bot_client = bot_client or HttpDiscordBotClient(config)

    def speak(self, text: str) -> bool:
        """Send text to the Discord bot for TTS."""
        if not self._bot_client.is_available():
            return False

        logger.info("[TTS] Enviando texto para o bot do Discord")
        request = self._bot_client.build_request(text)
        return self._bot_client.send_speak_request(request)

    def is_available(self) -> bool:
        """Check if Discord TTS is available."""
        return self._bot_client.is_available()


FallbackTTSEngine = TTSFallbackChain


class DesktopAppTTSService:
    """Main Desktop App TTS service that coordinates available engines."""

    def __init__(
        self,
        config: DesktopAppConfig,
        bot_client: Optional[DiscordBotClient] = None,
        local_engine_factory: Optional[object] = None,
    ):
        self._config = config
        self._bot_client = bot_client or HttpDiscordBotClient(config)
        self._local_engine_factory = local_engine_factory or (
            lambda cfg: LocalPyTTSX3Engine(cfg)
        )
        self._engine = self._create_engine()

    def _create_engine(self) -> TTSEngine:
        """Create the appropriate TTS engine based on configuration."""
        discord_engine = None
        if self._config.discord.bot_url:
            discord_engine = DiscordTTSService(self._config, bot_client=self._bot_client)

        local_engine = self._local_engine_factory(self._config)
        engines = build_tts_engine_chain(
            self._config.tts.engine,
            discord_engine=discord_engine,
            local_engine=local_engine,
        )

        return FallbackTTSEngine(engines, logger=logger)

    def speak_text(self, text: str) -> bool:
        """Speak the given text using available engines."""
        prepared_text = prepare_tts_text(text, self._config.network.max_text_length)
        if not prepared_text:
            return False

        if prepared_text != text.strip():
            logger.warning(
                "[TTS] Texto truncado para %s caracteres",
                self._config.network.max_text_length,
            )

        logger.info("[TTS] Processando texto para sintese")
        return self._engine.speak(prepared_text)

    def is_available(self) -> bool:
        """Check if TTS service is available."""
        return self._engine.is_available()

    def get_status_info(self) -> dict:
        """Get status information about available engines."""
        requests_installed = getattr(self._bot_client, "has_transport", lambda: None)()
        if requests_installed is None:
            requests_installed = self._bot_client.is_available()

        return {
            "discord_available": self._bot_client.is_available(),
            "local_available": LocalPyTTSX3Engine(self._config).is_available(),
            "pyttsx3_installed": is_pyttsx3_available(),
            "requests_installed": requests_installed,
            "bot_url_configured": bool(self._config.discord.bot_url),
        }


class KeyboardCleanupService:
    """Service for handling keyboard cleanup after TTS."""

    def __init__(self, keyboard_backend: Optional[KeyboardHookBackend] = None):
        self._keyboard_backend = keyboard_backend or KeyboardHookBackend()
        self._suppress_events = threading.Event()

    def cleanup_typed_text(self, backspace_count: int) -> None:
        """Remove typed characters from the active window."""
        try:
            if not self._keyboard_backend.is_available():
                raise ImportError
            self._suppress_events.set()

            for _ in range(backspace_count):
                self._keyboard_backend.send_backspace()

        except ImportError:
            logger.warning("[TTS] Keyboard library not available for cleanup")
        except Exception as exc:
            logger.error("[TTS] Erro durante cleanup: %s", exc)
        finally:
            self._suppress_events.clear()

    def is_suppressing_events(self) -> bool:
        """Check if keyboard events are currently being suppressed."""
        return self._suppress_events.is_set()


TTSService = DesktopAppTTSService
