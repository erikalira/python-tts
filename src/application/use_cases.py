"""Application layer - use cases following Single Responsibility Principle."""
import asyncio
import logging
from typing import Optional
from src.core.interfaces import ITTSEngine, IVoiceChannelRepository, IConfigRepository, IAudioQueue
from src.core.entities import TTSRequest, AudioQueueItem

logger = logging.getLogger(__name__)


class SpeakTextUseCase:
    """Use case for speaking text in voice channel with queue support.
    
    Supports multiple users queueing audio requests per guild.
    Follows Single Responsibility Principle - handles queue logic while
    delegating audio playback to injected dependencies.
    """
    
    def __init__(
        self,
        tts_engine: ITTSEngine,
        channel_repository: IVoiceChannelRepository,
        config_repository: IConfigRepository,
        audio_queue: IAudioQueue
    ):
        """Initialize use case with dependencies (Dependency Injection).
        
        Args:
            tts_engine: TTS engine for generating audio
            channel_repository: Voice channel repository
            config_repository: Configuration repository
            audio_queue: Audio queue for multi-user support
        """
        self._tts_engine = tts_engine
        self._channel_repository = channel_repository
        self._config_repository = config_repository
        self._audio_queue = audio_queue
        self._guild_processors: dict = {}  # Track active queue processors per guild
        self._guild_locks: dict = {}  # Asyncio locks per guild to prevent concurrent processing
        self._processing_guilds: set = set()  # Guilds currently processing first item
    
    async def execute(self, request: TTSRequest) -> dict:
        """Execute the speak text use case WITH QUEUE SUPPORT.
        
        Queues audio for processing in FIFO order per guild.
        If item is first in queue, processes immediately and starts queue processor.
        Otherwise returns queue position.
        
        Args:
            request: TTSRequest with text and optional channel/guild/member info
            
        Returns:
            dict with:
            - success: True/False
            - message: User-facing message with feedback
            - queued: True if waiting in queue, False if processed
            - position: Position in queue (if queued)
            - queue_size: Total items in queue (if queued)
        """
        logger.info(f"[USE_CASE] Speak request from user {request.member_id}: text='{request.text[:50]}...', guild_id={request.guild_id}")
        
        if not request.text:
            logger.warning("[USE_CASE] Missing text in request")
            return {"success": False, "message": "missing text", "queued": False}
        
        # Verify user is in a voice channel
        user_channel = await self._channel_repository.find_by_member_id(request.member_id)
        if not user_channel:
            logger.warning(f"[USE_CASE] User {request.member_id} not in any voice channel")
            return {
                "success": False,
                "message": "❌ Você não está em nenhuma sala de voz. Entre em uma sala e tente novamente.",
                "queued": False
            }
        
        # Create and enqueue audio item
        item = AudioQueueItem(request=request)
        item_id = await self._audio_queue.enqueue(item)
        position = await self._audio_queue.get_item_position(item_id)
        
        logger.info(f"[USE_CASE] Item {item_id} enqueued at position {position}, guild {request.guild_id}")
        
        # Check if there's already a processor running for this guild
        guild_id = request.guild_id
        is_already_processing = guild_id in self._processing_guilds
        
        if position == 0 and not is_already_processing:
            # First item AND no processing in progress - Process it
            logger.info(f"[USE_CASE] Item {item_id} is first in queue and no processing in progress - processing immediately")
            
            # Mark guild as processing to prevent other items from being position 0
            self._processing_guilds.add(guild_id)
            
            try:
                item = await self._audio_queue.dequeue(guild_id)
                result = await self._process_audio(item)
                
                # Start background processor for remaining items
                asyncio.create_task(self._process_queue_items(guild_id))
                
                return result
            
            finally:
                # Unmark processing
                self._processing_guilds.discard(guild_id)
        else:
            # Item in queue - return position
            if is_already_processing:
                logger.info(f"[USE_CASE] Guild {guild_id} is already processing, item {item_id} queued at position {position}")
            else:
                logger.info(f"[USE_CASE] Item {item_id} queued at position {position}")
            
            status = await self._audio_queue.get_queue_status(guild_id)
            message = f"⏳ Sua mensagem está na **fila** (posição **{position + 1}**/{status['size']}). Será reproduzida em breve!"
            
            logger.info(f"[USE_CASE] Item {item_id} queued at position {position}")
            return {
                "success": True,
                "queued": True,
                "position": position,
                "queue_size": status['size'],
                "message": message,
                "item_id": item_id
            }
    
    async def _process_queue_items(self, guild_id: Optional[int]):
        """Process remaining queue items after first item.
        
        Args:
            guild_id: Guild whose queue to process
        """
        try:
            while True:
                # Peek at next item without removing
                next_item = await self._audio_queue.peek_next(guild_id)
                
                if not next_item:
                    logger.debug(f"[USE_CASE] Queue empty for guild {guild_id}, processing complete")
                    break
                
                # Dequeue and process
                item = await self._audio_queue.dequeue(guild_id)
                if item:
                    logger.info(f"[USE_CASE] Processing queued item {item.item_id}")
                    await self._process_audio(item)
                    # Small delay between items to avoid overlapping audio
                    await asyncio.sleep(0.5)
        
        except Exception as e:
            logger.error(f"[USE_CASE] Error in _process_queue_items for guild {guild_id}: {e}", exc_info=True)
    
    async def _process_queue(self, guild_id: Optional[int]):
        """Deprecated: Use _process_first_and_queue() instead.
        
        Kept for backwards compatibility but not used anymore.
        """
        logger.warning(f"[USE_CASE] _process_queue() called but should use _process_first_and_queue() for guild {guild_id}")
        pass
    
    async def _process_audio(self, item: AudioQueueItem) -> dict:
        """Process a single audio item (generate and play).
        
        Internal method that processes one queue item completely.
        Updates item status in queue as it progresses.
        
        Args:
            item: AudioQueueItem to process
            
        Returns:
            dict with success status and message
        """
        item.mark_processing()
        logger.info(f"[USE_CASE] Processing item {item.item_id} from user {item.request.member_id} in guild {item.request.guild_id}")
        
        request = item.request
        audio = None
        
        try:
            # VALIDATION: Verify guild_id is set (critical for multi-server isolation)
            if not request.guild_id:
                error = "Guild ID não foi fornecido - isolamento de servidor falhou"
                item.mark_failed(error)
                logger.error(f"[USE_CASE] SECURITY: Item {item.item_id} has no guild_id!")
                return {"success": False, "message": f"❌ {error}", "queued": True}
            
            # Find voice channel
            channel_result = await self._find_voice_channel(request)
            if not channel_result:
                error = "Bot não conseguiu encontrar sua sala de voz"
                item.mark_failed(error)
                logger.error(f"[USE_CASE] Failed to find voice channel for item {item.item_id}")
                return {"success": False, "message": f"❌ {error}", "queued": True}
            
            voice_channel = channel_result["channel"]
            
            # VALIDATION: Verify voice channel belongs to same guild
            if voice_channel.guild_id != request.guild_id:
                error = "Canal de voz pertence a servidor diferente"
                item.mark_failed(error)
                logger.error(f"[USE_CASE] SECURITY: Item {item.item_id} voice channel guild {voice_channel.guild_id} != request guild {request.guild_id}")
                return {"success": False, "message": f"❌ {error}", "queued": True}
            
            # Get TTS config for this guild (load from storage if available)
            from src.infrastructure.persistence.config_storage import GuildConfigRepository
            if isinstance(self._config_repository, GuildConfigRepository):
                config = await self._config_repository.load_from_storage(request.guild_id)
            else:
                config = self._config_repository.get_config(request.guild_id)
            logger.info(f"[USE_CASE] Item {item.item_id}: generating audio with engine={config.engine}")
            
            # Generate audio
            audio = await self._tts_engine.generate_audio(request.text, config)
            logger.info(f"[USE_CASE] Item {item.item_id}: audio generated at {audio.path}")
            
            # Ensure connection
            if not voice_channel.is_connected():
                logger.info(f"[USE_CASE] Item {item.item_id}: connecting to voice channel")
                await voice_channel.connect()
            
            # Security check: verify user still in channel
            if request.member_id and not await self._is_user_in_channel(request.member_id, voice_channel):
                error = "Você saiu do canal de voz"
                item.mark_failed(error)
                logger.warning(f"[USE_CASE] Item {item.item_id}: user left channel, aborting playback")
                return {"success": False, "message": f"❌ {error}", "queued": True}
            
            # Play audio
            logger.info(f"[USE_CASE] Item {item.item_id}: playing audio")
            try:
                await asyncio.wait_for(voice_channel.play_audio(audio), timeout=60)
                item.mark_completed()
                logger.info(f"[USE_CASE] Item {item.item_id}: playback completed successfully")
                return {
                    "success": True,
                    "message": "✅ Áudio reproduzido",
                    "queued": False,
                    "item_id": item.item_id
                }
                
            except asyncio.TimeoutError:
                error = "Tempo limite excedido durante reprodução"
                item.mark_failed(error)
                logger.error(f"[USE_CASE] Item {item.item_id}: playback timeout")
                return {"success": False, "message": f"⏱️ {error}", "queued": True}
        
        except Exception as e:
            error_msg = str(e)
            item.mark_failed(error_msg)
            logger.error(f"[USE_CASE] Item {item.item_id}: error during processing: {e}", exc_info=True)
            
            # Provide helpful error message
            error_lower = error_msg.lower()
            if "4017" in error_lower or "dave" in error_lower:
                message = "❌ Discord recusou a conexao de voz (codigo 4017). A biblioteca atual do bot nao suporta esse handshake de voz."
            elif "not connected" in error_lower or "connection" in error_lower:
                message = "🔌 Bot não conseguiu se conectar ao canal"
            elif "permission" in error_lower:
                message = "⛔ Bot não tem permissão neste canal"
            else:
                message = "❌ Erro ao reproduzir áudio"
            
            return {"success": False, "message": message, "queued": True}
        
        finally:
            # Clean up audio file (critical for preventing memory leaks)
            if audio:
                try:
                    logger.debug(f"[USE_CASE] Item {item.item_id}: cleaning up audio file {audio.path}")
                    audio.cleanup()
                    logger.debug(f"[USE_CASE] Item {item.item_id}: audio file cleaned up successfully")
                except Exception as cleanup_error:
                    logger.warning(f"[USE_CASE] Item {item.item_id}: error during audio cleanup: {cleanup_error}")
    
    async def _find_voice_channel(self, request: TTSRequest):
        """Find appropriate voice channel based on request parameters.
        
        Returns:
            dict with 'channel', 'channel_changed' flag, or None if no valid channel
        """
        
        # SECURITY FIRST: Find where user is currently connected
        user_current_channel = None
        if request.member_id:
            logger.info(f"[USE_CASE] Looking for member {request.member_id} current voice channel...")
            user_current_channel = await self._channel_repository.find_by_member_id(request.member_id)
            
            if not user_current_channel:
                logger.warning(f"[USE_CASE] SECURITY: Member {request.member_id} not in any voice channel - refusing to speak")
                return None
                
            logger.info(f"[USE_CASE] Found member {request.member_id} in voice channel (id={user_current_channel.get_channel_id()})")
        
        # Check if bot is already connected to a channel
        connected_channel = await self._channel_repository.find_connected_channel()
        if connected_channel:
            # Check if user is in the same channel as bot
            if (user_current_channel and request.member_id and 
                await self._is_user_in_channel(request.member_id, connected_channel)):
                # User and bot are in the same channel - reuse connection
                logger.info("[USE_CASE] User is in bot's connected channel - using existing connection")
                return {"channel": connected_channel, "channel_changed": False}
            else:
                # User is in a DIFFERENT channel than bot
                # AUTO-JOIN: Allow bot to move to user's channel (instead of rejecting)
                if user_current_channel:
                    logger.info(f"[USE_CASE] AUTO-JOIN: User in different channel (id={user_current_channel.get_channel_id()}) than bot (id={connected_channel.get_channel_id()}) - bot will move to user's channel")
                    return {"channel": user_current_channel, "channel_changed": True}
                else:
                    logger.error("[USE_CASE] User not in any channel - cannot auto-join")
                    return None
        
        # Bot not connected - use the user's current channel
        if user_current_channel:
            logger.info("[USE_CASE] INITIAL CONNECTION: Using user's current voice channel")
            return {"channel": user_current_channel, "channel_changed": False}
        
        # Only allow explicit channel ID if user is present there (for manual /join commands)
        if request.channel_id and not request.member_id:
            logger.warning("[USE_CASE] SECURITY: Channel ID provided but no member_id - refusing for security")
            return None
        
        if request.channel_id and user_current_channel:
            # Verify the explicit channel matches user's current channel
            target_channel = await self._channel_repository.find_by_channel_id(request.channel_id)
            if target_channel and request.member_id and await self._is_user_in_channel(request.member_id, target_channel):
                logger.info("[USE_CASE] Explicit channel ID matches user's current channel")
                return {"channel": target_channel, "channel_changed": False}
            else:
                logger.warning(f"[USE_CASE] SECURITY: Explicit channel {request.channel_id} doesn't match user's current location")
        
        # If no member_id, refuse for security
        logger.warning("[USE_CASE] SECURITY: No member_id provided - refusing to prevent information leakage")
        return None
    
    async def _is_user_in_channel(self, member_id: int, channel) -> bool:
        """Check if user is currently in the specified voice channel.
        
        Args:
            member_id: Discord member ID
            channel: Voice channel to check (DiscordVoiceChannel instance)
            
        Returns:
            True if user is in channel, False otherwise
        """
        try:
            # Find where user is currently connected
            current_user_channel = await self._channel_repository.find_by_member_id(member_id)
            if current_user_channel is None:
                logger.info(f"[USE_CASE] SECURITY CHECK: User {member_id} not in any voice channel")
                return False
                
            # Compare channel IDs using the interface method
            channel_id = channel.get_channel_id()
            user_channel_id = current_user_channel.get_channel_id()
                
            is_same = channel_id == user_channel_id
            logger.info(f"[USE_CASE] SECURITY CHECK: User {member_id} in channel {user_channel_id}, bot in channel {channel_id}, same: {is_same}")
            return is_same
            
        except Exception as e:
            logger.error(f"[USE_CASE] SECURITY CHECK: Error checking user channel presence: {e}")
            # On error, assume user is NOT in channel for security
            return False

