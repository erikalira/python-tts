import json
import os

from src.desktop.config.desktop_config import (
    ConfigurationRepository,
    ConfigurationValidator,
    DesktopAppConfig,
    EnvironmentUpdater,
    HotkeyConfig,
    get_default_discord_bot_url,
    get_config_directory,
)


def test_get_config_directory_windows(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    config_dir = get_config_directory()

    assert config_dir == tmp_path / "DesktopApp"
    assert config_dir.exists()


def test_get_config_directory_windows_reuses_legacy_directory(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    legacy_dir = tmp_path / "TTS-Hotkey"
    legacy_dir.mkdir()

    config_dir = get_config_directory()

    assert config_dir == legacy_dir
    assert config_dir.exists()


def test_configuration_repository_loads_defaults_when_file_missing(tmp_path):
    repo = ConfigurationRepository(tmp_path / "config.json")

    config = repo.load()

    assert isinstance(config, DesktopAppConfig)
    assert config.tts.engine == "gtts"
    assert config.interface.local_tts_enabled is False
    assert config.hotkey.keys == "{text}"


def test_configuration_repository_save_and_load_roundtrip(tmp_path):
    config_file = tmp_path / "config.json"
    repo = ConfigurationRepository(config_file)
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "123"
    config.hotkey.trigger_open = "["
    config.hotkey.trigger_close = "]"
    config.interface.local_tts_enabled = True

    assert repo.save(config) is True

    saved_data = json.loads(config_file.read_text(encoding="utf-8"))
    assert saved_data["discord_member_id"] == "123"
    assert saved_data["trigger_open"] == "["
    assert saved_data["local_tts_enabled"] is True

    loaded = repo.load()
    assert loaded.discord.member_id == "123"
    assert loaded.interface.local_tts_enabled is True
    assert loaded.hotkey.keys == "[text]"


def test_configuration_repository_returns_defaults_on_invalid_json(capsys, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("{invalid", encoding="utf-8")

    repo = ConfigurationRepository(config_file)
    config = repo.load()

    assert config.tts.engine == "gtts"
    assert config.interface.local_tts_enabled is False
    assert "Erro ao carregar configura" in capsys.readouterr().out


def test_environment_updater_sets_expected_variables(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = "99"
    config.tts.output_device = "Speaker"

    monkeypatch.delenv("DISCORD_BOT_URL", raising=False)
    monkeypatch.delenv("DISCORD_MEMBER_ID", raising=False)
    monkeypatch.delenv("TTS_OUTPUT_DEVICE", raising=False)

    EnvironmentUpdater.update_from_config(config)

    assert config.discord.bot_url == get_default_discord_bot_url()
    assert os.environ["DISCORD_BOT_URL"] == get_default_discord_bot_url()
    assert os.environ["DISCORD_MEMBER_ID"] == "99"


def test_environment_updater_removes_optional_identifiers_when_missing(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = None
    config.tts.output_device = None

    monkeypatch.setenv("DISCORD_MEMBER_ID", "member")
    monkeypatch.setenv("TTS_OUTPUT_DEVICE", "Speaker")

    EnvironmentUpdater.update_from_config(config)

    assert "DISCORD_MEMBER_ID" not in os.environ


def test_configuration_validator_reports_invalid_values():
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "abc"
    config.tts.rate = 10
    config.network.request_timeout = 0
    config.network.max_text_length = 3000

    is_valid, errors = ConfigurationValidator.validate(config)

    assert is_valid is False
    assert len(errors) == 4


def test_configuration_validator_is_configured_requires_member_id():
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "   "
    assert ConfigurationValidator.is_configured(config) is False

    config.discord.member_id = "123456"
    assert ConfigurationValidator.is_configured(config) is True


def test_hotkey_config_keys_property():
    hotkey = HotkeyConfig(trigger_open="<", trigger_close=">")
    assert hotkey.keys == "<text>"
