"""Tests for Discord commands presentation layer."""
import pytest
from unittest.mock import Mock, AsyncMock
from discord import app_commands
from src.presentation.discord_commands import DiscordCommands
from src.application.use_cases import SpeakTextUseCase, ConfigureTTSUseCase


class TestDiscordCommands:
    """Test DiscordCommands presentation layer."""
    
    def test_initialization(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test DiscordCommands initialization."""
        speak_use_case = SpeakTextUseCase(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository
        )
        config_use_case = ConfigureTTSUseCase(mock_config_repository)
        
        # Mock command tree
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        commands = DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            mock_channel_repository
        )
        
        assert commands._tree == tree
        assert commands._speak_use_case == speak_use_case
        assert commands._config_use_case == config_use_case
        assert commands._channel_repository == mock_channel_repository
    
    @pytest.mark.asyncio
    async def test_handle_speak_command_success(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test successful /speak command."""
        speak_use_case = SpeakTextUseCase(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository
        )
        config_use_case = ConfigureTTSUseCase(mock_config_repository)
        
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        commands = DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            mock_channel_repository
        )
        
        # Mock interaction
        interaction = Mock()
        interaction.user.voice = Mock()
        interaction.user.voice.channel = Mock()
        interaction.user.voice.channel.id = 12345
        interaction.guild_id = 67890
        interaction.user.id = 11111
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        
        # Call handler
        await commands._handle_speak(interaction, "Test message")
        
        # Verify followup was sent
        interaction.followup.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_speak_not_in_voice_channel(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test /speak when user is not in voice channel."""
        speak_use_case = SpeakTextUseCase(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository
        )
        config_use_case = ConfigureTTSUseCase(mock_config_repository)
        
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        commands = DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            mock_channel_repository
        )
        
        # Mock interaction - user not in voice
        interaction = Mock()
        interaction.user.voice = None
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        
        # Call handler
        await commands._handle_speak(interaction, "Test")
        
        # Verify followup response
        interaction.followup.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_config_get(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test /config command to get current config."""
        speak_use_case = SpeakTextUseCase(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository
        )
        config_use_case = ConfigureTTSUseCase(mock_config_repository)
        
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        commands = DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            mock_channel_repository
        )
        
        # Mock interaction
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.user.mention = "<@67890>"
        interaction.response = AsyncMock()
        
        # Call handler with no parameters (get current config)
        await commands._handle_config(interaction, None, None, None)
        
        # Verify response contains config info
        interaction.response.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_config_update_engine(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test /config command to update engine."""
        speak_use_case = SpeakTextUseCase(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository
        )
        config_use_case = ConfigureTTSUseCase(mock_config_repository)
        
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        commands = DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            mock_channel_repository
        )
        
        # Mock interaction
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.response = AsyncMock()
        
        # Call handler with engine parameter
        await commands._handle_config(interaction, "pyttsx3", None, None)
        
        # Verify response
        interaction.response.send_message.assert_called_once()
        
        # Verify config was updated
        config = mock_config_repository.get_config(67890)
        assert config.engine == "pyttsx3"
    
    @pytest.mark.asyncio
    async def test_handle_join_no_voice_channel(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test /join when user is not in voice channel."""
        speak_use_case = SpeakTextUseCase(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository
        )
        config_use_case = ConfigureTTSUseCase(mock_config_repository)
        
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        commands = DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            mock_channel_repository
        )
        
        # Mock interaction with user not in voice
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.voice = None
        interaction.guild = None
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        
        await commands._handle_join(interaction)
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        assert "not connected" in call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_handle_leave(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test /leave command."""
        speak_use_case = SpeakTextUseCase(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository
        )
        config_use_case = ConfigureTTSUseCase(mock_config_repository)
        
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        commands = DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            mock_channel_repository
        )
        
        # Mock interaction with voice client
        interaction = Mock()
        interaction.guild = Mock()
        voice_client = AsyncMock()
        interaction.guild.voice_client = voice_client
        interaction.response = AsyncMock()
        
        await commands._handle_leave(interaction)
        
        voice_client.disconnect.assert_called_once()
        interaction.response.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_about(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test /about command."""
        speak_use_case = SpeakTextUseCase(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository
        )
        config_use_case = ConfigureTTSUseCase(mock_config_repository)
        
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        commands = DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            mock_channel_repository
        )
        
        # Mock interaction
        interaction = Mock()
        interaction.response = AsyncMock()
        
        await commands._handle_about(interaction)
        
        interaction.response.send_message.assert_called_once()
        # About command sends embed, not text message
        call_kwargs = interaction.response.send_message.call_args[1]
        assert "embed" in call_kwargs
