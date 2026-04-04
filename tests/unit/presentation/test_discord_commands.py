"""Tests for Discord commands presentation layer."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from discord import app_commands
from src.presentation.discord_commands import DiscordCommands
from src.application.use_cases import (
    ConfigureTTSUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
    SpeakTextUseCase,
)


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
        join_use_case = JoinVoiceChannelUseCase(mock_channel_repository)
        leave_use_case = LeaveVoiceChannelUseCase(mock_channel_repository)
        
        tree = Mock(spec=app_commands.CommandTree)
        tree.command = Mock(return_value=lambda func: func)
        
        return DiscordCommands(
            tree,
            speak_use_case,
            config_use_case,
            join_use_case,
            leave_use_case,
        )
    
    def test_initialization(self, commands_instance):
        """Test DiscordCommands initialization."""
        assert commands_instance._tree is not None
        assert commands_instance._speak_use_case is not None
        assert commands_instance._config_use_case is not None
        assert commands_instance._join_use_case is not None
        assert commands_instance._leave_use_case is not None
    
    @pytest.mark.asyncio
    async def test_handle_speak_command_success(
        self,
        commands_instance,
        mock_tts_engine,
        mock_channel_repository
    ):
        """Test successful /speak command."""
        commands_instance._speak_use_case.execute = AsyncMock(
            return_value={"success": True, "code": "ok", "queued": False}
        )
        
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.delete_original_response = AsyncMock()
        
        with patch('src.presentation.discord_commands.HAS_PYNACL', True), \
             patch('src.presentation.discord_commands.HAS_DAVEY', True), \
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
            return_value={"success": False, "code": "unknown_error", "queued": False}
        )
        
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        
        with patch('src.presentation.discord_commands.HAS_PYNACL', True), \
             patch('src.presentation.discord_commands.HAS_DAVEY', True), \
             patch('src.presentation.discord_commands.HAS_FFMPEG', True):
            await commands_instance._handle_speak(interaction, "Test")
        
        interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_speak_shutdown_fallback_ignores_non_http_send_errors(self, commands_instance):
        """Test /speak suppresses non-HTTP interaction update failures during shutdown."""
        commands_instance._speak_use_case.execute = AsyncMock(
            side_effect=RuntimeError("interpreter shutdown")
        )

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.user.name = "TestUser"
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock(
            side_effect=RuntimeError("cannot schedule new futures after interpreter shutdown")
        )

        with patch('src.presentation.discord_commands.HAS_PYNACL', True), \
             patch('src.presentation.discord_commands.HAS_DAVEY', True), \
             patch('src.presentation.discord_commands.HAS_FFMPEG', True):
            await commands_instance._handle_speak(interaction, "Test")

        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()
        sent_content = interaction.edit_original_response.call_args.kwargs["content"]
        assert "Bot est" in sent_content
        assert "inativo" in sent_content
    
    @pytest.mark.asyncio
    async def test_handle_config_get(self, commands_instance):
        """Test /config command to get current config."""
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.user.mention = "<@67890>"
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.guild.name = "Test Guild"
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
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.guild.name = "Test Guild"
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        
        await commands_instance._handle_config(interaction, "pyttsx3", None, None)
        
        # Should call defer and then edit_original_response
        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()
        
        config = mock_config_repository.get_config(67890)
        assert config.engine == "pyttsx3"
    
    @pytest.mark.asyncio
    async def test_handle_config_failure(self, commands_instance):
        """Test /config command failure."""
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.guild.name = "Test Guild"
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        
        # Mock update to fail
        commands_instance._config_use_case.update_config_async = AsyncMock(
            return_value={"success": False, "message": "Config error"}
        )
        
        await commands_instance._handle_config(interaction, "invalid", None, None)
        
        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_join_no_voice_channel(self, commands_instance):
        """Test /join when user is not in voice channel."""
        commands_instance._join_use_case.execute = AsyncMock(
            return_value={"success": False, "code": "user_not_in_channel"}
        )
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 123
        interaction.guild = Mock()
        interaction.guild.id = 456
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        
        with patch('src.presentation.discord_commands.HAS_PYNACL', True), \
             patch('src.presentation.discord_commands.HAS_DAVEY', True), \
             patch('src.presentation.discord_commands.HAS_FFMPEG', True):
            await commands_instance._handle_join(interaction)
        
        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()
        call_args = interaction.edit_original_response.call_args
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
    async def test_handle_join_success(self, commands_instance):
        """Test /join delegates success handling to the use case."""
        commands_instance._join_use_case.execute = AsyncMock(
            return_value={"success": True, "code": "ok"}
        )

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 123
        interaction.guild = Mock()
        interaction.guild.id = 456
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        with patch('src.presentation.discord_commands.HAS_PYNACL', True), \
             patch('src.presentation.discord_commands.HAS_DAVEY', True), \
             patch('src.presentation.discord_commands.HAS_FFMPEG', True):
            await commands_instance._handle_join(interaction)

        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once_with(content='Joined your channel.')
    
    @pytest.mark.asyncio
    async def test_handle_leave(self, commands_instance):
        """Test /leave command."""
        commands_instance._leave_use_case.execute = AsyncMock(
            return_value={"success": True, "code": "ok"}
        )
        interaction = Mock()
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        
        await commands_instance._handle_leave(interaction)
        
        interaction.response.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_leave_not_connected(self, commands_instance):
        """Test /leave when bot is not connected."""
        commands_instance._leave_use_case.execute = AsyncMock(
            return_value={"success": False, "code": "not_connected"}
        )
        interaction = Mock()
        interaction.guild = Mock()
        interaction.guild.id = 67890
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
