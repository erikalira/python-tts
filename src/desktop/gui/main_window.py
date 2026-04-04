"""Main Desktop App panel implementation."""

from __future__ import annotations

import logging
import queue
from typing import Callable, Optional

from ..config.desktop_config import ConfigurationValidator, DesktopAppConfig
from .config_dialogs import GUIConfig
from .main_window_presenter import DesktopAppMainWindowPresenter, MainWindowMessage
from .ui_logging import UILogHandler

logger = logging.getLogger(__name__)


class DesktopAppMainWindow:
    """Main Desktop App window that keeps configuration, actions, and logs visible."""

    def __init__(
        self,
        config: DesktopAppConfig,
        on_save: Callable[[DesktopAppConfig], dict],
        on_test_connection: Callable[[DesktopAppConfig], dict],
        on_send_test: Callable[[DesktopAppConfig], dict],
        on_refresh_voice_context: Callable[[DesktopAppConfig], dict],
    ):
        self.root: Optional[object] = None
        self.config = config
        self._on_save = on_save
        self._on_test_connection = on_test_connection
        self._on_send_test = on_send_test
        self._on_refresh_voice_context = on_refresh_voice_context
        self._presenter = DesktopAppMainWindowPresenter()
        self._config_form = GUIConfig()
        self._log_queue: "queue.Queue[str]" = queue.Queue()
        self._log_handler = UILogHandler(self._log_queue)
        self._status_var: Optional[object] = None
        self._config_var: Optional[object] = None
        self._connection_var: Optional[object] = None
        self._voice_context_var: Optional[object] = None
        self._logs_widget = None
        self._status_label = None
        self._config_label = None
        self._connection_label = None
        self._voice_context_label = None

    def show(self) -> None:
        from . import tk_support as compat

        if not compat.TKINTER_AVAILABLE:
            raise RuntimeError("Tkinter nao disponivel para a janela principal")
        self.root = compat.tk.Tk()
        self.root.title("Desktop App - Painel Principal")
        self.root.geometry("980x760")
        self.root.minsize(860, 640)
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self._attach_logging()
        self._create_main_layout()
        self._drain_logs()
        self.root.mainloop()

    def focus(self) -> None:
        if not self.root:
            return
        self.root.after(0, self._focus_now)

    def push_log(self, message: str) -> None:
        self._log_queue.put(message)

    def _focus_now(self) -> None:
        if not self.root:
            return
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        except Exception:
            logger.debug("[GUI] Falha ao focar janela principal", exc_info=True)

    def _create_main_layout(self) -> None:
        from . import tk_support as compat

        self._sync_config_form()
        main_frame = compat.ttk.Frame(self.root, padding="16")
        main_frame.pack(fill="both", expand=True)
        self._status_var = compat.tk.StringVar(value=self._presenter.initial_status().text)
        self._config_var = compat.tk.StringVar(value="")
        self._connection_var = compat.tk.StringVar(value=self._presenter.initial_connection().text)
        self._voice_context_var = compat.tk.StringVar(value=self._presenter.initial_voice_context().text)

        compat.ttk.Label(main_frame, text="Desktop App", font=("Arial", 18, "bold")).pack(anchor="w")
        compat.ttk.Label(
            main_frame,
            text=(
                "Use esta janela como painel principal do app. Aqui voce configura o Desktop App, "
                "valida a conexao com o bot e acompanha a atividade sem depender do terminal."
            ),
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(6, 12))

        status_frame = compat.ttk.LabelFrame(main_frame, text="Status do app", padding="10")
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

        form_frame = compat.ttk.LabelFrame(main_frame, text="Configuracao", padding="10")
        form_frame.pack(fill="both", expand=True, pady=(0, 12))
        self._build_config_notebook(form_frame)

        action_frame = compat.ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(0, 12))
        compat.ttk.Button(action_frame, text="Salvar configuracao", command=self._handle_save).pack(side="left")
        compat.ttk.Button(action_frame, text="Testar conexao", command=self._handle_test_connection).pack(side="left", padx=(10, 0))
        compat.ttk.Button(action_frame, text="Recarregar canal detectado", command=self._handle_refresh_voice_context).pack(side="left", padx=(10, 0))
        compat.ttk.Button(action_frame, text="Enviar teste de voz", command=self._handle_send_test).pack(side="left", padx=(10, 0))
        compat.ttk.Button(action_frame, text="Limpar logs", command=self._clear_logs).pack(side="left", padx=(10, 0))
        compat.ttk.Button(action_frame, text="Fechar app", command=self._close).pack(side="right")

        help_frame = compat.ttk.LabelFrame(main_frame, text="Como usar", padding="10")
        help_frame.pack(fill="x", pady=(0, 12))
        compat.ttk.Label(
            help_frame,
            text=(
                "1. Preencha os dados do bot e clique em 'Testar conexao'. "
                "2. Use 'Recarregar canal detectado' para verificar o servidor e canal de voz encontrados para seu usuario. "
                "3. Salve a configuracao. "
                f"4. Use {self.config.hotkey.trigger_open}texto{self.config.hotkey.trigger_close} para enviar fala no uso normal. "
                "5. Se quiser, use 'Enviar teste de voz' para validar o fluxo manualmente."
            ),
            wraplength=900,
            justify="left",
        ).pack(anchor="w")

        logs_frame = compat.ttk.LabelFrame(main_frame, text="Atividade", padding="10")
        logs_frame.pack(fill="both", expand=True)
        self._logs_widget = compat.tk.Text(logs_frame, height=14, wrap="word", state="disabled")
        self._logs_widget.pack(side="left", fill="both", expand=True)
        scrollbar = compat.ttk.Scrollbar(logs_frame, orient="vertical", command=self._logs_widget.yview)
        scrollbar.pack(side="right", fill="y")
        self._logs_widget.configure(yscrollcommand=scrollbar.set)
        self.push_log("Painel principal iniciado")
        self._refresh_local_status()

    def _handle_save(self) -> None:
        from . import tk_support as compat

        try:
            new_config = self._build_config_from_form()
            if new_config is None:
                return
        except ValueError as exc:
            compat.messagebox.showerror("Erro", f"Valor invalido: {exc}")
            return
        except Exception as exc:
            compat.messagebox.showerror("Erro", f"Erro ao montar configuracao: {exc}")
            return

        is_valid, errors = ConfigurationValidator.validate(new_config)
        if not is_valid:
            compat.messagebox.showerror("Erro de Validacao", "Erros encontrados:\n\n" + "\n".join(errors))
            self._set_status("Configuracao invalida. Corrija os campos destacados nas mensagens.", success=False)
            return

        result = self._on_save(new_config)
        if result.get("success"):
            self.config = new_config
            self._set_status(result.get("message", "Configuracao salva com sucesso"), success=True)
            self._refresh_local_status()
        else:
            self._set_status(result.get("message", "Falha ao salvar configuracao"), success=False)

    def _handle_test_connection(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._apply_message(
                self._connection_var,
                self._connection_label,
                self._presenter.build_invalid_value_message("Teste", exc),
            )
            return

        result = self._on_test_connection(config)
        self._apply_message(
            self._connection_var,
            self._connection_label,
            self._presenter.build_connection_result(result, "Sem resposta do teste"),
        )
        self.push_log(f"Teste de conexao: {self._connection_var.get()}")

    def _handle_send_test(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._apply_message(
                self._connection_var,
                self._connection_label,
                self._presenter.build_invalid_value_message("Envio de teste", exc),
            )
            return

        result = self._on_send_test(config)
        feedback = self._presenter.build_connection_result(result, "Sem resposta do envio de teste")
        self._apply_message(self._connection_var, self._connection_label, feedback)
        self.push_log(f"Envio de teste: {feedback.text}")

    def _handle_refresh_voice_context(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._apply_message(
                self._voice_context_var,
                self._voice_context_label,
                self._presenter.build_invalid_value_message("Deteccao", exc),
            )
            return

        result = self._on_refresh_voice_context(config)
        feedback = self._presenter.build_connection_result(result, "Sem resposta da deteccao de canal")
        self._apply_message(self._voice_context_var, self._voice_context_label, feedback)
        self.push_log(f"Canal detectado: {feedback.text}")

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

    def _apply_message(self, variable: Optional[object], label, message: MainWindowMessage) -> None:
        if variable is not None and hasattr(variable, "set"):
            variable.set(message.text)
        self._set_label_color(label, message.color)

    def _set_label_color(self, label, color: str) -> None:
        if label is not None and hasattr(label, "configure"):
            label.configure(fg=color)

    def _clear_logs(self) -> None:
        from . import tk_support as compat

        if not self._logs_widget:
            return
        self._logs_widget.configure(state="normal")
        self._logs_widget.delete("1.0", compat.tk.END)
        self._logs_widget.configure(state="disabled")
        self.push_log("Logs limpos pelo usuario")

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
