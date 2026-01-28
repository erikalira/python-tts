#!/usr/bin/env python3
"""
TTS Services Module - Clean Architecture
Provides text-to-speech services with different engines and delivery methods.
"""

import threading
from abc import ABC, abstractmethod
from typing import Optional, Protocol

try:
    import pyttsx3
    _pyttsx3_available = True
except ImportError:
    _pyttsx3_available = False

try:
    import requests
    _requests_available = True
except ImportError:
    _requests_available = False

from ..config.standalone_config import StandaloneConfig


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
    
    def __init__(self, config: StandaloneConfig):
        self._config = config
        self._engine: Optional[object] = None
        self._lock = threading.Lock()
    
    def _initialize_engine(self) -> bool:
        """Initialize the pyttsx3 engine."""
        if not _pyttsx3_available:
            return False
        
        try:
            if self._engine is None:
                self._engine = pyttsx3.init()
                self._engine.setProperty('rate', self._config.tts.rate)
                
                # Set voice if specified
                if self._config.tts.voice_id:
                    voices = self._engine.getProperty('voices')
                    for voice in voices:
                        if self._config.tts.voice_id.lower() in voice.id.lower():
                            self._engine.setProperty('voice', voice.id)
                            break
            
            return True
        except Exception as e:
            print(f"[TTS] Erro ao inicializar pyttsx3: {e}")
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
                print(f"[TTS] Erro ao reproduzir com pyttsx3: {e}")
                return False
    
    def is_available(self) -> bool:
        """Check if pyttsx3 is available."""
        return _pyttsx3_available


class DiscordTTSService(TTSEngine):
    """TTS service that sends text to Discord bot."""
    
    def __init__(self, config: StandaloneConfig):
        self._config = config
    
    def speak(self, text: str) -> bool:
        """Send text to Discord bot for TTS."""
        if not _requests_available or not self._config.discord.bot_url:
            return False
        
        try:
            payload = {'text': text}
            
            if self._config.discord.channel_id:
                payload['channel_id'] = self._config.discord.channel_id
            
            if self._config.discord.member_id:
                payload['member_id'] = self._config.discord.member_id
            
            url = self._config.discord.bot_url.rstrip('/') + '/speak'
            
            print(f"[TTS] 🚀 Enviando '{text}' para Discord...")
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=self._config.network.request_timeout,
                headers={'User-Agent': self._config.network.user_agent}
            )
            
            if response.ok:
                print("[TTS] ✅ Enviado com sucesso!")
                return True
            else:
                print(f"[TTS] ❌ Erro HTTP: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print('[TTS] ⏰ Timeout ao conectar com Discord')
            return False
        except Exception as e:
            print(f'[TTS] ❌ Erro ao conectar com Discord: {e}')
            return False
    
    def is_available(self) -> bool:
        """Check if Discord TTS is available."""
        return _requests_available and bool(self._config.discord.bot_url)


class FallbackTTSEngine(TTSEngine):
    """TTS engine that tries multiple engines in sequence."""
    
    def __init__(self, engines: list[TTSEngine]):
        self._engines = engines
    
    def speak(self, text: str) -> bool:
        """Try engines in order until one succeeds."""
        for engine in self._engines:
            if engine.is_available():
                if engine.speak(text):
                    return True
                else:
                    print(f"[TTS] Engine {engine.__class__.__name__} falhou, tentando próximo...")
        
        print("[TTS] ❌ Todos os engines falharam")
        return False
    
    def is_available(self) -> bool:
        """Check if any engine is available."""
        return any(engine.is_available() for engine in self._engines)


class TTSService:
    """Main TTS service that coordinates different engines."""
    
    def __init__(self, config: StandaloneConfig):
        self._config = config
        self._engine = self._create_engine()
    
    def _create_engine(self) -> TTSEngine:
        """Create the appropriate TTS engine based on configuration."""
        engines = []
        
        # Add Discord engine if configured
        if self._config.discord.bot_url:
            discord_engine = DiscordTTSService(self._config)
            engines.append(discord_engine)
        
        # Add local engine as fallback
        local_engine = LocalPyTTSX3Engine(self._config)
        engines.append(local_engine)
        
        return FallbackTTSEngine(engines)
    
    def speak_text(self, text: str) -> bool:
        """Speak the given text using available engines."""
        if not text or not text.strip():
            return False
        
        # Limit text length
        if len(text) > self._config.network.max_text_length:
            text = text[:self._config.network.max_text_length]
            print(f"[TTS] ⚠️ Texto truncado para {self._config.network.max_text_length} caracteres")
        
        print(f"[TTS] 🔊 Processando: '{text}'")
        return self._engine.speak(text)
    
    def is_available(self) -> bool:
        """Check if TTS service is available."""
        return self._engine.is_available()
    
    def get_status_info(self) -> dict:
        """Get status information about available engines."""
        return {
            'discord_available': DiscordTTSService(self._config).is_available(),
            'local_available': LocalPyTTSX3Engine(self._config).is_available(),
            'pyttsx3_installed': _pyttsx3_available,
            'requests_installed': _requests_available,
            'bot_url_configured': bool(self._config.discord.bot_url)
        }


class KeyboardCleanupService:
    """Service for handling keyboard cleanup after TTS."""
    
    def __init__(self):
        self._suppress_events = threading.Event()
    
    def cleanup_typed_text(self, backspace_count: int) -> None:
        """Remove typed characters from the active window."""
        try:
            import keyboard
            
            self._suppress_events.set()
            
            for _ in range(backspace_count):
                keyboard.send('backspace')
                
        except ImportError:
            print("[TTS] ⚠️ Keyboard library not available for cleanup")
        except Exception as e:
            print(f"[TTS] ❌ Erro durante cleanup: {e}")
        finally:
            self._suppress_events.clear()
    
    def is_suppressing_events(self) -> bool:
        """Check if keyboard events are currently being suppressed."""
        return self._suppress_events.is_set()


class TTSProcessor:
    """High-level processor that coordinates TTS and cleanup."""
    
    def __init__(self, config: StandaloneConfig):
        self._tts_service = TTSService(config)
        self._cleanup_service = KeyboardCleanupService()
    
    def process_text(self, text: str, cleanup_count: int = 0) -> None:
        """Process text for TTS and perform cleanup in a separate thread."""
        def _process():
            success = self._tts_service.speak_text(text)
            
            if success and cleanup_count > 0:
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
            'tts_available': self._tts_service.is_available(),
            'engines_info': self._tts_service.get_status_info()
        }