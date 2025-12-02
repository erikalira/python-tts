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
        print("💡 Usando implementação standalone embutida...")
        # Fallback implementation when clean architecture is not available
        run_embedded_standalone()


def run_embedded_standalone():
    """Embedded standalone implementation with all features."""
    import os
    import sys
    import json
    import time
    import threading
    import requests
    from io import BytesIO
    
    # Try to import required packages
    try:
        import keyboard
    except ImportError:
        print("❌ Erro: biblioteca 'keyboard' não encontrada!")
        print("Execute: pip install keyboard")
        input("Pressione Enter para sair...")
        return
    
    # Audio playback
    pygame = None
    try:
        import pygame
        pygame.mixer.init()
    except ImportError:
        print("⚠️ pygame não encontrado - usando TTS local apenas")
    
    # TTS engines
    pyttsx3 = None
    try:
        import pyttsx3
    except ImportError:
        print("⚠️ pyttsx3 não encontrado - usando gTTS apenas")
    
    gTTS = None
    try:
        from gtts import gTTS
    except ImportError:
        print("⚠️ gTTS não encontrado - usando pyttsx3 apenas")
    
    # System tray support
    pystray = None
    Image = None
    ImageDraw = None
    _tray_available = False
    try:
        import pystray
        from PIL import Image, ImageDraw
        _tray_available = True
    except ImportError:
        print("⚠️ System tray não disponível")
    
    class TTSHotkeyApp:
        def __init__(self):
            self.is_running = True
            self.is_recording = False
            self.current_text = ""
            self.config = self.load_config()
            self.tray_icon = None
            
        def load_config(self):
            """Load configuration from embedded defaults."""
            return {
                'discord_bot_url': DEFAULT_DISCORD_BOT_URL,
                'discord_channel_id': DEFAULT_DISCORD_CHANNEL_ID,
                'discord_member_id': DEFAULT_DISCORD_MEMBER_ID,
                'tts_engine': DEFAULT_TTS_ENGINE,
                'tts_language': DEFAULT_TTS_LANGUAGE,
                'tts_voice_id': DEFAULT_TTS_VOICE_ID,
                'tts_rate': DEFAULT_TTS_RATE,
                'trigger_open': DEFAULT_TRIGGER_OPEN,
                'trigger_close': DEFAULT_TRIGGER_CLOSE,
                'show_notifications': DEFAULT_SHOW_NOTIFICATIONS,
                'console_logs': DEFAULT_CONSOLE_LOGS,
                'request_timeout': DEFAULT_REQUEST_TIMEOUT,
                'max_text_length': DEFAULT_MAX_TEXT_LENGTH
            }
        
        def create_system_tray(self):
            """Create system tray icon."""
            if not _tray_available or not pystray or not Image or not ImageDraw:
                return None
                
            try:
                # Create a simple icon
                image = Image.new('RGB', (64, 64), color='blue')
                draw = ImageDraw.Draw(image)
                draw.rectangle([16, 16, 48, 48], fill='white')
                draw.text((20, 24), "TTS", fill='blue')
                
                menu = pystray.Menu(
                    pystray.MenuItem("TTS Hotkey Ativo", lambda: None, enabled=False),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(f"Trigger: {self.config['trigger_open']}...{self.config['trigger_close']}", lambda: None, enabled=False),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("Sair", self.quit_app)
                )
                
                return pystray.Icon("TTS Hotkey", image, "TTS Hotkey", menu)
            except Exception as e:
                print(f"⚠️ Erro criando system tray: {e}")
                return None
        
        def speak_with_discord(self, text):
            """Send text to Discord bot for TTS."""
            try:
                url = self.config['discord_bot_url']
                if not url:
                    return False
                    
                payload = {
                    'text': text,
                    'channel_id': self.config['discord_channel_id'],
                    'member_id': self.config['discord_member_id']
                }
                
                response = requests.post(
                    f"{url}/speak",
                    json=payload,
                    timeout=self.config['request_timeout'],
                    headers={'User-Agent': DEFAULT_USER_AGENT}
                )
                
                if response.status_code == 200:
                    print(f"✅ Enviado para Discord: {text}")
                    return True
                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', response.text)
                        print(f"⚠️ Discord: {error_msg}")
                        
                        # Se o bot não está conectado, tenta conectar
                        if "não está conectado" in error_msg or "not connected" in error_msg.lower():
                            print("🔄 Tentando conectar o bot automaticamente...")
                            self._try_connect_bot()
                            
                    except:
                        print(f"❌ Discord bot error ({response.status_code}): {response.text}")
                    return False
                else:
                    print(f"❌ Discord bot error: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro Discord: {e}")
                return False
        
        def _try_connect_bot(self):
            """Try to connect the bot to a voice channel."""
            try:
                url = self.config['discord_bot_url']
                if not url:
                    return False
                    
                # Try to get bot status or available channels
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print("💡 Bot está online. Para usar o TTS do Discord:")
                    print("   1. Entre em um canal de voz no Discord")
                    print("   2. Use o comando /join no chat do Discord")
                    print("   3. Tente novamente o hotkey")
                else:
                    print("❌ Bot não está respondendo")
                    
            except Exception as e:
                print(f"⚠️ Não foi possível verificar status do bot: {e}")
        
        def speak_local_tts(self, text):
            """Use local TTS engines."""
            success = False
            
            # Try gTTS first (better quality)
            if gTTS and self.config['tts_engine'] == 'gtts':
                try:
                    tts = gTTS(text=text, lang=self.config['tts_language'], slow=False)
                    audio_buffer = BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    
                    if pygame:
                        pygame.mixer.music.load(audio_buffer, 'mp3')
                        pygame.mixer.music.play()
                        
                        # Wait for playback to finish
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                        
                        print(f"✅ gTTS local: {text}")
                        success = True
                    else:
                        print("❌ pygame não disponível para reprodução")
                        
                except Exception as e:
                    print(f"❌ Erro gTTS: {e}")
            
            # Fallback to pyttsx3
            if not success and pyttsx3:
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', self.config['tts_rate'])
                    
                    voices = engine.getProperty('voices')
                    if voices and hasattr(voices, '__iter__'):
                        # Try to find Portuguese voice
                        try:
                            for voice in voices:
                                if hasattr(voice, 'name') and ('portuguese' in voice.name.lower() or 'brasil' in voice.name.lower()):
                                    engine.setProperty('voice', voice.id)
                                    break
                        except Exception:
                            pass  # Use default voice
                    
                    engine.say(text)
                    engine.runAndWait()
                    print(f"✅ pyttsx3 local: {text}")
                    success = True
                    
                except Exception as e:
                    print(f"❌ Erro pyttsx3: {e}")
            
            return success
        
        def speak_text(self, text):
            """Main TTS function - tries Discord first, then local."""
            if not text.strip():
                return
                
            text = text.strip()[:self.config['max_text_length']]
            
            print(f"🎤 Falando: {text}")
            
            # Try Discord first
            discord_success = self.speak_with_discord(text)
            
            # If Discord fails, use local TTS
            if not discord_success:
                print("🔄 Tentando TTS local...")
                self.speak_local_tts(text)
        
        def on_key_event(self, event):
            """Handle keyboard events for hotkey functionality."""
            if event.event_type != keyboard.KEY_DOWN:
                return
                
            char = event.name
            
            # Handle trigger characters
            if char == self.config['trigger_open'] and not self.is_recording:
                self.is_recording = True
                self.current_text = ""
                print(f"🎙️ Iniciando gravação... (termine com '{self.config['trigger_close']}')")
                
            elif char == self.config['trigger_close'] and self.is_recording:
                self.is_recording = False
                if self.current_text:
                    # Process in separate thread to avoid blocking
                    threading.Thread(
                        target=self.speak_text,
                        args=(self.current_text,),
                        daemon=True
                    ).start()
                self.current_text = ""
                
            elif self.is_recording and len(char) == 1:
                # Regular character while recording
                self.current_text += char
                
            elif self.is_recording and char == 'space':
                self.current_text += " "
                
            elif self.is_recording and char == 'backspace':
                self.current_text = self.current_text[:-1]
        
        def quit_app(self, icon=None, item=None):
            """Quit the application."""
            self.is_running = False
            if self.tray_icon:
                self.tray_icon.stop()
            print("👋 TTS Hotkey encerrado")
        
        def run(self):
            """Main application loop."""
            print("🚀 TTS Hotkey iniciado!")
            print(f"📝 Use: {self.config['trigger_open']}seu texto{self.config['trigger_close']} para falar")
            print(f"🌐 Discord Bot: {self.config['discord_bot_url']}")
            print(f"🎤 TTS Engine: {self.config['tts_engine']}")
            print("📌 Pressione Ctrl+C para sair")
            print("-" * 50)
            
            # Setup system tray
            if _tray_available:
                self.tray_icon = self.create_system_tray()
                if self.tray_icon:
                    threading.Thread(target=self.tray_icon.run, daemon=True).start()
                    print("📍 Ícone na bandeja do sistema criado")
            
            # Setup keyboard hook
            keyboard.hook(self.on_key_event)
            
            try:
                # Keep the main thread alive
                while self.is_running:
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                self.quit_app()
            finally:
                keyboard.unhook_all()
    
    # Create and run the app
    app = TTSHotkeyApp()
    app.run()


if __name__ == '__main__':
    main()