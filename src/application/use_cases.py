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
            tts_engine: TTS engine for generating audio
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
        logger.info("[USE_CASE] Finding voice channel...")
        voice_channel = await self._find_voice_channel(request)
        if not voice_channel:
            logger.warning("[USE_CASE] No voice channel found for request")
            return {"success": False, "message": "Bot não está conectado a nenhuma sala de voz. Use o comando /join primeiro ou certifique-se de que o bot tenha acesso ao canal."}
        
        logger.info("[USE_CASE] Voice channel found, getting config...")
        # Get TTS config for user
        config = self._config_repository.get_config(request.member_id)
        logger.info(f"[USE_CASE] User ID for config: {request.member_id}")
        logger.info(f"[USE_CASE] Config retrieved: engine={config.engine}, language={config.language}, voice_id={config.voice_id}")
        
        # Generate audio using injected TTS engine
        logger.info("[USE_CASE] Generating audio...")
        audio = await self._tts_engine.generate_audio(request.text, config)
        logger.info(f"[USE_CASE] Audio generated: {audio.path}")
        
        try:
            # Connect if needed
            if not voice_channel.is_connected():
                logger.info("[USE_CASE] Not connected, attempting to connect to voice channel...")
                try:
                    await voice_channel.connect()
                    logger.info("[USE_CASE] Successfully connected to voice channel")
                except Exception as connect_error:
                    logger.error(f"[USE_CASE] Failed to connect to voice channel: {connect_error}")
                    return {"success": False, "message": f"Não foi possível conectar ao canal de voz: {str(connect_error)}. Verifique se o bot tem permissão para entrar no canal."}
            else:
                logger.info("[USE_CASE] Already connected to voice channel")
            
            # Double-check connection after potential connect attempt
            if not voice_channel.is_connected():
                logger.error("[USE_CASE] Voice channel connection verification failed")
                return {"success": False, "message": "Falha na verificação de conexão com o canal de voz. Tente novamente ou use o comando /join primeiro."}
            
            # Play audio
            logger.info("[USE_CASE] Playing audio...")
            await voice_channel.play_audio(audio)
            logger.info("[USE_CASE] Audio playback completed")
            
            return {"success": True, "message": "Áudio reproduzido com sucesso"}
        except Exception as e:
            logger.error(f"[USE_CASE] Error during audio playback: {e}", exc_info=True)
            error_msg = str(e)
            if "not connected" in error_msg.lower():
                return {"success": False, "message": "Bot não está conectado ao canal de voz. Use o comando /join primeiro."}
            elif "permission" in error_msg.lower():
                return {"success": False, "message": "Bot não tem permissão para reproduzir áudio neste canal."}
            else:
                return {"success": False, "message": f"Erro durante reprodução: {error_msg}"}
        finally:
            # Clean up audio file
            logger.info("[USE_CASE] Cleaning up audio file")
            audio.cleanup()
    
    async def _find_voice_channel(self, request: TTSRequest):
        """Find appropriate voice channel based on request parameters."""
        # PRIORITY: Try to find already connected channel first
        connected_channel = await self._channel_repository.find_connected_channel()
        if connected_channel:
            logger.info("[USE_CASE] Using already connected voice channel")
            return connected_channel
        
        # Try to find user in a voice channel (most common case for executável)
        if request.member_id:
            logger.info(f"[USE_CASE] Looking for member {request.member_id} in voice channels...")
            channel = await self._channel_repository.find_by_member_id(request.member_id)
            if channel:
                logger.info(f"[USE_CASE] Found member {request.member_id} in voice channel, will connect there")
                return channel
            else:
                logger.warning(f"[USE_CASE] Member {request.member_id} not found in any voice channel")
        
        # Try explicit channel ID
        if request.channel_id:
            logger.info(f"[USE_CASE] Trying explicit channel ID: {request.channel_id}")
            channel = await self._channel_repository.find_by_channel_id(request.channel_id)
            if channel:
                logger.info("[USE_CASE] Found channel by explicit channel ID")
                return channel
        
        # Try guild ID - find any available channel
        if request.guild_id:
            logger.info(f"[USE_CASE] Trying any channel in guild: {request.guild_id}")
            channel = await self._channel_repository.find_by_guild_id(request.guild_id)
            if channel:
                logger.info("[USE_CASE] Found available channel in specified guild")
                return channel
        
        # Last resort: try any available channel
        logger.info("[USE_CASE] Last resort: trying any available channel")
        fallback_channel = await self._channel_repository.find_by_guild_id(None)
        if fallback_channel:
            logger.info("[USE_CASE] Found fallback channel")
        else:
            logger.warning("[USE_CASE] No voice channels found anywhere")
        
        return fallback_channel


class ConfigureTTSUseCase:
    """Use case for configuring TTS settings."""
    
    def __init__(self, config_repository: IConfigRepository):
        """Initialize use case with dependencies.
        
        Args:
            config_repository: Configuration repository
        """
        self._config_repository = config_repository
    
    def execute(self, user_id: int, engine: Optional[str] = None, 
                language: Optional[str] = None, voice_id: Optional[str] = None) -> dict:
        """Execute TTS configuration.
        
        Args:
            user_id: User to configure
            engine: TTS engine ('gtts' or 'pyttsx3')
            language: Language code
            voice_id: Voice ID for pyttsx3
            
        Returns:
            dict with current configuration
        """
        current_config = self._config_repository.get_config(user_id)
        
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
        self._config_repository.set_config(user_id, current_config)
        
        return {
            "success": True,
            "config": {
                "engine": current_config.engine,
                "language": current_config.language,
                "voice_id": current_config.voice_id
            }
        }
