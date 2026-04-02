#!/usr/bin/env python3
"""Main runtime orchestration for the Windows desktop app."""

import logging
import queue
import threading
from typing import Callable, Optional

from src.application.tts_execution import (
    TTS_EXECUTION_RESULT_FAILED,
    TTS_EXECUTION_RESULT_MISSING_TEXT,
    TTS_EXECUTION_RESULT_OK,
)

from ..adapters.keyboard_backend import KeyboardHookBackend
from ..config.standalone_config import ConfigurationRepository, StandaloneConfig
from ..gui.simple_gui import ConfigurationService, StandaloneMainWindow, TKINTER_AVAILABLE
from ..services.hotkey_services import HotkeyEvent, HotkeyHandler, HotkeyManager
from ..services.notification_services import SystemTrayService
from ..services.tts_services import TTSProcessor
from .desktop_actions import DesktopBotActions, DesktopConfigurationCoordinator

logger = logging.getLogger(__name__)


class StandaloneTTSResultPresenter:
    """Translate structured TTS execution results into desktop notifications."""

    def __init__(self, notification_service: SystemTrayService):
        self._notification_service = notification_service

    def show_processing(self, text: str) -> None:
        """Show a processing notification for captured text."""
        self._notification_service.notify_info(
            "TTS Hotkey",
            f"Processando: '{text[:50]}{'...' if len(text) > 50 else ''}'",
        )

    def present(self, result: dict) -> None:
        """Show user-facing feedback after TTS execution completes."""
        code = result.get("code")
        if code == TTS_EXECUTION_RESULT_OK:
            self._notification_service.notify_success(
                "TTS Hotkey", "Texto reproduzido com sucesso"
            )
            return

        if code == TTS_EXECUTION_RESULT_MISSING_TEXT:
            self._notification_service.notify_error(
                "TTS Hotkey", "Nenhum texto valido foi capturado"
            )
            return

        if code == TTS_EXECUTION_RESULT_FAILED:
            self._notification_service.notify_error(
                "TTS Hotkey", "Falha ao reproduzir o texto"
            )
            return

        self._notification_service.notify_error(
            "TTS Hotkey", "Falha inesperada ao processar TTS"
        )


class StandaloneHotkeyHandler:
    """Hotkey handler that integrates captured text with TTS processing."""

    def __init__(
        self,
        tts_processor: TTSProcessor,
        result_presenter: StandaloneTTSResultPresenter,
    ):
        self._tts_processor = tts_processor
        self._result_presenter = result_presenter

    def handle_text_captured(self, event: HotkeyEvent) -> None:
        """Handle when text is captured between hotkey triggers."""
        if not event.text:
            return

        logger.info("[DESKTOP_APP] Texto capturado pelo hotkey handler")
        self._result_presenter.show_processing(event.text)
        self._tts_processor.process_text(
            event.text,
            event.character_count,
            on_complete=self._result_presenter.present,
        )


