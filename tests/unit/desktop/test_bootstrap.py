from unittest.mock import Mock

from src.desktop.app import bootstrap
from src.desktop.app.desktop_app import DesktopApp
from src.desktop.config.desktop_config import DesktopAppConfig


def test_create_desktop_application_wires_desktop_dependencies(monkeypatch):
    config_repository = Mock(name="config_repository")
    config_service = Mock(name="config_service")

    class FakeConfigurationRepository:
        def __new__(cls):
            return config_repository

    class FakeConfigurationService:
        def __new__(cls, prefer_gui):
            assert prefer_gui is True
            return config_service

    class FakeKeyboardBackend:
        def __init__(self):
            self.marker = object()

    class FakeBotClient:
        def __init__(self, config):
            self.config = config

    class FakePyttsx3Adapter:
        pass

    class FakeLocalEngine:
        def __init__(self, config, adapter):
            self.config = config
            self.adapter = adapter

    class FakeTTSService:
        def __init__(self, config, bot_client, local_engine_factory):
            self.config = config
            self.bot_client = bot_client
            self.local_engine = local_engine_factory(config)

    class FakeCleanupService:
        def __init__(self, keyboard_backend):
            self.keyboard_backend = keyboard_backend

    class FakeTTSProcessor:
        def __init__(self, tts_service, cleanup_service):
            self.tts_service = tts_service
            self.cleanup_service = cleanup_service

    class FakeStandardKeyboardMonitor:
        def __init__(self, config, handler, backend):
            self.config = config
            self.handler = handler
            self.backend = backend

    class FakeHotkeyService:
        def __init__(self, config, handler, monitor_factory):
            self.config = config
            self.handler = handler
            self.monitor = monitor_factory(config, handler)

    class FakeHotkeyManager:
        def __init__(self, config, service_factory):
            self.config = config
            self.service = service_factory(config, "handler")

    tray_icon = Mock(name="tray_icon")

    class FakeConsoleNotificationService:
        pass

    class FakeSystemTrayService:
        def __init__(self, config, tray_icon, notification_service):
            self.config = config
            self.tray_icon = tray_icon
            self.notification_service = notification_service

    monkeypatch.setattr(bootstrap, "ConfigurationRepository", FakeConfigurationRepository)
    monkeypatch.setattr(bootstrap, "ConfigurationService", FakeConfigurationService)
    monkeypatch.setattr(bootstrap, "KeyboardHookBackend", FakeKeyboardBackend)
    monkeypatch.setattr(bootstrap, "HttpDiscordBotClient", FakeBotClient)
    monkeypatch.setattr(bootstrap, "Pyttsx3Adapter", FakePyttsx3Adapter)
    monkeypatch.setattr(bootstrap, "LocalPyTTSX3Engine", FakeLocalEngine)
    monkeypatch.setattr(bootstrap, "DesktopAppTTSService", FakeTTSService)
    monkeypatch.setattr(bootstrap, "KeyboardCleanupService", FakeCleanupService)
    monkeypatch.setattr(bootstrap, "DesktopAppTTSProcessor", FakeTTSProcessor)
    monkeypatch.setattr(bootstrap, "StandardKeyboardMonitor", FakeStandardKeyboardMonitor)
    monkeypatch.setattr(bootstrap, "HotkeyService", FakeHotkeyService)
    monkeypatch.setattr(bootstrap, "HotkeyManager", FakeHotkeyManager)
    monkeypatch.setattr(bootstrap, "ConsoleNotificationService", FakeConsoleNotificationService)
    monkeypatch.setattr(bootstrap, "SystemTrayService", FakeSystemTrayService)
    monkeypatch.setattr(bootstrap, "create_system_tray_icon", lambda config: tray_icon)

    app = bootstrap.create_desktop_application()
    config = DesktopAppConfig.create_default()

    assert isinstance(app, DesktopApp)
    assert app._config_repository is config_repository
    assert app._config_service is config_service

    tts_processor = app._tts_processor_factory(config)
    assert isinstance(tts_processor, FakeTTSProcessor)
    assert isinstance(tts_processor.tts_service, FakeTTSService)
    assert isinstance(tts_processor.tts_service.bot_client, FakeBotClient)
    assert isinstance(tts_processor.tts_service.local_engine, FakeLocalEngine)
    assert isinstance(tts_processor.tts_service.local_engine.adapter, FakePyttsx3Adapter)
    assert isinstance(tts_processor.cleanup_service, FakeCleanupService)
    assert isinstance(tts_processor.cleanup_service.keyboard_backend, FakeKeyboardBackend)

    hotkey_manager = app._hotkey_manager_factory(config)
    assert isinstance(hotkey_manager, FakeHotkeyManager)
    assert isinstance(hotkey_manager.service, FakeHotkeyService)
    assert isinstance(hotkey_manager.service.monitor, FakeStandardKeyboardMonitor)
    assert isinstance(hotkey_manager.service.monitor.backend, FakeKeyboardBackend)

    notification_service = app._notification_service_factory(config)
    assert isinstance(notification_service, FakeSystemTrayService)
    assert notification_service.tray_icon is tray_icon
    assert isinstance(notification_service.notification_service, FakeConsoleNotificationService)
