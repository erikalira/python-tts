"""Tests for Discord commands presentation layer."""
import pytest
from unittest.mock import Mock, AsyncMock
import discord
from discord import app_commands
from src.application.dto import (
    ConfigureTTSResult,
    JoinVoiceChannelResult,
    LeaveVoiceChannelResult,
    SpeakTextResult,
)
from src.application.interface_language_preferences import ConfigureInterfaceLanguageUseCase
from src.infrastructure.rate_limiting import InMemoryRateLimiter
from src.application.voice_runtime import VoiceRuntimeStatus
from src.presentation.discord_commands import DiscordCommands
from src.presentation.discord_i18n import (
    DiscordCommandTranslator,
    DiscordLocaleResolver,
    command_text,
    supported_locales,
    supported_message_locales,
)
from src.application.use_cases import (
    ConfigureTTSUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
)


class FakeInterfaceLanguagePreferenceRepository:
    def __init__(self):
        self.user_languages = {}
        self.guild_languages = {}
        self.calls = []

    def get_user_language(self, guild_id: int, user_id: int) -> str | None:
        return self.user_languages.get((guild_id, user_id))

    def get_guild_language(self, guild_id: int) -> str | None:
        return self.guild_languages.get(guild_id)

    async def set_user_language(self, guild_id: int, user_id: int, locale: str) -> bool:
        self.calls.append("set_user_language")
        self.user_languages[(guild_id, user_id)] = locale
        return True

    async def set_guild_language(self, guild_id: int, locale: str) -> bool:
        self.calls.append("set_guild_language")
        self.guild_languages[guild_id] = locale
        return True

    async def delete_user_language(self, guild_id: int, user_id: int) -> bool:
        self.calls.append("delete_user_language")
        self.user_languages.pop((guild_id, user_id), None)
        return True

    async def delete_guild_language(self, guild_id: int) -> bool:
        self.calls.append("delete_guild_language")
        self.guild_languages.pop(guild_id, None)
        return True


