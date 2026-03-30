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

import os

# =============================================================================
# 🔧 CONFIGURAÇÕES PADRÃO - EDITE AQUI ANTES DE COMPILAR
# =============================================================================

# 🌐 Discord Bot Configuration
DEFAULT_DISCORD_BOT_URL = os.getenv('DISCORD_BOT_URL')
# CONFIGURAÇÃO OBRIGATÓRIA: Configure seus IDs do Discord aqui
DEFAULT_DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')  # Cole aqui o ID do canal de voz (botão direito > Copiar ID)
DEFAULT_DISCORD_MEMBER_ID = os.getenv('DISCORD_MEMBER_ID')   # Cole aqui SEU Discord User ID (Configurações > Avançado > Modo Dev > botão direito no seu nome > Copiar ID)

# 🎤 TTS Configuration  
DEFAULT_TTS_ENGINE = os.getenv('TTS_ENGINE', "gtts")           # gtts, pyttsx3, edge-tts
DEFAULT_TTS_LANGUAGE = os.getenv('TTS_LANGUAGE', "pt")           # pt, en, es, fr, etc.
DEFAULT_TTS_VOICE_ID = os.getenv('TTS_VOICE_ID', "roa/pt-br")   # Voice for specific engines
DEFAULT_TTS_RATE = int(os.getenv('TTS_RATE', '180'))               # Speech rate (words per minute)

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
# 2. Execute: build_clean_architecture.ps1
# 3. Distribua o novo .exe
# =============================================================================

import sys
from pathlib import Path
from typing import Optional, Type

# Add src to path for imports
current_dir = Path(__file__).resolve().parent
src_path = current_dir / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))


# Initialize module-level variables
StandaloneConfig: Optional[Type] = None
TTSConfig: Optional[Type] = None
DiscordConfig: Optional[Type] = None
HotkeyConfig: Optional[Type] = None
InterfaceConfig: Optional[Type] = None
NetworkConfig: Optional[Type] = None
SimpleApplication: Optional[Type] = None

try:
    # Import the clean architecture components
    # The src/ directory is already in sys.path, so imports work as-is
    from src.standalone.config.standalone_config import (
        StandaloneConfig,
        TTSConfig,
        DiscordConfig,
        HotkeyConfig,
        InterfaceConfig,
        NetworkConfig
    )
    from src.standalone.app.simple_app import SimpleApplication
    
    _clean_architecture_available = True
except ImportError as e:
    print(f"[tts_hotkey] ⚠️ Clean architecture not available: {e}")
    print("[tts_hotkey] 💡 Falling back to embedded legacy code...")
    _clean_architecture_available = False


