"""Tests for Discord commands presentation layer."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from discord import app_commands
from src.presentation.discord_commands import DiscordCommands
from src.application.use_cases import SpeakTextUseCase, ConfigureTTSUseCase


class TestDiscordCommands:
    """Test DiscordCommands presentation layer."""
    
    @pytest.fixture
    def commands_instance(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue
    ):
        """Create a DiscordCommands instance for testing."""
        speak_use_case = SpeakTextUseCase(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository,
            mock_audio_queue
        )
        config_use_case = ConfigureTTSUseCase(mock_config_repository)
        
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        return DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            mock_channel_repository
        )
    
    def test_initialization(self, commands_instance):
        """Test DiscordCommands initialization."""
        assert commands_instance._tree is not None
        assert commands_instance._speak_use_case is not None
        assert commands_instance._config_use_case is not None
        assert commands_instance._channel_repository is not None
    
    @pytest.mark.asyncio
    async def test_handle_speak_command_success(
        self,
        commands_instance,
        mock_tts_engine,
        mock_channel_repository
    ):
        """Test successful /speak command."""
        commands_instance._speak_use_case.execute = AsyncMock(
            return_value={"success": True, "message": "Success"}
        )
        
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.delete_original_response = AsyncMock()
        
        with patch('src.presentation.discord_commands.HAS_PYNACL', True), \
             patch('src.presentation.discord_commands.HAS_FFMPEG', True):
            await commands_instance._handle_speak(interaction, "Test message")
        
        interaction.response.defer.assert_called_once()
        interaction.delete_original_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_speak_missing_dependencies(self, commands_instance):
        """Test /speak when dependencies are missing."""
        interaction = Mock()
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        
        with patch('src.presentation.discord_commands.HAS_PYNACL', False):
            await commands_instance._handle_speak(interaction, "Test")
        
        interaction.edit_original_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_speak_failure(self, commands_instance):
        """Test /speak command failure."""
        commands_instance._speak_use_case.execute = AsyncMock(
            return_value={"success": False, "message": "Error occurred"}
        )
        
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        
        with patch('src.presentation.discord_commands.HAS_PYNACL', True), \
             patch('src.presentation.discord_commands.HAS_FFMPEG', True):
            await commands_instance._handle_speak(interaction, "Test")
        
        interaction.edit_original_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_config_get(self, commands_instance):
        """Test /config command to get current config."""
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.user.mention = "<@67890>"
        interaction.response = AsyncMock()
        
        await commands_instance._handle_config(interaction, None, None, None)
        
        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert "embed" in call_kwargs
    
    @pytest.mark.asyncio
    async def test_handle_config_update_engine(
        self,
        commands_instance,
        mock_config_repository
    ):
        """Test /config command to update engine."""
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.response = AsyncMock()
        
        await commands_instance._handle_config(interaction, "pyttsx3", None, None)
        
        interaction.response.send_message.assert_called_once()
        
        config = mock_config_repository.get_config(67890)
        assert config.engine == "pyttsx3"
    
    @pytest.mark.asyncio
    async def test_handle_config_failure(self, commands_instance):
        """Test /config command failure."""
        commands_instance._config_use_case.execute = Mock(
            return_value={"success": False, "message": "Config error"}
        )
        
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.response = AsyncMock()
        
        await commands_instance._handle_config(interaction, "invalid", None, None)
        
        interaction.response.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_join_no_voice_channel(self, commands_instance):
        """Test /join when user is not in voice channel."""
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.voice = None
        interaction.guild = None
        interaction.response = AsyncMock()
        
        with patch('src.presentation.discord_commands.HAS_PYNACL', True):
            await commands_instance._handle_join(interaction)
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        assert "not connected" in call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_handle_join_missing_pynacl(self, commands_instance):
        """Test /join when PyNaCl is missing."""
        interaction = Mock()
        interaction.response = AsyncMock()
        
        with patch('src.presentation.discord_commands.HAS_PYNACL', False):
            await commands_instance._handle_join(interaction)
        
        interaction.response.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_leave(self, commands_instance):
        """Test /leave command."""
        interaction = Mock()
        interaction.guild = Mock()
        voice_client = AsyncMock()
        interaction.guild.voice_client = voice_client
        interaction.response = AsyncMock()
        
        await commands_instance._handle_leave(interaction)
        
        voice_client.disconnect.assert_called_once()
        interaction.response.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_leave_not_connected(self, commands_instance):
        """Test /leave when bot is not connected."""
        interaction = Mock()
        interaction.guild = Mock()
        interaction.guild.voice_client = None
        interaction.response = AsyncMock()
        
        await commands_instance._handle_leave(interaction)
        
        interaction.response.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_about(self, commands_instance):
        """Test /about command."""
        interaction = Mock()
        interaction.response = AsyncMock()
        
        await commands_instance._handle_about(interaction)
        
        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert "embed" in call_kwargs