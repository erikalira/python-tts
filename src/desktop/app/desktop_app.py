#!/usr/bin/env python3
"""Main runtime orchestration for the Windows Desktop App."""

import logging
import threading
from typing import Callable, Optional

from ..adapters.keyboard_backend import KeyboardHookBackend
from ..config.desktop_config import ConfigurationRepository, DesktopAppConfig
from ..gui.configuration_service import ConfigurationService
from ..gui.tk_support import TKINTER_AVAILABLE
from ..services.hotkey_services import HotkeyManager
from ..services.notification_services import SystemTrayService
from .configuration_application import DesktopConfigurationApplicationService
from .desktop_actions import DesktopBotActions, DesktopConfigurationCoordinator
from .runtime_lifecycle import DesktopAppLifecycleCoordinator
from .runtime_status import DesktopAppStatusBuilder
from .tts_runtime import DesktopAppHotkeyHandler, DesktopAppTTSProcessor, DesktopAppTTSResultPresenter
from .ui_tray_actions import DesktopAppUIActionsCoordinator
from .ui_runtime import DesktopAppUIRuntimeCoordinator

logger = logging.getLogger(__name__)


class DesktopApp:
    """Desktop App runtime that coordinates config, hotkeys, panel, and tray."""

    def __init__(
        self,
        config_repository: Optional[ConfigurationRepository] = None,
        config_service: Optional[ConfigurationService] = None,
        tts_processor_factory: Callable[[DesktopAppConfig], DesktopAppTTSProcessor] = DesktopAppTTSProcessor,
        hotkey_manager_factory: Callable[[DesktopAppConfig], HotkeyManager] = HotkeyManager,
        notification_service_factory: Callable[[DesktopAppConfig], SystemTrayService] = SystemTrayService,
        console_wait_factory: Optional[Callable[[], object]] = None,
    ):
        self._config: Optional[DesktopAppConfig] = None
        self._config_repository: Optional[ConfigurationRepository] = config_repository

        self._tts_processor: Optional[DesktopAppTTSProcessor] = None
        self._hotkey_manager: Optional[HotkeyManager] = None
        self._notification_service: Optional[SystemTrayService] = None

        self._config_service: Optional[ConfigurationService] = config_service
        self._tts_processor_factory = tts_processor_factory
        self._hotkey_manager_factory = hotkey_manager_factory
        self._notification_service_factory = notification_service_factory
        self._console_wait_factory = console_wait_factory or KeyboardHookBackend

        self._bot_actions: Optional[DesktopBotActions] = None
        self._configuration_coordinator: Optional[DesktopConfigurationCoordinator] = None
        self._lifecycle_coordinator = DesktopAppLifecycleCoordinator(TKINTER_AVAILABLE)
        self._ui_actions_coordinator = DesktopAppUIActionsCoordinator()
        self._ui_runtime_coordinator = DesktopAppUIRuntimeCoordinator()
        self._status_builder = DesktopAppStatusBuilder()

        self._initialized = False
        self._running = False
        self._shutdown_requested = threading.Event()

    def initialize(self) -> bool:
        """Initialize all Desktop App components."""
        if self._initialized:
            return True

        try:
            if self._config_repository is None:
                self._config_repository = ConfigurationRepository()
            self._config = self._config_repository.load()

            if self._config_service is None:
                self._config_service = ConfigurationService(prefer_gui=True)

            self._ensure_action_coordinators()

            self._tts_processor = self._tts_processor_factory(self._config)
            self._hotkey_manager = self._hotkey_manager_factory(self._config)
            self._notification_service = self._notification_service_factory(self._config)

            self._setup_integrations()

            self._initialized = True
            logger.info("[DESKTOP_APP] Aplicacao inicializada com sucesso")
            return True
        except Exception as exc:
            logger.error("[DESKTOP_APP] Erro durante inicializacao: %s", exc)
            return False

    def _ensure_action_coordinators(self) -> None:
        """Create action coordinators lazily for direct unit-test usage."""
        if self._bot_actions is None:
            self._bot_actions = DesktopBotActions()
        if self._config_service is None:
            self._config_service = ConfigurationService(prefer_gui=True)
        if self._config_repository is None:
            self._config_repository = ConfigurationRepository()
        if self._configuration_coordinator is None:
            self._configuration_coordinator = DesktopConfigurationCoordinator(
                config_service=self._config_service,
                configuration_application=DesktopConfigurationApplicationService(
                    config_repository=self._config_repository,
                    update_services=self._update_services_config,
                ),
            )

    def _setup_integrations(self) -> None:
        """Wire tray callbacks and hotkey processing to the current services."""
        self._initialize_notification_service(self._notification_service)
        self._rebuild_hotkey_manager()

    def _initialize_notification_service(self, notification_service: SystemTrayService) -> None:
        """Wire tray callbacks to the provided notification service."""
        notification_service.initialize(
            status_click=self._handle_status_click_request,
            configure=self._handle_configure_request,
            quit_handler=self._handle_quit_request,
        )

    def _rebuild_hotkey_manager(self, start_if_active: bool = False) -> None:
        """Recreate the hotkey manager so it points at the latest services."""
        if not self._config:
            return

        self._hotkey_manager = self._hotkey_manager_factory(self._config)
        result_presenter = DesktopAppTTSResultPresenter(self._notification_service)
        hotkey_handler = DesktopAppHotkeyHandler(self._tts_processor, result_presenter)
        self._hotkey_manager.initialize(hotkey_handler)
        self._hotkey_manager.set_external_suppression_check(
            lambda: self._tts_processor.is_processing()
        )
        if start_if_active:
            self._hotkey_manager.start()

    def run(self) -> None:
        """Run the Desktop App."""
        self._shutdown_requested.clear()

        if not self._initialized and not self.initialize():
            logger.error("[DESKTOP_APP] Falha na inicializacao. Encerrando.")
            return

        try:
            if not self._handle_initial_configuration():
                print("[DESKTOP_APP] Configuracao cancelada. Encerrando.")
                return

            self._show_current_configuration()

            if not self._start_services():
                print("[DESKTOP_APP] Falha ao iniciar servicos. Encerrando.")
                return

            self._run_main_loop()
        except KeyboardInterrupt:
            logger.info("[DESKTOP_APP] Interrompido pelo usuario")
        except Exception as exc:
            logger.error("[DESKTOP_APP] Erro durante execucao: %s", exc)
        finally:
            self._shutdown()

    def _handle_initial_configuration(self) -> bool:
        """Handle first-run configuration when required."""
        self._ensure_action_coordinators()
        if self._configuration_coordinator is None:
            return True

        should_continue, updated_config = self._configuration_coordinator.handle_initial_configuration(
            self._config
        )
        self._config = updated_config
        return should_continue

    def _start_services(self) -> bool:
        """Start all runtime services."""
        started = self._lifecycle_coordinator.start_services(
            self._hotkey_manager,
            self._notification_service,
        )
        self._running = started
        return started

    def _run_main_loop(self) -> None:
        """Run the main Desktop App loop."""
        self._lifecycle_coordinator.run_main_loop(
            show_main_window=self._show_main_window,
            notification_service=self._notification_service,
            process_pending_ui_action=self._process_pending_ui_action,
            is_running=lambda: self._running,
            shutdown_requested=self._shutdown_requested,
            console_wait_factory=self._console_wait_factory,
        )

    def _process_pending_ui_action(self, timeout: float) -> None:
        """Execute queued UI actions on the main thread."""
        self._lifecycle_coordinator.process_pending_ui_action(
            action_queue=self._ui_runtime_coordinator.action_queue,
            timeout=timeout,
        )

    def _show_main_window(self) -> None:
        """Show the main Desktop App panel when Tkinter is available."""
        self._ui_runtime_coordinator.show_main_window(
            config=self._config,
            on_save=self._save_configuration_from_ui,
            on_test_connection=self._test_bot_connection,
            on_send_test=self._send_test_message,
            on_refresh_voice_context=self._refresh_voice_context,
        )

    def _save_configuration_from_ui(self, updated_config: DesktopAppConfig) -> dict:
        """Validate, persist, and apply config changes from the main window."""
        self._ensure_action_coordinators()
        if self._configuration_coordinator is None:
            return {"success": False, "message": "Coordenador de configuracao indisponivel"}

        result = self._configuration_coordinator.save_from_ui(updated_config)
        if result.get("success"):
            self._config = updated_config
        return result

    def _test_bot_connection(self, config: DesktopAppConfig) -> dict:
        """Test connectivity against the bot health endpoint."""
        self._ensure_action_coordinators()
        return self._bot_actions.test_bot_connection(config)

    def _send_test_message(self, config: DesktopAppConfig) -> dict:
        """Send a short manual test message through the bot."""
        self._ensure_action_coordinators()
        return self._bot_actions.send_test_message(config)

    def _refresh_voice_context(self, config: DesktopAppConfig) -> dict:
        """Refresh the currently detected Discord voice context."""
        self._ensure_action_coordinators()
        return self._bot_actions.fetch_current_voice_context(config)

    def _show_current_configuration(self) -> None:
        """Log the current Desktop App configuration summary."""
        if not self._config:
            return

        logger.info(
            "[DESKTOP_APP] Config atual: bot_url=%s, guild_id=%s, member_id=%s, engine=%s, local_tts_enabled=%s, hotkey=%s",
            self._config.discord.bot_url,
            self._config.discord.guild_id,
            self._config.discord.member_id,
            self._config.tts.engine,
            self._config.interface.local_tts_enabled,
            self._config.hotkey.keys,
        )

    def _update_services_config(self) -> None:
        """Update dependent services after configuration changes."""
        (
            self._tts_processor,
            self._notification_service,
        ) = self._lifecycle_coordinator.update_services_config(
            running=self._running,
            config=self._config,
            hotkey_manager=self._hotkey_manager,
            tts_processor=self._tts_processor,
            notification_service=self._notification_service,
            tts_processor_factory=self._tts_processor_factory,
            notification_service_factory=self._notification_service_factory,
            initialize_notification_service=self._initialize_notification_service,
            rebuild_hotkey_manager=self._rebuild_hotkey_manager,
        )

    def _shutdown(self) -> None:
        """Gracefully shut down runtime services."""
        self._running = self._lifecycle_coordinator.shutdown(
            running=self._running,
            hotkey_manager=self._hotkey_manager,
            notification_service=self._notification_service,
            shutdown_requested=self._shutdown_requested,
            main_window=self._ui_runtime_coordinator.main_window,
        )

    def _handle_status_click_request(self) -> None:
        """Queue status display on the main thread."""
        self._ui_runtime_coordinator.queue(self._handle_status_click)

    def _handle_status_click(self) -> None:
        """Handle system tray status click."""
        self._ui_actions_coordinator.show_status(
            main_window=self._ui_runtime_coordinator.main_window,
            get_status=self._get_application_status,
            notification_service=self._notification_service,
        )

    def _handle_configure_request(self) -> None:
        """Queue configuration dialog on the main thread."""
        self._ui_runtime_coordinator.queue(self._handle_configure)

    def _handle_configure(self) -> None:
        """Handle system tray configure action."""
        updated_config, applied = self._ui_actions_coordinator.handle_configure(
            main_window=self._ui_runtime_coordinator.main_window,
            ensure_action_coordinators=self._ensure_action_coordinators,
            hotkey_manager=self._hotkey_manager,
            get_configuration_coordinator=lambda: self._configuration_coordinator,
            current_config=self._config,
            notification_service=self._notification_service,
        )
        if applied and updated_config:
            self._config = updated_config

    def _handle_quit_request(self) -> None:
        """Queue shutdown on the main thread."""
        self._ui_runtime_coordinator.queue(self._handle_quit)

    def _handle_quit(self) -> None:
        """Handle system tray quit action."""
        logger.info("[DESKTOP_APP] Encerrando via system tray...")
        self._shutdown()

    def _get_application_status(self) -> dict:
        """Get a compact view of current runtime status."""
        return self._status_builder.build(
            initialized=self._initialized,
            running=self._running,
            config=self._config,
            hotkey_manager=self._hotkey_manager,
            tts_processor=self._tts_processor,
            notification_service=self._notification_service,
        )


def create_desktop_application() -> DesktopApp:
    """Factory function to create the Desktop App runtime."""
    from .bootstrap import create_desktop_application as build_application

    return build_application()


def main() -> None:
    """Main entry point for the Windows Desktop App."""
    app = create_desktop_application()
    app.run()


if __name__ == "__main__":
    main()
