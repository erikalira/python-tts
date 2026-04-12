"""Infrastructure layer - TTS engines implementation."""
import tempfile
import asyncio
import logging
from typing import Optional

import pyttsx3
from gtts import gTTS
from src.core.interfaces import ITTSEngine
from src.core.entities import TTSConfig, AudioFile
from src.infrastructure.tts.pyttsx3_support import configure_pyttsx3_engine

logger = logging.getLogger(__name__)


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
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmpname = tmp.name
        tmp.close()
        
        # Run in executor to avoid blocking
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._generate_sync, text, config, tmpname)
        
        return AudioFile(path=tmpname)
    
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
                configure_pyttsx3_engine(self._engine, config, logger)
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
            configure_pyttsx3_engine(self._engine, config, logger)
        
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmpname = tmp.name
        tmp.close()
        
        # Run in executor to avoid blocking
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._generate_sync, text, tmpname)
        
        return AudioFile(path=tmpname)
    
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

        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmpname = tmp.name
        tmp.close()

        communicate = edge_tts.Communicate(
            text=text,
            voice=config.voice_id,
            rate=self._map_rate(config.rate),
        )
        await communicate.save(tmpname)
        return AudioFile(path=tmpname)

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
        elif config.engine == 'pyttsx3':
            return Pyttsx3Engine()
        elif config.engine == 'edge-tts':
            return EdgeTTSEngine()
        else:
            raise ValueError(f"Unknown TTS engine: {config.engine}")
