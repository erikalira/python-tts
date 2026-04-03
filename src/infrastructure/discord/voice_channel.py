"""Discord voice channel implementation."""
import asyncio
import logging
from typing import Optional, Dict
import discord
from src.core.interfaces import IVoiceChannel, IVoiceChannelRepository
from src.core.entities import AudioFile

logger = logging.getLogger(__name__)

# Timeout configuration
# Auto-disconnect after 30 minutes of inactivity
IDLE_DISCONNECT_TIMEOUT = 30 * 60  # 30 minutes in seconds


class DiscordVoiceChannel(IVoiceChannel):
    """Discord voice channel wrapper.
    
    Follows Single Responsibility: only handles Discord voice operations.
    Follows Adapter pattern to adapt discord.py to our interface.
    """
    
    def __init__(self, channel: discord.VoiceChannel):
        """Initialize with discord.VoiceChannel.
        
        Args:
            channel: Discord voice channel
        """
        self._channel = channel
        self._voice_client: Optional[discord.VoiceClient] = None
        self._disconnect_task: Optional[asyncio.Task] = None
        self._last_activity: float = 0
        self._connection_lock = asyncio.Lock()

    def _sync_voice_client(self) -> Optional[discord.VoiceClient]:
        """Synchronize cached voice client with Discord's guild state."""
        guild_voice_client = self._channel.guild.voice_client
        if guild_voice_client and guild_voice_client.channel and guild_voice_client.channel.guild.id == self.get_guild_id():
            self._voice_client = guild_voice_client
        elif self._voice_client and not self._voice_client.is_connected():
            self._voice_client = None
        return self._voice_client
    
    async def connect(self) -> None:
        """Connect to the voice channel with retry logic."""
        async with self._connection_lock:
            guild = self._channel.guild
            existing_client = self._sync_voice_client()

            if existing_client and existing_client.channel and existing_client.channel.id == self._channel.id:
                if existing_client.is_connected():
                    logger.info("[VOICE_CHANNEL] Already connected to this channel, reusing connection")
                    return

                logger.info("[VOICE_CHANNEL] Found stale connection for target channel, resetting it")
                try:
                    await existing_client.disconnect(force=True)
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.warning(f"[VOICE_CHANNEL] Error resetting stale connection: {e}")
                self._voice_client = None
                existing_client = guild.voice_client

            try:
                if existing_client and existing_client.channel:
                    logger.info(f"[VOICE_CHANNEL] Moving existing voice connection to channel: {self._channel.name}")
                    await existing_client.move_to(self._channel, timeout=30.0)
                    self._voice_client = existing_client
                else:
                    logger.info(f"[VOICE_CHANNEL] Connecting to voice channel: {self._channel.name}")
                    # Avoid discord.py's internal reconnect loop when the voice gateway
                    # rejects the session with a fatal close code (e.g. 4017).
                    self._voice_client = await self._channel.connect(timeout=30.0, reconnect=False, self_deaf=True)

                await asyncio.sleep(0.5)
                active_client = self._sync_voice_client()
                if active_client and active_client.is_connected() and active_client.channel and active_client.channel.id == self._channel.id:
                    logger.info("[VOICE_CHANNEL] Successfully connected")
                    return

                logger.error("[VOICE_CHANNEL] Connection established but verification failed")
                raise RuntimeError("Connection verification failed")

            except Exception as e:
                logger.error(f"[VOICE_CHANNEL] Connection failed: {e}")
                active_client = self._sync_voice_client()
                if active_client:
                    try:
                        await active_client.disconnect(force=True)
                    except (discord.errors.ClientException, Exception):
                        pass
                self._voice_client = None
                raise RuntimeError(f"Failed to connect to voice channel: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from the voice channel."""
        # Cancel any pending disconnect timer
        self._cancel_disconnect_timer()

        voice_client = self._sync_voice_client()
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect(force=False)
        self._voice_client = None
    
    async def play_audio(self, audio: AudioFile) -> None:
        """Play audio in the voice channel with resilient connection handling.
        
        Args:
            audio: AudioFile to play
        """
        # Check and fix connection if needed
        voice_client = self._sync_voice_client()
        if not voice_client or not voice_client.is_connected():
            logger.warning("[VOICE_CHANNEL] Connection lost, attempting to reconnect...")
            try:
                await self.connect()
            except Exception as e:
                logger.error(f"[VOICE_CHANNEL] Failed to reconnect: {e}")
                raise RuntimeError("Failed to reconnect to voice channel")
            voice_client = self._sync_voice_client()
        
        logger.info(f"[VOICE_CHANNEL] Voice client is connected, preparing to play audio: {audio.path}")
        
        # Cancel any pending disconnect
        self._cancel_disconnect_timer()
        
        # Stop current playback if any
        if voice_client and voice_client.is_playing():
            logger.info("[VOICE_CHANNEL] Stopping current playback")
            voice_client.stop()
            await asyncio.sleep(0.1)  # Wait for stop to complete
        
        # Play audio with event-based completion detection (reliable synchronization)
        try:
            logger.info("[VOICE_CHANNEL] Starting audio playback")
            
            # Create event to signal when playback completes
            playback_done = asyncio.Event()
            playback_error = None
            
            def audio_finished_callback(error):
                """Callback triggered by discord.py when audio finishes playing.
                
                This is called by discord.py's internal audio player when:
                - Audio finishes naturally
                - An error occurs  
                - Player is stopped
                
                This method ensures reliable synchronization - the queue processor
                won't continue until this callback is invoked by discord.py.
                """
                nonlocal playback_error
                playback_error = error
                
                if error:
                    logger.error(f"[VOICE_CHANNEL] Audio player error: {error}")
                else:
                    logger.info("[VOICE_CHANNEL] Audio playback finished (callback triggered)")
                
                # Signal that playback is complete (success or error)
                playback_done.set()
            
            # Start audio playback with callback
            source = discord.FFmpegPCMAudio(audio.path)
            if not voice_client:
                raise RuntimeError("Voice client unavailable after connection")

            voice_client.play(source, after=audio_finished_callback)
            logger.info("[VOICE_CHANNEL] Audio queued for playback, waiting for discord.py callback...")
            
            # WAIT FOR PLAYBACK TO COMPLETE (event-driven, not polling)
            # This is much more reliable than checking is_playing() repeatedly
            try:
                await asyncio.wait_for(playback_done.wait(), timeout=60)
                logger.info("[VOICE_CHANNEL] Playback completed successfully")
                
                # If there was an error in the callback, raise it
                if playback_error:
                    raise RuntimeError(f"Audio playback error: {playback_error}")
                    
            except asyncio.TimeoutError:
                logger.warning("[VOICE_CHANNEL] Playback timeout (60s), stopping player...")
                if voice_client:
                    voice_client.stop()
                raise TimeoutError("Audio playback exceeded 60 second timeout")
            
        except Exception as e:
            logger.error(f"[VOICE_CHANNEL] Error during playback: {e}")
            # Try to stop playback on error
            try:
                if voice_client and voice_client.is_playing():
                    voice_client.stop()
            except (discord.errors.ClientException, Exception):
                pass
            raise
        
        finally:
            # Schedule auto-disconnect after idle timeout
            self._schedule_disconnect()
    
    def is_connected(self) -> bool:
        """Check if connected to voice channel."""
        voice_client = self._sync_voice_client()
        return (
            voice_client is not None and
            voice_client.is_connected() and
            voice_client.channel is not None and
            voice_client.channel.id == self._channel.id
        )

    def get_channel_id(self) -> int:
        """Get the channel ID."""
        return self._channel.id

    def get_channel_name(self) -> str:
        """Get the channel name."""
        return self._channel.name

    def get_guild_id(self) -> int:
        """Get guild ID."""
        return self._channel.guild.id

    def get_guild_name(self) -> str:
        """Get guild name."""
        return self._channel.guild.name
    
    def _schedule_disconnect(self) -> None:
        """Schedule automatic disconnect after idle timeout."""
        import time
        self._last_activity = time.time()
        
        # Cancel existing timer if any
        self._cancel_disconnect_timer()
        
        # Schedule new disconnect
        if IDLE_DISCONNECT_TIMEOUT:
            logger.info(f"[VOICE_CHANNEL] Scheduling auto-disconnect in {IDLE_DISCONNECT_TIMEOUT}s (30 minutes)")
            self._disconnect_task = asyncio.create_task(self._auto_disconnect())
    
    def _cancel_disconnect_timer(self) -> None:
        """Cancel scheduled disconnect."""
        if self._disconnect_task and not self._disconnect_task.done():
            logger.info("[VOICE_CHANNEL] Cancelling scheduled disconnect (new activity)")
            self._disconnect_task.cancel()
            self._disconnect_task = None
    
    async def _auto_disconnect(self) -> None:
        """Auto-disconnect after timeout."""
        try:
            await asyncio.sleep(IDLE_DISCONNECT_TIMEOUT)
            
            # Double-check we're still connected and idle
            if self.is_connected():
                logger.info(f"[VOICE_CHANNEL] Auto-disconnecting after {IDLE_DISCONNECT_TIMEOUT}s of inactivity")
                await self.disconnect()
                logger.info("[VOICE_CHANNEL] Auto-disconnect completed")
        except asyncio.CancelledError:
            logger.debug("[VOICE_CHANNEL] Auto-disconnect cancelled")
        except Exception as e:
            logger.error(f"[VOICE_CHANNEL] Error during auto-disconnect: {e}", exc_info=True)


class DiscordVoiceChannelRepository(IVoiceChannelRepository):
    """Repository for finding Discord voice channels.
    
    Follows Single Responsibility: only handles channel lookup logic.
    
    Features:
    - Per-channel instance caching to preserve disconnect timers
    - Guild-isolated lookups
    - Automatic cleanup of stale connection instances
    - Prevents memory leaks from long-lived connections
    """
    
    def __init__(self, client: discord.Client):
        """Initialize repository with Discord client.
        
        Args:
            client: Discord client instance
        """
        self._client = client
        self._member_cache: Dict[int, DiscordVoiceChannel] = {}
        # Cache to reuse same instance per channel (critical for timer management)
        self._channel_instances: Dict[int, DiscordVoiceChannel] = {}
        # Track when instances were last used for cleanup
        self._instance_last_used: Dict[int, float] = {}
        logger.info("[VOICE_REPO] Initialized DiscordVoiceChannelRepository")
    
    async def find_connected_channel(self) -> Optional[IVoiceChannel]:
        """Find any voice channel where bot is already connected.
        
        VALIDATION: Returns only channels from guilds where bot is active.
        
        Returns:
            IVoiceChannel if bot is connected, None otherwise
        """
        try:
            import time
            now = time.time()
            
            for guild in self._client.guilds:
                if guild.voice_client and guild.voice_client.is_connected():
                    channel = guild.voice_client.channel
                    if channel:
                        logger.info(f"[VOICE_REPO] Found connected channel: {channel.name} in guild {guild.name} (id={guild.id})")
                        # Reuse existing instance if available
                        if channel.id not in self._channel_instances:
                            self._channel_instances[channel.id] = DiscordVoiceChannel(channel)
                        # Update last used timestamp
                        self._instance_last_used[channel.id] = now
                        # Clean up stale instances periodically
                        self._cleanup_stale_instances(now)
                        return self._channel_instances[channel.id]
        except Exception as e:
            logger.error(f"[VOICE_REPO] Error finding connected channel: {e}", exc_info=True)
        
        return None
    
    async def find_by_member_id(self, member_id: int) -> Optional[IVoiceChannel]:
        """Find voice channel where member is connected.
        
        VALIDATION: Ensures member exists in Discord cache before returning.
        
        Args:
            member_id: Member ID to search for
            
        Returns:
            IVoiceChannel if found, None otherwise
        """
        import time
        now = time.time()
        
        try:
            # Search all guilds
            for guild in self._client.guilds:
                for vc in guild.voice_channels:
                    for member in vc.members:
                        if member.id == member_id:
                            logger.debug(f"[VOICE_REPO] Found member {member_id} in channel {vc.name} (guild={guild.id})")
                            # Reuse existing instance if available to preserve timer state
                            if vc.id not in self._channel_instances:
                                self._channel_instances[vc.id] = DiscordVoiceChannel(vc)
                            # Update last used timestamp
                            self._instance_last_used[vc.id] = now
                            # Clean up stale instances
                            self._cleanup_stale_instances(now)
                            return self._channel_instances[vc.id]
        except Exception as e:
            logger.error(f"[VOICE_REPO] Error finding member {member_id}: {e}", exc_info=True)
        
        return None
    
    async def find_by_channel_id(self, channel_id: int) -> Optional[IVoiceChannel]:
        """Find voice channel by ID.
        
        Args:
            channel_id: Channel ID
            
        Returns:
            IVoiceChannel if found, None otherwise
        """
        try:
            channel = self._client.get_channel(channel_id)
            if isinstance(channel, discord.VoiceChannel):
                # Reuse existing instance if available to preserve timer state
                if channel.id not in self._channel_instances:
                    self._channel_instances[channel.id] = DiscordVoiceChannel(channel)
                return self._channel_instances[channel.id]
        except Exception as e:
            logger.error(f"Error finding channel by ID {channel_id}: {e}")
        
        return None
    
    async def find_by_guild_id(self, guild_id: Optional[int]) -> Optional[IVoiceChannel]:
        """Find first available voice channel in guild.
        
        Args:
            guild_id: Guild ID or None for any guild
            
        Returns:
            IVoiceChannel if found, None otherwise
        """
        if guild_id:
            try:
                guild = self._client.get_guild(guild_id)
                if guild:
                    # Try to find connected channel first
                    if guild.voice_client and guild.voice_client.is_connected():
                        for vc in guild.voice_channels:
                            if vc.guild.voice_client == guild.voice_client:
                                # Reuse existing instance if available
                                if vc.id not in self._channel_instances:
                                    self._channel_instances[vc.id] = DiscordVoiceChannel(vc)
                                return self._channel_instances[vc.id]
                    
                    # Return first available channel
                    if guild.voice_channels:
                        vc = guild.voice_channels[0]
                        # Reuse existing instance if available
                        if vc.id not in self._channel_instances:
                            self._channel_instances[vc.id] = DiscordVoiceChannel(vc)
                        return self._channel_instances[vc.id]
            except Exception as e:
                logger.error(f"Error finding channel by guild ID {guild_id}: {e}")
        
        # Fallback: any available channel
        for guild in self._client.guilds:
            if guild.voice_channels:
                vc = guild.voice_channels[0]
                # Reuse existing instance if available
                if vc.id not in self._channel_instances:
                    self._channel_instances[vc.id] = DiscordVoiceChannel(vc)
                return self._channel_instances[vc.id]
        
        return None
    
    def update_member_cache(self, member_id: int, channel: Optional[discord.VoiceChannel]):
        """Update member cache on voice state change.
        
        Args:
            member_id: Member ID
            channel: Voice channel or None if disconnected
        """
        if channel:
            self._member_cache[member_id] = DiscordVoiceChannel(channel)
        else:
            self._member_cache.pop(member_id, None)
    
    def _is_member_in_channel(self, member_id: int, channel: DiscordVoiceChannel) -> bool:
        """Check if member is still in the cached channel."""
        try:
            return any(m.id == member_id for m in channel._channel.members)
        except Exception:
            return False
    
    def _cleanup_stale_instances(self, now: float, max_idle_time: int = 3600) -> None:
        """Clean up voice channel instances that haven't been used recently.
        
        Removes instances that are idle for more than max_idle_time seconds.
        Prevents memory leaks from server connections that are no longer active.
        
        Args:
            now: Current timestamp (from time.time())
            max_idle_time: Maximum idle time in seconds (default: 1 hour)
        """
        stale_channels = []
        
        for channel_id, last_used in self._instance_last_used.items():
            if now - last_used > max_idle_time:
                stale_channels.append(channel_id)
        
        for channel_id in stale_channels:
            try:
                # Get channel info for logging before removing
                channel_instance = self._channel_instances.get(channel_id)
                guild_id = channel_instance.get_guild_id() if channel_instance else "unknown"
                
                # Disconnect if still connected
                if channel_instance and channel_instance.is_connected():
                    logger.info(f"[VOICE_REPO] Auto-disconnecting stale channel {channel_id} (guild {guild_id})")
                    # Run disconnect in background without waiting
                    import asyncio
                    asyncio.create_task(channel_instance.disconnect())
                
                # Remove from cache
                del self._channel_instances[channel_id]
                del self._instance_last_used[channel_id]
                logger.info(f"[VOICE_REPO] Cleaned up stale instance for channel {channel_id}")
                
            except Exception as e:
                logger.warning(f"[VOICE_REPO] Error cleaning up stale instance {channel_id}: {e}")
    
    def get_cache_stats(self) -> dict:
        """Get statistics about the channel instance cache.
        
        Returns:
            dict with cache statistics
        """
        return {
            "cached_channels": len(self._channel_instances),
            "cached_members": len(self._member_cache),
            "total_tracked": len(self._instance_last_used)
        }
    
    async def cleanup_all(self) -> None:
        """Clean up all cached voice channel instances.
        
        Useful for graceful shutdown or memory reclamation.
        """
        logger.info(f"[VOICE_REPO] Cleaning up all {len(self._channel_instances)} cached channels")
        
        for channel_id, channel_instance in list(self._channel_instances.items()):
            try:
                if channel_instance.is_connected():
                    await channel_instance.disconnect()
                    logger.debug(f"[VOICE_REPO] Disconnected channel {channel_id}")
            except Exception as e:
                logger.warning(f"[VOICE_REPO] Error disconnecting channel {channel_id}: {e}")
        
        self._channel_instances.clear()
        self._instance_last_used.clear()
        self._member_cache.clear()
        
        logger.info("[VOICE_REPO] Cleanup complete")
