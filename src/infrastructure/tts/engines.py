"""Infrastructure layer - TTS engines implementation."""
import tempfile
import asyncio
import logging
from typing import Optional
import pyttsx3
from gtts import gTTS
from src.core.interfaces import ITTSEngine
from src.core.entities import TTSConfig, AudioFile

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
                self._engine.setProperty('rate', config.rate)
                self._configure_voice(config)
                self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            raise
    
    def _configure_voice(self, config: TTSConfig):
        """Configure voice based on settings."""
        if not self._engine:
            return
        
        try:
            voices = self._engine.getProperty('voices')
            target_voice = None
            
            for voice in voices:
                if config.voice_id.lower() in voice.id.lower():
                    target_voice = voice.id
                    logger.info(f"✅ Found configured voice: {voice.name}")
                    break
            
            if target_voice:
                self._engine.setProperty('voice', target_voice)
            elif voices:
                self._engine.setProperty('voice', voices[0].id)
                logger.warning(f"⚠️ Voice '{config.voice_id}' not found, using default")
        except Exception as e:
            logger.warning(f"Could not configure voices: {e}")
    
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        """Generate audio using pyttsx3.
        
        Args:
            text: Text to convert
            config: TTS configuration
            
        Returns:
            AudioFile with generated audio path
        """
        self._initialize_engine(config)
        
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
        else:
            raise ValueError(f"Unknown TTS engine: {config.engine}")
