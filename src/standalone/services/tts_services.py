#!/usr/bin/env python3
"""
TTS Services Module - Clean Architecture
Provides text-to-speech services with different engines and delivery methods.
"""

import logging
import threading
from abc import ABC, abstractmethod
from typing import Optional, Protocol

from src.application.tts_execution import SpeakTextExecutionUseCase
from src.application.tts_routing import TTSFallbackChain, build_tts_engine_chain
from src.application.tts_text import prepare_tts_text
from ..config.standalone_config import StandaloneConfig
from ..adapters.keyboard_backend import KeyboardHookBackend
from ..adapters.local_tts import Pyttsx3Adapter, is_pyttsx3_available
from .discord_bot_client import DiscordBotClient, HttpDiscordBotClient
from src.infrastructure.tts.pyttsx3_support import configure_pyttsx3_engine

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
    
    def __init__(self, config: StandaloneConfig, adapter: Optional[Pyttsx3Adapter] = None):
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
        except Exception as e:
            logger.error(f"[TTS] Erro ao inicializar pyttsx3: {e}")
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
            except Exception as e:
                logger.error(f"[TTS] Erro ao reproduzir com pyttsx3: {e}")
                return False
    
    def is_available(self) -> bool:
        """Check if pyttsx3 is available."""
        return self._adapter.is_available()


class DiscordTTSService(TTSEngine):
    """TTS service that sends text to Discord bot."""
    
    def __init__(self, config: StandaloneConfig, bot_client: Optional[DiscordBotClient] = None):
        self._config = config
        self._bot_client = bot_client or HttpDiscordBotClient(config)
    
    def speak(self, text: str) -> bool:
        """Send text to Discord bot for TTS."""
        if not self._bot_client.is_available():
            return False

        logger.info("[TTS] Enviando texto para o bot do Discord")
        request = self._bot_client.build_request(text)
        return self._bot_client.send_speak_request(request)
    
    def is_available(self) -> bool:
        """Check if Discord TTS is available."""
        return self._bot_client.is_available()


FallbackTTSEngine = TTSFallbackChain


class TTSService:
    """Main TTS service that coordinates different engines."""
    
    def __init__(
        self,
        config: StandaloneConfig,
        bot_client: Optional[DiscordBotClient] = None,
        local_engine_factory: Optional[callable] = None
    ):
        self._config = config
        self._bot_client = bot_client or HttpDiscordBotClient(config)
        self._local_engine_factory = local_engine_factory or (lambda cfg: LocalPyTTSX3Engine(cfg))
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
            logger.warning(f"[TTS] Texto truncado para {self._config.network.max_text_length} caracteres")
        
        logger.info("[TTS] Processando texto para síntese")
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
            'discord_available': self._bot_client.is_available(),
            'local_available': LocalPyTTSX3Engine(self._config).is_available(),
            'pyttsx3_installed': is_pyttsx3_available(),
            'requests_installed': requests_installed,
            'bot_url_configured': bool(self._config.discord.bot_url)
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
        except Exception as e:
            logger.error(f"[TTS] Erro durante cleanup: {e}")
        finally:
            self._suppress_events.clear()
    
    def is_suppressing_events(self) -> bool:
        """Check if keyboard events are currently being suppressed."""
        return self._suppress_events.is_set()


class TTSProcessor:
    """Standalone runtime wrapper that coordinates execution threading and cleanup."""
    
    def __init__(
        self,
        config: StandaloneConfig,
        tts_service: Optional[TTSService] = None,
        cleanup_service: Optional[KeyboardCleanupService] = None,
        execution_service: Optional[SpeakTextExecutionUseCase] = None,
    ):
        if cleanup_service is None:
            raise ValueError("TTSProcessor requires explicit tts_service and cleanup_service")
        if execution_service is None:
            if tts_service is None:
                raise ValueError("TTSProcessor requires explicit tts_service and cleanup_service")
            execution_service = SpeakTextExecutionUseCase(tts_service)
        self._execution_service = execution_service
        self._cleanup_service = cleanup_service
    
    def process_text(self, text: str, cleanup_count: int = 0) -> None:
        """Process text for TTS and perform cleanup in a separate thread."""
        def _process():
            result = self._execution_service.execute(text)
            
            if result.get("success") and cleanup_count > 0:
                self._cleanup_service.cleanup_typed_text(cleanup_count)
        
        # Run in separate thread to avoid blocking
        thread = threading.Thread(target=_process, daemon=True)
        thread.start()
    
    def is_processing(self) -> bool:
        """Check if currently processing (suppressing keyboard events)."""
        return self._cleanup_service.is_suppressing_events()
    
    def get_service_status(self) -> dict:
        """Get status of all services."""
        return {
            'tts_available': self._execution_service.is_available(),
            'engines_info': self._execution_service.get_status_info()
        }
