"""Configuration dialog implementations for the Desktop App."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..config.desktop_config import (
    ConfigurationValidator,
    DesktopAppConfig,
    get_default_discord_bot_url,
)
from .config_dialog_presenter import ConfigDialogsPresenter, InitialSetupResult
from .config_helpers import (
    build_updated_config,
    prompt_numeric_input,
    resolve_text_value,
)


class ConfigInterface(ABC):
    """Abstract interface for configuration."""

    @abstractmethod
    def show_config(self, config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        """Show configuration dialog."""


class ConsoleConfig(ConfigInterface):
    """Console configuration interface."""

    def show_config(self, config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        print("\n" + "=" * 50)
        print("Desktop App - Configuracao")
        print("=" * 50)

        current_id = config.discord.member_id or ""
        member_id = prompt_numeric_input(
            f"Discord User ID [{current_id}]: ",
            current_id,
            "Discord User ID deve conter apenas numeros!",
        )
        bot_url = resolve_text_value(input(f"Bot URL [{config.discord.bot_url}]: "), config.discord.bot_url)

        print("\nEngines TTS disponiveis:")
        print("1. gtts (Google TTS)")
        print("2. pyttsx3 (local)")
        while True:
            choice = input(f"Escolha [1-2, atual: {config.tts.engine}]: ").strip()
            if not choice:
                engine = config.tts.engine
                break
            if choice == "1":
                engine = "gtts"
                break
            if choice == "2":
                engine = "pyttsx3"
                break
            print("Opcao invalida!")

        language = resolve_text_value(input(f"Idioma [{config.tts.language}]: "), config.tts.language)
        voice_id = resolve_text_value(input(f"Voice ID [{config.tts.voice_id}]: "), config.tts.voice_id)

        while True:
            rate_input = input(f"Velocidade [{config.tts.rate}]: ").strip()
            if not rate_input:
                rate = config.tts.rate
                break
            try:
                rate = int(rate_input)
                if 50 <= rate <= 400:
                    break
                print("Velocidade deve estar entre 50 e 400!")
            except ValueError:
                print("Velocidade deve ser um numero!")

        print("\nLocal voice in the Windows app:")
        print("1. Disabled (recommended: use only the Discord bot)")
        print("2. Enabled (accessibility/local fallback with pyttsx3)")
        while True:
            local_choice = input(
                "Enable local voice in the Windows app? "
                f"[1-2, current: {'enabled' if config.interface.local_tts_enabled else 'disabled'}]: "
            ).strip()
            if not local_choice:
                local_tts_enabled = config.interface.local_tts_enabled
                break
            if local_choice == "1":
                local_tts_enabled = False
                break
            if local_choice == "2":
                local_tts_enabled = True
                break
            print("Invalid option!")

        print("\nConfiguracao de Triggers")
        trigger_open = resolve_text_value(
            input(f"Trigger abrir [{config.hotkey.trigger_open}]: "),
            config.hotkey.trigger_open,
        )
        trigger_close = resolve_text_value(
            input(f"Trigger fechar [{config.hotkey.trigger_close}]: "),
            config.hotkey.trigger_close,
        )

        new_config = build_updated_config(
            config,
            member_id=member_id,
            bot_url=bot_url,
            engine=engine,
            language=language,
            voice_id=voice_id,
            rate=rate,
            trigger_open=trigger_open,
            trigger_close=trigger_close,
            local_tts_enabled=local_tts_enabled,
        )

        is_valid, errors = ConfigurationValidator.validate(new_config)
        if is_valid:
            print("Configuracao salva com sucesso!")
            return new_config

        print("Erros na configuracao:")
        for error in errors:
            print(f"   - {error}")
        return None


class InitialSetupGUI:
    """Initial setup GUI for first-time configuration."""

    def __init__(self):
        self.root: Optional[object] = None
        self.result: Optional[InitialSetupResult] = None
        self.member_id_var: Optional[object] = None
        self.bot_url_var: Optional[object] = None
        self._presenter = ConfigDialogsPresenter()

    def show_initial_setup(self) -> Optional[InitialSetupResult]:
        from . import tk_support as compat

        if not compat.TKINTER_AVAILABLE:
            return self._console_initial_setup()
        try:
            self.root = compat.tk.Tk()
            self.root.title("Desktop App - Configuracao Inicial")
            self.root.geometry("550x500")
            self.root.resizable(False, False)
            self.root.geometry(
                "+%d+%d"
                % (
                    (self.root.winfo_screenwidth() / 2 - 275),
                    (self.root.winfo_screenheight() / 2 - 250),
                )
            )
            self._create_initial_setup_widgets()
            self.root.transient()
            self.root.grab_set()
            self.root.mainloop()
            return self.result
        except Exception as exc:
            print(f"Erro na interface grafica: {exc}")
            return self._console_initial_setup()

    def _create_initial_setup_widgets(self):
        from . import tk_support as compat

        main_frame = compat.ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=compat.tk.BOTH, expand=True)
        compat.ttk.Label(
            main_frame,
            text="Desktop App - Configuracao Inicial",
            font=("Arial", 16, "bold"),
        ).pack(pady=(0, 20))
        compat.ttk.Label(
            main_frame,
            text=(
                "Para usar o TTS no Discord, configure seu Discord User ID.\n"
                "O bot vai inferir o servidor e o canal pela sua presenca em voz."
            ),
            justify=compat.tk.CENTER,
        ).pack(pady=(0, 20))

        discord_frame = compat.ttk.LabelFrame(main_frame, text="Discord Configuration", padding="10")
        discord_frame.pack(fill=compat.tk.X, pady=(0, 15))
        compat.ttk.Label(discord_frame, text="Seu Discord User ID:").pack(anchor=compat.tk.W)
        self.member_id_var = compat.tk.StringVar()
        compat.ttk.Entry(discord_frame, textvariable=self.member_id_var, width=30).pack(fill=compat.tk.X, pady=(5, 10))
        compat.ttk.Label(
            discord_frame,
            text=(
                "Como encontrar: Discord -> Configuracoes -> Avancado -> Modo Desenvolvedor (ON)\n"
                "   Botao direito no seu nome -> Copiar ID"
            ),
            foreground="gray",
            font=("Arial", 8),
        ).pack(anchor=compat.tk.W, pady=(0, 10))

        compat.ttk.Label(discord_frame, text="Bot URL:").pack(anchor=compat.tk.W)
        self.bot_url_var = compat.tk.StringVar(value=get_default_discord_bot_url())
        compat.ttk.Entry(discord_frame, textvariable=self.bot_url_var, width=50).pack(fill=compat.tk.X, pady=(5, 10))

        warning_frame = compat.ttk.Frame(main_frame)
        warning_frame.pack(fill=compat.tk.X, pady=(0, 20))
        compat.ttk.Label(
            warning_frame,
            text="Sem o Discord User ID, o TTS funcionara apenas localmente",
            foreground="orange",
            font=("Arial", 9, "italic"),
        ).pack()

        button_frame = compat.ttk.Frame(main_frame)
        button_frame.pack(fill=compat.tk.X)
        compat.ttk.Button(button_frame, text="Continuar Sem Discord", command=self._skip_discord).pack(
            side=compat.tk.LEFT, padx=(0, 10)
        )
        compat.ttk.Button(button_frame, text="Salvar e Continuar", command=self._save_and_continue).pack(
            side=compat.tk.RIGHT
        )

    def _skip_discord(self):
        self.result = self._presenter.build_skip_discord_result(
            bot_url=get_default_discord_bot_url()
        )
        self.root.destroy()

    def _save_and_continue(self):
        from . import tk_support as compat

        member_id = self.member_id_var.get().strip()
        bot_url = self.bot_url_var.get().strip()

        validation_error = self._presenter.validate_initial_setup(
            member_id=member_id,
            bot_url=bot_url,
        )
        if validation_error:
            compat.messagebox.showerror(validation_error.title, validation_error.message)
            return

        self.result, feedback = self._presenter.build_initial_setup_result(
            member_id=member_id,
            bot_url=bot_url,
        )
        compat.messagebox.showinfo(feedback.title, feedback.message)
        self.root.destroy()

    def _console_initial_setup(self) -> Optional[InitialSetupResult]:
        print("\n" + "=" * 60)
        print("Desktop App - Configuracao Inicial")
        print("=" * 60)
        print("Para usar o TTS no Discord, configure seu Discord User ID:")
        print("")
        print("1. Discord User ID (seu ID de usuario):")
        print("   Como encontrar: Discord -> Configuracoes -> Avancado -> Modo Desenvolvedor")
        print("   Depois: Botao direito no seu nome -> Copiar ID")
        member_id = input("   Discord User ID (deixe vazio para pular): ").strip()
        if member_id and not member_id.isdigit():
            print("ID deve conter apenas numeros!")
            member_id = ""

        print("\n2. Bot URL:")
        default_url = get_default_discord_bot_url()
        bot_url = input(f"   Bot URL [{default_url}]: ").strip()
        if not bot_url:
            bot_url = default_url

        if member_id:
            print("\nConfiguracao salva! TTS funcionara no Discord.")
        else:
            print("\nSem Discord User ID, TTS funcionara apenas localmente.")

        return self._presenter.build_console_initial_setup_result(
            member_id=member_id,
            bot_url=bot_url,
        )


class GUIConfig(ConfigInterface):
    """GUI configuration interface."""

    def __init__(self):
        self.root: Optional[object] = None
        self.config: Optional[DesktopAppConfig] = None
        self.result: Optional[DesktopAppConfig] = None
        self._presenter = ConfigDialogsPresenter()
        self.member_id_var: Optional[object] = None
        self.bot_url_var: Optional[object] = None
        self.engine_var: Optional[object] = None
        self.language_var: Optional[object] = None
        self.voice_id_var: Optional[object] = None
        self.rate_var: Optional[object] = None
        self.trigger_open_var: Optional[object] = None
        self.trigger_close_var: Optional[object] = None
        self.show_notifications_var = None
        self.console_logs_var = None
        self.local_tts_enabled_var = None

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
        compat.ttk.Combobox(parent, textvariable=self.engine_var, values=["gtts", "pyttsx3"], state="readonly").pack(fill="x", pady=(0, 10))
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

    def _cancel(self):
        self.result = None
        if self.root:
            self.root.destroy()