def create_default_config():
    """Create default configuration from embedded constants.
    
    Returns:
        StandaloneConfig: Default configuration instance or None if architecture unavailable.
    """
    if not _clean_architecture_available or StandaloneConfig is None:
        return None

    # garante pro Pylance que não é None
    assert TTSConfig is not None
    assert DiscordConfig is not None
    assert HotkeyConfig is not None
    assert InterfaceConfig is not None
    assert NetworkConfig is not None
        
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
    print("🎤 TTS Hotkey - Versão App Windows Configurável")
    print("=" * 70)
    
    if _clean_architecture_available:
        print("✅ Usando arquitetura limpa (Clean Architecture)")
        
        try:
            assert SimpleApplication is not None
            # Create and run the clean architecture application
            app = SimpleApplication()
            app.run()
        except Exception as e:
            print(f"❌ Erro na arquitetura limpa: {e}")
            print("🔄 Alternando para implementação embutida...")
            run_embedded_standalone()
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
            
            # Check if initial setup is needed
            if not self.config['discord_member_id'] or not self.config['discord_bot_url']:
                self.show_initial_setup()
            
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
        
        def show_initial_setup(self):
            """Show initial setup dialog."""
            try:
                # Try GUI first
                import tkinter as tk
                from tkinter import ttk, messagebox
                self._show_gui_setup()
            except ImportError:
                # Fallback to console
                self._show_console_setup()
        
        def _show_gui_setup(self):
            """Show GUI setup dialog."""
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            root = tk.Tk()
            root.title("TTS Hotkey - Configuração Inicial")
            root.geometry("550x400")
            root.resizable(False, False)
            
            # Center window
            root.geometry("+%d+%d" % (
                (root.winfo_screenwidth() / 2 - 275),
                (root.winfo_screenheight() / 2 - 200)
            ))
            
            main_frame = ttk.Frame(root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="🎤 TTS Hotkey - Configuração Inicial", 
                                   font=('Arial', 14, 'bold'))
            title_label.pack(pady=(0, 15))
            
            # Instructions
            instructions = ttk.Label(main_frame, 
                text="Para usar o TTS no Discord, configure seu Discord User ID:",
                justify=tk.CENTER)
            instructions.pack(pady=(0, 15))
            
            # Member ID
            ttk.Label(main_frame, text="Seu Discord User ID:").pack(anchor=tk.W)
            member_id_var = tk.StringVar()
            member_id_entry = ttk.Entry(main_frame, textvariable=member_id_var, width=40)
            member_id_entry.pack(fill=tk.X, pady=(5, 10))
            
            # Help text
            help_text = ttk.Label(main_frame, 
                text="💡 Como encontrar: Discord → Configurações → Avançado → Modo Desenvolvedor (ON)\n"
                     "   Depois: Botão direito no seu nome → Copiar ID",
                foreground='gray', font=('Arial', 8))
            help_text.pack(anchor=tk.W, pady=(0, 15))
            
            # Channel ID (opcional)
            ttk.Label(main_frame, text="Channel ID (opcional):").pack(anchor=tk.W)
            channel_id_var = tk.StringVar()
            channel_id_entry = ttk.Entry(main_frame, textvariable=channel_id_var, width=40)
            channel_id_entry.pack(fill=tk.X, pady=(5, 10))
            
            channel_help = ttk.Label(main_frame, 
                text="💡 Botão direito no canal de voz → Copiar ID",
                foreground='gray', font=('Arial', 8))
            channel_help.pack(anchor=tk.W, pady=(0, 15))
            
            # Warning
            warning = ttk.Label(main_frame, 
                text="⚠️ Sem o Discord User ID, o TTS funcionará apenas localmente",
                foreground='orange')
            warning.pack(pady=(0, 20))
            
            def save_config():
                member_id = member_id_var.get().strip()
                channel_id = channel_id_var.get().strip()
                
                if member_id and not member_id.isdigit():
                    messagebox.showerror("Erro", "Discord User ID deve conter apenas números!")
                    return
                
                if channel_id and not channel_id.isdigit():
                    messagebox.showerror("Erro", "Channel ID deve conter apenas números!")
                    return
                
                self.config['discord_member_id'] = member_id if member_id else None
                self.config['discord_channel_id'] = channel_id if channel_id else None
                
                if member_id:
                    messagebox.showinfo("Sucesso", "Configuração salva! O TTS funcionará no Discord.")
                else:
                    messagebox.showinfo("Aviso", "Sem Discord User ID, o TTS funcionará apenas localmente.")
                
                root.destroy()
            
            def skip_config():
                self.config['discord_member_id'] = None
                self.config['discord_channel_id'] = None
                root.destroy()
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            ttk.Button(button_frame, text="Continuar Sem Discord", 
                      command=skip_config).pack(side=tk.LEFT)
            
            ttk.Button(button_frame, text="Salvar e Continuar", 
                      command=save_config).pack(side=tk.RIGHT)
            
            root.mainloop()
        
        def _show_console_setup(self):
            """Show console setup."""
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
            
            # Channel ID
            print("\n2. Channel ID (opcional):")
            print("   Como encontrar: Botão direito no canal de voz → Copiar ID")
            channel_id = input("   Channel ID (opcional): ").strip()
            
            if channel_id and not channel_id.isdigit():
                print("❌ ID deve conter apenas números!")
                channel_id = ""
            
            self.config['discord_member_id'] = member_id if member_id else None
            self.config['discord_channel_id'] = channel_id if channel_id else None
            
            if member_id:
                print(f"\n✅ Configuração salva! TTS funcionará no Discord.")
            else:
                print(f"\n⚠️ Sem Discord User ID, TTS funcionará apenas localmente.")
        
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
        
        def speak_with_discord(self, text: str) -> bool:
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
                            
                    except (ValueError, json.JSONDecodeError, TypeError):
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
        
        def speak_local_tts(self, text: str) -> bool:
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
                    if voices:
                        try:
                            # Ensure voices is iterable (could be list or single object)
                            voices_list = voices if isinstance(voices, (list, tuple)) else [voices]
                            for voice in voices_list:
                                if hasattr(voice, 'name') and hasattr(voice, 'id'):
                                    voice_name = getattr(voice, 'name', '')
                                    if isinstance(voice_name, str) and ('portuguese' in voice_name.lower() or 'brasil' in voice_name.lower()):
                                        voice_id = getattr(voice, 'id', None)
                                        if voice_id is not None:
                                            engine.setProperty('voice', voice_id)
                                        break
                        except (TypeError, AttributeError, StopIteration):
                            pass  # Use default voice
                    
                    engine.say(text)
                    engine.runAndWait()
                    print(f"✅ pyttsx3 local: {text}")
                    success = True
                    
                except Exception as e:
                    print(f"❌ Erro pyttsx3: {e}")
            
            return success
        
        def speak_text(self, text: str) -> None:
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
        
        def on_key_event(self, event) -> None:
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
        
        def run(self) -> None:
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