class TestDiscordCommands:
    """Test DiscordCommands presentation layer."""

    @pytest.fixture
    def voice_runtime_availability(self):
        availability = Mock()
        availability.get_status.return_value = VoiceRuntimeStatus(
            ffmpeg_available=True,
            pynacl_installed=True,
            davey_installed=True,
        )
        return availability
    
    @pytest.fixture
    def commands_instance(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
        voice_runtime_availability,
        mock_tts_catalog,
    ):
        """Create a DiscordCommands instance for testing."""
        speak_use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
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
            voice_runtime_availability,
            mock_tts_catalog,
        )
    
    def test_initialization(self, commands_instance):
        """Test DiscordCommands initialization."""
        assert commands_instance._tree is not None
        assert commands_instance._speak_use_case is not None
        assert commands_instance._config_use_case is not None
        assert commands_instance._join_use_case is not None
        assert commands_instance._leave_use_case is not None

    @pytest.mark.asyncio
    async def test_handle_language_updates_user_interface_language(self, commands_instance):
        repository = FakeInterfaceLanguagePreferenceRepository()
        commands_instance._interface_language_use_case = ConfigureInterfaceLanguageUseCase(repository)

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.locale = discord.Locale.american_english
        interaction.guild_locale = discord.Locale.american_english
        interaction.guild = Mock()
        interaction.guild.id = 12345
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        async def record_defer(*args, **kwargs):
            repository.calls.append("defer")

        interaction.response.defer.side_effect = record_defer

        await commands_instance._handle_language(interaction, "pt-BR")

        assert repository.user_languages[(12345, 67890)] == "pt-BR"
        assert repository.calls == ["defer", "set_user_language"]
        interaction.response.defer.assert_called_once_with(ephemeral=True, thinking=True)
        interaction.response.send_message.assert_not_called()
        interaction.edit_original_response.assert_called_once()
        assert "portugu" in interaction.edit_original_response.call_args.kwargs["content"].lower()

    @pytest.mark.asyncio
    async def test_handle_language_auto_resets_user_interface_language(self, commands_instance):
        repository = FakeInterfaceLanguagePreferenceRepository()
        repository.user_languages[(12345, 67890)] = "pt-BR"
        commands_instance._interface_language_use_case = ConfigureInterfaceLanguageUseCase(repository)

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.locale = discord.Locale.american_english
        interaction.guild_locale = discord.Locale.brazil_portuguese
        interaction.guild = Mock()
        interaction.guild.id = 12345
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        async def record_defer(*args, **kwargs):
            repository.calls.append("defer")

        interaction.response.defer.side_effect = record_defer

        await commands_instance._handle_language(interaction, "auto")

        assert (12345, 67890) not in repository.user_languages
        assert repository.calls == ["defer", "delete_user_language"]
        interaction.response.defer.assert_called_once_with(ephemeral=True, thinking=True)
        interaction.response.send_message.assert_not_called()
        assert "discord language" in interaction.edit_original_response.call_args.kwargs["content"].lower()

    @pytest.mark.asyncio
    async def test_handle_server_language_requires_manage_guild(self, commands_instance):
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.guild_permissions = Mock(manage_guild=False)
        interaction.guild = Mock()
        interaction.guild.id = 12345
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_server_language(interaction, "pt-BR")

        interaction.response.send_message.assert_called_once()
        interaction.response.defer.assert_not_called()
        interaction.edit_original_response.assert_not_called()
        assert "permission" in interaction.response.send_message.call_args.args[0].lower()

    @pytest.mark.asyncio
    async def test_handle_server_language_updates_guild_interface_language(self, commands_instance):
        repository = FakeInterfaceLanguagePreferenceRepository()
        commands_instance._interface_language_use_case = ConfigureInterfaceLanguageUseCase(repository)

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.user.guild_permissions = Mock(manage_guild=True)
        interaction.locale = discord.Locale.american_english
        interaction.guild_locale = discord.Locale.american_english
        interaction.guild = Mock()
        interaction.guild.id = 12345
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        async def record_defer(*args, **kwargs):
            repository.calls.append("defer")

        interaction.response.defer.side_effect = record_defer

        await commands_instance._handle_server_language(interaction, "pt-BR")

        assert repository.guild_languages[12345] == "pt-BR"
        assert repository.calls == ["defer", "set_guild_language"]
        interaction.response.defer.assert_called_once_with(ephemeral=True, thinking=True)
        interaction.response.send_message.assert_not_called()
        assert "server default interface language" in interaction.edit_original_response.call_args.kwargs["content"].lower()

    def test_resolve_locale_prefers_user_preference_then_discord_locale_then_guild_preference(
        self,
        commands_instance,
    ):
        repository = FakeInterfaceLanguagePreferenceRepository()
        repository.user_languages[(12345, 67890)] = "pt-BR"
        repository.guild_languages[12345] = "en-US"
        commands_instance._interface_language_use_case = ConfigureInterfaceLanguageUseCase(repository)

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.locale = discord.Locale.american_english
        interaction.guild_locale = discord.Locale.american_english
        interaction.guild = Mock()
        interaction.guild.id = 12345

        assert commands_instance._resolve_locale(interaction) == "pt-BR"

        repository.user_languages.clear()

        assert commands_instance._resolve_locale(interaction) == "en-US"

        interaction.locale = discord.Locale.japanese

        assert commands_instance._resolve_locale(interaction) == "en-US"
    
    @pytest.mark.asyncio
    async def test_handle_speak_command_success(
        self,
        commands_instance,
        mock_tts_engine,
        mock_channel_repository
    ):
        """Test successful /speak command."""
        commands_instance._speak_use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="ok", queued=False)
        )
        
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.delete_original_response = AsyncMock()
        
        await commands_instance._handle_speak(interaction, "Test message")
        
        interaction.response.defer.assert_called_once()
        interaction.delete_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_speak_hides_response_when_result_starts_immediately(self, commands_instance):
        commands_instance._speak_use_case.execute = AsyncMock(
            return_value=SpeakTextResult(
                success=True,
                code="queued",
                queued=True,
                starts_immediately=True,
                position=0,
                queue_size=1,
            )
        )

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.user.name = "User"
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.delete_original_response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_speak(interaction, "Test message")

        interaction.response.defer.assert_called_once()
        interaction.delete_original_response.assert_called_once()
        interaction.edit_original_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_speak_keeps_queue_message_when_there_is_backlog(self, commands_instance):
        commands_instance._speak_use_case.execute = AsyncMock(
            return_value=SpeakTextResult(
                success=True,
                code="queued",
                queued=True,
                starts_immediately=False,
                position=1,
                queue_size=2,
            )
        )

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.user.name = "User"
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.delete_original_response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_speak(interaction, "Test message")

        interaction.response.defer.assert_called_once()
        interaction.delete_original_response.assert_not_called()
        interaction.edit_original_response.assert_called_once()
        content = interaction.edit_original_response.call_args.kwargs["content"].lower()
        assert "queue" in content
        assert "entered" in content
    
    @pytest.mark.asyncio
    async def test_handle_speak_missing_dependencies(self, commands_instance):
        """Test /speak when dependencies are missing."""
        interaction = Mock()
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        
        commands_instance._voice_runtime_availability.get_status.return_value = VoiceRuntimeStatus(
            ffmpeg_available=False,
            pynacl_installed=True,
            davey_installed=True,
        )
        await commands_instance._handle_speak(interaction, "Test")

        interaction.edit_original_response.assert_called_once()
        assert "unavailable" in interaction.edit_original_response.call_args.kwargs["content"].lower()

    @pytest.mark.asyncio
    async def test_handle_speak_rate_limits_by_guild_and_user(self, commands_instance):
        commands_instance._rate_limiter = InMemoryRateLimiter(clock=lambda: 100.0)
        commands_instance._rate_limit_max_requests = 1
        commands_instance._rate_limit_window_seconds = 10
        commands_instance._speak_use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="ok", queued=False)
        )

        interaction = Mock()
        interaction.id = 123
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.user.name = "User"
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.delete_original_response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_speak(interaction, "Test message")
        await commands_instance._handle_speak(interaction, "Test message")

        assert commands_instance._speak_use_case.execute.await_count == 1
        assert interaction.edit_original_response.await_count == 1
        content = interaction.edit_original_response.await_args.kwargs["content"].lower()
        assert "requests" in content

    @pytest.mark.asyncio
    async def test_handle_speak_ignores_expired_interaction_before_defer(self, commands_instance):
        commands_instance._speak_use_case.execute = AsyncMock()
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.user.name = "User"
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.response.defer = AsyncMock(side_effect=discord.NotFound(Mock(), {"code": 10062, "message": "Unknown interaction"}))
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_speak(interaction, "Test")

        interaction.response.defer.assert_awaited_once()
        commands_instance._speak_use_case.execute.assert_not_awaited()
        interaction.edit_original_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_speak_ignores_already_acknowledged_interaction_before_defer(self, commands_instance):
        commands_instance._speak_use_case.execute = AsyncMock()
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.user.name = "User"
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = Mock()
        interaction.response.is_done = Mock(return_value=False)
        interaction.response.defer = AsyncMock(
            side_effect=discord.HTTPException(
                Mock(),
                {"code": 40060, "message": "Interaction has already been acknowledged."},
            )
        )
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_speak(interaction, "Test")

        interaction.response.defer.assert_awaited_once()
        commands_instance._speak_use_case.execute.assert_not_awaited()
        interaction.edit_original_response.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_speak_failure(self, commands_instance):
        """Test /speak command failure."""
        commands_instance._speak_use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=False, code="unknown_error", queued=False)
        )
        
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        
        await commands_instance._handle_speak(interaction, "Test")
        
        interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_speak_with_voice_override_passes_request_config(self, commands_instance):
        commands_instance._speak_use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="ok", queued=False)
        )

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 11111
        interaction.user.name = "User"
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.response = AsyncMock()
        interaction.delete_original_response = AsyncMock()

        await commands_instance._handle_speak(interaction, "Test message", "edge-tts:pt-br-francisca")

        request = commands_instance._speak_use_case.execute.await_args.args[0]
        assert request.config_override is not None
        assert request.config_override.engine == "edge-tts"
        assert request.config_override.voice_id == "pt-BR-FranciscaNeural"

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

        await commands_instance._handle_speak(interaction, "Test")

        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()
        sent_content = interaction.edit_original_response.call_args.kwargs["content"]
        assert "Bot is inactive" in sent_content
    
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
        
        await commands_instance._handle_config(interaction, None)
        
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
        
        await commands_instance._handle_config(interaction, "pyttsx3:david")
        
        # Should call defer and then edit_original_response
        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()
        
        config = mock_config_repository.get_config(67890, user_id=67890)
        assert config.engine == "pyttsx3"
        assert config.voice_id == "David"
    
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
            return_value=ConfigureTTSResult(success=False, message="Config error")
        )
        
        await commands_instance._handle_config(interaction, "invalid")
        
        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_server_config_requires_manage_guild(self, commands_instance):
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.user.guild_permissions = Mock(manage_guild=False)
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.guild.name = "Test Guild"
        interaction.response = AsyncMock()

        await commands_instance._handle_server_config(interaction, None)

        interaction.response.send_message.assert_called_once()
        assert "permission" in interaction.response.send_message.call_args.args[0].lower()

    @pytest.mark.asyncio
    async def test_handle_server_config_update_engine(
        self,
        commands_instance,
        mock_config_repository
    ):
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.user.guild_permissions = Mock(manage_guild=True)
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.guild.name = "Test Guild"
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_server_config(interaction, "pyttsx3:david")

        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()

        config = mock_config_repository.get_config(67890)
        assert config.engine == "pyttsx3"
        assert config.voice_id == "David"

    @pytest.mark.asyncio
    async def test_handle_config_reset(self, commands_instance, mock_config_repository):
        await commands_instance._config_use_case.update_config_async(
            guild_id=67890,
            user_id=67890,
            voice_id="Maria",
        )

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.guild.name = "Test Guild"
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_config_reset(interaction)

        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_server_config_reset(self, commands_instance):
        await commands_instance._config_use_case.update_config_async(
            guild_id=67890,
            voice_id="David",
        )

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 67890
        interaction.user.guild_permissions = Mock(manage_guild=True)
        interaction.guild = Mock()
        interaction.guild.id = 67890
        interaction.guild.name = "Test Guild"
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_server_config_reset(interaction)

        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_join_no_voice_channel(self, commands_instance):
        """Test /join when user is not in voice channel."""
        commands_instance._join_use_case.execute = AsyncMock(
            return_value=JoinVoiceChannelResult(success=False, code="user_not_in_channel")
        )
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 123
        interaction.guild = Mock()
        interaction.guild.id = 456
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        
        await commands_instance._handle_join(interaction)
        
        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once()
        call_kwargs = interaction.edit_original_response.call_args.kwargs
        assert "not connected" in call_kwargs["content"].lower()
    
    @pytest.mark.asyncio
    async def test_handle_join_missing_pynacl(self, commands_instance):
        """Test /join when PyNaCl is missing."""
        interaction = Mock()
        interaction.response = AsyncMock()
        
        commands_instance._voice_runtime_availability.get_status.return_value = VoiceRuntimeStatus(
            ffmpeg_available=False,
            pynacl_installed=False,
            davey_installed=True,
        )
        await commands_instance._handle_join(interaction)

        interaction.response.send_message.assert_called_once()
        assert "unavailable" in interaction.response.send_message.call_args.args[0].lower()

    @pytest.mark.asyncio
    async def test_handle_join_success(self, commands_instance):
        """Test /join delegates success handling to the use case."""
        commands_instance._join_use_case.execute = AsyncMock(
            return_value=JoinVoiceChannelResult(success=True, code="ok")
        )

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 123
        interaction.guild = Mock()
        interaction.guild.id = 456
        interaction.response = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        await commands_instance._handle_join(interaction)

        interaction.response.defer.assert_called_once()
        interaction.edit_original_response.assert_called_once_with(content='Joined your channel.')
    
    @pytest.mark.asyncio
    async def test_handle_leave(self, commands_instance):
        """Test /leave command."""
        commands_instance._leave_use_case.execute = AsyncMock(
            return_value=LeaveVoiceChannelResult(success=True, code="ok")
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
            return_value=LeaveVoiceChannelResult(success=False, code="not_connected")
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

    @pytest.mark.asyncio
    async def test_autocomplete_voice_uses_catalog(self, commands_instance):
        interaction = Mock()

        choices = await commands_instance._autocomplete_voice(interaction, "davi")

        assert choices
        assert choices[0].value == "pyttsx3:david"

    @pytest.mark.asyncio
    async def test_autocomplete_voice_returns_edge_tts_profiles(self, commands_instance):
        interaction = Mock()

        choices = await commands_instance._autocomplete_voice(interaction, "francisca")

        assert choices
        assert choices[0].value == "edge-tts:pt-br-francisca"

    def test_config_embed_warns_when_pyttsx3_voice_is_missing(self, commands_instance):
        result = ConfigureTTSResult(
            success=True,
            guild_id=67890,
            config=type("Cfg", (), {"engine": "pyttsx3", "language": "en", "voice_id": "UnknownVoice", "rate": 180})(),
        )

        embed = commands_instance._config_handler._build_updated_config_embed("Test Guild", 67890, result)

        resolution_field = next(field for field in embed.fields if field.name == "Voice Resolution")
        assert "default windows voice" in resolution_field.value.lower()

    def test_config_embed_describes_edge_tts_voice(self, commands_instance):
        result = ConfigureTTSResult(
            success=True,
            guild_id=67890,
            config=type("Cfg", (), {"engine": "edge-tts", "language": "pt-BR", "voice_id": "pt-BR-FranciscaNeural", "rate": 180})(),
        )

        embed = commands_instance._config_handler._build_updated_config_embed("Test Guild", 67890, result)

        resolution_field = next(field for field in embed.fields if field.name == "Voice Resolution")
        assert "edge tts" in resolution_field.value.lower()
        assert "francisca" in resolution_field.value.lower()


class TestDiscordI18n:
    def test_message_catalog_has_same_keys_for_all_supported_locales(self):
        catalogs = supported_message_locales()
        expected_keys = set(catalogs["en-US"])

        for locale, messages in catalogs.items():
            assert set(messages) == expected_keys, locale

    def test_command_translations_have_same_keys_for_all_supported_locales(self):
        translations = supported_locales()
        expected_keys = set(translations["en-US"])

        for locale, commands in translations.items():
            assert set(commands) == expected_keys, locale

    def test_locale_resolver_prefers_user_locale_over_guild_locale(self):
        interaction = Mock()
        interaction.guild_locale = discord.Locale.brazil_portuguese
        interaction.locale = discord.Locale.american_english

        assert DiscordLocaleResolver().resolve(interaction) == "en-US"

    def test_locale_resolver_falls_back_to_user_locale(self):
        interaction = Mock()
        interaction.guild_locale = discord.Locale.japanese
        interaction.locale = discord.Locale.american_english

        assert DiscordLocaleResolver().resolve(interaction) == "en-US"

    def test_locale_resolver_falls_back_to_guild_locale(self):
        interaction = Mock()
        interaction.guild_locale = discord.Locale.brazil_portuguese
        interaction.locale = discord.Locale.japanese

        assert DiscordLocaleResolver().resolve(interaction) == "pt-BR"

    def test_locale_resolver_uses_ordered_candidates(self):
        assert DiscordLocaleResolver().resolve_candidates(
            None,
            discord.Locale.japanese,
            "pt-BR",
            "en-US",
        ) == "pt-BR"

    def test_locale_resolver_defaults_to_english_when_no_locale_is_supported(self):
        interaction = Mock()
        interaction.guild_locale = discord.Locale.japanese
        interaction.locale = discord.Locale.korean

        assert DiscordLocaleResolver().resolve(interaction) == "en-US"

    @pytest.mark.asyncio
    async def test_command_translator_translates_command_metadata(self):
        translator = DiscordCommandTranslator()

        translated = await translator.translate(
            command_text("cmd.speak.description"),
            discord.Locale.brazil_portuguese,
            Mock(),
        )

        assert translated == "Faz o bot falar o texto informado no canal de voz"
# pyright: reportArgumentType=false, reportOptionalMemberAccess=false
