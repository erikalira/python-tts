"""Main Desktop App panel implementation."""

from __future__ import annotations

import logging
import queue
from typing import Any, Optional
from collections.abc import Callable

from src.application.dto import (
    DesktopBotActionResultDTO,
    DesktopBotVoiceContextResultDTO,
    DesktopConfigurationSaveResultDTO,
)
from ..config.desktop_config import ConfigurationValidator, DesktopAppConfig
from .config_dialogs import GUIConfig
from .main_window_presenter import DesktopAppMainWindowPresenter, MainWindowMessage
from .main_window_sections import build_action_buttons, build_header, build_help_section
from .ui_logging import UILogHandler

logger = logging.getLogger(__name__)


class DesktopAppMainWindow:
    """Main Desktop App window that keeps configuration, actions, and logs visible."""

    def __init__(
        self,
        config: DesktopAppConfig,
        on_save: Callable[[DesktopAppConfig], DesktopConfigurationSaveResultDTO],
        on_test_connection: Callable[[DesktopAppConfig], DesktopBotActionResultDTO],
        on_send_test: Callable[[DesktopAppConfig], DesktopBotActionResultDTO],
        on_refresh_voice_context: Callable[[DesktopAppConfig], DesktopBotVoiceContextResultDTO],
        on_process_ui_actions: Optional[Callable[[], None]] = None,
    ):
        self.root: Optional[Any] = None
        self.config = config
        self._on_save = on_save
        self._on_test_connection = on_test_connection
        self._on_send_test = on_send_test
        self._on_refresh_voice_context = on_refresh_voice_context
        self._on_process_ui_actions = on_process_ui_actions
        self._presenter = DesktopAppMainWindowPresenter()
        self._config_form = GUIConfig()
        self._log_queue: "queue.Queue[str]" = queue.Queue()
        self._log_handler = UILogHandler(self._log_queue)
        self._status_var: Optional[Any] = None
        self._config_var: Optional[Any] = None
        self._connection_var: Optional[Any] = None
        self._voice_context_var: Optional[Any] = None
        self._logs_widget: Any | None = None
        self._status_label: Any | None = None
        self._config_label: Any | None = None
        self._connection_label: Any | None = None
        self._voice_context_label: Any | None = None

    def show(self) -> None:
        from . import tk_support as compat

        if not compat.TKINTER_AVAILABLE:
            raise RuntimeError("Tkinter is not available for the main window")
        self.root = compat.tk.Tk()
        self.root.title("Desktop App - Main Panel")
        self.root.geometry("980x760")
        self.root.minsize(860, 640)
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self._attach_logging()
        self._create_main_layout()
        self._drain_logs()
        self._drain_ui_actions()
        self.root.mainloop()

    def focus(self) -> None:
        if not self.root:
            return
        self.root.after(0, self._focus_now)

    def push_log(self, message: str) -> None:
        self._log_queue.put(message)

    def hide_to_tray(self) -> None:
        if not self.root:
            return
        try:
            self.root.withdraw()
            self.push_log("Main window minimized to tray")
        except Exception:
            logger.debug("[GUI] Failed to minimize main window to tray", exc_info=True)

    def _focus_now(self) -> None:
        if not self.root:
            return
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        except Exception:
            logger.debug("[GUI] Failed to focus main window", exc_info=True)

    def _create_main_layout(self) -> None:
        from . import tk_support as compat

        self._sync_config_form()
        main_frame = compat.ttk.Frame(self.root, padding="16")
        main_frame.pack(fill="both", expand=True)
        self._status_var = compat.tk.StringVar(value=self._presenter.initial_status().text)
        self._config_var = compat.tk.StringVar(value="")
        self._connection_var = compat.tk.StringVar(value=self._presenter.initial_connection().text)
        self._voice_context_var = compat.tk.StringVar(value=self._presenter.initial_voice_context().text)

        build_header(
            compat.ttk,
            main_frame,
            help_text=(
                "Use this window as the app's main panel. Configure the Desktop App, "
                "validate the bot connection, and follow activity without depending on the terminal."
            ),
        )

        status_frame = compat.ttk.LabelFrame(main_frame, text="App Status", padding="10")
        status_frame.pack(fill="x", pady=(0, 12))
        self._status_label = compat.tk.Label(
            status_frame,
            textvariable=self._status_var,
            anchor="w",
            justify="left",
            fg=self._presenter.initial_status().color,
        )
        self._status_label.pack(anchor="w")
        self._config_label = compat.tk.Label(status_frame, textvariable=self._config_var, anchor="w", justify="left")
        self._config_label.pack(anchor="w", pady=(8, 0))
        self._connection_label = compat.tk.Label(
            status_frame,
            textvariable=self._connection_var,
            anchor="w",
            justify="left",
            fg=self._presenter.initial_connection().color,
        )
        self._connection_label.pack(anchor="w", pady=(8, 0))
        self._voice_context_label = compat.tk.Label(
            status_frame,
            textvariable=self._voice_context_var,
            anchor="w",
            justify="left",
            fg=self._presenter.initial_voice_context().color,
        )
        self._voice_context_label.pack(anchor="w", pady=(8, 0))

        form_frame = compat.ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        form_frame.pack(fill="x", pady=(0, 12))
        self._build_config_notebook(form_frame)

        build_action_buttons(
            compat.ttk,
            main_frame,
            on_save=self._handle_save,
            on_test_connection=self._handle_test_connection,
            on_refresh_voice_context=self._handle_refresh_voice_context,
            on_send_test=self._handle_send_test,
            on_clear_logs=self._clear_logs,
            on_minimize=self.hide_to_tray,
        )

        build_help_section(
            compat.ttk,
            main_frame,
            text=(
                "1. Fill in the bot details and click 'Test connection'. "
                "2. Use 'Refresh detected channel' to check the server and voice channel found for your user. "
                "3. Save the configuration. "
                f"4. Use {self.config.hotkey.trigger_open}text{self.config.hotkey.trigger_close} to send speech in normal use. "
                "5. Optionally use 'Send voice test' to validate the flow manually."
            ),
        )

        logs_frame = compat.ttk.LabelFrame(main_frame, text="Activity", padding="10")
        logs_frame.pack(fill="both", expand=True)
        self._logs_widget = compat.tk.Text(logs_frame, height=14, wrap="word", state="disabled")
        self._logs_widget.pack(side="left", fill="both", expand=True)
        scrollbar = compat.ttk.Scrollbar(logs_frame, orient="vertical", command=self._logs_widget.yview)
        scrollbar.pack(side="right", fill="y")
        self._logs_widget.configure(yscrollcommand=scrollbar.set)
        self.push_log("Main panel started")
        self._refresh_local_status()

    def _handle_save(self) -> None:
        from . import tk_support as compat

        try:
            new_config = self._build_config_from_form()
            if new_config is None:
                return
        except ValueError as exc:
            compat.messagebox.showerror("Error", f"Invalid value: {exc}")
            return
        except Exception as exc:
            compat.messagebox.showerror("Error", f"Error building configuration: {exc}")
            return

        is_valid, errors = ConfigurationValidator.validate(new_config)
        if not is_valid:
            compat.messagebox.showerror("Validation Error", "Errors found:\n\n" + "\n".join(errors))
            self._set_status("Invalid configuration. Fix the fields highlighted in the messages.", success=False)
            return

        result = self._on_save(new_config)
        if result.success:
            self.config = new_config
            self._set_status(result.message, success=True)
            self._refresh_local_status()
        else:
            self._set_status(result.message, success=False)

    def _handle_test_connection(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._apply_message(
                self._connection_var,
                self._connection_label,
                self._presenter.build_invalid_value_message("Test", exc),
            )
            return

        result = self._on_test_connection(config)
        feedback = self._presenter.build_connection_result(result, "No test response")
        self._apply_message(
            self._connection_var,
            self._connection_label,
            feedback,
        )
        self.push_log(f"Connection test: {feedback.text}")

    def _handle_send_test(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._apply_message(
                self._connection_var,
                self._connection_label,
                self._presenter.build_invalid_value_message("Test delivery", exc),
            )
            return

        result = self._on_send_test(config)
        feedback = self._presenter.build_connection_result(result, "No test delivery response")
        self._apply_message(self._connection_var, self._connection_label, feedback)
        self.push_log(f"Test delivery: {feedback.text}")

    def _handle_refresh_voice_context(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._apply_message(
                self._voice_context_var,
                self._voice_context_label,
                self._presenter.build_invalid_value_message("Detection", exc),
            )
            return

        result = self._on_refresh_voice_context(config)
        feedback = self._presenter.build_connection_result(result, "No channel detection response")
        self._apply_message(self._voice_context_var, self._voice_context_label, feedback)
        self.push_log(f"Detected channel: {feedback.text}")

    def _set_status(self, message: str, success: bool) -> None:
        self._apply_message(
            self._status_var,
            self._status_label,
            self._presenter.build_status(message, success),
        )
        self.push_log(message)

    def _refresh_local_status(self) -> None:
        self._apply_message(
            self._config_var,
            self._config_label,
            self._presenter.build_local_config_status(self.config),
        )

    def _sync_config_form(self) -> None:
        self._config_form.root = self.root
        self._config_form.config = self.config

    def _build_config_notebook(self, parent):
        self._sync_config_form()
        return self._config_form._build_config_notebook(parent)

    def _build_config_from_form(self) -> Optional[DesktopAppConfig]:
        self._sync_config_form()
        return self._config_form._build_config_from_form()

    def _apply_message(self, variable: Optional[Any], label: Any, message: MainWindowMessage) -> None:
        if variable is not None and hasattr(variable, "set"):
            variable.set(message.text)
        self._set_label_color(label, message.color)

    def _set_label_color(self, label: Any, color: str) -> None:
        if label is not None and hasattr(label, "configure"):
            label.configure(fg=color)

    def _clear_logs(self) -> None:
        from . import tk_support as compat

        if not self._logs_widget:
            return
        self._logs_widget.configure(state="normal")
        self._logs_widget.delete("1.0", compat.tk.END)
        self._logs_widget.configure(state="disabled")
        self.push_log("Logs cleared by user")

    def _append_log(self, message: str) -> None:
        from . import tk_support as compat

        if not self._logs_widget:
            return
        self._logs_widget.configure(state="normal")
        self._logs_widget.insert(compat.tk.END, message + "\n")
        self._logs_widget.see(compat.tk.END)
        self._logs_widget.configure(state="disabled")

    def _drain_logs(self) -> None:
        while True:
            try:
                message = self._log_queue.get_nowait()
            except queue.Empty:
                break
            self._append_log(message)
        if self.root:
            self.root.after(250, self._drain_logs)

    def _drain_ui_actions(self) -> None:
        if self._on_process_ui_actions is not None:
            self._on_process_ui_actions()
        if self.root:
            self.root.after(100, self._drain_ui_actions)

    def _attach_logging(self) -> None:
        root_logger = logging.getLogger()
        self._log_handler.setLevel(logging.INFO)
        root_logger.addHandler(self._log_handler)

    def _detach_logging(self) -> None:
        logging.getLogger().removeHandler(self._log_handler)

    def _close(self) -> None:
        self._detach_logging()
        if self.root:
            self.root.destroy()
