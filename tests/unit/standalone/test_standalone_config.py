import json
from pathlib import Path

from src.standalone.config.standalone_config import (
    ConfigurationRepository,
    ConfigurationValidator,
    EnvironmentUpdater,
    HotkeyConfig,
    StandaloneConfig,
    get_config_directory,
)


def test_get_config_directory_linux(monkeypatch, tmp_path):
    monkeypatch.setattr("src.standalone.config.standalone_config.os.name", "posix")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    config_dir = get_config_directory()

    assert config_dir == tmp_path / ".config" / "tts-hotkey"
    assert config_dir.exists()


def test_configuration_repository_loads_defaults_when_file_missing(tmp_path):
    repo = ConfigurationRepository(tmp_path / "config.json")

    config = repo.load()

    assert isinstance(config, StandaloneConfig)
    assert config.tts.engine == "gtts"
    assert config.hotkey.keys == "{text}"


def test_configuration_repository_save_and_load_roundtrip(tmp_path):
    config_file = tmp_path / "config.json"
    repo = ConfigurationRepository(config_file)
    config = StandaloneConfig.create_default()
    config.discord.member_id = "123"
    config.discord.guild_id = "456"
    config.hotkey.trigger_open = "["
    config.hotkey.trigger_close = "]"

    assert repo.save(config) is True

    saved_data = json.loads(config_file.read_text(encoding="utf-8"))
    assert saved_data["discord_member_id"] == "123"
    assert saved_data["discord_guild_id"] == "456"
    assert saved_data["trigger_open"] == "["

    loaded = repo.load()
    assert loaded.discord.member_id == "123"
    assert loaded.discord.guild_id == "456"
    assert loaded.hotkey.keys == "[text]"


def test_configuration_repository_returns_defaults_on_invalid_json(tmp_path, capsys):
    config_file = tmp_path / "config.json"
    config_file.write_text("{invalid", encoding="utf-8")

    repo = ConfigurationRepository(config_file)
    config = repo.load()

    assert config.tts.engine == "gtts"
    assert "Erro ao carregar configuração" in capsys.readouterr().out


def test_environment_updater_sets_expected_variables(monkeypatch):
    config = StandaloneConfig.create_default()
    config.discord.bot_url = "http://localhost:10000"
    config.discord.guild_id = "44"
    config.discord.channel_id = "55"
    config.discord.member_id = "99"
    config.tts.output_device = "Speaker"

    monkeypatch.delenv("DISCORD_BOT_URL", raising=False)
    monkeypatch.delenv("DISCORD_GUILD_ID", raising=False)
    monkeypatch.delenv("DISCORD_CHANNEL_ID", raising=False)
    monkeypatch.delenv("DISCORD_MEMBER_ID", raising=False)
    monkeypatch.delenv("TTS_OUTPUT_DEVICE", raising=False)

    EnvironmentUpdater.update_from_config(config)

    assert config.discord.bot_url == "http://localhost:10000"
    assert config.discord.guild_id == "44"


def test_configuration_validator_reports_invalid_values():
    config = StandaloneConfig.create_default()
    config.discord.member_id = "abc"
    config.discord.guild_id = "def"
    config.tts.rate = 10
    config.network.request_timeout = 0
    config.network.max_text_length = 3000

    is_valid, errors = ConfigurationValidator.validate(config)

    assert is_valid is False
    assert len(errors) == 5


def test_configuration_validator_is_configured_requires_member_id():
    config = StandaloneConfig.create_default()
    config.discord.member_id = "   "
    assert ConfigurationValidator.is_configured(config) is False

    config.discord.member_id = "123456"
    assert ConfigurationValidator.is_configured(config) is False

    config.discord.guild_id = "654321"
    assert ConfigurationValidator.is_configured(config) is True


def test_hotkey_config_keys_property():
    hotkey = HotkeyConfig(trigger_open="<", trigger_close=">")
    assert hotkey.keys == "<text>"
