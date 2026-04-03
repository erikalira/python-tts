"""Configuration dialog implementations for the Desktop App."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..config.desktop_config import (
    ConfigurationValidator,
    DesktopAppConfig,
    get_default_discord_bot_url,
)
from .config_helpers import (
    build_updated_config,
    normalize_optional_text,
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
        print("🎤 Desktop App - Configuração")
        print("=" * 50)

        current_id = config.discord.member_id or ""
        member_id = prompt_numeric_input(
            f"Discord User ID [{current_id}]: ",
            current_id,
            "Discord User ID deve conter apenas números!",
        )
        bot_url = resolve_text_value(input(f"Bot URL [{config.discord.bot_url}]: "), config.discord.bot_url)

        print("\n🎵 Engines TTS disponíveis:")
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
            print("Opção inválida!")

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
                print("Velocidade deve ser um número!")

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

        print("\n⌨️ Configuração de Triggers")
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
            print("Configuração salva com sucesso!")
            return new_config

        print("Erros na configuração:")
        for error in errors:
            print(f"   - {error}")
        return None


class InitialSetupGUI:
    """Initial setup GUI for first-time configuration."""

    def __init__(self):
        self.root: Optional[object] = None
        self.result: Optional[dict] = None
        self.member_id_var: Optional[object] = None
        self.channel_id_var: Optional[object] = None
        self.bot_url_var: Optional[object] = None

    def show_initial_setup(self) -> Optional[dict]:
        from . import simple_gui as compat

        if not compat.TKINTER_AVAILABLE:
            return self._console_initial_setup()
        try:
            self.root = compat.tk.Tk()
            self.root.title("Desktop App - Configuração Inicial")
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
            print(f"Erro na interface gráfica: {exc}")
            return self._console_initial_setup()

    def _create_initial_setup_widgets(self):
        from . import simple_gui as compat

        main_frame = compat.ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=compat.tk.BOTH, expand=True)
        compat.ttk.Label(
            main_frame,
            text="🎤 Desktop App - Configuração Inicial",
            font=("Arial", 16, "bold"),
        ).pack(pady=(0, 20))
        compat.ttk.Label(
            main_frame,
            text=(
                "Para usar o TTS no Discord, você precisa configurar seus IDs.\n"
                "Estes campos são obrigatórios para o funcionamento correto."
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
                "💡 Como encontrar: Discord → Configurações → Avançado → Modo Desenvolvedor (ON)\n"
                "   Botão direito no seu nome → Copiar ID"
            ),
            foreground="gray",
            font=("Arial", 8),
        ).pack(anchor=compat.tk.W, pady=(0, 10))

        compat.ttk.Label(discord_frame, text="Channel ID (opcional):").pack(anchor=compat.tk.W)
        self.channel_id_var = compat.tk.StringVar()
        compat.ttk.Entry(discord_frame, textvariable=self.channel_id_var, width=30).pack(fill=compat.tk.X, pady=(5, 10))
        compat.ttk.Label(
            discord_frame,
            text="💡 Como encontrar: Botão direito no canal de voz → Copiar ID",
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
            text="⚠️ Sem o Discord User ID, o TTS funcionará apenas localmente",
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
        self.result = {
            "member_id": None,
            "guild_id": None,
            "channel_id": None,
            "bot_url": get_default_discord_bot_url(),
            "skip_discord": True,
        }
        self.root.destroy()

    def _save_and_continue(self):
        from . import simple_gui as compat

        member_id = self.member_id_var.get().strip()
        channel_id = self.channel_id_var.get().strip()
        bot_url = self.bot_url_var.get().strip()

        if member_id and not member_id.isdigit():
            compat.messagebox.showerror("Erro", "Discord User ID deve conter apenas números!")
            return
        if channel_id and not channel_id.isdigit():
            compat.messagebox.showerror("Erro", "Channel ID deve conter apenas números!")
            return
        if not bot_url:
            compat.messagebox.showerror("Erro", "Bot URL é obrigatória!")
            return

        self.result = {
            "member_id": normalize_optional_text(member_id),
            "guild_id": None,
            "channel_id": normalize_optional_text(channel_id),
            "bot_url": bot_url,
            "skip_discord": False,
        }
        if member_id:
            compat.messagebox.showinfo("Sucesso", "Configuração salva! O TTS funcionará no Discord.")
        else:
            compat.messagebox.showinfo("Aviso", "Sem Discord User ID, o TTS funcionará apenas localmente.")
        self.root.destroy()

    def _console_initial_setup(self) -> Optional[dict]:
        print("\n" + "=" * 60)
        print("🎤 Desktop App - Configuração Inicial")
        print("=" * 60)
        print("Para usar o TTS no Discord, configure seus IDs:")
        print("")
        print("1. Discord User ID (seu ID de usuário):")
        print("   Como encontrar: Discord → Configurações → Avançado → Modo Desenvolvedor")
        print("   Depois: Botão direito no seu nome → Copiar ID")
        member_id = input("   Discord User ID (deixe vazio para pular): ").strip()
        if member_id and not member_id.isdigit():
            print("ID deve conter apenas números!")
            member_id = ""

        print("\n2. Channel ID (opcional):")
        print("   Como encontrar: Botão direito no canal de voz → Copiar ID")
        channel_id = input("   Channel ID (opcional): ").strip()
        if channel_id and not channel_id.isdigit():
            print("ID deve conter apenas números!")
            channel_id = ""

        print("\n3. Bot URL:")
        default_url = get_default_discord_bot_url()
        bot_url = input(f"   Bot URL [{default_url}]: ").strip()
        if not bot_url:
            bot_url = default_url

        if member_id:
            print("\nConfiguração salva! TTS funcionará no Discord.")
        else:
            print("\nSem Discord User ID, TTS funcionará apenas localmente.")

        return {
            "member_id": normalize_optional_text(member_id),
            "guild_id": None,
            "channel_id": normalize_optional_text(channel_id),
            "bot_url": bot_url,
            "skip_discord": not bool(member_id),
        }


class GUIConfig(ConfigInterface):
    """GUI configuration interface."""

    def __init__(self):
        self.root: Optional[object] = None
        self.config: Optional[DesktopAppConfig] = None
        self.result: Optional[DesktopAppConfig] = None
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
        from . import simple_gui as compat

        if not compat.TKINTER_AVAILABLE:
            print("Tkinter não disponível, usando console...")
            return ConsoleConfig().show_config(config)
        self.config = config
        self.result = None
        self.root = compat.tk.Tk()
        self.root.title("🎤 Desktop App - Configuração")
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
        from . import simple_gui as compat

        if not self.root or not self.config:
            return
        main_frame = compat.ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        compat.ttk.Label(main_frame, text="🎤 Desktop App Configuration", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        self._build_config_notebook(main_frame)
        button_frame = compat.ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        compat.ttk.Button(button_frame, text="Salvar", command=self._save_config).pack(side="right", padx=(10, 0))
        compat.ttk.Button(button_frame, text="Cancelar", command=self._cancel).pack(side="right")

    def _build_config_notebook(self, parent):
        from . import simple_gui as compat

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
        from . import simple_gui as compat

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
                "Dica: Clique com botão direito no seu nome no Discord, "
                "depois 'Copiar ID' para obter seu User ID. "
                "O bot vai descobrir o servidor pelo seu canal de voz atual."
            ),
            wraplength=400,
            font=("Arial", 8),
        ).pack(anchor="w", pady=(10, 0))

    def _create_tts_tab(self, parent):
        from . import simple_gui as compat

        if not self.config:
            return
        compat.ttk.Label(parent, text="Engine de voz do bot:").pack(anchor="w", pady=(0, 5))
        self.engine_var = compat.tk.StringVar(value=self.config.tts.engine)
        compat.ttk.Combobox(parent, textvariable=self.engine_var, values=["gtts", "pyttsx3"], state="readonly").pack(fill="x", pady=(0, 10))
        compat.ttk.Label(
            parent,
            text=(
                "O caminho principal do app e enviar o texto para o bot do Discord. "
                "A voz local do Windows é opcional e fica nas preferencias da interface."
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
        from . import simple_gui as compat

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
                f"Exemplo: Digite '{self.config.hotkey.trigger_open}olá mundo"
                f"{self.config.hotkey.trigger_close}' para falar 'olá mundo'"
            ),
            wraplength=400,
            font=("Arial", 8),
        ).pack(anchor="w", pady=(10, 0))

    def _create_interface_tab(self, parent):
        from . import simple_gui as compat

        if not self.config:
            return
        self.show_notifications_var = compat.tk.BooleanVar(value=self.config.interface.show_notifications)
        self.console_logs_var = compat.tk.BooleanVar(value=self.config.interface.console_logs)
        self.local_tts_enabled_var = compat.tk.BooleanVar(value=self.config.interface.local_tts_enabled)
        compat.ttk.Checkbutton(parent, text="Exibir notificações do app", variable=self.show_notifications_var).pack(anchor="w", pady=(0, 10))
        compat.ttk.Checkbutton(parent, text="Manter logs detalhados na interface", variable=self.console_logs_var).pack(anchor="w", pady=(0, 10))
        compat.ttk.Checkbutton(
            parent,
            text="Ativar voz local opcional no app Windows (pyttsx3)",
            variable=self.local_tts_enabled_var,
        ).pack(anchor="w", pady=(0, 10))
        compat.ttk.Label(
            parent,
            text=(
                "Comportamento padrão: ao abrir o executável, a janela principal permanece visível. "
                "A bandeja funciona como acesso rápido e não faz verificações automáticas de conexão."
            ),
            wraplength=420,
            justify="left",
            font=("Arial", 8),
        ).pack(anchor="w", pady=(10, 0))

    def _save_config(self):
        from . import simple_gui as compat

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
                compat.messagebox.showerror("Erro de Validação", f"Erros encontrados:\n\n{chr(10).join(errors)}")
        except ValueError as exc:
            compat.messagebox.showerror("Erro", f"Valor inválido: {exc}")
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
