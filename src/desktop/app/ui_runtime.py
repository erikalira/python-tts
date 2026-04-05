"""UI runtime coordination for the Desktop App."""

from __future__ import annotations

import queue
from typing import Callable, Optional

from ..config.desktop_config import DesktopAppConfig
from ..gui.main_window import DesktopAppMainWindow


class DesktopAppUIRuntimeCoordinator:
    """Own the main window instance and queued UI actions for the desktop runtime."""

    def __init__(self):
        self._main_loop_actions: "queue.Queue[Callable[[], None]]" = queue.Queue()
        self._main_window: Optional[DesktopAppMainWindow] = None

    @property
    def action_queue(self) -> "queue.Queue[Callable[[], None]]":
        return self._main_loop_actions

    @property
    def main_window(self) -> Optional[DesktopAppMainWindow]:
        return self._main_window

    def show_main_window(
        self,
        *,
        config: DesktopAppConfig,
        on_save: Callable[[DesktopAppConfig], dict],
        on_test_connection: Callable[[DesktopAppConfig], dict],
        on_send_test: Callable[[DesktopAppConfig], dict],
        on_refresh_voice_context: Callable[[DesktopAppConfig], dict],
    ) -> None:
        """Create and show the main Desktop App window."""
        self._main_window = DesktopAppMainWindow(
            config,
            on_save=on_save,
            on_test_connection=on_test_connection,
            on_send_test=on_send_test,
            on_refresh_voice_context=on_refresh_voice_context,
            on_process_ui_actions=self.drain_queued_actions,
        )
        self._main_window.show()

    def queue(self, action: Callable[[], None]) -> None:
        """Queue a UI action to run on the main thread."""
        self._main_loop_actions.put(action)

    def drain_queued_actions(self) -> None:
        """Run all queued UI actions without blocking the Tk main loop."""
        while True:
            try:
                action = self._main_loop_actions.get_nowait()
            except queue.Empty:
                return
            action()
