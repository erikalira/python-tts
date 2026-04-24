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
        text="Teste",
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

    result = builder.build(text="Teste", guild_id=None, member_id=11111)

    assert result.request is None
    assert "servidor" in result.error_message.lower()
