#!/usr/bin/env python3
"""
Simple Configuration GUI - Clean Architecture
Provides simplified interfaces for configuration without complex type hints.
"""

from abc import ABC, abstractmethod
from typing import Optional

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
        
        # Bot URL
        bot_url = input(f"Bot URL [{config.discord.bot_url}]: ").strip()
        if not bot_url:
            bot_url = config.discord.bot_url
        
        # TTS Engine
        print(f"\n🎵 Engines TTS disponíveis:")
        print("1. pyttsx3 (local)")
        print("2. discord (via bot)")
        print("3. both (ambos)")
        
        while True:
            choice = input(f"Escolha [1-3, atual: {config.tts.engine}]: ").strip()
            if not choice:
                engine = config.tts.engine
                break
            elif choice == "1":
                engine = "pyttsx3"
                break
            elif choice == "2":
                engine = "discord"
                break
            elif choice == "3":
                engine = "both"
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
        
        # Hotkey
        print(f"\n⌨️ Configuração de Hotkey")
        hotkey = input(f"Hotkey [{config.hotkey.keys}]: ").strip()
        if not hotkey:
            hotkey = config.hotkey.keys
        
        # Create new config
        new_config = StandaloneConfig(
            discord=config.discord._replace(
                member_id=member_id,
                bot_url=bot_url
            ),
            tts=config.tts._replace(
                engine=engine,
                language=language,
                voice_id=voice_id,
                rate=rate
            ),
            hotkey=config.hotkey._replace(
                keys=hotkey
            ),
            notifications=config.notifications
        )
        
        # Validate
        validator = ConfigurationValidator()
        if validator.validate_config(new_config):
            print("✅ Configuração salva com sucesso!")
            return new_config
        else:
            print("❌ Erro na validação da configuração!")
            return None


class GUIConfig(ConfigInterface):
    """GUI configuration interface."""
    
    def __init__(self):
        self.root = None
        self.config = None
        self.result = None
        
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
        # Member ID
        ttk.Label(parent, text="Discord User ID:").pack(anchor="w", pady=(0, 5))
        self.member_id_var = tk.StringVar(value=self.config.discord.member_id or "")
        ttk.Entry(parent, textvariable=self.member_id_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Bot URL
        ttk.Label(parent, text="Bot URL:").pack(anchor="w", pady=(0, 5))
        self.bot_url_var = tk.StringVar(value=self.config.discord.bot_url)
        ttk.Entry(parent, textvariable=self.bot_url_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Help text
        help_text = ("Dica: Clique com botão direito no seu nome no Discord, "
                    "depois 'Copiar ID' para obter seu User ID.")
        ttk.Label(parent, text=help_text, wraplength=400, 
                 font=("Arial", 8)).pack(anchor="w", pady=(10, 0))
    
    def _create_tts_tab(self, parent):
        """Create TTS configuration tab."""
        # Engine
        ttk.Label(parent, text="Engine TTS:").pack(anchor="w", pady=(0, 5))
        self.engine_var = tk.StringVar(value=self.config.tts.engine)
        engine_combo = ttk.Combobox(parent, textvariable=self.engine_var, 
                                  values=["pyttsx3", "discord", "both"], state="readonly")
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
        # Keys
        ttk.Label(parent, text="Combinação de teclas:").pack(anchor="w", pady=(0, 5))
        self.keys_var = tk.StringVar(value=self.config.hotkey.keys)
        ttk.Entry(parent, textvariable=self.keys_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Help
        help_text = ("Exemplos: 'ctrl+shift+t', 'alt+space', 'f12'\n"
                    "Use + para separar teclas modificadoras.")
        ttk.Label(parent, text=help_text, wraplength=400, 
                 font=("Arial", 8)).pack(anchor="w", pady=(10, 0))
    
    def _save_config(self):
        """Save configuration."""
        try:
            # Get values
            member_id = self.member_id_var.get().strip()
            bot_url = self.bot_url_var.get().strip()
            engine = self.engine_var.get()
            language = self.language_var.get().strip()
            voice_id = self.voice_id_var.get().strip()
            rate = int(self.rate_var.get())
            keys = self.keys_var.get().strip()
            
            # Create new config
            new_config = StandaloneConfig(
                discord=self.config.discord._replace(
                    member_id=member_id,
                    bot_url=bot_url
                ),
                tts=self.config.tts._replace(
                    engine=engine,
                    language=language,
                    voice_id=voice_id,
                    rate=rate
                ),
                hotkey=self.config.hotkey._replace(
                    keys=keys
                ),
                notifications=self.config.notifications
            )
            
            # Validate
            validator = ConfigurationValidator()
            if validator.validate_config(new_config):
                self.result = new_config
                self.root.destroy()
            else:
                messagebox.showerror("Erro", "Configuração inválida!")
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _cancel(self):
        """Cancel configuration."""
        self.result = None
        self.root.destroy()


class ConfigurationService:
    """Service for managing configuration interfaces."""
    
    def __init__(self, prefer_gui: bool = True):
        self.prefer_gui = prefer_gui
    
    def get_configuration(self, current_config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Get configuration from user."""
        if self.prefer_gui and TKINTER_AVAILABLE:
            interface = GUIConfig()
        else:
            interface = ConsoleConfig()
        
        return interface.show_config(current_config)