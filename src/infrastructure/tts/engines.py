"""Infrastructure layer - TTS engines implementation."""
import asyncio
import logging
import os
import tempfile
from typing import Optional, cast

import pyttsx3
from gtts import gTTS
from src.core.interfaces import ITTSEngine
from src.core.entities import TTSConfig, AudioFile
from src.infrastructure.tts.pyttsx3_support import Pyttsx3EngineLike, configure_pyttsx3_engine

logger = logging.getLogger(__name__)


def _create_temp_audio_path(suffix: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        return tmp.name


def _remove_temp_audio_file(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        return
    except OSError as exc:
        logger.warning("Failed to remove temporary audio file %s: %s", path, exc)


def _cleanup_temp_audio_file_when_done(future: asyncio.Future, path: str) -> None:
    def _cleanup(_future) -> None:
        _remove_temp_audio_file(path)

    future.add_done_callback(_cleanup)


class GTTSEngine(ITTSEngine):
    """Google Text-to-Speech engine implementation.
    
    Follows Single Responsibility: only handles gTTS audio generation.
    """

    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        """Generate audio using Google TTS.
        
        Args:
            text: Text to convert
            config: TTS configuration
            
        Returns:
            AudioFile with generated audio path
        """
        loop = asyncio.get_running_loop()
        tmpname = _create_temp_audio_path(".mp3")
        generation_future = loop.run_in_executor(None, self._generate_sync, text, config, tmpname)

        try:
            await asyncio.shield(generation_future)
            return AudioFile(path=tmpname)
        except asyncio.CancelledError:
            logger.warning("gTTS audio generation cancelled; scheduling cleanup for %s", tmpname)
            _cleanup_temp_audio_file_when_done(generation_future, tmpname)
            raise
        except Exception:
            _remove_temp_audio_file(tmpname)
            raise
    
    def _generate_sync(self, text: str, config: TTSConfig, output_path: str):
        """Synchronous audio generation."""
        tts = gTTS(text=text, lang=config.language)
        tts.save(output_path)


class Pyttsx3Engine(ITTSEngine):
    """Pyttsx3 TTS engine implementation (espeak-ng on Linux, SAPI5 on Windows).
    
    Follows Single Responsibility: only handles pyttsx3 audio generation.
    """
    
    def __init__(self):
        """Initialize pyttsx3 engine."""
        self._engine: Optional[pyttsx3.Engine] = None
        self._initialized = False
    
    def _initialize_engine(self, config: TTSConfig):
        """Lazy initialization of pyttsx3 engine."""
        if self._initialized:
            return
        
        try:
            import platform
            if platform.system() == 'Windows':
                logger.info("🎤 Initializing TTS with SAPI5 (Windows native)")
                self._engine = pyttsx3.init(driverName='sapi5')
            else:
                logger.info("🎤 Initializing TTS with pyttsx3 (espeak-ng on Linux)")
                self._engine = pyttsx3.init()
            
            if self._engine:
                configure_pyttsx3_engine(cast(Pyttsx3EngineLike, self._engine), config, logger)
                self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            raise
    
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        """Generate audio using pyttsx3.
        
        Args:
            text: Text to convert
            config: TTS configuration
            
        Returns:
            AudioFile with generated audio path
        """
        self._initialize_engine(config)
        if self._engine:
            configure_pyttsx3_engine(cast(Pyttsx3EngineLike, self._engine), config, logger)
        
        loop = asyncio.get_running_loop()
        tmpname = _create_temp_audio_path(".wav")
        generation_future = loop.run_in_executor(None, self._generate_sync, text, tmpname)

        try:
            await asyncio.shield(generation_future)
            return AudioFile(path=tmpname)
        except asyncio.CancelledError:
            logger.warning("pyttsx3 audio generation cancelled; scheduling cleanup for %s", tmpname)
            _cleanup_temp_audio_file_when_done(generation_future, tmpname)
            raise
        except Exception:
            _remove_temp_audio_file(tmpname)
            raise
    
    def _generate_sync(self, text: str, output_path: str):
        """Synchronous audio generation."""
        if not self._engine:
            raise RuntimeError("TTS engine not initialized")
        
        self._engine.save_to_file(text, output_path)
        self._engine.runAndWait()


class EdgeTTSEngine(ITTSEngine):
    """Microsoft Edge online TTS engine implementation."""

    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        try:
            import edge_tts
        except ImportError as exc:
            raise RuntimeError("edge-tts is not installed") from exc

        tmpname = _create_temp_audio_path(".mp3")

        communicate = edge_tts.Communicate(
            text=text,
            voice=config.voice_id,
            rate=self._map_rate(config.rate),
        )
        try:
            await communicate.save(tmpname)
            return AudioFile(path=tmpname)
        except asyncio.CancelledError:
            logger.warning("edge-tts audio generation cancelled; cleaning up %s", tmpname)
            _remove_temp_audio_file(tmpname)
            raise
        except Exception:
            _remove_temp_audio_file(tmpname)
            raise

    @staticmethod
    def _map_rate(rate: int) -> str:
        baseline = 180
        delta = int(round(((rate - baseline) / baseline) * 100))
        clamped = max(-50, min(100, delta))
        sign = "+" if clamped >= 0 else ""
        return f"{sign}{clamped}%"


class RoutedTTSEngine(ITTSEngine):
    """Route audio generation to the engine requested by the current config."""

    def __init__(self):
        self._engines: dict[str, ITTSEngine] = {}

    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        engine_key = config.engine.lower()
        engine = self._engines.get(engine_key)
        if engine is None:
            engine = TTSEngineFactory.create(config)
            self._engines[engine_key] = engine
        return await engine.generate_audio(text, config)


class TTSEngineFactory:
    """Factory for creating TTS engines.
    
    Follows Open/Closed Principle: easy to extend with new engines.
    """
    
    @staticmethod
    def create(config: TTSConfig) -> ITTSEngine:
        """Create TTS engine based on configuration.
        
        Args:
            config: TTS configuration
            
        Returns:
            ITTSEngine implementation
            
        Raises:
            ValueError: If engine type is unknown
        """
        if config.engine == 'gtts':
            return GTTSEngine()
        if config.engine == 'pyttsx3':
            return Pyttsx3Engine()
        if config.engine == 'edge-tts':
            return EdgeTTSEngine()
        raise ValueError(f"Unknown TTS engine: {config.engine}")
