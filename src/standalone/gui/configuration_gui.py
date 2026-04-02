#!/usr/bin/env python3
"""
Configuration GUI Module - Clean Architecture
Provides graphical and console interfaces for configuration.
"""

from abc import ABC, abstractmethod
from typing import Optional

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    _tkinter_available = True
except ImportError:
    _tkinter_available = False

from ..config.standalone_config import StandaloneConfig, ConfigurationValidator
from .config_helpers import (
    build_updated_config,
    prompt_numeric_input,
    resolve_text_value,
    validate_numeric_field,
)


class ConfigurationInterface(ABC):
    """Abstract interface for configuration input."""
    
    @abstractmethod
    def show_configuration_dialog(self, current_config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Show configuration dialog and return updated config or None if cancelled."""
        pass


class ConsoleConfigurationInterface(ConfigurationInterface):
    """Console-based configuration interface."""
    
    def show_configuration_dialog(self, current_config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Show console configuration dialog."""
        print("\n" + "="*50)
        print("🎤 TTS Hotkey - Configuração via Console")
        print("="*50)
        
        # Discord Member ID
        current_id = current_config.discord.member_id or ""
        member_id = prompt_numeric_input(
            f"Discord User ID [{current_id}]: ",
            current_id,
            "❌ Discord User ID deve conter apenas números!",
        )

        current_guild_id = current_config.discord.guild_id or ""
        guild_id = prompt_numeric_input(
            f"Discord Guild ID [{current_guild_id}]: ",
            current_guild_id,
            "❌ Discord Guild ID deve conter apenas números!",
        )
        
        updated_config = build_updated_config(
            current_config,
            member_id=member_id,
            guild_id=guild_id,
        )
        
        print("✅ Configuração atualizada!")
        return updated_config


class GUIConfigurationInterface(ConfigurationInterface):
    """GUI-based configuration interface using tkinter."""
    
    def __init__(self):
        self.result: Optional[StandaloneConfig] = None
        self.root: Optional[tk.Tk] = None
        self._current_config: Optional[StandaloneConfig] = None
        
        # Form variables
        self.member_id_var: Optional[tk.StringVar] = None
        self.guild_id_var: Optional[tk.StringVar] = None
        self.bot_url_var: Optional[tk.StringVar] = None
        self.engine_var: Optional[tk.StringVar] = None
        self.language_var: Optional[tk.StringVar] = None
    
    def show_configuration_dialog(self, current_config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Show GUI configuration dialog."""
        if not _tkinter_available:
            console_interface = ConsoleConfigurationInterface()
            return console_interface.show_configuration_dialog(current_config)
        
        try:
            self._current_config = current_config
            self._create_window()
            self._create_widgets()
            self.root.mainloop()
            
            return self.result
        except Exception as e:
            print(f"[CONFIG] Erro na interface gráfica: {e}")
            console_interface = ConsoleConfigurationInterface()
            return console_interface.show_configuration_dialog(current_config)
    
    def _create_window(self) -> None:
        """Create the main window."""
        self.root = tk.Tk()
        self.root.title("TTS Hotkey - Configuração")
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
    
    def _create_widgets(self) -> None:
        """Create the configuration widgets."""
        # Title
        title_label = tk.Label(
            self.root, 
            text="🎤 TTS Hotkey - Configuração", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Main frame with scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Main content frame
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        self._create_discord_section(main_frame)
        self._create_tts_section(main_frame)
        self._create_buttons(main_frame)
    
    def _create_discord_section(self, parent) -> None:
        """Create Discord configuration section."""
        # Discord section
        discord_frame = ttk.LabelFrame(parent, text="🌐 Discord Configuration", padding="10")
        discord_frame.pack(fill="x", pady=(0, 15))
        
        # Discord Member ID (required)
        ttk.Label(
            discord_frame, 
            text="Discord User ID (obrigatório):", 
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.member_id_var = tk.StringVar(value=self._current_config.discord.member_id or "")
        member_id_entry = ttk.Entry(discord_frame, textvariable=self.member_id_var, width=50)
        member_id_entry.pack(fill="x", pady=(0, 5))
        
        # Help text for Discord ID
        help_text = tk.Text(discord_frame, height=3, wrap=tk.WORD, font=("Arial", 8))
        help_text.insert("1.0", "💡 Para obter seu Discord User ID:\n"
                                "1. No Discord, vá em Configurações > Avançado > Modo Desenvolvedor (ativar)\n"
                                "2. Clique com botão direito em seu nome e escolha 'Copiar ID'")
        help_text.config(state="disabled", bg="#f0f0f0")
        help_text.pack(fill="x", pady=(0, 10))

        ttk.Label(
            discord_frame,
            text="Discord Guild ID (obrigatório):",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.guild_id_var = tk.StringVar(value=self._current_config.discord.guild_id or "")
        guild_id_entry = ttk.Entry(discord_frame, textvariable=self.guild_id_var, width=50)
        guild_id_entry.pack(fill="x", pady=(0, 5))

        guild_help_text = tk.Text(discord_frame, height=2, wrap=tk.WORD, font=("Arial", 8))
        guild_help_text.insert("1.0", "💡 Para obter o Guild ID:\n"
                                      "1. No Discord, clique com botão direito no servidor e escolha 'Copiar ID'")
        guild_help_text.config(state="disabled", bg="#f0f0f0")
        guild_help_text.pack(fill="x", pady=(0, 10))
        
        # Bot URL
        ttk.Label(discord_frame, text="URL do Bot (opcional):").pack(anchor="w", pady=(0, 5))
        self.bot_url_var = tk.StringVar(value=self._current_config.discord.bot_url or "")
        bot_url_entry = ttk.Entry(discord_frame, textvariable=self.bot_url_var, width=50)
        bot_url_entry.pack(fill="x", pady=(0, 10))
    
    def _create_tts_section(self, parent: ttk.Frame) -> None:
        """Create TTS configuration section."""
        # TTS section
        tts_frame = ttk.LabelFrame(parent, text="🎤 TTS Configuration", padding="10")
        tts_frame.pack(fill="x", pady=(0, 15))
        
        # TTS Engine
        ttk.Label(tts_frame, text="Engine de TTS:").pack(anchor="w", pady=(0, 5))
        self.engine_var = tk.StringVar(value=self._current_config.tts.engine)
        engine_combo = ttk.Combobox(
            tts_frame, 
            textvariable=self.engine_var, 
            values=["gtts", "pyttsx3", "edge-tts"], 
            state="readonly"
        )
        engine_combo.pack(fill="x", pady=(0, 10))
        
        # Language
        ttk.Label(tts_frame, text="Idioma:").pack(anchor="w", pady=(0, 5))
        self.language_var = tk.StringVar(value=self._current_config.tts.language)
        language_combo = ttk.Combobox(
            tts_frame, 
            textvariable=self.language_var,
            values=["pt", "en", "es", "fr"], 
            state="readonly"
        )
        language_combo.pack(fill="x", pady=(0, 10))
    
    def _create_buttons(self, parent: ttk.Frame) -> None:
        """Create action buttons."""
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(
            button_frame, 
            text="💾 Salvar e Continuar", 
            command=self._save_config
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_frame, 
            text="❌ Cancelar", 
            command=self._cancel
        ).pack(side="right")
    
    def _save_config(self) -> None:
        """Save configuration and close."""
        member_id = self.member_id_var.get().strip()
        guild_id = self.guild_id_var.get().strip()

        member_error = validate_numeric_field(
            member_id,
            required=True,
            required_message="Discord User ID é obrigatório!",
            numeric_message="Discord User ID deve conter apenas números!",
        )
        if member_error:
            messagebox.showerror("Erro", member_error)
            return

        guild_error = validate_numeric_field(
            guild_id,
            required=True,
            required_message="Discord Guild ID é obrigatório!",
            numeric_message="Discord Guild ID deve conter apenas números!",
        )
        if guild_error:
            messagebox.showerror("Erro", guild_error)
            return

        updated_config = build_updated_config(
            self._current_config,
            member_id=member_id,
            guild_id=guild_id,
            bot_url=resolve_text_value(self.bot_url_var.get(), self._current_config.discord.bot_url),
            engine=self.engine_var.get(),
            language=self.language_var.get(),
        )
        
        # Validate configuration
        is_valid, errors = ConfigurationValidator.validate(updated_config)
        if not is_valid:
            messagebox.showerror("Erro de Validação", "\n".join(errors))
            return
        
        self.result = updated_config
        self._close_window()
    
    def _cancel(self) -> None:
        """Cancel configuration."""
        self.result = None
        self._close_window()
    
    def _close_window(self) -> None:
        """Close the configuration window."""
        if self.root:
            self.root.quit()
            self.root.destroy()


class ConfigurationUIFactory:
    """Factory for creating configuration interfaces."""
    
    @staticmethod
    def create_interface(prefer_gui: bool = True) -> ConfigurationInterface:
        """Create configuration interface based on availability and preference."""
        if prefer_gui and _tkinter_available:
            return GUIConfigurationInterface()
        else:
            return ConsoleConfigurationInterface()


class ConfigurationDisplayService:
    """Service for displaying configuration information."""
    
    def show_current_configuration(self, config: StandaloneConfig) -> None:
        """Display current configuration in a formatted way."""
        print("=" * 70)
        print("🎤 TTS Hotkey - Configuração Atual")
        print("=" * 70)
        
        # Discord Configuration
        print("🌐 DISCORD:")
        print(f"   Bot URL: {config.discord.bot_url or 'Não configurado'}")
        if config.discord.guild_id:
            print(f"   🏠 Guild ID: {config.discord.guild_id}")
        if config.discord.channel_id:
            print(f"   📺 Channel ID: {config.discord.channel_id}")
        if config.discord.member_id:
            print(f"   👤 Member ID: {config.discord.member_id}")
        else:
            print("   ⚠️  Member ID: NÃO CONFIGURADO (recomendado para melhor funcionamento)")
        
        # TTS Configuration
        print("\n🎤 TTS:")
        print(f"   Engine: {config.tts.engine}")
        print(f"   Idioma: {config.tts.language}")
        print(f"   Velocidade: {config.tts.rate} wpm")
        if config.tts.output_device:
            print(f"   🔊 Device: {config.tts.output_device}")
        
        # Hotkey Configuration
        print("\n⌨️ HOTKEYS:")
        print(f"   Iniciar: '{config.hotkey.trigger_open}'")
        print(f"   Finalizar: '{config.hotkey.trigger_close}'")
        print(f"   Exemplo: {config.hotkey.trigger_open}olá mundo{config.hotkey.trigger_close}")
        
        # Network Configuration
        print("\n🌐 REDE:")
        print(f"   Timeout: {config.network.request_timeout}s")
        
        # Status
        print("\n📊 STATUS:")
        try:
            import requests
            _requests_available = True
        except ImportError:
            _requests_available = False
        
        discord_available = config.discord.bot_url and _requests_available
        if discord_available:
            print("   ✅ Modo Discord: Enviará áudio para o bot")
        else:
            print("   🔇 Modo Local: Reproduzirá áudio localmente")
            if not config.discord.bot_url:
                print("   💡 Configure URL do bot para usar Discord")
            if not _requests_available:
                print("   💡 Biblioteca 'requests' não disponível")
        
        print("\n🔧 RECURSOS:")
        print(f"   Notificações: {'✅' if config.interface.show_notifications else '❌'}")
        print(f"   Logs detalhados: {'✅' if config.interface.console_logs else '❌'}")
        
        try:
            import pystray
            _pystray_available = True
        except ImportError:
            _pystray_available = False
        
        print(f"   System Tray: {'✅' if _pystray_available else '❌'}")
        
        print("\n📝 COMO CONFIGURAR:")
        if not config.discord.member_id or not config.discord.guild_id:
            print("   ⚠️  Na primeira execução, uma janela aparecerá para configuração")
        print("   1. Insira seu Discord User ID e Guild ID (obrigatórios)")
        print("   2. Configure outras opções se necessário")
        print("   3. Clique em 'Salvar e Continuar'")
        print("   4. Use {texto} para falar!")
        
        print("\n🔧 PARA RECONFIGURAR:")
        if _pystray_available:
            print("   • Clique com botão direito no ícone da bandeja → Configurações")
        print("   • Ou delete o arquivo de config e reinicie:")
        print("     Linux/macOS: ~/.config/tts-hotkey/config.json")
        print("     Windows: %LOCALAPPDATA%/TTS-Hotkey/config.json")
        
        print("\n💡 DICAS IMPORTANTES:")
        print("   • Configure DISCORD_MEMBER_ID e DISCORD_GUILD_ID para usar o bot com isolamento por servidor")
        print("   • Bot tenta conectar automaticamente onde você estiver")
        print("   • Bot sai da sala após 30 minutos de inatividade")
        print("   • Use /join no Discord se precisar conectar manualmente")
        print("=" * 70)
