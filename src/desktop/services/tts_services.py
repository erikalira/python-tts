#!/usr/bin/env python3
"""
TTS Services Module - Clean Architecture
Provides Desktop App TTS engines and orchestration helpers.
"""

import logging
import threading
from abc import ABC, abstractmethod
from typing import Optional, Protocol
from collections.abc import Callable

from src.application.dto import DesktopTTSStatusDTO
from src.application.desktop_tts import DesktopTTSFlowService, DesktopTTSStatusUseCase
from src.infrastructure.tts.pyttsx3_support import Pyttsx3EngineLike

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

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the TTS engine is available."""

    @abstractmethod
    def get_last_error_message(self) -> str | None:
        """Return the last human-readable error for the engine."""


class LocalPyTTSX3Engine(TTSEngine):
    """Local TTS engine using pyttsx3."""

    def __init__(self, config: DesktopAppConfig, adapter: Optional[Pyttsx3Adapter] = None):
        self._config = config
        self._adapter = adapter or Pyttsx3Adapter()
        self._engine: Optional[Pyttsx3EngineLike] = None
        self._lock = threading.Lock()
        self._last_error_message: str | None = None

    def _initialize_engine(self) -> bool:
        """Initialize the pyttsx3 engine."""
        if not self._adapter.is_available():
            self._last_error_message = "pyttsx3 is not available"
            return False

        try:
            if self._engine is None:
                self._engine = self._adapter.create_configured_engine(self._config.tts, logger)

            self._last_error_message = None
            return True
        except Exception as exc:
            logger.error("[TTS] Failed to initialize pyttsx3: %s", exc)
            self._last_error_message = f"Failed to initialize pyttsx3: {exc}"
            return False

    def speak(self, text: str) -> bool:
        """Speak text using pyttsx3."""
        with self._lock:
            if not self._initialize_engine():
                return False

            try:
                engine = self._engine
                if engine is None:
                    self._last_error_message = "pyttsx3 engine is not initialized"
                    return False
                engine.say(text)
                engine.runAndWait()
                self._last_error_message = None
                return True
            except Exception as exc:
                logger.error("[TTS] Failed to play with pyttsx3: %s", exc)
                self._last_error_message = f"Failed to play with pyttsx3: {exc}"
                return False

    def is_available(self) -> bool:
        """Check if pyttsx3 is available."""
        return self._adapter.is_available()

    def get_last_error_message(self) -> str | None:
        """Return the latest local TTS error, when any."""
        return self._last_error_message


class DiscordTTSService(TTSEngine):
    """TTS service that sends text to the Discord bot."""

    def __init__(self, config: DesktopAppConfig, bot_client: Optional[DiscordBotClient] = None):
        self._config = config
        self._bot_client = bot_client or HttpDiscordBotClient(config)

    def speak(self, text: str) -> bool:
        """Send text to the Discord bot for TTS."""
        if not self._bot_client.is_available():
            return False

        logger.info("[TTS] Sending text to the Discord bot")
        request = self._bot_client.build_request(text)
        return self._bot_client.send_speak_request(request)

    def is_available(self) -> bool:
        """Check if Discord TTS is available."""
        return self._bot_client.is_available()

    def get_last_error_message(self) -> str | None:
        """Return the latest error reported by the bot client."""
        return self._bot_client.get_last_error_message()

class DesktopAppTTSService:
    """Main Desktop App TTS service that coordinates available engines."""

    def __init__(
        self,
        config: DesktopAppConfig,
        bot_client: DiscordBotClient,
        local_engine_factory: Optional[Callable[[DesktopAppConfig], TTSEngine]] = None,
    ):
        self._config = config
        self._bot_client = bot_client
        self._local_engine_factory = local_engine_factory or (
            lambda cfg: LocalPyTTSX3Engine(cfg)
        )
        self._flow_service = self._create_flow_service()

    def _create_flow_service(self) -> DesktopTTSFlowService:
        """Create the shared Desktop App TTS flow service."""
        discord_engine = None
        if self._config.discord.bot_url:
            discord_engine = DiscordTTSService(self._config, bot_client=self._bot_client)

        local_engine = None
        if self._config.interface.local_tts_enabled:
            local_engine = self._local_engine_factory(self._config)

        return DesktopTTSFlowService(
            preferred_engine=self._config.tts.engine,
            discord_engine=discord_engine,
            local_engine=local_engine,
            max_text_length=self._config.network.max_text_length,
            logger=logger,
        )

    def speak_text(self, text: str) -> bool:
        """Speak the given text using available engines."""
        return self._flow_service.speak_text(text)

    def is_available(self) -> bool:
        """Check if TTS service is available."""
        return self._flow_service.is_available()

    def get_status_info(self) -> DesktopTTSStatusDTO:
        """Get status information about available engines."""
        return DesktopTTSStatusUseCase(_DesktopAppTTSStatusGateway(self)).execute()

    def is_remote_available(self) -> bool:
        """Return whether the Discord bot transport is currently usable."""
        return self._bot_client.is_available()

    def is_local_enabled(self) -> bool:
        """Return whether local voice is enabled in Desktop App configuration."""
        return self._config.interface.local_tts_enabled

    def is_local_available(self) -> bool:
        """Return whether the configured local engine is available."""
        if not self.is_local_enabled():
            return False
        return self._local_engine_factory(self._config).is_available()

    def has_transport(self) -> bool:
        """Return whether the bot client transport dependency is installed."""
        requests_installed = getattr(self._bot_client, "has_transport", lambda: None)()
        if requests_installed is None:
            return self._bot_client.is_available()
        return requests_installed

    def has_bot_url(self) -> bool:
        """Return whether a Discord bot URL is configured."""
        return bool(self._config.discord.bot_url)

    def get_last_error_message(self) -> str | None:
        """Return the latest error from the shared Desktop App TTS flow."""
        return self._flow_service.get_last_error_message()


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
            logger.error("[TTS] Error during cleanup: %s", exc)
        finally:
            self._suppress_events.clear()

    def is_suppressing_events(self) -> bool:
        """Check if keyboard events are currently being suppressed."""
        return self._suppress_events.is_set()

class _DesktopAppTTSStatusGateway:
    """Adapter exposing Desktop App TTS status through the shared status port."""

    def __init__(self, service: DesktopAppTTSService):
        self._service = service

    def is_remote_available(self) -> bool:
        return self._service.is_remote_available()

    def is_local_enabled(self) -> bool:
        return self._service.is_local_enabled()

    def is_local_available(self) -> bool:
        return self._service.is_local_available()

    def is_local_dependency_installed(self) -> bool:
        return is_pyttsx3_available()

    def has_transport(self) -> bool:
        return self._service.has_transport()

    def has_bot_url(self) -> bool:
        return self._service.has_bot_url()
