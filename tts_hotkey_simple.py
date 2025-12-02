#!/usr/bin/env python3
"""
TTS Hotkey - Versão Simples para Windows (Minimal Dependencies)
Esta versão funciona apenas com requests e keyboard, ideal para distribuição.
"""

# =============================================================================
# 🔧 CONFIGURAÇÕES PADRÃO - EDITE AQUI ANTES DE COMPILAR
# =============================================================================

# 🌐 Discord Bot Configuration
DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
DISCORD_CHANNEL_ID = None  # Ex: "123456789012345678" (opcional)
DISCORD_MEMBER_ID = None   # Ex: "987654321098765432" (IMPORTANTE: seu Discord User ID)

# ⚙️ Hotkey Configuration
TRIGGER_OPEN = "{"         # Character to start recording
TRIGGER_CLOSE = "}"        # Character to stop and speak

# ⏱️ Network Configuration
REQUEST_TIMEOUT = 10       # Seconds to wait for Discord bot
MAX_TEXT_LENGTH = 500      # Maximum characters to speak

def main():
    """Main TTS Hotkey application with minimal dependencies."""
    import os
    import time
    import threading
    import requests
    
    # Check for keyboard library
    try:
        import keyboard
    except ImportError:
        print("❌ ERRO: Biblioteca 'keyboard' não encontrada!")
        print("Este executável precisa da biblioteca keyboard.")
        print("Execute: pip install keyboard")
        input("\nPressione Enter para sair...")
        return 1
    
    print("=" * 70)
    print("🎤 TTS Hotkey - Versão Simples")
    print("=" * 70)
    print()
    
    class SimpleTTSApp:
        def __init__(self):
            self.is_running = True
            self.is_recording = False
            self.current_text = ""
            
        def send_to_discord(self, text):
            """Send text to Discord bot for TTS."""
            if not text.strip():
                return False
                
            try:
                text = text.strip()[:MAX_TEXT_LENGTH]
                
                payload = {
                    'text': text,
                    'channel_id': DISCORD_CHANNEL_ID,
                    'member_id': DISCORD_MEMBER_ID
                }
                
                print(f"🌐 Enviando para Discord: {text}")
                
                response = requests.post(
                    f"{DISCORD_BOT_URL}/speak",
                    json=payload,
                    timeout=REQUEST_TIMEOUT,
                    headers={'User-Agent': 'TTS-Hotkey-Simple/1.0'}
                )
                
                if response.status_code == 200:
                    print(f"✅ Sucesso! Texto enviado: {text}")
                    return True
                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', response.text)
                        print(f"⚠️ Discord: {error_msg}")
                        
                        # Instrução para o usuário
                        if "não está conectado" in error_msg or "not connected" in error_msg.lower():
                            print("💡 Para usar o Discord TTS:")
                            print("   1. Entre em um canal de voz no Discord")
                            print("   2. Use o comando /join no chat")
                            print("   3. Tente o hotkey novamente")
                            
                    except:
                        print(f"❌ Discord error ({response.status_code}): {response.text}")
                    return False
                else:
                    print(f"❌ Erro Discord ({response.status_code}): {response.text}")
                    return False
                    
            except requests.exceptions.Timeout:
                print("❌ Timeout: Discord bot não respondeu")
                return False
            except requests.exceptions.ConnectionError:
                print("❌ Erro de conexão: Verifique sua internet e URL do bot")
                return False
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
                return False
        
        def on_key_event(self, event):
            """Handle keyboard events for hotkey functionality."""
            if event.event_type != keyboard.KEY_DOWN:
                return
                
            char = event.name
            
            # Handle trigger characters
            if char == TRIGGER_OPEN and not self.is_recording:
                self.is_recording = True
                self.current_text = ""
                print(f"\n🎙️ Gravando... (termine com '{TRIGGER_CLOSE}')")
                print("💡 Digite seu texto normalmente...")
                
            elif char == TRIGGER_CLOSE and self.is_recording:
                self.is_recording = False
                print(f"🎯 Texto capturado: '{self.current_text}'")
                
                if self.current_text.strip():
                    # Process in separate thread to avoid blocking
                    threading.Thread(
                        target=self.send_to_discord,
                        args=(self.current_text,),
                        daemon=True
                    ).start()
                else:
                    print("⚠️ Texto vazio - nada para enviar")
                    
                self.current_text = ""
                print(f"📝 Pronto para próximo texto: {TRIGGER_OPEN}...{TRIGGER_CLOSE}")
                
            elif self.is_recording:
                # Handle special keys while recording
                if len(char) == 1:
                    # Regular character
                    self.current_text += char
                elif char == 'space':
                    self.current_text += " "
                elif char == 'backspace':
                    self.current_text = self.current_text[:-1]
                elif char == 'enter':
                    self.current_text += "\n"
        
        def run(self):
            """Main application loop."""
            print("🚀 TTS Hotkey iniciado com sucesso!")
            print()
            print("📋 CONFIGURAÇÃO:")
            print(f"   🌐 Discord Bot: {DISCORD_BOT_URL}")
            print(f"   🎯 Triggers: '{TRIGGER_OPEN}' para iniciar, '{TRIGGER_CLOSE}' para falar")
            if DISCORD_MEMBER_ID:
                print(f"   👤 Member ID: {DISCORD_MEMBER_ID}")
            else:
                print("   ⚠️ Member ID não configurado - pode afetar funcionamento")
            print()
            print("📝 COMO USAR:")
            print(f"   1. Digite {TRIGGER_OPEN} em qualquer lugar")
            print("   2. Digite seu texto")
            print(f"   3. Digite {TRIGGER_CLOSE} para enviar")
            print()
            print("🔧 DICAS:")
            print("   • Funciona em qualquer aplicativo")
            print("   • Use textos curtos para melhor resultado")
            print("   • Pressione Ctrl+C aqui para sair")
            print()
            print("=" * 70)
            print(f"✅ Aguardando hotkey: {TRIGGER_OPEN}texto{TRIGGER_CLOSE}")
            print("=" * 70)
            
            # Setup keyboard hook
            keyboard.hook(self.on_key_event)
            
            try:
                # Keep the main thread alive
                while self.is_running:
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Encerrando TTS Hotkey...")
                print("Obrigado por usar o TTS Hotkey!")
            finally:
                keyboard.unhook_all()
                return 0
    
    # Test Discord connection first
    print("🔍 Testando conexão com Discord bot...")
    try:
        response = requests.get(f"{DISCORD_BOT_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Discord bot online e funcionando!")
        else:
            print(f"⚠️ Discord bot respondeu com status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Não foi possível conectar ao Discord bot: {e}")
        print("💡 O aplicativo ainda funcionará, mas TTS pode não funcionar")
    
    print()
    
    # Create and run the app
    app = SimpleTTSApp()
    return app.run()


if __name__ == '__main__':
    import sys
    exit_code = main()
    sys.exit(exit_code)