class StandaloneApplication:
    """Desktop app runtime that coordinates config, hotkeys, panel, and tray."""

    def __init__(
        self,
        config_repository: Optional[ConfigurationRepository] = None,
        config_service: Optional[ConfigurationService] = None,
        tts_processor_factory: Callable[[StandaloneConfig], TTSProcessor] = TTSProcessor,
        hotkey_manager_factory: Callable[[StandaloneConfig], HotkeyManager] = HotkeyManager,
        notification_service_factory: Callable[
            [StandaloneConfig], SystemTrayService
        ] = SystemTrayService,
        console_wait_factory: Optional[Callable[[], object]] = None,
    ):
        self._config: Optional[StandaloneConfig] = None
        self._config_repository: Optional[ConfigurationRepository] = config_repository

        self._tts_processor: Optional[TTSProcessor] = None
        self._hotkey_manager: Optional[HotkeyManager] = None
        self._notification_service: Optional[SystemTrayService] = None

        self._config_service: Optional[ConfigurationService] = config_service
        self._tts_processor_factory = tts_processor_factory
        self._hotkey_manager_factory = hotkey_manager_factory
        self._notification_service_factory = notification_service_factory
        self._console_wait_factory = console_wait_factory or KeyboardHookBackend

        self._bot_actions: Optional[DesktopBotActions] = None
        self._configuration_coordinator: Optional[DesktopConfigurationCoordinator] = None

        self._initialized = False
        self._running = False
        self._main_loop_actions: "queue.Queue[Callable[[], None]]" = queue.Queue()
        self._shutdown_requested = threading.Event()
        self._main_window: Optional[StandaloneMainWindow] = None

    def initialize(self) -> bool:
        """Initialize all desktop app components."""
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
        if (
            self._configuration_coordinator is None
        ):
            self._configuration_coordinator = DesktopConfigurationCoordinator(
                config_repository=self._config_repository,
                config_service=self._config_service,
                update_services=self._update_services_config,
            )

    def _setup_integrations(self) -> None:
        """Wire tray callbacks and hotkey processing to the current services."""
        self._notification_service.initialize(
            status_click=self._handle_status_click_request,
            configure=self._handle_configure_request,
            quit_handler=self._handle_quit_request,
        )
        self._rebuild_hotkey_manager()

    def _rebuild_hotkey_manager(self, start_if_active: bool = False) -> None:
        """Recreate the hotkey manager so it points at the latest services."""
        if not self._config:
            return

        self._hotkey_manager = self._hotkey_manager_factory(self._config)
        result_presenter = StandaloneTTSResultPresenter(self._notification_service)
        hotkey_handler = StandaloneHotkeyHandler(self._tts_processor, result_presenter)
        self._hotkey_manager.initialize(hotkey_handler)
        self._hotkey_manager.set_external_suppression_check(
            lambda: self._tts_processor.is_processing()
        )
        if start_if_active:
            self._hotkey_manager.start()

    def run(self) -> None:
        """Run the desktop app."""
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
        logger.info("[DESKTOP_APP] Iniciando servicos...")

        if not self._hotkey_manager.start():
            logger.error("[DESKTOP_APP] Falha ao iniciar monitoramento de hotkey")
            return False

        tray_started = self._notification_service.start()
        if not tray_started:
            logger.warning("[DESKTOP_APP] System tray nao disponivel, executando em modo console")

        self._running = True
        logger.info("[DESKTOP_APP] Todos os servicos iniciados")
        return True

    def _run_main_loop(self) -> None:
        """Run the main desktop app loop."""
        if TKINTER_AVAILABLE:
            self._show_main_window()
            return

        tray_available = self._notification_service.is_available()
        if tray_available:
            logger.info("[DESKTOP_APP] Executando com system tray em background...")
            while self._running and not self._shutdown_requested.is_set():
                self._process_pending_ui_action(timeout=0.2)
            return

        logger.info("[DESKTOP_APP] Modo console ativo. Pressione Ctrl+C para sair...")
        wait_backend = self._console_wait_factory()
        if hasattr(wait_backend, "is_available") and wait_backend.is_available():
            try:
                import keyboard

                keyboard.wait()
                return
            except ImportError:
                pass
        input("Pressione Enter para sair...")

    def _process_pending_ui_action(self, timeout: float) -> None:
        """Execute queued UI actions on the main thread."""
        try:
            action = self._main_loop_actions.get(timeout=timeout)
        except queue.Empty:
            return
        action()

    def _show_main_window(self) -> None:
        """Show the main desktop panel when Tkinter is available."""
        self._main_window = StandaloneMainWindow(
            self._config,
            on_save=self._save_configuration_from_ui,
            on_test_connection=self._test_bot_connection,
            on_send_test=self._send_test_message,
        )
        self._main_window.show()

    def _save_configuration_from_ui(self, updated_config: StandaloneConfig) -> dict:
        """Validate, persist, and apply config changes from the main window."""
        self._ensure_action_coordinators()
        if self._configuration_coordinator is None:
            return {"success": False, "message": "Coordenador de configuracao indisponivel"}

        result = self._configuration_coordinator.save_from_ui(updated_config)
        if result.get("success"):
            self._config = updated_config
        return result

    def _test_bot_connection(self, config: StandaloneConfig) -> dict:
        """Test connectivity against the bot health endpoint."""
        self._ensure_action_coordinators()
        return self._bot_actions.test_bot_connection(config)

    def _send_test_message(self, config: StandaloneConfig) -> dict:
        """Send a short manual test message through the bot."""
        self._ensure_action_coordinators()
        return self._bot_actions.send_test_message(config)

    def _show_current_configuration(self) -> None:
        """Log the current desktop app configuration summary."""
        if not self._config:
            return

        logger.info(
            "[DESKTOP_APP] Config atual: bot_url=%s, guild_id=%s, member_id=%s, engine=%s, hotkey=%s",
            self._config.discord.bot_url,
            self._config.discord.guild_id,
            self._config.discord.member_id,
            self._config.tts.engine,
            self._config.hotkey.keys,
        )

    def _update_services_config(self) -> None:
        """Update dependent services after configuration changes."""
        hotkeys_were_active = bool(self._hotkey_manager and self._hotkey_manager.is_active())
        if hotkeys_were_active:
            self._hotkey_manager.stop()

        if self._tts_processor:
            self._tts_processor = self._tts_processor_factory(self._config)

        if self._notification_service:
            tray_should_restart = self._running and self._notification_service.is_available()
            self._notification_service.stop()
            self._notification_service = self._notification_service_factory(self._config)
            self._notification_service.initialize(
                status_click=self._handle_status_click_request,
                configure=self._handle_configure_request,
                quit_handler=self._handle_quit_request,
            )
            if tray_should_restart:
                self._notification_service.start()

        self._rebuild_hotkey_manager(start_if_active=hotkeys_were_active)

    def _shutdown(self) -> None:
        """Gracefully shut down runtime services."""
        logger.info("[DESKTOP_APP] Encerrando aplicacao...")
        self._shutdown_requested.set()

        if self._running:
            if self._hotkey_manager:
                self._hotkey_manager.stop()
            if self._notification_service:
                self._notification_service.stop()
            self._running = False

        if self._main_window and self._main_window.root:
            try:
                self._main_window.root.quit()
            except Exception:
                logger.debug(
                    "[DESKTOP_APP] Falha ao encerrar loop da janela principal",
                    exc_info=True,
                )

        logger.info("[DESKTOP_APP] Aplicacao encerrada")

    def _handle_status_click_request(self) -> None:
        """Queue status display on the main thread."""
        self._main_loop_actions.put(self._handle_status_click)

    def _handle_status_click(self) -> None:
        """Handle system tray status click."""
        if self._main_window:
            self._main_window.focus()
            self._main_window.push_log("Janela principal trazida para frente via tray")
            return

        status = self._get_application_status()
        mode = "Discord" if status["discord_configured"] else "Local"
        hotkeys = "ativas" if status["hotkey_active"] else "inativas"
        tts = "disponivel" if status["tts_available"] else "indisponivel"
        summary = f"Modo {mode} | Hotkeys {hotkeys} | TTS {tts}"
        logger.info("[DESKTOP_APP] Status solicitado: %s", summary)
        if self._notification_service:
            self._notification_service.notify_info("TTS Hotkey", summary)

    def _handle_configure_request(self) -> None:
        """Queue configuration dialog on the main thread."""
        self._main_loop_actions.put(self._handle_configure)

    def _handle_configure(self) -> None:
        """Handle system tray configure action."""
        if self._main_window:
            self._main_window.focus()
            self._main_window.push_log("Acao de configuracao solicitada via tray")
            return

        logger.info("[DESKTOP_APP] Abrindo configuracoes...")
        self._ensure_action_coordinators()

        hotkeys_were_active = bool(self._hotkey_manager and self._hotkey_manager.is_active())
        if hotkeys_were_active:
            self._hotkey_manager.stop()

        if self._configuration_coordinator is None:
            logger.error("[DESKTOP_APP] Coordenador de configuracao indisponivel")
            return

        updated_config, applied = self._configuration_coordinator.reconfigure(
            current_config=self._config,
            hotkeys_were_active=hotkeys_were_active,
            pause_hotkeys=lambda: self._hotkey_manager.stop() if self._hotkey_manager else None,
            resume_hotkeys=lambda: self._hotkey_manager.start() if self._hotkey_manager else None,
            notify_error=self._notification_service.notify_error if self._notification_service else None,
            notify_success=self._notification_service.notify_success if self._notification_service else None,
            are_hotkeys_active=self._hotkey_manager.is_active if self._hotkey_manager else None,
        )
        if applied and updated_config:
            self._config = updated_config

    def _handle_quit_request(self) -> None:
        """Queue shutdown on the main thread."""
        self._main_loop_actions.put(self._handle_quit)

    def _handle_quit(self) -> None:
        """Handle system tray quit action."""
        logger.info("[DESKTOP_APP] Encerrando via system tray...")
        self._shutdown()

    def _get_application_status(self) -> dict:
        """Get a compact view of current runtime status."""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "discord_configured": (
                self._config
                and self._config.discord.bot_url
                and self._config.discord.guild_id
                and self._config.discord.member_id
            ),
            "hotkey_active": (self._hotkey_manager and self._hotkey_manager.is_active()),
            "tts_available": (
                self._tts_processor
                and self._tts_processor.get_service_status()["tts_available"]
            ),
            "tray_available": (
                self._notification_service and self._notification_service.is_available()
            ),
        }


def create_standalone_application() -> StandaloneApplication:
    """Factory function to create the desktop app runtime."""
    from .bootstrap import create_standalone_application as build_application

    return build_application()


def main() -> None:
    """Main entry point for the Windows desktop app."""
    app = create_standalone_application()
    app.run()


if __name__ == "__main__":
    main()
