import asyncio

from src.application.dto import ConfigureTTSResult, TTSConfigurationData
from src.application.use_cases import ConfigureTTSUseCase
from src.core.entities import TTSConfig
from src.infrastructure.persistence.config_storage import GuildConfigRepository, JSONConfigStorage


def test_guild_config_repository_get_config_loads_persisted_value_on_cache_miss(tmp_path):
    storage = JSONConfigStorage(storage_dir=str(tmp_path))
    default_config = TTSConfig(engine="gtts", language="pt", voice_id="roa/pt-br", rate=180)

    saved = TTSConfig(engine="pyttsx3", language="en", voice_id="en-us", rate=220)
    save_result = asyncio.run(storage.save(123, saved))
    assert save_result is True

    repo = GuildConfigRepository(default_config=default_config, storage=storage)

    loaded = repo.get_config(123)

    assert loaded.engine == "pyttsx3"
    assert loaded.language == "en"
    assert loaded.voice_id == "en-us"
    assert loaded.rate == 220


def test_update_config_async_preserves_persisted_fields_after_cache_miss(tmp_path):
    storage = JSONConfigStorage(storage_dir=str(tmp_path))
    default_config = TTSConfig(engine="gtts", language="pt", voice_id="roa/pt-br", rate=180)

    original = TTSConfig(engine="pyttsx3", language="es", voice_id="custom-voice", rate=240)
    save_result = asyncio.run(storage.save(456, original))
    assert save_result is True

    repo = GuildConfigRepository(default_config=default_config, storage=storage)
    use_case = ConfigureTTSUseCase(config_repository=repo)

    result = asyncio.run(use_case.update_config_async(guild_id=456, language="fr"))

    assert result == ConfigureTTSResult(
        success=True,
        guild_id=456,
        config=TTSConfigurationData(
            engine="pyttsx3",
            language="fr",
            voice_id="custom-voice",
            rate=240,
        ),
    )
    assert result.config is not None
    assert result.config.engine == "pyttsx3"
    assert result.config.language == "fr"
    assert result.config.voice_id == "custom-voice"
    assert result.config.rate == 240

    persisted = asyncio.run(storage.load(456))
    assert persisted is not None
    assert persisted.engine == "pyttsx3"
    assert persisted.language == "fr"
    assert persisted.voice_id == "custom-voice"
    assert persisted.rate == 240
