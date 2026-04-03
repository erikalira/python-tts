"""Action coordinators for the Windows Desktop App runtime."""

from __future__ import annotations

import logging
from typing import Callable, Optional

from src.application.desktop_bot import (
    CheckDesktopBotConnectionUseCase,
    FetchDesktopBotVoiceContextUseCase,
    SendDesktopBotTestMessageUseCase,
)

from ..config.desktop_config import (
    DesktopAppConfig,
)
from ..gui.simple_gui import ConfigurationService
from ..services.discord_bot_client import HttpDiscordBotClient
from .configuration_application import DesktopConfigurationApplicationService

logger = logging.getLogger(__name__)


class DesktopBotActions:
    """Handle Desktop App panel actions that talk to the Discord bot runtime."""

    def __init__(self, gateway_factory: Optional[Callable[[DesktopAppConfig], object]] = None):
        self._gateway_factory = gateway_factory or HttpDiscordBotClient

    def test_bot_connection(self, config: DesktopAppConfig) -> dict:
        """Test connectivity against the bot health endpoint."""
        gateway = self._gateway_factory(config)
        result = CheckDesktopBotConnectionUseCase(gateway).execute()
        if result.get("success"):
            logger.info("[DESKTOP_APP] Teste de conexao com o bot concluido com sucesso")
        else:
            logger.warning(
                "[DESKTOP_APP] Teste de conexao com o bot falhou: %s",
                result.get("message"),
            )
        return result

    def send_test_message(self, config: DesktopAppConfig) -> dict:
        """Send a short manual test message to validate the speak flow."""
        gateway = self._gateway_factory(config)
        result = SendDesktopBotTestMessageUseCase(gateway).execute()
        if result.get("success"):
            logger.info("[DESKTOP_APP] Mensagem curta de teste enviada ao bot")
        else:
            logger.warning(
                "[DESKTOP_APP] Falha ao enviar mensagem curta de teste ao bot: %s",
                result.get("message"),
            )
        return result

    def fetch_current_voice_context(self, config: DesktopAppConfig) -> dict:
        """Fetch the currently detected guild/channel for the configured Discord user."""
        gateway = self._gateway_factory(config)
        result = FetchDesktopBotVoiceContextUseCase(gateway).execute()
        if result.get("success"):
            logger.info(
                "[DESKTOP_APP] Canal detectado para o usuario: guild=%s channel=%s",
                result.get("guild_name"),
                result.get("channel_name"),
            )
        else:
            logger.warning(
                "[DESKTOP_APP] Nao foi possivel detectar o canal atual: %s",
                result.get("message"),
            )
        return result


class DesktopConfigurationCoordinator:
    """Coordinate configuration edits and their side effects for the Desktop App."""

    def __init__(
        self,
        config_service: ConfigurationService,
        configuration_application: DesktopConfigurationApplicationService,
    ):
        self._config_service = config_service
        self._configuration_application = configuration_application

    def handle_initial_configuration(
        self,
        current_config: DesktopAppConfig,
    ) -> tuple[bool, DesktopAppConfig]:
        """Run first-time configuration when required."""
        if self._configuration_application.is_configured(current_config):
            return True, current_config

        logger.info("[DESKTOP_APP] Primeira execucao detectada, abrindo configuracao inicial")
        updated_config = self._config_service.get_configuration(current_config)
        if not updated_config:
            return False, current_config

        self._persist_and_apply(updated_config)
        return True, updated_config

    def save_from_ui(self, updated_config: DesktopAppConfig) -> dict:
        """Validate, persist, and apply configuration changes from the main window."""
        is_valid, errors = self._configuration_application.validate(updated_config)
        if not is_valid:
            message = "; ".join(errors)
            logger.error("[DESKTOP_APP] Configuracao invalida recebida da interface: %s", message)
            return {"success": False, "message": message}

        save_success = self._configuration_application.apply(updated_config)
        logger.info("[DESKTOP_APP] Configuracao salva pelo painel principal")
        return {
            "success": True,
            "message": (
                "Configuracao aplicada com sucesso"
                if save_success
                else "Configuracao aplicada, mas nao foi possivel persistir o arquivo"
            ),
        }

    def reconfigure(
        self,
        current_config: DesktopAppConfig,
        hotkeys_were_active: bool,
        pause_hotkeys: Callable[[], None],
        resume_hotkeys: Callable[[], None],
        notify_error: Optional[Callable[[str, str], None]] = None,
        notify_success: Optional[Callable[[str, str], None]] = None,
        are_hotkeys_active: Optional[Callable[[], bool]] = None,
    ) -> tuple[Optional[DesktopAppConfig], bool]:
        """Open configuration UI and apply changes from the tray flow."""
        updated_config = None
        try:
            updated_config = self._config_service.get_configuration(current_config)
        finally:
            if hotkeys_were_active and not updated_config:
                resume_hotkeys()

        if not updated_config:
            logger.info("[DESKTOP_APP] Configuracao cancelada")
            return None, False

        is_valid, errors = self._configuration_application.validate(updated_config)
        if not is_valid:
            logger.error("[DESKTOP_APP] Configuracao invalida: %s", "; ".join(errors))
            if notify_error:
                notify_error("Desktop App", "Configuracao invalida")
            if hotkeys_were_active:
                resume_hotkeys()
            return None, False

        self._configuration_application.apply(updated_config)
        if hotkeys_were_active and are_hotkeys_active and not are_hotkeys_active():
            resume_hotkeys()

        logger.info("[DESKTOP_APP] Configuracao atualizada com sucesso")
        if notify_success:
            notify_success("Desktop App", "Configuracao atualizada")
        return updated_config, True
