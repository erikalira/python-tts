"""Application layer - use cases following Single Responsibility Principle."""
import logging
from typing import Optional
from src.core.interfaces import ITTSEngine, IVoiceChannelRepository, IConfigRepository
from src.core.entities import TTSRequest

logger = logging.getLogger(__name__)


class SpeakTextUseCase:
    """Use case for speaking text in voice channel.
    
    Follows Single Responsibility Principle - only handles the business logic
    of speaking text, delegating infrastructure concerns to injected dependencies.
    """
    
    def __init__(
        self,
        tts_engine: ITTSEngine,
        channel_repository: IVoiceChannelRepository,
        config_repository: IConfigRepository
    ):
        """Initialize use case with dependencies (Dependency Injection).
        
        Args:
            tts_engine: TTS engine implementation
            channel_repository: Voice channel repository
            config_repository: Configuration repository
        """
        self._tts_engine = tts_engine
        self._channel_repository = channel_repository
        self._config_repository = config_repository
    
    async def execute(self, request: TTSRequest) -> dict:
        """Execute the speak text use case.
        
        Args:
            request: TTSRequest with text and optional channel/guild/member info
            
        Returns:
            dict with success status and message
        """
        logger.info(f"[USE_CASE] SpeakUseCase.execute called with text: '{request.text[:50]}...', guild_id: {request.guild_id}, member_id: {request.member_id}")
        
        if not request.text:
            logger.warning("[USE_CASE] Missing text in request")
            return {"success": False, "message": "missing text"}
        
        # Find voice channel
        logger.info(f"[USE_CASE] Finding voice channel...")
        voice_channel = await self._find_voice_channel(request)
        if not voice_channel:
            logger.warning(f"[USE_CASE] No voice channel found for request")
            return {"success": False, "message": "no voice channel found"}
        
        logger.info(f"[USE_CASE] Voice channel found, getting config...")
        # Get TTS config for guild
        config = self._config_repository.get_config(request.guild_id)
        logger.info(f"[USE_CASE] Config: engine={config.engine}, language={config.language}")
        
        # Generate audio
        logger.info(f"[USE_CASE] Generating audio...")
        audio = await self._tts_engine.generate_audio(request.text, config)
        logger.info(f"[USE_CASE] Audio generated: {audio.path}")
        
        try:
            # Connect if needed
            if not voice_channel.is_connected():
                logger.info(f"[USE_CASE] Not connected, connecting to voice channel...")
                await voice_channel.connect()
                logger.info(f"[USE_CASE] Connected to voice channel")
            else:
                logger.info(f"[USE_CASE] Already connected to voice channel")
            
            # Play audio
            logger.info(f"[USE_CASE] Playing audio...")
            await voice_channel.play_audio(audio)
            logger.info(f"[USE_CASE] Audio playback completed")
            
            return {"success": True, "message": "ok"}
        except Exception as e:
            logger.error(f"[USE_CASE] Error during audio playback: {e}", exc_info=True)
            return {"success": False, "message": f"playback error: {str(e)}"}
        finally:
            # Clean up audio file
            logger.info(f"[USE_CASE] Cleaning up audio file")
            audio.cleanup()
    
    async def _find_voice_channel(self, request: TTSRequest):
        """Find appropriate voice channel based on request parameters."""
        # Try explicit channel ID first
        if request.channel_id:
            channel = await self._channel_repository.find_by_channel_id(request.channel_id)
            if channel:
                return channel
        
        # Try member ID
        if request.member_id:
            channel = await self._channel_repository.find_by_member_id(request.member_id)
            if channel:
                return channel
        
        # Try guild ID
        if request.guild_id:
            channel = await self._channel_repository.find_by_guild_id(request.guild_id)
            if channel:
                return channel
        
        # Try any available channel as fallback
        return await self._channel_repository.find_by_guild_id(None)


class ConfigureTTSUseCase:
    """Use case for configuring TTS settings."""
    
    def __init__(self, config_repository: IConfigRepository):
        """Initialize use case with dependencies.
        
        Args:
            config_repository: Configuration repository
        """
        self._config_repository = config_repository
    
    def execute(self, guild_id: int, engine: Optional[str] = None, 
                language: Optional[str] = None, voice_id: Optional[str] = None) -> dict:
        """Execute TTS configuration.
        
        Args:
            guild_id: Guild to configure
            engine: TTS engine ('gtts' or 'pyttsx3')
            language: Language code
            voice_id: Voice ID for pyttsx3
            
        Returns:
            dict with current configuration
        """
        current_config = self._config_repository.get_config(guild_id)
        
        # If no parameters, return current config
        if engine is None and language is None and voice_id is None:
            return {
                "success": True,
                "config": {
                    "engine": current_config.engine,
                    "language": current_config.language,
                    "voice_id": current_config.voice_id
                }
            }
        
        # Validate and update
        if engine is not None:
            if engine.lower() not in ['gtts', 'pyttsx3']:
                return {"success": False, "message": "Invalid engine"}
            current_config.engine = engine.lower()
        
        if language is not None:
            current_config.language = language.lower()
        
        if voice_id is not None:
            current_config.voice_id = voice_id
        
        # Save configuration
        self._config_repository.set_config(guild_id, current_config)
        
        return {
            "success": True,
            "config": {
                "engine": current_config.engine,
                "language": current_config.language,
                "voice_id": current_config.voice_id
            }
        }
