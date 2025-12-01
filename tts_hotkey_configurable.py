#!/usr/bin/env python3
"""
TTS Hotkey - Versão Standalone Configurável (Clean Architecture)
Este arquivo permite personalizar as configurações antes de compilar usando uma arquitetura limpa.

NOVA ARQUITETURA:
- Separação clara de responsabilidades
- Princípios SOLID aplicados
- Fácil manutenção e teste
- Configuração centralizada
- Dependency Injection
"""

# =============================================================================
# 🔧 CONFIGURAÇÕES PADRÃO - EDITE AQUI ANTES DE COMPILAR
# =============================================================================

# 🌐 Discord Bot Configuration
DEFAULT_DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
DEFAULT_DISCORD_CHANNEL_ID = None  # Ex: "123456789012345678" (opcional)
DEFAULT_DISCORD_MEMBER_ID = None   # Ex: "987654321098765432" (IMPORTANTE: seu Discord User ID)

# 🎤 TTS Configuration  
DEFAULT_TTS_ENGINE = "gtts"           # gtts, pyttsx3, edge-tts
DEFAULT_TTS_LANGUAGE = "pt"           # pt, en, es, fr, etc.
DEFAULT_TTS_VOICE_ID = "roa/pt-br"   # Voice for specific engines
DEFAULT_TTS_RATE = 180               # Speech rate (words per minute)

# 🔊 Audio Output
DEFAULT_TTS_OUTPUT_DEVICE = None     # Ex: "CABLE Input (VB-Audio Virtual Cable)"

# ⚙️ Hotkey Configuration
DEFAULT_TRIGGER_OPEN = "{"           # Character to start recording
DEFAULT_TRIGGER_CLOSE = "}"          # Character to stop and speak

# 🎨 Interface
DEFAULT_SHOW_NOTIFICATIONS = True    # Show desktop notifications
DEFAULT_CONSOLE_LOGS = True          # Show detailed console logs

# ⏱️ Network Configuration
DEFAULT_REQUEST_TIMEOUT = 10         # Seconds to wait for Discord bot
DEFAULT_USER_AGENT = "TTS-Hotkey/2.0"
DEFAULT_MAX_TEXT_LENGTH = 500        # Maximum characters to speak

# =============================================================================
# 💡 COMO USAR:
# 1. Execute o .exe - uma janela de configuração aparecerá na primeira vez
# 2. Insira seu Discord User ID e outras configurações
# 3. Pronto! Use {texto} para falar
# 
# 🔧 PARA RECOMPILAR:
# 1. Edite as configurações padrão acima (opcional)
# 2. Execute: build_configurable.ps1
# 3. Distribua o novo .exe
# =============================================================================

import sys
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).resolve().parent
src_path = current_dir / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    # Import the clean architecture components
    from standalone.config import (
        StandaloneConfig,
        TTSConfig,
        DiscordConfig,
        HotkeyConfig,
        InterfaceConfig,
        NetworkConfig
    )
    from standalone.app.simple_app import SimpleApplication
    
    _clean_architecture_available = True
except ImportError as e:
    print(f"[tts_hotkey] ⚠️ Clean architecture not available: {e}")
    print("[tts_hotkey] 💡 Falling back to embedded legacy code...")
    _clean_architecture_available = False


def create_default_config() -> 'StandaloneConfig':
    """Create default configuration from embedded constants."""
    if not _clean_architecture_available:
        return None
        
    return StandaloneConfig(
        tts=TTSConfig(
            engine=DEFAULT_TTS_ENGINE,
            language=DEFAULT_TTS_LANGUAGE,
            voice_id=DEFAULT_TTS_VOICE_ID,
            rate=DEFAULT_TTS_RATE,
            output_device=DEFAULT_TTS_OUTPUT_DEVICE
        ),
        discord=DiscordConfig(
            bot_url=DEFAULT_DISCORD_BOT_URL,
            channel_id=DEFAULT_DISCORD_CHANNEL_ID,
            member_id=DEFAULT_DISCORD_MEMBER_ID
        ),
        hotkey=HotkeyConfig(
            trigger_open=DEFAULT_TRIGGER_OPEN,
            trigger_close=DEFAULT_TRIGGER_CLOSE
        ),
        interface=InterfaceConfig(
            show_notifications=DEFAULT_SHOW_NOTIFICATIONS,
            console_logs=DEFAULT_CONSOLE_LOGS
        ),
        network=NetworkConfig(
            request_timeout=DEFAULT_REQUEST_TIMEOUT,
            user_agent=DEFAULT_USER_AGENT,
            max_text_length=DEFAULT_MAX_TEXT_LENGTH
        )
    )


def main() -> None:
    """Main entry point for the configurable standalone application."""
    print("=" * 70)
    print("🎤 TTS Hotkey - Versão Standalone Configurável")
    print("=" * 70)
    
    if _clean_architecture_available:
        print("✅ Usando arquitetura limpa (Clean Architecture)")
        
        # Create and run the clean architecture application
        app = SimpleApplication()
        
        # If we have custom defaults, we could inject them here
        # For now, the defaults are handled in the configuration system
        
        app.run()
    else:
        print("❌ Arquitetura limpa não disponível - implementação necessária")
        print("💡 Execute este arquivo apenas após a estrutura estar completa")
        return


if __name__ == '__main__':
    main()