#!/usr/bin/env python3
"""
Teste da interface de configuração do TTS Hotkey
"""
import sys
sys.path.append('.')

# Import our config classes
from tts_hotkey_configurable import Config, ConfigWindow

def test_config_gui():
    """Test the configuration GUI"""
    print("🧪 Testando interface de configuração...")
    
    # Load existing config
    Config.load_from_file()
    print(f"Config atual - Member ID: {Config.DISCORD_MEMBER_ID}")
    
    # Show config dialog
    config_window = ConfigWindow()
    result = config_window.show_config_dialog()
    
    if result:
        print("✅ Configuração salva com sucesso!")
        print(f"Novo Member ID: {Config.DISCORD_MEMBER_ID}")
    else:
        print("❌ Configuração cancelada")

if __name__ == '__main__':
    test_config_gui()