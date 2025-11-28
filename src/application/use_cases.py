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
            # Ensure connection - single attempt
            if not voice_channel.is_connected():
                logger.info("[USE_CASE] Connecting to voice channel...")
                try:
                    await voice_channel.connect()
                    logger.info("[USE_CASE] Successfully connected to voice channel")
                except Exception as connect_error:
                    logger.error(f"[USE_CASE] Connection failed: {connect_error}")
                    return {"success": False, "message": "Não foi possível conectar ao canal de voz. Verifique se o bot tem permissão ou use o comando /join no Discord."}
            else:
                logger.info("[USE_CASE] Already connected to voice channel")
            
            # Play audio with timeout protection
            logger.info("[USE_CASE] Playing audio...")
            import asyncio
            
            try:
                # Wrap play_audio in timeout to prevent hanging
                await asyncio.wait_for(voice_channel.play_audio(audio), timeout=60)
                logger.info("[USE_CASE] Audio playback completed")
                return {"success": True, "message": "Áudio reproduzido com sucesso"}
                
            except asyncio.TimeoutError:
                logger.error("[USE_CASE] Audio playback timed out after 60 seconds")
                return {"success": False, "message": "Tempo limite excedido durante reprodução de áudio. Tente novamente."}
                
        except Exception as e:
            logger.error(f"[USE_CASE] Error during audio playback: {e}", exc_info=True)
            error_msg = str(e).lower()
            
            # Simple, direct error messages
            if "not connected" in error_msg or "connection" in error_msg:
                return {"success": False, "message": "Bot não conectado ao canal de voz. Use o comando /join no Discord."}
            elif "permission" in error_msg:
                return {"success": False, "message": "Bot não tem permissão para falar no canal."}
            elif "timeout" in error_msg:
                return {"success": False, "message": "Tempo limite excedido. Tente novamente."}
            else:
                return {"success": False, "message": "Erro ao reproduzir áudio. Tente novamente."}
                
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
        
        # EXECUTÁVEL INDEPENDENCE: Find target channel and auto-connect
        target_channel = None
        
        # SECURITY FIRST: Only connect to channel where user is currently connected
        if request.member_id:
            logger.info(f"[USE_CASE] Looking for member {request.member_id} in voice channels...")
            target_channel = await self._channel_repository.find_by_member_id(request.member_id)
            if target_channel:
                logger.info(f"[USE_CASE] Found member {request.member_id} in voice channel, will auto-connect there")
                # AUTO-CONNECT: Only to user's current channel for security
                await self._auto_connect_to_channel(target_channel)
                return target_channel
            else:
                logger.warning(f"[USE_CASE] SECURITY: Member {request.member_id} not in any voice channel - no auto-connect")
                return None
        
        # Try explicit channel ID (for manual /join commands)
        if request.channel_id:
            logger.info(f"[USE_CASE] Trying explicit channel ID: {request.channel_id}")
            target_channel = await self._channel_repository.find_by_channel_id(request.channel_id)
            if target_channel:
                logger.info("[USE_CASE] Found channel by explicit channel ID, will connect")
                await self._auto_connect_to_channel(target_channel)
                return target_channel
        
        # If no member_id or explicit channel_id, don't auto-connect for security
        logger.warning("[USE_CASE] SECURITY: No member_id provided - refusing to auto-connect to prevent information leakage")
        return None
    
    async def _auto_connect_to_channel(self, channel):
        """Auto-connect bot to voice channel ONLY where user is currently connected."""
        try:
            logger.info("[USE_CASE] AUTO-CONNECT: Connecting to user's current voice channel")
            if not channel.is_connected():
                await channel.connect()
                logger.info("[USE_CASE] AUTO-CONNECT: Successfully connected bot to user's voice channel")
            else:
                logger.info("[USE_CASE] AUTO-CONNECT: Bot already connected to user's voice channel")
        except Exception as e:
            logger.warning(f"[USE_CASE] AUTO-CONNECT: Failed to auto-connect: {e}")
            # Continue anyway, the regular connection logic will handle retries


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
