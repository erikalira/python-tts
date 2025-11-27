"""Discord voice channel implementation."""
import asyncio
import logging
from typing import Optional, Dict
import discord
from src.core.interfaces import IVoiceChannel, IVoiceChannelRepository
from src.core.entities import AudioFile

logger = logging.getLogger(__name__)

# Timeout configuration
# Disabled auto-disconnect - bot will stay connected until manually disconnected
IDLE_DISCONNECT_TIMEOUT = None  # No auto-disconnect


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
        """Connect to the voice channel."""
        # Check if already connected to this guild
        guild = self._channel.guild
        existing_client = guild.voice_client
        
        if existing_client:
            # If connected to the same channel, reuse
            if existing_client.channel.id == self._channel.id:
                self._voice_client = existing_client
                return
            # If connected to different channel, disconnect first
            await existing_client.disconnect()
        
        # Connect to the channel
        self._voice_client = await self._channel.connect()
    
    async def disconnect(self) -> None:
        """Disconnect from the voice channel."""
        # Cancel any pending disconnect timer
        self._cancel_disconnect_timer()
        
        if self._voice_client and self._voice_client.is_connected():
            await self._voice_client.disconnect()
            self._voice_client = None
    
    async def play_audio(self, audio: AudioFile) -> None:
        """Play audio in the voice channel.
        
        Args:
            audio: AudioFile to play
        """
        if not self._voice_client or not self._voice_client.is_connected():
            raise RuntimeError("Not connected to voice channel")
        
        # Cancel any pending disconnect
        self._cancel_disconnect_timer()
        
        # Stop current playback if any
        if self._voice_client.is_playing():
            self._voice_client.stop()
        
        # Play audio
        source = discord.FFmpegPCMAudio(audio.path)
        self._voice_client.play(source)
        
        # Wait for playback to finish
        while self._voice_client.is_playing():
            await asyncio.sleep(0.1)
        
        # Schedule auto-disconnect after idle timeout (disabled)
        # self._schedule_disconnect()
    
    def is_connected(self) -> bool:
        """Check if connected to voice channel."""
        return self._voice_client is not None and self._voice_client.is_connected()
    
    @property
    def guild_id(self) -> int:
        """Get guild ID."""
        return self._channel.guild.id
    
    def _schedule_disconnect(self) -> None:
        """Schedule automatic disconnect after idle timeout."""
        # Auto-disconnect disabled - bot stays connected until manual /leave
        return
        
        import time
        self._last_activity = time.time()
        
        # Cancel existing timer if any
        self._cancel_disconnect_timer()
        
        # Schedule new disconnect
        if IDLE_DISCONNECT_TIMEOUT:
            logger.info(f"[VOICE_CHANNEL] Scheduling auto-disconnect in {IDLE_DISCONNECT_TIMEOUT}s")
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
