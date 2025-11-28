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
    
    async def connect(self) -> None:
        """Connect to the voice channel with retry logic."""
        # Check if already connected to this guild
        guild = self._channel.guild
        existing_client = guild.voice_client
        
        if existing_client:
            # If connected to the same channel and working, reuse
            if (existing_client.channel.id == self._channel.id and 
                existing_client.is_connected()):
                self._voice_client = existing_client
                logger.info("[VOICE_CHANNEL] Already connected to this channel, reusing connection")
                return
            
            # If connected but broken or to different channel, disconnect first
            logger.info("[VOICE_CHANNEL] Existing connection needs to be reset, disconnecting first")
            try:
                await existing_client.disconnect()
                await asyncio.sleep(1)  # Wait for disconnect to complete
            except Exception as e:
                logger.warning(f"[VOICE_CHANNEL] Error during disconnect: {e}")
        
        # Retry connection logic with longer delays for Render
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"[VOICE_CHANNEL] Connecting to voice channel: {self._channel.name} (attempt {attempt + 1}/{max_retries})")
                self._voice_client = await self._channel.connect()
                
                # Wait longer for connection to fully establish (Render can be slow)
                await asyncio.sleep(5)
                
                # Multiple verification attempts
                for verify_attempt in range(3):
                    if self._voice_client and self._voice_client.is_connected():
                        logger.info("[VOICE_CHANNEL] Successfully connected and verified")
                        return
                    await asyncio.sleep(2)
                
                logger.warning(f"[VOICE_CHANNEL] Connection verification failed on attempt {attempt + 1} after multiple checks")
                    
            except Exception as e:
                logger.warning(f"[VOICE_CHANNEL] Connection attempt {attempt + 1} failed: {e}")
                
                # Clean up failed connection
                if self._voice_client:
                    try:
                        await self._voice_client.disconnect()
                    except (discord.errors.ClientException, Exception):
                        pass
                    self._voice_client = None
                
                # Wait before retry (except on last attempt)
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        # All attempts failed
        logger.error("[VOICE_CHANNEL] All connection attempts failed")
        raise RuntimeError("Failed to establish voice connection after 3 attempts")
    
    async def disconnect(self) -> None:
        """Disconnect from the voice channel."""
        # Cancel any pending disconnect timer
        self._cancel_disconnect_timer()
        
        if self._voice_client and self._voice_client.is_connected():
            await self._voice_client.disconnect()
            self._voice_client = None
    
    async def play_audio(self, audio: AudioFile) -> None:
        """Play audio in the voice channel with resilient connection handling.
        
        Args:
            audio: AudioFile to play
        """
        # Check and fix connection if needed
        if not self._voice_client or not self._voice_client.is_connected():
            logger.warning("[VOICE_CHANNEL] Connection lost, attempting to reconnect...")
            try:
                await self.connect()
            except Exception as e:
                logger.error(f"[VOICE_CHANNEL] Failed to reconnect: {e}")
                raise RuntimeError("Failed to reconnect to voice channel")
        
        logger.info(f"[VOICE_CHANNEL] Voice client is connected, preparing to play audio: {audio.path}")
        
        # Cancel any pending disconnect
        self._cancel_disconnect_timer()
        
        # Stop current playback if any
        if self._voice_client.is_playing():
            logger.info("[VOICE_CHANNEL] Stopping current playback")
            self._voice_client.stop()
            await asyncio.sleep(0.2)  # Wait for stop to complete
        
        # Play audio with timeout protection
        try:
            logger.info("[VOICE_CHANNEL] Starting audio playback")
            source = discord.FFmpegPCMAudio(audio.path)
            self._voice_client.play(source)
            
            # Wait for playbook to finish with timeout protection
            logger.info("[VOICE_CHANNEL] Waiting for playback to complete...")
            max_wait_time = 300  # 5 minutes max wait
            wait_time = 0
            
            while self._voice_client.is_playing() and wait_time < max_wait_time:
                await asyncio.sleep(0.1)
                wait_time += 0.1
            
            if wait_time >= max_wait_time:
                logger.warning("[VOICE_CHANNEL] Playback timeout, stopping...")
                self._voice_client.stop()
                
            logger.info("[VOICE_CHANNEL] Playback completed")
            
        except Exception as e:
            logger.error(f"[VOICE_CHANNEL] Error during playback: {e}")
            # Try to stop playback on error
            try:
                if self._voice_client and self._voice_client.is_playing():
                    self._voice_client.stop()
            except (discord.errors.ClientException, Exception):
                pass
            raise
        
        # Schedule auto-disconnect after idle timeout
        self._schedule_disconnect()
    
    def is_connected(self) -> bool:
        """Check if connected to voice channel."""
        return self._voice_client is not None and self._voice_client.is_connected()
    
    @property
    def guild_id(self) -> int:
        """Get guild ID."""
        return self._channel.guild.id
    
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
    
    async def find_connected_channel(self) -> Optional[IVoiceChannel]:
        """Find any voice channel where bot is already connected.
        
        Returns:
            IVoiceChannel if bot is connected, None otherwise
        """
        try:
            for guild in self._client.guilds:
                if guild.voice_client and guild.voice_client.is_connected():
                    channel = guild.voice_client.channel
                    if channel:
                        logger.info(f"Found connected channel: {channel.name} in guild {guild.name}")
                        # Reuse existing instance if available
                        if channel.id not in self._channel_instances:
                            self._channel_instances[channel.id] = DiscordVoiceChannel(channel)
                        return self._channel_instances[channel.id]
        except Exception as e:
            logger.error(f"Error finding connected channel: {e}")
        
        return None
    
    async def find_by_member_id(self, member_id: int) -> Optional[IVoiceChannel]:
        """Find voice channel where member is connected.
        
        Args:
            member_id: Member ID to search for
            
        Returns:
            IVoiceChannel if found, None otherwise
        """
        # Search all guilds
        for guild in self._client.guilds:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if member.id == member_id:
                        # Reuse existing instance if available to preserve timer state
                        if vc.id not in self._channel_instances:
                            self._channel_instances[vc.id] = DiscordVoiceChannel(vc)
                        return self._channel_instances[vc.id]
        
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
