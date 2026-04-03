"""Main Desktop App panel implementation."""

from __future__ import annotations

import logging
import queue
from typing import Callable, Optional

from ..config.desktop_config import ConfigurationValidator, DesktopAppConfig
from .config_dialogs import GUIConfig
from .ui_logging import UILogHandler

logger = logging.getLogger(__name__)


class DesktopAppMainWindow(GUIConfig):
    """Main Desktop App window that keeps configuration, actions, and logs visible."""

    def __init__(
        self,
        config: DesktopAppConfig,
        on_save: Callable[[DesktopAppConfig], dict],
        on_test_connection: Callable[[DesktopAppConfig], dict],
        on_send_test: Callable[[DesktopAppConfig], dict],
        on_refresh_voice_context: Callable[[DesktopAppConfig], dict],
    ):
        super().__init__()
        self.config = config
        self._on_save = on_save
        self._on_test_connection = on_test_connection
        self._on_send_test = on_send_test
        self._on_refresh_voice_context = on_refresh_voice_context
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
            raise RuntimeError("Tkinter nÃ£o disponÃ­vel para a janela principal")
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

        main_frame = compat.ttk.Frame(self.root, padding="16")
        main_frame.pack(fill="both", expand=True)
        self._status_var = compat.tk.StringVar(
            value="Preencha os campos, teste a conexÃ£o e mantenha a janela aberta durante o uso."
        )
        self._config_var = compat.tk.StringVar(value="")
        self._connection_var = compat.tk.StringVar(value="ConexÃ£o ainda nÃ£o testada")
        self._voice_context_var = compat.tk.StringVar(value="Canal detectado ainda nao consultado")

        compat.ttk.Label(main_frame, text="Desktop App", font=("Arial", 18, "bold")).pack(anchor="w")
        compat.ttk.Label(
            main_frame,
            text=(
                "Use esta janela como painel principal do app. Aqui vocÃª configura o Desktop App, "
                "valida a conexÃ£o com o bot e acompanha a atividade sem depender do terminal."
            ),
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(6, 12))

        status_frame = compat.ttk.LabelFrame(main_frame, text="Status do app", padding="10")
        status_frame.pack(fill="x", pady=(0, 12))
        self._status_label = compat.tk.Label(status_frame, textvariable=self._status_var, anchor="w", justify="left", fg="#155724")
        self._status_label.pack(anchor="w")
        self._config_label = compat.tk.Label(status_frame, textvariable=self._config_var, anchor="w", justify="left", fg="#856404")
        self._config_label.pack(anchor="w", pady=(8, 0))
        self._connection_label = compat.tk.Label(status_frame, textvariable=self._connection_var, anchor="w", justify="left", fg="#856404")
        self._connection_label.pack(anchor="w", pady=(8, 0))
        self._voice_context_label = compat.tk.Label(status_frame, textvariable=self._voice_context_var, anchor="w", justify="left", fg="#856404")
        self._voice_context_label.pack(anchor="w", pady=(8, 0))

        form_frame = compat.ttk.LabelFrame(main_frame, text="ConfiguraÃ§Ã£o", padding="10")
        form_frame.pack(fill="both", expand=True, pady=(0, 12))
        self._build_config_notebook(form_frame)

        action_frame = compat.ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(0, 12))
        compat.ttk.Button(action_frame, text="Salvar configuraÃ§Ã£o", command=self._handle_save).pack(side="left")
        compat.ttk.Button(action_frame, text="Testar conexÃ£o", command=self._handle_test_connection).pack(side="left", padx=(10, 0))
        compat.ttk.Button(action_frame, text="Recarregar canal detectado", command=self._handle_refresh_voice_context).pack(side="left", padx=(10, 0))
        compat.ttk.Button(action_frame, text="Enviar teste de voz", command=self._handle_send_test).pack(side="left", padx=(10, 0))
        compat.ttk.Button(action_frame, text="Limpar logs", command=self._clear_logs).pack(side="left", padx=(10, 0))
        compat.ttk.Button(action_frame, text="Fechar app", command=self._close).pack(side="right")

        help_frame = compat.ttk.LabelFrame(main_frame, text="Como usar", padding="10")
        help_frame.pack(fill="x", pady=(0, 12))
        compat.ttk.Label(
            help_frame,
            text=(
                "1. Preencha os dados do bot e clique em 'Testar conexÃ£o'. "
                "2. Use 'Recarregar canal detectado' para verificar o servidor e canal de voz encontrados para seu usuario. "
                "3. Salve a configuraÃ§Ã£o. "
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
            compat.messagebox.showerror("Erro", f"Valor invÃ¡lido: {exc}")
            return
        except Exception as exc:
            compat.messagebox.showerror("Erro", f"Erro ao montar configuraÃ§Ã£o: {exc}")
            return

        is_valid, errors = ConfigurationValidator.validate(new_config)
        if not is_valid:
            compat.messagebox.showerror("Erro de ValidaÃ§Ã£o", "Erros encontrados:\n\n" + "\n".join(errors))
            self._set_status("ConfiguraÃ§Ã£o invÃ¡lida. Corrija os campos destacados nas mensagens.", success=False)
            return

        result = self._on_save(new_config)
        if result.get("success"):
            self.config = new_config
            self._set_status(result.get("message", "ConfiguraÃ§Ã£o salva com sucesso"), success=True)
            self._refresh_local_status()
        else:
            self._set_status(result.get("message", "Falha ao salvar configuraÃ§Ã£o"), success=False)

    def _handle_test_connection(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._connection_var.set(f"Teste falhou: valor invÃ¡lido ({exc})")
            return
        result = self._on_test_connection(config)
        self._connection_var.set(result.get("message", "Sem resposta do teste"))
        self._set_label_color(self._connection_label, "#155724" if result.get("success") else "#721c24")
        self.push_log(f"Teste de conexÃ£o: {self._connection_var.get()}")

    def _handle_send_test(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._connection_var.set(f"Envio de teste falhou: valor invÃ¡lido ({exc})")
            self._set_label_color(self._connection_label, "#721c24")
            return
        result = self._on_send_test(config)
        message = result.get("message", "Sem resposta do envio de teste")
        self._connection_var.set(message)
        self._set_label_color(self._connection_label, "#155724" if result.get("success") else "#721c24")
        self.push_log(f"Envio de teste: {message}")

    def _handle_refresh_voice_context(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            if self._voice_context_var:
                self._voice_context_var.set(f"Deteccao falhou: valor invalido ({exc})")
            self._set_label_color(self._voice_context_label, "#721c24")
            return
        result = self._on_refresh_voice_context(config)
        message = result.get("message", "Sem resposta da deteccao de canal")
        if self._voice_context_var:
            self._voice_context_var.set(message)
        self._set_label_color(self._voice_context_label, "#155724" if result.get("success") else "#721c24")
        self.push_log(f"Canal detectado: {message}")

    def _set_status(self, message: str, success: bool) -> None:
        if self._status_var:
            prefix = "OK:" if success else "AtenÃ§Ã£o:"
            self._status_var.set(f"{prefix} {message}")
        self._set_label_color(self._status_label, "#155724" if success else "#721c24")
        self.push_log(message)

    def _refresh_local_status(self) -> None:
        is_discord_ready = bool(self.config and self.config.discord.bot_url and self.config.discord.member_id)
        config_message = (
            "Bot configurado: URL e User ID preenchidos."
            if is_discord_ready
            else "ConfiguraÃ§Ã£o incompleta: preencha Bot URL e User ID para usar o bot."
        )
        if self.config and not is_discord_ready and self.config.interface.local_tts_enabled:
            config_message += " Voz local opcional ativada como fallback."
        elif self.config and not is_discord_ready:
            config_message += " Voz local opcional desativada."
        if self._config_var:
            self._config_var.set(config_message)
        self._set_label_color(self._config_label, "#155724" if is_discord_ready else "#856404")

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
        self.push_log("Logs limpos pelo usuÃ¡rio")

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
