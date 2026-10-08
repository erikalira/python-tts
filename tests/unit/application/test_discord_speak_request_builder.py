# pyright: reportArgumentType=false
from src.application.discord_speak_request_builder import DiscordSpeakRequestBuilder
from src.application.dto import ConfigureTTSResult, TTSConfigurationData


def test_builder_creates_request_with_voice_override(mock_tts_catalog):
    config_use_case = type(
        "ConfigUseCaseStub",
        (),
        {
            "get_config": lambda self, guild_id, user_id=None: ConfigureTTSResult(
                success=True,
                guild_id=guild_id,
                config=TTSConfigurationData(
                    engine="gtts",
                    language="pt",
                    voice_id="roa/pt-br",
                    rate=210,
                ),
            )
        },
    )()

    builder = DiscordSpeakRequestBuilder(config_use_case, mock_tts_catalog)

    result = builder.build(
        text="Test",
        guild_id=67890,
        member_id=11111,
        voice_key="edge-tts:pt-br-francisca",
    )

    assert result.error_message is None
    assert result.request is not None
    assert result.request.config_override is not None
    assert result.request.config_override.engine == "edge-tts"
    assert result.request.config_override.rate == 210


def test_builder_requires_guild_id(mock_tts_catalog):
    config_use_case = type("ConfigUseCaseStub", (), {"get_config": lambda self, guild_id, user_id=None: None})()
    builder = DiscordSpeakRequestBuilder(config_use_case, mock_tts_catalog)

    result = builder.build(text="Test", guild_id=None, member_id=11111)

    assert result.request is None
    assert result.error_code == "missing_guild_id"
    assert result.error_message == "missing guild id"


def _config_use_case_stub(engine="gtts", language="pt", voice_id="roa/pt-br", rate=180):
    return type(
        "ConfigUseCaseStub",
        (),
        {
            "get_config": lambda self, guild_id, user_id=None: ConfigureTTSResult(
                success=True,
                guild_id=guild_id,
                config=TTSConfigurationData(engine=engine, language=language, voice_id=voice_id, rate=rate),
            )
        },
    )()


class TestFishAudioVoiceFallThrough:
    """A raw 32-hex reference_id is accepted where a catalog key is expected.

    Fish Audio voices are account-scoped and community-authored, so the
    application ships no catalog for them and the user supplies the id.
    """

    def test_raw_reference_id_selects_fish_audio(self, mock_tts_catalog):
        builder = DiscordSpeakRequestBuilder(_config_use_case_stub(), mock_tts_catalog)

        result = builder.build(text="oi", guild_id=123, member_id=None, voice_key="0123456789abcdef0123456789abcdef")

        assert result.error_code is None
        assert result.request is not None
        override = result.request.config_override
        assert override is not None
        assert override.engine == "fish-audio"
        assert override.voice_id == "0123456789abcdef0123456789abcdef"
        # Drives the retention notice shown on the /speak reply.
        assert result.used_supplied_provider_voice is True

    def test_raw_reference_id_preserves_stored_language_and_rate(self, mock_tts_catalog):
        """Fish ignores language, so the stored value must not be overwritten."""
        builder = DiscordSpeakRequestBuilder(_config_use_case_stub(language="en", rate=210), mock_tts_catalog)

        result = builder.build(text="oi", guild_id=123, member_id=None, voice_key="0123456789abcdef0123456789abcdef")

        assert result.request is not None
        override = result.request.config_override
        assert override is not None
        assert override.language == "en"
        assert override.rate == 210

    def test_uppercase_reference_id_is_accepted(self, mock_tts_catalog):
        builder = DiscordSpeakRequestBuilder(_config_use_case_stub(), mock_tts_catalog)

        result = builder.build(text="oi", guild_id=123, member_id=None, voice_key="0123456789ABCDEF0123456789ABCDEF")

        assert result.error_code is None
        assert result.request is not None
        assert result.request.config_override is not None
        assert result.request.config_override.engine == "fish-audio"

    def test_catalog_key_still_wins_over_the_fall_through(self, mock_tts_catalog):
        builder = DiscordSpeakRequestBuilder(_config_use_case_stub(), mock_tts_catalog)

        result = builder.build(text="oi", guild_id=123, member_id=None, voice_key="edge-tts:pt-br-francisca")

        assert result.request is not None
        override = result.request.config_override
        assert override is not None
        # The new branch rebuilds the TTSConfig, so every field the catalog
        # option supplies has to survive, not just the engine.
        assert override.engine == "edge-tts"
        assert override.language == "pt-BR"
        assert override.voice_id == "pt-BR-FranciscaNeural"
        assert result.used_supplied_provider_voice is False

    def test_non_hex_voice_is_still_rejected(self, mock_tts_catalog):
        builder = DiscordSpeakRequestBuilder(_config_use_case_stub(), mock_tts_catalog)

        result = builder.build(text="oi", guild_id=123, member_id=None, voice_key="definitely-not-a-voice")

        assert result.error_code == "invalid_voice"
        assert result.request is None


class TestSuppliedProviderVoiceSignal:
    """The flag that makes /speak disclose the third-party hop."""

    def test_pasted_reference_id_is_stripped_before_transmission(self, mock_tts_catalog):
        builder = DiscordSpeakRequestBuilder(_config_use_case_stub(), mock_tts_catalog)

        pasted = "  0123456789abcdef0123456789abcdef\n"
        result = builder.build(text="oi", guild_id=123, member_id=None, voice_key=pasted)

        assert result.request is not None
        override = result.request.config_override
        assert override is not None
        # The canonical value: this override is what reaches the engine and is
        # sent to the provider as reference_id.
        assert override.voice_id == "0123456789abcdef0123456789abcdef"
        assert override.voice_id.strip() == override.voice_id

    def test_no_voice_key_does_not_signal_a_supplied_voice(self, mock_tts_catalog):
        builder = DiscordSpeakRequestBuilder(_config_use_case_stub(), mock_tts_catalog)

        result = builder.build(text="oi", guild_id=123, member_id=None)

        assert result.used_supplied_provider_voice is False
        assert result.request is not None
        assert result.request.config_override is None

    def test_rejected_voice_does_not_signal_a_supplied_voice(self, mock_tts_catalog):
        builder = DiscordSpeakRequestBuilder(_config_use_case_stub(), mock_tts_catalog)

        result = builder.build(text="oi", guild_id=123, member_id=None, voice_key="nope")

        assert result.used_supplied_provider_voice is False
