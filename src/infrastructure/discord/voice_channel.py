"""Discord voice channel implementation."""
import asyncio
import logging
from typing import Optional, Dict
import discord
from src.core.interfaces import IVoiceChannel, IVoiceChannelRepository
from src.core.entities import AudioFile

logger = logging.getLogger(__name__)


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
    
    async def connect(self) -> None:
        """Connect to the voice channel."""
        if not self._voice_client or not self._voice_client.is_connected():
            self._voice_client = await self._channel.connect()
    
    async def disconnect(self) -> None:
        """Disconnect from the voice channel."""
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
        
        # Stop current playback if any
        if self._voice_client.is_playing():
            self._voice_client.stop()
        
        # Play audio
        source = discord.FFmpegPCMAudio(audio.path)
        self._voice_client.play(source)
        
        # Wait for playback to finish
        while self._voice_client.is_playing():
            await asyncio.sleep(0.1)
    
    def is_connected(self) -> bool:
        """Check if connected to voice channel."""
        return self._voice_client is not None and self._voice_client.is_connected()
    
    @property
    def guild_id(self) -> int:
        """Get guild ID."""
        return self._channel.guild.id


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
    
    async def find_by_member_id(self, member_id: int) -> Optional[IVoiceChannel]:
        """Find voice channel where member is connected.
        
        Args:
            member_id: Member ID to search for
            
        Returns:
            IVoiceChannel if found, None otherwise
        """
        # Check cache first
        if member_id in self._member_cache:
            channel = self._member_cache[member_id]
            # Verify channel is still valid
            if self._is_member_in_channel(member_id, channel):
                return channel
            else:
                self._member_cache.pop(member_id, None)
        
        # Search all guilds
        for guild in self._client.guilds:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if member.id == member_id:
                        channel = DiscordVoiceChannel(vc)
                        self._member_cache[member_id] = channel
                        return channel
        
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
                return DiscordVoiceChannel(channel)
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
                                return DiscordVoiceChannel(vc)
                    
                    # Return first available channel
                    if guild.voice_channels:
                        return DiscordVoiceChannel(guild.voice_channels[0])
            except Exception as e:
                logger.error(f"Error finding channel by guild ID {guild_id}: {e}")
        
        # Fallback: any available channel
        for guild in self._client.guilds:
            if guild.voice_channels:
                return DiscordVoiceChannel(guild.voice_channels[0])
        
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
