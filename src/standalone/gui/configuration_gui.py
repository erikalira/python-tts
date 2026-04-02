#!/usr/bin/env python3
"""Compatibility wrappers for the consolidated standalone configuration UI."""

from typing import Optional

try:
    from tkinter import messagebox, ttk
    import tkinter as tk
    _tkinter_available = True
except ImportError:
    messagebox = None
    ttk = None
    tk = None
    _tkinter_available = False

from ..config.standalone_config import StandaloneConfig
from .simple_gui import ConfigInterface, ConfigurationService, ConsoleConfig, GUIConfig


class ConfigurationInterface(ConfigInterface):
    """Compatibility alias for the consolidated configuration interface."""


class ConsoleConfigurationInterface(ConfigurationInterface):
    """Compatibility wrapper over the consolidated console configuration UI."""

    def __init__(self):
        self._delegate = ConsoleConfig()

    def show_config(self, current_config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Compatibility alias expected by the shared interface."""
        return self.show_configuration_dialog(current_config)

    def show_configuration_dialog(self, current_config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Show console configuration dialog."""
        return self._delegate.show_config(current_config)


class GUIConfigurationInterface(ConfigurationInterface):
    """Compatibility wrapper over the consolidated GUI configuration UI."""

    def __init__(self):
        self._delegate = GUIConfig()

    def show_config(self, current_config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Compatibility alias expected by the shared interface."""
        return self.show_configuration_dialog(current_config)

    def show_configuration_dialog(self, current_config: StandaloneConfig) -> Optional[StandaloneConfig]:
        """Show GUI configuration dialog."""
        return self._delegate.show_config(current_config)


class ConfigurationUIFactory:
    """Factory for creating configuration interfaces."""

    @staticmethod
    def create_interface(prefer_gui: bool = True) -> ConfigurationInterface:
        """Create configuration interface based on availability and preference."""
        if prefer_gui and _tkinter_available:
            return GUIConfigurationInterface()
        return ConsoleConfigurationInterface()


class ConfigurationDisplayService:
    """Service for displaying configuration information."""

    def show_current_configuration(self, config: StandaloneConfig) -> None:
        """Display current configuration in a formatted way."""
        print("=" * 70)
        print("🎤 TTS Hotkey - Configuração Atual")
        print("=" * 70)

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

        print("\n🎤 TTS:")
        print(f"   Engine: {config.tts.engine}")
        print(f"   Idioma: {config.tts.language}")
        print(f"   Velocidade: {config.tts.rate} wpm")
        if config.tts.output_device:
            print(f"   🔊 Device: {config.tts.output_device}")

        print("\n⌨️ HOTKEYS:")
        print(f"   Iniciar: '{config.hotkey.trigger_open}'")
        print(f"   Finalizar: '{config.hotkey.trigger_close}'")
        print(f"   Exemplo: {config.hotkey.trigger_open}olá mundo{config.hotkey.trigger_close}")

        print("\n🌐 REDE:")
        print(f"   Timeout: {config.network.request_timeout}s")

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
