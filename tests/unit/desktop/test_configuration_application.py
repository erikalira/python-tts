from unittest.mock import Mock

from src.desktop.app.configuration_application import DesktopConfigurationApplicationService
from src.desktop.config.desktop_config import DesktopAppConfig


def test_configuration_application_service_applies_config_side_effects():
    repository = Mock()
    repository.save.return_value = True
    environment_updater = Mock()
    update_services = Mock()
    service = DesktopConfigurationApplicationService(
        config_repository=repository,
        update_services=update_services,
        environment_updater=environment_updater,
    )
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "123"

    result = service.apply(config)

    assert result is True
    repository.save.assert_called_once_with(config)
    environment_updater.update_from_config.assert_called_once_with(config)
    update_services.assert_called_once_with()


def test_configuration_application_service_keeps_applying_side_effects_when_save_fails():
    repository = Mock()
    repository.save.return_value = False
    environment_updater = Mock()
    update_services = Mock()
    service = DesktopConfigurationApplicationService(
        config_repository=repository,
        update_services=update_services,
        environment_updater=environment_updater,
    )

    result = service.apply(DesktopAppConfig.create_default())

    assert result is False
    environment_updater.update_from_config.assert_called_once()
    update_services.assert_called_once_with()


def test_configuration_application_service_delegates_validation():
    service = DesktopConfigurationApplicationService(
        config_repository=Mock(),
        update_services=Mock(),
        environment_updater=Mock(),
    )
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "abc"

    is_valid, errors = service.validate(config)

    assert is_valid is False
    assert errors


def test_configuration_application_service_reports_when_config_is_complete():
    service = DesktopConfigurationApplicationService(
        config_repository=Mock(),
        update_services=Mock(),
        environment_updater=Mock(),
    )
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "123"

    assert service.is_configured(config) is True
