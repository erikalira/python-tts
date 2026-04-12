"""Tk-based settings dialog for the Desktop App."""

from __future__ import annotations

from typing import Optional

from src.application.tts_voice_catalog import TTSCatalog, TTSVoiceOption
from src.infrastructure.tts.voice_catalog import RuntimeTTSCatalog

from ..config.desktop_config import ConfigurationValidator, DesktopAppConfig
from .config_dialog_contracts import ConfigInterface
from .config_dialog_presenter import ConfigDialogsPresenter
from .config_helpers import build_updated_config
from .settings_console_dialog import ConsoleConfig


class GUIConfig(ConfigInterface):
    """GUI configuration interface."""

    def __init__(self, tts_catalog: TTSCatalog | None = None):
        self.root: Optional[object] = None
        self.config: Optional[DesktopAppConfig] = None
        self.result: Optional[DesktopAppConfig] = None
        self._presenter = ConfigDialogsPresenter()
        self._tts_catalog = tts_catalog or RuntimeTTSCatalog()
        self.member_id_var: Optional[object] = None
        self.bot_url_var: Optional[object] = None
        self.engine_var: Optional[object] = None
        self.voice_selection_var: Optional[object] = None
        self.language_var: Optional[object] = None
        self.voice_id_var: Optional[object] = None
        self.rate_var: Optional[object] = None
        self.trigger_open_var: Optional[object] = None
        self.trigger_close_var: Optional[object] = None
        self.show_notifications_var = None
        self.console_logs_var = None
        self.local_tts_enabled_var = None
        self._voice_options_by_label: dict[str, TTSVoiceOption] = {}

    def show_config(self, config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        from . import tk_support as compat

        if not compat.TKINTER_AVAILABLE:
            print("Tkinter nao disponivel, usando console...")
            return ConsoleConfig().show_config(config)
        self.config = config
        self.result = None
        self.root = compat.tk.Tk()
        self.root.title("Desktop App - Configuracao")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)
        self._create_interface()
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        self.root.mainloop()
        return self.result

    def _create_interface(self):
        from . import tk_support as compat

        if not self.root or not self.config:
            return
        main_frame = compat.ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        compat.ttk.Label(main_frame, text="Desktop App Configuration", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        self._build_config_notebook(main_frame)
        button_frame = compat.ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        compat.ttk.Button(button_frame, text="Salvar", command=self._save_config).pack(side="right", padx=(10, 0))
        compat.ttk.Button(button_frame, text="Cancelar", command=self._cancel).pack(side="right")

    def _build_config_notebook(self, parent):
        from . import tk_support as compat

        notebook = compat.ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True, pady=(0, 10))

        discord_frame = compat.ttk.Frame(notebook, padding="10")
        notebook.add(discord_frame, text="Discord")
        self._create_discord_tab(discord_frame)

        tts_frame = compat.ttk.Frame(notebook, padding="10")
        notebook.add(tts_frame, text="TTS")
        self._create_tts_tab(tts_frame)

        hotkey_frame = compat.ttk.Frame(notebook, padding="10")
        notebook.add(hotkey_frame, text="Hotkey")
        self._create_hotkey_tab(hotkey_frame)

        interface_frame = compat.ttk.Frame(notebook, padding="10")
        notebook.add(interface_frame, text="Interface")
        self._create_interface_tab(interface_frame)
        return notebook

    def _create_discord_tab(self, parent):
        from . import tk_support as compat

        if not self.config:
            return
        compat.ttk.Label(parent, text="Discord User ID:").pack(anchor="w", pady=(0, 5))
        self.member_id_var = compat.tk.StringVar(value=self.config.discord.member_id or "")
        member_id_entry = compat.ttk.Entry(parent, textvariable=self.member_id_var, width=50)
        member_id_entry.pack(fill="x", pady=(0, 10))
        if hasattr(member_id_entry, "focus_set"):
            self.root.after(0, member_id_entry.focus_set)
        compat.ttk.Label(parent, text="Bot URL:").pack(anchor="w", pady=(0, 5))
        self.bot_url_var = compat.tk.StringVar(value=self.config.discord.bot_url)
        compat.ttk.Entry(parent, textvariable=self.bot_url_var, width=50).pack(fill="x", pady=(0, 10))
        compat.ttk.Label(
            parent,
            text=(
                "Dica: Clique com botao direito no seu nome no Discord, "
                "depois 'Copiar ID' para obter seu User ID. "
                "O bot vai descobrir o servidor pelo seu canal de voz atual."
            ),
            wraplength=400,
            font=("Arial", 8),
        ).pack(anchor="w", pady=(10, 0))

    def _create_tts_tab(self, parent):
        from . import tk_support as compat

        if not self.config:
            return
        compat.ttk.Label(parent, text="Engine de voz do bot:").pack(anchor="w", pady=(0, 5))
        self.engine_var = compat.tk.StringVar(value=self.config.tts.engine)
        compat.ttk.Combobox(
            parent,
            textvariable=self.engine_var,
            values=self._list_engine_values(),
            state="readonly",
        ).pack(fill="x", pady=(0, 10))
        compat.ttk.Label(
            parent,
            text=(
                "O caminho principal do app e enviar o texto para o bot do Discord. "
                "A voz local do Windows e opcional e fica nas preferencias da interface."
            ),
            wraplength=420,
            justify="left",
            font=("Arial", 8),
        ).pack(anchor="w", pady=(0, 10))
        compat.ttk.Label(parent, text="Voz do catalogo:").pack(anchor="w", pady=(0, 5))
        self.voice_selection_var = compat.tk.StringVar(value=self._resolve_selected_voice_label())
        voice_combobox = compat.ttk.Combobox(
            parent,
            textvariable=self.voice_selection_var,
            values=self._list_voice_labels(),
            state="readonly",
        )
        voice_combobox.pack(fill="x", pady=(0, 10))
        if hasattr(voice_combobox, "bind"):
            voice_combobox.bind("<<ComboboxSelected>>", self._handle_voice_selection)
        compat.ttk.Label(
            parent,
            text=(
                "Ao escolher uma voz do catalogo, o app atualiza engine, idioma e Voice ID automaticamente. "
                "Os campos abaixo continuam editaveis para configuracoes personalizadas."
            ),
            wraplength=420,
            justify="left",
            font=("Arial", 8),
        ).pack(anchor="w", pady=(0, 10))
        compat.ttk.Label(parent, text="Idioma:").pack(anchor="w", pady=(0, 5))
        self.language_var = compat.tk.StringVar(value=self.config.tts.language)
        compat.ttk.Entry(parent, textvariable=self.language_var, width=50).pack(fill="x", pady=(0, 10))
        compat.ttk.Label(parent, text="Voice ID:").pack(anchor="w", pady=(0, 5))
        self.voice_id_var = compat.tk.StringVar(value=self.config.tts.voice_id)
        compat.ttk.Entry(parent, textvariable=self.voice_id_var, width=50).pack(fill="x", pady=(0, 10))
        compat.ttk.Label(parent, text="Velocidade (50-400):").pack(anchor="w", pady=(0, 5))
        self.rate_var = compat.tk.StringVar(value=str(self.config.tts.rate))
        compat.ttk.Entry(parent, textvariable=self.rate_var, width=50).pack(fill="x", pady=(0, 10))

    def _create_hotkey_tab(self, parent):
        from . import tk_support as compat

        if not self.config:
            return
        compat.ttk.Label(parent, text="Trigger para iniciar:").pack(anchor="w", pady=(0, 5))
        self.trigger_open_var = compat.tk.StringVar(value=self.config.hotkey.trigger_open)
        compat.ttk.Entry(parent, textvariable=self.trigger_open_var, width=50).pack(fill="x", pady=(0, 10))
        compat.ttk.Label(parent, text="Trigger para finalizar:").pack(anchor="w", pady=(0, 5))
        self.trigger_close_var = compat.tk.StringVar(value=self.config.hotkey.trigger_close)
        compat.ttk.Entry(parent, textvariable=self.trigger_close_var, width=50).pack(fill="x", pady=(0, 10))
        compat.ttk.Label(
            parent,
            text=(
                f"Exemplo: Digite '{self.config.hotkey.trigger_open}ola mundo"
                f"{self.config.hotkey.trigger_close}' para falar 'ola mundo'"
            ),
            wraplength=400,
            font=("Arial", 8),
        ).pack(anchor="w", pady=(10, 0))

    def _create_interface_tab(self, parent):
        from . import tk_support as compat

        if not self.config:
            return
        self.show_notifications_var = compat.tk.BooleanVar(value=self.config.interface.show_notifications)
        self.console_logs_var = compat.tk.BooleanVar(value=self.config.interface.console_logs)
        self.local_tts_enabled_var = compat.tk.BooleanVar(value=self.config.interface.local_tts_enabled)
        compat.ttk.Checkbutton(parent, text="Exibir notificacoes do app", variable=self.show_notifications_var).pack(anchor="w", pady=(0, 10))
        compat.ttk.Checkbutton(parent, text="Manter logs detalhados na interface", variable=self.console_logs_var).pack(anchor="w", pady=(0, 10))
        compat.ttk.Checkbutton(
            parent,
            text="Ativar voz local opcional no app Windows (pyttsx3)",
            variable=self.local_tts_enabled_var,
        ).pack(anchor="w", pady=(0, 10))
        compat.ttk.Label(
            parent,
            text=(
                "Comportamento padrao: ao abrir o executavel, a janela principal permanece visivel. "
                "A bandeja funciona como acesso rapido e nao faz verificacoes automaticas de conexao."
            ),
            wraplength=420,
            justify="left",
            font=("Arial", 8),
        ).pack(anchor="w", pady=(10, 0))

    def _save_config(self):
        from . import tk_support as compat

        try:
            new_config = self._build_config_from_form()
            if new_config is None:
                return
            is_valid, errors = ConfigurationValidator.validate(new_config)
            if is_valid:
                self.result = new_config
                if self.root:
                    self.root.destroy()
            else:
                compat.messagebox.showerror(
                    "Erro de Validacao",
                    self._presenter.format_validation_errors(errors),
                )
        except ValueError as exc:
            compat.messagebox.showerror("Erro", f"Valor invalido: {exc}")
        except Exception as exc:
            compat.messagebox.showerror("Erro", f"Erro inesperado: {exc}")

    def _build_config_from_form(self) -> Optional[DesktopAppConfig]:
        if not self.config or not all(
            [
                self.member_id_var,
                self.bot_url_var,
                self.engine_var,
                self.voice_selection_var,
                self.language_var,
                self.voice_id_var,
                self.rate_var,
                self.trigger_open_var,
                self.trigger_close_var,
                self.show_notifications_var,
                self.console_logs_var,
                self.local_tts_enabled_var,
            ]
        ):
            return None
        return build_updated_config(
            self.config,
            member_id=self.member_id_var.get().strip(),
            bot_url=self.bot_url_var.get().strip(),
            engine=self.engine_var.get(),
            language=self.language_var.get().strip(),
            voice_id=self.voice_id_var.get().strip(),
            rate=int(self.rate_var.get()),
            trigger_open=self.trigger_open_var.get().strip(),
            trigger_close=self.trigger_close_var.get().strip(),
            show_notifications=bool(self.show_notifications_var.get()),
            console_logs=bool(self.console_logs_var.get()),
            local_tts_enabled=bool(self.local_tts_enabled_var.get()),
        )

    def _list_engine_values(self) -> list[str]:
        available_engines = {option.engine for option in self._tts_catalog.list_voice_options()}
        ordered_engines = ["gtts", "pyttsx3", "edge-tts"]
        return [engine for engine in ordered_engines if engine in available_engines] or ordered_engines

    def _list_voice_labels(self) -> list[str]:
        options = self._tts_catalog.list_voice_options()
        self._voice_options_by_label = {option.label: option for option in options}
        return [option.label for option in options]

    def _resolve_selected_voice_label(self) -> str:
        if not self.config:
            return ""

        selected_option = self._tts_catalog.find_voice_option(
            engine=self.config.tts.engine,
            language=self.config.tts.language,
            voice_id=self.config.tts.voice_id,
        )
        return selected_option.label if selected_option is not None else ""

    def _handle_voice_selection(self, _event=None) -> None:
        if not self.voice_selection_var:
            return

        selected_label = self.voice_selection_var.get().strip()
        selected_option = self._voice_options_by_label.get(selected_label)
        if selected_option is None:
            return

        if self.engine_var is not None and hasattr(self.engine_var, "set"):
            self.engine_var.set(selected_option.engine)
        if self.language_var is not None and hasattr(self.language_var, "set"):
            self.language_var.set(selected_option.language)
        if self.voice_id_var is not None and hasattr(self.voice_id_var, "set"):
            self.voice_id_var.set(selected_option.voice_id)

    def _cancel(self):
        self.result = None
        if self.root:
            self.root.destroy()