class ConfigureTTSUseCase:
    """Use case for configuring TTS settings per guild.
    
    Manages guild-specific TTS configuration with persistence.
    """
    
    def __init__(self, config_repository: IConfigRepository):
        """Initialize use case with dependencies.
        
        Args:
            config_repository: Configuration repository (must be GuildConfigRepository)
        """
        self._config_repository = config_repository
    
    def get_config(self, guild_id: int) -> dict:
        """Get current TTS configuration for a guild.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            dict with current configuration
        """
        if guild_id is None:
            return {"success": False, "message": "Guild ID is required"}
        
        config = self._config_repository.get_config(guild_id)
        
        return {
            "success": True,
            "guild_id": guild_id,
            "config": {
                "engine": config.engine,
                "language": config.language,
                "voice_id": config.voice_id,
                "rate": config.rate
            }
        }
    
    async def update_config_async(
        self,
        guild_id: int,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
        rate: Optional[int] = None
    ) -> dict:
        """Update TTS configuration for a guild asynchronously.
        
        Changes are persisted to storage.
        
        Args:
            guild_id: Guild identifier
            engine: TTS engine ('gtts' or 'pyttsx3')
            language: Language code
            voice_id: Voice ID for pyttsx3
            rate: Speech rate
            
        Returns:
            dict with updated configuration and success status
        """
        if guild_id is None:
            return {"success": False, "message": "Guild ID is required"}
        
        logger.info(f"[CONFIG_USE_CASE] Updating config for guild {guild_id}")
        
        # Get current config
        current_config = self._config_repository.get_config(guild_id)
        
        # Validate and update
        if engine is not None:
            if engine.lower() not in ['gtts', 'pyttsx3']:
                return {"success": False, "message": "Invalid engine. Use 'gtts' or 'pyttsx3'"}
            current_config.engine = engine.lower()
        
        if language is not None:
            current_config.language = language.lower()
        
        if voice_id is not None:
            current_config.voice_id = voice_id
        
        if rate is not None:
            if not (50 <= rate <= 300):
                return {"success": False, "message": "Rate must be between 50 and 300"}
            current_config.rate = rate
        
        # Save configuration to persistent storage
        from src.infrastructure.persistence.config_storage import GuildConfigRepository
        if isinstance(self._config_repository, GuildConfigRepository):
            saved = await self._config_repository.save_config_async(guild_id, current_config)
            if not saved:
                logger.error(f"[CONFIG_USE_CASE] Failed to persist config for guild {guild_id}")
                return {"success": False, "message": "Failed to save configuration"}
        else:
            # Fallback for tests or old repositories
            self._config_repository.set_config(guild_id, current_config)
        
        logger.info(f"[CONFIG_USE_CASE] Updated config for guild {guild_id}: {current_config}")
        
        return {
            "success": True,
            "guild_id": guild_id,
            "config": {
                "engine": current_config.engine,
                "language": current_config.language,
                "voice_id": current_config.voice_id,
                "rate": current_config.rate
            }
        }
    
    # Backwards-compatible synchronous wrapper (for old HTTP endpoints)
    def execute(self, user_id: int, engine: Optional[str] = None,
                language: Optional[str] = None, voice_id: Optional[str] = None) -> dict:
        """Deprecated: Use update_config_async() instead.
        
        Kept for backwards compatibility with old HTTP endpoints.
        
        Args:
            user_id: Old parameter (treated as guild_id now)
            engine: TTS engine
            language: Language
            voice_id: Voice ID
            
        Returns:
            dict with configuration
        """
        logger.warning("[CONFIG_USE_CASE] Using deprecated execute() method, use update_config_async() instead")
        
        guild_id = user_id  # Treat old user_id as guild_id
        current_config = self._config_repository.get_config(guild_id)
        
        # If no parameters, return current config
        if engine is None and language is None and voice_id is None:
            return self.get_config(guild_id)
        
        # Validate and update
        if engine is not None:
            if engine.lower() not in ['gtts', 'pyttsx3']:
                return {"success": False, "message": "Invalid engine"}
            current_config.engine = engine.lower()
        
        if language is not None:
            current_config.language = language.lower()
        
        if voice_id is not None:
            current_config.voice_id = voice_id
        
        # Save configuration (sync version for backwards compatibility)
        self._config_repository.set_config(guild_id, current_config)
        
        return {
            "success": True,
            "config": {
                "engine": current_config.engine,
                "language": current_config.language,
                "voice_id": current_config.voice_id
            }
        }
