#!/usr/bin/env python3
"""
Simple Configuration GUI - Clean Architecture (Fixed)
Provides simplified interfaces for configuration without complex type hints.
"""

from abc import ABC, abstractmethod
import logging
import queue
from typing import Callable, Optional
import os

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

from ..config.desktop_config import DesktopAppConfig, ConfigurationValidator
from .config_helpers import (
    build_updated_config,
    normalize_optional_text,
    prompt_numeric_input,
    resolve_text_value,
)

logger = logging.getLogger(__name__)


class ConfigInterface(ABC):
    """Abstract interface for configuration."""
    
    @abstractmethod
    def show_config(self, config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        """Show configuration dialog."""
        pass


class ConsoleConfig(ConfigInterface):
    """Console configuration interface."""
    
    def show_config(self, config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        """Show console configuration."""
        print("\n" + "="*50)
        print("🎤 Desktop App - Configuração")
        print("="*50)
        
        # Discord ID
        current_id = config.discord.member_id or ""
        member_id = prompt_numeric_input(
            f"Discord User ID [{current_id}]: ",
            current_id,
            "❌ Discord User ID deve conter apenas números!",
        )

        current_guild_id = config.discord.guild_id or ""
        guild_id = prompt_numeric_input(
            f"Discord Guild ID [{current_guild_id}]: ",
            current_guild_id,
            "❌ Discord Guild ID deve conter apenas números!",
        )
        
        # Bot URL
        bot_url = resolve_text_value(input(f"Bot URL [{config.discord.bot_url}]: "), config.discord.bot_url)
        
        # TTS Engine
        print("\n🎵 Engines TTS disponíveis:")
        print("1. gtts (Google TTS)")
        print("2. pyttsx3 (local)")
        
        while True:
            choice = input(f"Escolha [1-2, atual: {config.tts.engine}]: ").strip()
            if not choice:
                engine = config.tts.engine
                break
            elif choice == "1":
                engine = "gtts"
                break
            elif choice == "2":
                engine = "pyttsx3"
                break
            else:
                print("❌ Opção inválida!")
        
        # Language
        language = resolve_text_value(input(f"Idioma [{config.tts.language}]: "), config.tts.language)
        
        # Voice ID
        voice_id = resolve_text_value(input(f"Voice ID [{config.tts.voice_id}]: "), config.tts.voice_id)
        
        # Rate
        while True:
            rate_input = input(f"Velocidade [{config.tts.rate}]: ").strip()
            if not rate_input:
                rate = config.tts.rate
                break
            try:
                rate = int(rate_input)
                if 50 <= rate <= 400:
                    break
                else:
                    print("❌ Velocidade deve estar entre 50 e 400!")
            except ValueError:
                print("❌ Velocidade deve ser um número!")
        
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

        # Triggers
        print("\n⌨️ Configuração de Triggers")
        trigger_open = resolve_text_value(input(f"Trigger abrir [{config.hotkey.trigger_open}]: "), config.hotkey.trigger_open)
        trigger_close = resolve_text_value(input(f"Trigger fechar [{config.hotkey.trigger_close}]: "), config.hotkey.trigger_close)
        
        new_config = build_updated_config(
            config,
            member_id=member_id,
            guild_id=guild_id,
            bot_url=bot_url,
            engine=engine,
            language=language,
            voice_id=voice_id,
            rate=rate,
            trigger_open=trigger_open,
            trigger_close=trigger_close,
            local_tts_enabled=local_tts_enabled,
        )
        
        # Validate
        is_valid, errors = ConfigurationValidator.validate(new_config)
        if is_valid:
            print("✅ Configuração salva com sucesso!")
            return new_config
        else:
            print("❌ Erros na configuração:")
            for error in errors:
                print(f"   - {error}")
            return None


class InitialSetupGUI:
    """Initial setup GUI for first-time configuration."""
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.result: Optional[dict] = None
        
        # Variables for form fields
        self.member_id_var: Optional[tk.StringVar] = None
        self.guild_id_var: Optional[tk.StringVar] = None
        self.channel_id_var: Optional[tk.StringVar] = None
        self.bot_url_var: Optional[tk.StringVar] = None
    
    def show_initial_setup(self) -> Optional[dict]:
        """Show initial setup dialog for Discord IDs."""
        if not TKINTER_AVAILABLE:
            return self._console_initial_setup()
        
        try:
            self.root = tk.Tk()
            self.root.title("Desktop App - Configuração Inicial")
            self.root.geometry("550x500")
            self.root.resizable(False, False)
            
            # Center window
            self.root.geometry("+%d+%d" % (
                (self.root.winfo_screenwidth() / 2 - 275),
                (self.root.winfo_screenheight() / 2 - 250)
            ))
            
            self._create_initial_setup_widgets()
            
            # Make dialog modal
            self.root.transient()
            self.root.grab_set()
            
            # Start the GUI
            self.root.mainloop()
            
            return self.result
            
        except Exception as e:
            print(f"❌ Erro na interface gráfica: {e}")
            return self._console_initial_setup()
    
    def _create_initial_setup_widgets(self):
        """Create widgets for initial setup."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎤 Desktop App - Configuração Inicial", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
            text="Para usar o TTS no Discord, você precisa configurar seus IDs.\n"
                 "Estes campos são obrigatórios para o funcionamento correto.",
            justify=tk.CENTER)
        instructions.pack(pady=(0, 20))
        
        # Discord ID Section
        discord_frame = ttk.LabelFrame(main_frame, text="Discord Configuration", padding="10")
        discord_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Member ID
        ttk.Label(discord_frame, text="Seu Discord User ID:").pack(anchor=tk.W)
        self.member_id_var = tk.StringVar()
        member_id_entry = ttk.Entry(discord_frame, textvariable=self.member_id_var, width=30)
        member_id_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Member ID Help
        help_text = ttk.Label(discord_frame, 
            text="💡 Como encontrar: Discord → Configurações → Avançado → Modo Desenvolvedor (ON)\n"
                 "   Botão direito no seu nome → Copiar ID",
            foreground='gray', font=('Arial', 8))
        help_text.pack(anchor=tk.W, pady=(0, 10))

        # Guild ID
        ttk.Label(discord_frame, text="Guild ID (servidor):").pack(anchor=tk.W)
        self.guild_id_var = tk.StringVar()
        guild_id_entry = ttk.Entry(discord_frame, textvariable=self.guild_id_var, width=30)
        guild_id_entry.pack(fill=tk.X, pady=(5, 10))

        guild_help = ttk.Label(
            discord_frame,
            text="💡 Como encontrar: Botão direito no servidor → Copiar ID",
            foreground='gray',
            font=('Arial', 8),
        )
        guild_help.pack(anchor=tk.W, pady=(0, 10))
        
        # Channel ID
        ttk.Label(discord_frame, text="Channel ID (opcional):").pack(anchor=tk.W)
        self.channel_id_var = tk.StringVar()
        channel_id_entry = ttk.Entry(discord_frame, textvariable=self.channel_id_var, width=30)
        channel_id_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Channel ID Help
        channel_help = ttk.Label(discord_frame, 
            text="💡 Como encontrar: Botão direito no canal de voz → Copiar ID",
            foreground='gray', font=('Arial', 8))
        channel_help.pack(anchor=tk.W, pady=(0, 10))
        
        # Bot URL
        ttk.Label(discord_frame, text="Bot URL:").pack(anchor=tk.W)
        self.bot_url_var = tk.StringVar(value=os.getenv('DISCORD_BOT_URL'))
        bot_url_entry = ttk.Entry(discord_frame, textvariable=self.bot_url_var, width=50)
        bot_url_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Warning
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        warning_label = ttk.Label(warning_frame, 
            text="⚠️ Sem o Discord User ID, o TTS funcionará apenas localmente",
            foreground='orange', font=('Arial', 9, 'italic'))
        warning_label.pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Continuar Sem Discord", 
                  command=self._skip_discord).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Salvar e Continuar", 
                  command=self._save_and_continue).pack(side=tk.RIGHT)
    
    def _skip_discord(self):
        """Skip Discord configuration."""
        self.result = {
            'member_id': None,
            'guild_id': None,
            'channel_id': None,
            'bot_url': os.getenv('DISCORD_BOT_URL'),
            'skip_discord': True
        }
        self.root.destroy()
    
    def _save_and_continue(self):
        """Save configuration and continue."""
        member_id = self.member_id_var.get().strip()
        guild_id = self.guild_id_var.get().strip()
        channel_id = self.channel_id_var.get().strip()
        bot_url = self.bot_url_var.get().strip()
        
        # Validate Member ID
        if member_id and not member_id.isdigit():
            messagebox.showerror("Erro", "Discord User ID deve conter apenas números!")
            return

        if guild_id and not guild_id.isdigit():
            messagebox.showerror("Erro", "Guild ID deve conter apenas números!")
            return
        
        # Validate Channel ID
        if channel_id and not channel_id.isdigit():
            messagebox.showerror("Erro", "Channel ID deve conter apenas números!")
            return
        
        # Validate Bot URL
        if not bot_url:
            messagebox.showerror("Erro", "Bot URL é obrigatória!")
            return

        if member_id and not guild_id:
            messagebox.showerror("Erro", "Guild ID é obrigatória para usar o bot do Discord!")
            return
        
        self.result = {
            'member_id': normalize_optional_text(member_id),
            'guild_id': normalize_optional_text(guild_id),
            'channel_id': normalize_optional_text(channel_id),
            'bot_url': bot_url,
            'skip_discord': False
        }
        
        if member_id:
            messagebox.showinfo("Sucesso", "Configuração salva! O TTS funcionará no Discord.")
        else:
            messagebox.showinfo("Aviso", "Sem Discord User ID, o TTS funcionará apenas localmente.")
        
        self.root.destroy()
    
    def _console_initial_setup(self) -> Optional[dict]:
        """Console version of initial setup."""
        print("\n" + "="*60)
        print("🎤 Desktop App - Configuração Inicial")
        print("="*60)
        print("Para usar o TTS no Discord, configure seus IDs:")
        print("")
        
        # Member ID
        print("1. Discord User ID (seu ID de usuário):")
        print("   Como encontrar: Discord → Configurações → Avançado → Modo Desenvolvedor")
        print("   Depois: Botão direito no seu nome → Copiar ID")
        member_id = input("   Discord User ID (deixe vazio para pular): ").strip()
        
        if member_id and not member_id.isdigit():
            print("❌ ID deve conter apenas números!")
            member_id = ""

        # Guild ID
        print("\n2. Guild ID (ID do servidor, obrigatório para modo Discord):")
        print("   Como encontrar: Botão direito no servidor → Copiar ID")
        guild_id = input("   Guild ID (deixe vazio para pular): ").strip()

        if guild_id and not guild_id.isdigit():
            print("❌ ID deve conter apenas números!")
            guild_id = ""
        
        # Channel ID
        print("\n3. Channel ID (opcional):")
        print("   Como encontrar: Botão direito no canal de voz → Copiar ID")
        channel_id = input("   Channel ID (opcional): ").strip()
        
        if channel_id and not channel_id.isdigit():
            print("❌ ID deve conter apenas números!")
            channel_id = ""
        
        # Bot URL
        print("\n4. Bot URL:")
        default_url = os.getenv('DISCORD_BOT_URL')
        bot_url = input(f"   Bot URL [{default_url}]: ").strip()
        if not bot_url:
            bot_url = default_url
        
        if member_id:
            print(f"\n✅ Configuração salva! TTS funcionará no Discord.")
        else:
            print(f"\n⚠️ Sem Discord User ID, TTS funcionará apenas localmente.")
        
        return {
            'member_id': normalize_optional_text(member_id),
            'guild_id': normalize_optional_text(guild_id),
            'channel_id': normalize_optional_text(channel_id),
            'bot_url': bot_url,
            'skip_discord': not bool(member_id and guild_id)
        }


class GUIConfig(ConfigInterface):
    """GUI configuration interface."""
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.config: Optional[DesktopAppConfig] = None
        self.result: Optional[DesktopAppConfig] = None
        
        # Variables for form fields
        self.member_id_var: Optional[tk.StringVar] = None
        self.guild_id_var: Optional[tk.StringVar] = None
        self.bot_url_var: Optional[tk.StringVar] = None
        self.engine_var: Optional[tk.StringVar] = None
        self.language_var: Optional[tk.StringVar] = None
        self.voice_id_var: Optional[tk.StringVar] = None
        self.rate_var: Optional[tk.StringVar] = None
        self.trigger_open_var: Optional[tk.StringVar] = None
        self.trigger_close_var: Optional[tk.StringVar] = None
        self.show_notifications_var = None
        self.console_logs_var = None
        self.local_tts_enabled_var = None
        
    def show_config(self, config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        """Show GUI configuration."""
        if not TKINTER_AVAILABLE:
            print("❌ Tkinter não disponível, usando console...")
            console = ConsoleConfig()
            return console.show_config(config)
        
        self.config = config
        self.result = None
        
        self.root = tk.Tk()
        self.root.title("🎤 Desktop App - Configuração")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)
        
        # Create interface
        self._create_interface()
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        self.root.mainloop()
        return self.result
    
    def _create_interface(self):
        """Create the GUI interface."""
        if not self.root or not self.config:
            return
            
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="🎤 Desktop App Configuration", 
                         font=("Arial", 14, "bold"))
        title.pack(pady=(0, 20))
        self._build_config_notebook(main_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="💾 Salvar", 
                  command=self._save_config).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self._cancel).pack(side="right")

    def _build_config_notebook(self, parent):
        """Create and populate the shared configuration notebook."""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True, pady=(0, 10))

        discord_frame = ttk.Frame(notebook, padding="10")
        notebook.add(discord_frame, text="🌐 Discord")
        self._create_discord_tab(discord_frame)

        tts_frame = ttk.Frame(notebook, padding="10")
        notebook.add(tts_frame, text="🎵 TTS")
        self._create_tts_tab(tts_frame)

        hotkey_frame = ttk.Frame(notebook, padding="10")
        notebook.add(hotkey_frame, text="⌨️ Hotkey")
        self._create_hotkey_tab(hotkey_frame)

        interface_frame = ttk.Frame(notebook, padding="10")
        notebook.add(interface_frame, text="🖥️ Interface")
        self._create_interface_tab(interface_frame)
        return notebook
    
    def _create_discord_tab(self, parent):
        """Create Discord configuration tab."""
        if not self.config:
            return
            
        # Member ID
        ttk.Label(parent, text="Discord User ID:").pack(anchor="w", pady=(0, 5))
        self.member_id_var = tk.StringVar(value=self.config.discord.member_id or "")
        member_id_entry = ttk.Entry(parent, textvariable=self.member_id_var, width=50)
        member_id_entry.pack(fill="x", pady=(0, 10))
        if hasattr(member_id_entry, "focus_set"):
            self.root.after(0, member_id_entry.focus_set)

        # Guild ID
        ttk.Label(parent, text="Discord Guild ID:").pack(anchor="w", pady=(0, 5))
        self.guild_id_var = tk.StringVar(value=self.config.discord.guild_id or "")
        ttk.Entry(parent, textvariable=self.guild_id_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Bot URL
        ttk.Label(parent, text="Bot URL:").pack(anchor="w", pady=(0, 5))
        self.bot_url_var = tk.StringVar(value=self.config.discord.bot_url)
        ttk.Entry(parent, textvariable=self.bot_url_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Help text
        help_text = ("Dica: Clique com botão direito no seu nome no Discord, "
                    "depois 'Copiar ID' para obter seu User ID. "
                    "Faça o mesmo no servidor para obter o Guild ID.")
        ttk.Label(parent, text=help_text, wraplength=400, 
                 font=("Arial", 8)).pack(anchor="w", pady=(10, 0))
    
    def _create_tts_tab(self, parent):
        """Create TTS configuration tab."""
        if not self.config:
            return
            
        # Engine
        ttk.Label(parent, text="Engine de voz do bot:").pack(anchor="w", pady=(0, 5))
        self.engine_var = tk.StringVar(value=self.config.tts.engine)
        engine_combo = ttk.Combobox(parent, textvariable=self.engine_var, 
                                  values=["gtts", "pyttsx3"], state="readonly")
        engine_combo.pack(fill="x", pady=(0, 10))
        ttk.Label(
            parent,
            text=(
                "O caminho principal do app e enviar o texto para o bot do Discord. "
                "A voz local do Windows e opcional e fica nas preferencias da interface."
            ),
            wraplength=420,
            justify="left",
            font=("Arial", 8),
        ).pack(anchor="w", pady=(0, 10))
        
        # Language
        ttk.Label(parent, text="Idioma:").pack(anchor="w", pady=(0, 5))
        self.language_var = tk.StringVar(value=self.config.tts.language)
        ttk.Entry(parent, textvariable=self.language_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Voice ID
        ttk.Label(parent, text="Voice ID:").pack(anchor="w", pady=(0, 5))
        self.voice_id_var = tk.StringVar(value=self.config.tts.voice_id)
        ttk.Entry(parent, textvariable=self.voice_id_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Rate
        ttk.Label(parent, text="Velocidade (50-400):").pack(anchor="w", pady=(0, 5))
        self.rate_var = tk.StringVar(value=str(self.config.tts.rate))
        ttk.Entry(parent, textvariable=self.rate_var, width=50).pack(fill="x", pady=(0, 10))
    
    def _create_hotkey_tab(self, parent):
        """Create Hotkey configuration tab."""
        if not self.config:
            return
            
        # Trigger Open
        ttk.Label(parent, text="Trigger para iniciar:").pack(anchor="w", pady=(0, 5))
        self.trigger_open_var = tk.StringVar(value=self.config.hotkey.trigger_open)
        ttk.Entry(parent, textvariable=self.trigger_open_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Trigger Close
        ttk.Label(parent, text="Trigger para finalizar:").pack(anchor="w", pady=(0, 5))
        self.trigger_close_var = tk.StringVar(value=self.config.hotkey.trigger_close)
        ttk.Entry(parent, textvariable=self.trigger_close_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Help
        help_text = (f"Exemplo: Digite '{self.config.hotkey.trigger_open}olá mundo{self.config.hotkey.trigger_close}' "
                    "para falar 'olá mundo'")
        ttk.Label(parent, text=help_text, wraplength=400, 
                 font=("Arial", 8)).pack(anchor="w", pady=(10, 0))

    def _create_interface_tab(self, parent):
        """Create interface configuration tab."""
        if not self.config:
            return

        self.show_notifications_var = tk.BooleanVar(value=self.config.interface.show_notifications)
        self.console_logs_var = tk.BooleanVar(value=self.config.interface.console_logs)
        self.local_tts_enabled_var = tk.BooleanVar(value=self.config.interface.local_tts_enabled)

        ttk.Checkbutton(
            parent,
            text="Exibir notificações do app",
            variable=self.show_notifications_var,
        ).pack(anchor="w", pady=(0, 10))
        ttk.Checkbutton(
            parent,
            text="Manter logs detalhados na interface",
            variable=self.console_logs_var,
        ).pack(anchor="w", pady=(0, 10))
        ttk.Checkbutton(
            parent,
            text="Ativar voz local opcional no app Windows (pyttsx3)",
            variable=self.local_tts_enabled_var,
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(
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
        """Save configuration."""
        try:
            new_config = self._build_config_from_form()
            if new_config is None:
                return
            
            # Validate
            is_valid, errors = ConfigurationValidator.validate(new_config)
            if is_valid:
                self.result = new_config
                if self.root:
                    self.root.destroy()
            else:
                error_msg = "\n".join(errors)
                messagebox.showerror("Erro de Validação", f"Erros encontrados:\n\n{error_msg}")
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def _build_config_from_form(self) -> Optional[DesktopAppConfig]:
        """Build configuration from the current form values."""
        if not self.config or not all([
            self.member_id_var, self.bot_url_var, self.engine_var,
            self.guild_id_var,
            self.language_var, self.voice_id_var, self.rate_var,
            self.trigger_open_var, self.trigger_close_var
            , self.show_notifications_var, self.console_logs_var, self.local_tts_enabled_var
        ]):
            return None

        member_id = self.member_id_var.get().strip()
        guild_id = self.guild_id_var.get().strip()
        bot_url = self.bot_url_var.get().strip()
        engine = self.engine_var.get()
        language = self.language_var.get().strip()
        voice_id = self.voice_id_var.get().strip()
        rate = int(self.rate_var.get())
        trigger_open = self.trigger_open_var.get().strip()
        trigger_close = self.trigger_close_var.get().strip()
        show_notifications = bool(self.show_notifications_var.get())
        console_logs = bool(self.console_logs_var.get())
        local_tts_enabled = bool(self.local_tts_enabled_var.get())

        return build_updated_config(
            self.config,
            member_id=member_id,
            guild_id=guild_id,
            bot_url=bot_url,
            engine=engine,
            language=language,
            voice_id=voice_id,
            rate=rate,
            trigger_open=trigger_open,
            trigger_close=trigger_close,
            show_notifications=show_notifications,
            console_logs=console_logs,
            local_tts_enabled=local_tts_enabled,
        )
    
    def _cancel(self):
        """Cancel configuration."""
        self.result = None
        if self.root:
            self.root.destroy()


class UILogHandler(logging.Handler):
    """Logging handler that forwards formatted records to a queue."""

    def __init__(self, target_queue: "queue.Queue[str]"):
        super().__init__()
        self._target_queue = target_queue
        self.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S"))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._target_queue.put_nowait(self.format(record))
        except Exception:
            pass


class DesktopAppMainWindow(GUIConfig):
    """Main Desktop App window that keeps configuration, actions, and logs visible."""

    def __init__(
        self,
        config: DesktopAppConfig,
        on_save: Callable[[DesktopAppConfig], dict],
        on_test_connection: Callable[[DesktopAppConfig], dict],
        on_send_test: Callable[[DesktopAppConfig], dict],
    ):
        super().__init__()
        self.config = config
        self._on_save = on_save
        self._on_test_connection = on_test_connection
        self._on_send_test = on_send_test
        self._log_queue: "queue.Queue[str]" = queue.Queue()
        self._log_handler = UILogHandler(self._log_queue)
        self._status_var: Optional[tk.StringVar] = None
        self._config_var: Optional[tk.StringVar] = None
        self._connection_var: Optional[tk.StringVar] = None
        self._logs_widget = None
        self._status_label = None
        self._config_label = None
        self._connection_label = None

    def show(self) -> None:
        """Display the Desktop App main window."""
        if not TKINTER_AVAILABLE:
            raise RuntimeError("Tkinter não disponível para a janela principal")

        self.root = tk.Tk()
        self.root.title("Desktop App - Painel Principal")
        self.root.geometry("980x760")
        self.root.minsize(860, 640)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        self._attach_logging()
        self._create_main_layout()
        self._drain_logs()
        self.root.mainloop()

    def focus(self) -> None:
        """Bring the window to the foreground when possible."""
        if not self.root:
            return
        self.root.after(0, self._focus_now)

    def push_log(self, message: str) -> None:
        """Append an ad-hoc log message to the visible activity panel."""
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
        main_frame = ttk.Frame(self.root, padding="16")
        main_frame.pack(fill="both", expand=True)

        self._status_var = tk.StringVar(value="Preencha os campos, teste a conexão e mantenha a janela aberta durante o uso.")
        self._config_var = tk.StringVar(value="")
        self._connection_var = tk.StringVar(value="Conexão ainda não testada")

        ttk.Label(main_frame, text="Desktop App", font=("Arial", 18, "bold")).pack(anchor="w")
        ttk.Label(
            main_frame,
            text=(
                "Use esta janela como painel principal do app. Aqui você configura o Desktop App, "
                "valida a conexão com o bot e acompanha a atividade sem depender do terminal."
            ),
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(6, 12))

        status_frame = ttk.LabelFrame(main_frame, text="Status do app", padding="10")
        status_frame.pack(fill="x", pady=(0, 12))
        self._status_label = tk.Label(status_frame, textvariable=self._status_var, anchor="w", justify="left", fg="#155724")
        self._status_label.pack(anchor="w")
        self._config_label = tk.Label(status_frame, textvariable=self._config_var, anchor="w", justify="left", fg="#856404")
        self._config_label.pack(anchor="w", pady=(8, 0))
        self._connection_label = tk.Label(status_frame, textvariable=self._connection_var, anchor="w", justify="left", fg="#856404")
        self._connection_label.pack(anchor="w", pady=(8, 0))

        form_frame = ttk.LabelFrame(main_frame, text="Configuração", padding="10")
        form_frame.pack(fill="both", expand=True, pady=(0, 12))
        self._build_config_notebook(form_frame)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(0, 12))
        ttk.Button(action_frame, text="Salvar configuração", command=self._handle_save).pack(side="left")
        ttk.Button(action_frame, text="Testar conexão", command=self._handle_test_connection).pack(side="left", padx=(10, 0))
        ttk.Button(action_frame, text="Enviar teste de voz", command=self._handle_send_test).pack(side="left", padx=(10, 0))
        ttk.Button(action_frame, text="Limpar logs", command=self._clear_logs).pack(side="left", padx=(10, 0))
        ttk.Button(action_frame, text="Fechar app", command=self._close).pack(side="right")

        help_frame = ttk.LabelFrame(main_frame, text="Como usar", padding="10")
        help_frame.pack(fill="x", pady=(0, 12))
        ttk.Label(
            help_frame,
            text=(
                "1. Preencha os dados do bot e clique em 'Testar conexão'. "
                "2. Salve a configuração. "
                f"3. Use {self.config.hotkey.trigger_open}texto{self.config.hotkey.trigger_close} para enviar fala no uso normal. "
                "4. Se quiser, use 'Enviar teste de voz' para validar o fluxo manualmente."
            ),
            wraplength=900,
            justify="left",
        ).pack(anchor="w")

        logs_frame = ttk.LabelFrame(main_frame, text="Atividade", padding="10")
        logs_frame.pack(fill="both", expand=True)
        self._logs_widget = tk.Text(logs_frame, height=14, wrap="word", state="disabled")
        self._logs_widget.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=self._logs_widget.yview)
        scrollbar.pack(side="right", fill="y")
        self._logs_widget.configure(yscrollcommand=scrollbar.set)

        self.push_log("Painel principal iniciado")
        self._refresh_local_status()

    def _handle_save(self) -> None:
        try:
            new_config = self._build_config_from_form()
            if new_config is None:
                return
        except ValueError as exc:
            messagebox.showerror("Erro", f"Valor inválido: {exc}")
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Erro ao montar configuração: {exc}")
            return

        is_valid, errors = ConfigurationValidator.validate(new_config)
        if not is_valid:
            messagebox.showerror("Erro de Validação", "Erros encontrados:\n\n" + "\n".join(errors))
            self._set_status("Configuração inválida. Corrija os campos destacados nas mensagens.", success=False)
            return

        result = self._on_save(new_config)
        if result.get("success"):
            self.config = new_config
            self._set_status(result.get("message", "Configuração salva com sucesso"), success=True)
            self._refresh_local_status()
        else:
            self._set_status(result.get("message", "Falha ao salvar configuração"), success=False)

    def _handle_test_connection(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._connection_var.set(f"Teste falhou: valor inválido ({exc})")
            return

        result = self._on_test_connection(config)
        self._connection_var.set(result.get("message", "Sem resposta do teste"))
        self._set_label_color(self._connection_label, "#155724" if result.get("success") else "#721c24")
        self.push_log(f"Teste de conexão: {self._connection_var.get()}")

    def _handle_send_test(self) -> None:
        try:
            config = self._build_config_from_form()
            if config is None:
                return
        except ValueError as exc:
            self._connection_var.set(f"Envio de teste falhou: valor inválido ({exc})")
            self._set_label_color(self._connection_label, "#721c24")
            return

        result = self._on_send_test(config)
        message = result.get("message", "Sem resposta do envio de teste")
        self._connection_var.set(message)
        self._set_label_color(self._connection_label, "#155724" if result.get("success") else "#721c24")
        self.push_log(f"Envio de teste: {message}")

    def _set_status(self, message: str, success: bool) -> None:
        if self._status_var:
            prefix = "OK:" if success else "Atenção:"
            self._status_var.set(f"{prefix} {message}")
        self._set_label_color(self._status_label, "#155724" if success else "#721c24")
        self.push_log(message)

    def _refresh_local_status(self) -> None:
        is_discord_ready = bool(
            self.config
            and self.config.discord.bot_url
            and self.config.discord.guild_id
            and self.config.discord.member_id
        )
        config_message = (
            "Bot configurado: URL, Guild ID e User ID preenchidos."
            if is_discord_ready
            else "Configuração incompleta: preencha Bot URL, Guild ID e User ID para usar o bot."
        )
        if (
            self.config
            and not is_discord_ready
            and self.config.interface.local_tts_enabled
        ):
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
        if not self._logs_widget:
            return
        self._logs_widget.configure(state="normal")
        self._logs_widget.delete("1.0", tk.END)
        self._logs_widget.configure(state="disabled")
        self.push_log("Logs limpos pelo usuário")

    def _append_log(self, message: str) -> None:
        if not self._logs_widget:
            return
        self._logs_widget.configure(state="normal")
        self._logs_widget.insert(tk.END, message + "\n")
        self._logs_widget.see(tk.END)
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


class ConfigurationService:
    """Service for managing configuration interfaces."""
    
    def __init__(self, prefer_gui: bool = True):
        self.prefer_gui = prefer_gui
    
    def get_configuration(self, current_config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        """Get configuration from user."""
        if self.prefer_gui and TKINTER_AVAILABLE:
            try:
                gui = GUIConfig()
                return gui.show_config(current_config)
            except Exception as e:
                print(f"[CONFIG] ❌ Erro na GUI: {e}")
                print("[CONFIG] 🔄 Alternando para console...")
        
        # Fallback to console
        console = ConsoleConfig()
        return console.show_config(current_config)
