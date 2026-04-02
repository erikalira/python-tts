#!/usr/bin/env python3
"""
Simple Configuration GUI - Clean Architecture (Fixed)
Provides simplified interfaces for configuration without complex type hints.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import replace
import os

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

from ..config.standalone_config import StandaloneConfig, ConfigurationValidator


class ConfigInterface(ABC):
    """Abstract interface for configuration."""
    
    @abstractmethod
    def show_config(self, config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Show configuration dialog."""
        pass


class ConsoleConfig(ConfigInterface):
    """Console configuration interface."""
    
    def show_config(self, config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Show console configuration."""
        print("\n" + "="*50)
        print("🎤 TTS Hotkey - Configuração")
        print("="*50)
        
        # Discord ID
        current_id = config.discord.member_id or ""
        while True:
            member_id = input(f"Discord User ID [{current_id}]: ").strip()
            if not member_id and current_id:
                member_id = current_id
                break
            if member_id and member_id.isdigit():
                break
            print("❌ Discord User ID deve conter apenas números!")

        current_guild_id = config.discord.guild_id or ""
        while True:
            guild_id = input(f"Discord Guild ID [{current_guild_id}]: ").strip()
            if not guild_id and current_guild_id:
                guild_id = current_guild_id
                break
            if guild_id and guild_id.isdigit():
                break
            print("❌ Discord Guild ID deve conter apenas números!")
        
        # Bot URL
        bot_url = input(f"Bot URL [{config.discord.bot_url}]: ").strip()
        if not bot_url:
            bot_url = config.discord.bot_url
        
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
        language = input(f"Idioma [{config.tts.language}]: ").strip()
        if not language:
            language = config.tts.language
        
        # Voice ID
        voice_id = input(f"Voice ID [{config.tts.voice_id}]: ").strip()
        if not voice_id:
            voice_id = config.tts.voice_id
        
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
        
        # Triggers
        print("\n⌨️ Configuração de Triggers")
        trigger_open = input(f"Trigger abrir [{config.hotkey.trigger_open}]: ").strip()
        if not trigger_open:
            trigger_open = config.hotkey.trigger_open
            
        trigger_close = input(f"Trigger fechar [{config.hotkey.trigger_close}]: ").strip()
        if not trigger_close:
            trigger_close = config.hotkey.trigger_close
        
        # Create new config using dataclasses.replace
        new_config = StandaloneConfig(
            discord=replace(config.discord,
                member_id=member_id,
                guild_id=guild_id,
                bot_url=bot_url
            ),
            tts=replace(config.tts,
                engine=engine,
                language=language,
                voice_id=voice_id,
                rate=rate
            ),
            hotkey=replace(config.hotkey,
                trigger_open=trigger_open,
                trigger_close=trigger_close
            ),
            interface=config.interface,
            network=config.network
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
            self.root.title("TTS Hotkey - Configuração Inicial")
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
        title_label = ttk.Label(main_frame, text="🎤 TTS Hotkey - Configuração Inicial", 
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
            'member_id': member_id if member_id else None,
            'guild_id': guild_id if guild_id else None,
            'channel_id': channel_id if channel_id else None,
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
        print("🎤 TTS Hotkey - Configuração Inicial")
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
            'member_id': member_id if member_id else None,
            'guild_id': guild_id if guild_id else None,
            'channel_id': channel_id if channel_id else None,
            'bot_url': bot_url,
            'skip_discord': not bool(member_id and guild_id)
        }


class GUIConfig(ConfigInterface):
    """GUI configuration interface."""
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.config: Optional[StandaloneConfig] = None
        self.result: Optional[StandaloneConfig] = None
        
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
        
    def show_config(self, config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Show GUI configuration."""
        if not TKINTER_AVAILABLE:
            print("❌ Tkinter não disponível, usando console...")
            console = ConsoleConfig()
            return console.show_config(config)
        
        self.config = config
        self.result = None
        
        self.root = tk.Tk()
        self.root.title("🎤 TTS Hotkey - Configuração")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
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
        title = ttk.Label(main_frame, text="🎤 TTS Hotkey Configuration", 
                         font=("Arial", 14, "bold"))
        title.pack(pady=(0, 20))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Discord tab
        discord_frame = ttk.Frame(notebook, padding="10")
        notebook.add(discord_frame, text="🌐 Discord")
        self._create_discord_tab(discord_frame)
        
        # TTS tab
        tts_frame = ttk.Frame(notebook, padding="10")
        notebook.add(tts_frame, text="🎵 TTS")
        self._create_tts_tab(tts_frame)
        
        # Hotkey tab
        hotkey_frame = ttk.Frame(notebook, padding="10")
        notebook.add(hotkey_frame, text="⌨️ Hotkey")
        self._create_hotkey_tab(hotkey_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="💾 Salvar", 
                  command=self._save_config).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self._cancel).pack(side="right")
    
    def _create_discord_tab(self, parent):
        """Create Discord configuration tab."""
        if not self.config:
            return
            
        # Member ID
        ttk.Label(parent, text="Discord User ID:").pack(anchor="w", pady=(0, 5))
        self.member_id_var = tk.StringVar(value=self.config.discord.member_id or "")
        ttk.Entry(parent, textvariable=self.member_id_var, width=50).pack(fill="x", pady=(0, 10))

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
        ttk.Label(parent, text="Engine TTS:").pack(anchor="w", pady=(0, 5))
        self.engine_var = tk.StringVar(value=self.config.tts.engine)
        engine_combo = ttk.Combobox(parent, textvariable=self.engine_var, 
                                  values=["gtts", "pyttsx3"], state="readonly")
        engine_combo.pack(fill="x", pady=(0, 10))
        
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
    
    def _save_config(self):
        """Save configuration."""
        if not self.config or not all([
            self.member_id_var, self.bot_url_var, self.engine_var,
            self.guild_id_var,
            self.language_var, self.voice_id_var, self.rate_var,
            self.trigger_open_var, self.trigger_close_var
        ]):
            return
            
        try:
            # Get values
            member_id = self.member_id_var.get().strip()
            guild_id = self.guild_id_var.get().strip()
            bot_url = self.bot_url_var.get().strip()
            engine = self.engine_var.get()
            language = self.language_var.get().strip()
            voice_id = self.voice_id_var.get().strip()
            rate = int(self.rate_var.get())
            trigger_open = self.trigger_open_var.get().strip()
            trigger_close = self.trigger_close_var.get().strip()
            
            # Create new config using dataclasses.replace
            new_config = StandaloneConfig(
                discord=replace(self.config.discord,
                    member_id=member_id,
                    guild_id=guild_id,
                    bot_url=bot_url
                ),
                tts=replace(self.config.tts,
                    engine=engine,
                    language=language,
                    voice_id=voice_id,
                    rate=rate
                ),
                hotkey=replace(self.config.hotkey,
                    trigger_open=trigger_open,
                    trigger_close=trigger_close
                ),
                interface=self.config.interface,
                network=self.config.network
            )
            
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
    
    def _cancel(self):
        """Cancel configuration."""
        self.result = None
        if self.root:
            self.root.destroy()


class ConfigurationService:
    """Service for managing configuration interfaces."""
    
    def __init__(self, prefer_gui: bool = True):
        self.prefer_gui = prefer_gui
    
    def get_configuration(self, current_config: StandaloneConfig) -> Optional[StandaloneConfig]:
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
