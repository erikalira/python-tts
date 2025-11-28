#!/usr/bin/env python3
"""
TTS Hotkey - Versão Standalone Configurável
Este arquivo permite personalizar as configurações antes de compilar.
"""

# =============================================================================
# 🔧 CONFIGURAÇÕES - EDITE AQUI ANTES DE COMPILAR
# =============================================================================

class Config:
    """Configurações centralizadas do TTS Hotkey."""
    
    # 🌐 Discord Bot Configuration
    DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
    DISCORD_CHANNEL_ID = None  # Ex: "123456789012345678"
    DISCORD_MEMBER_ID = None   # Ex: "987654321098765432"
    
    # 🎤 TTS Configuration  
    TTS_ENGINE = "gtts"           # gtts, pyttsx3, edge-tts
    TTS_LANGUAGE = "pt"           # pt, en, es, fr, etc.
    TTS_VOICE_ID = "roa/pt-br"   # Voice for specific engines
    TTS_RATE = 180               # Speech rate (words per minute)
    
    # 🔊 Audio Output
    TTS_OUTPUT_DEVICE = None     # Ex: "CABLE Input (VB-Audio Virtual Cable)"
    
    # ⚙️ Hotkey Configuration
    TRIGGER_OPEN = "{"           # Character to start recording
    TRIGGER_CLOSE = "}"          # Character to stop and speak
    
    # 🎨 Interface
    SHOW_NOTIFICATIONS = True    # Show desktop notifications
    CONSOLE_LOGS = True          # Show detailed console logs
    
    # ⏱️ Network Configuration
    REQUEST_TIMEOUT = 10         # Seconds to wait for Discord bot
    RETRY_ATTEMPTS = 1           # Number of retries if request fails
    
    # 🔐 Advanced (usually don't need to change)
    USER_AGENT = "TTS-Hotkey/2.0"
    MAX_TEXT_LENGTH = 500        # Maximum characters to speak

# =============================================================================
# 💡 PARA PERSONALIZAR:
# 1. Edite as configurações acima
# 2. Execute: build_standalone.ps1
# 3. Distribua apenas o arquivo .exe gerado
# =============================================================================

import os
import tempfile
import keyboard
import pyttsx3
import threading
from pathlib import Path

# Set embedded configuration from Config class
os.environ.setdefault('DISCORD_BOT_URL', Config.DISCORD_BOT_URL or '')
if Config.DISCORD_CHANNEL_ID:
    os.environ.setdefault('DISCORD_CHANNEL_ID', Config.DISCORD_CHANNEL_ID)
if Config.DISCORD_MEMBER_ID:
    os.environ.setdefault('DISCORD_MEMBER_ID', Config.DISCORD_MEMBER_ID)
os.environ.setdefault('TTS_ENGINE', Config.TTS_ENGINE)
os.environ.setdefault('TTS_LANGUAGE', Config.TTS_LANGUAGE)
os.environ.setdefault('TTS_VOICE_ID', Config.TTS_VOICE_ID)
if Config.TTS_OUTPUT_DEVICE:
    os.environ.setdefault('TTS_OUTPUT_DEVICE', Config.TTS_OUTPUT_DEVICE)

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image
    _pystray_available = True
except Exception:
    _pystray_available = False
    print("[tts_hotkey] ⚠️ pystray not available, running without system tray icon")

# Optional: play audio directly to a specific output device
try:
    import sounddevice as sd
    import soundfile as sf
    _sd_available = True
    try:
        import numpy as np
    except Exception:
        np = None
except Exception:
    sd = None
    sf = None
    _sd_available = False

# Test if requests is available
try:
    import requests
    _requests_available = True
except ImportError:
    _requests_available = False
    print("[tts_hotkey] ❌ requests library not available - will use local TTS only")

recording = False
buffer = []
suppress_events = threading.Event()

def show_config():
    """Show current configuration from Config class."""
    print("=" * 70)
    print("🎤 TTS Hotkey - Configuração Personalizada")
    print("=" * 70)
    
    # Discord Configuration
    print("🌐 DISCORD:")
    print(f"   Bot URL: {Config.DISCORD_BOT_URL or 'Não configurado'}")
    if Config.DISCORD_CHANNEL_ID:
        print(f"   📺 Channel ID: {Config.DISCORD_CHANNEL_ID}")
    if Config.DISCORD_MEMBER_ID:
        print(f"   👤 Member ID: {Config.DISCORD_MEMBER_ID}")
    
    # TTS Configuration
    print(f"\n🎤 TTS:")
    print(f"   Engine: {Config.TTS_ENGINE}")
    print(f"   Idioma: {Config.TTS_LANGUAGE}")
    print(f"   Velocidade: {Config.TTS_RATE} wpm")
    if Config.TTS_OUTPUT_DEVICE:
        print(f"   🔊 Device: {Config.TTS_OUTPUT_DEVICE}")
    
    # Hotkey Configuration
    print(f"\n⌨️ HOTKEYS:")
    print(f"   Iniciar: '{Config.TRIGGER_OPEN}'")
    print(f"   Finalizar: '{Config.TRIGGER_CLOSE}'")
    print(f"   Exemplo: {Config.TRIGGER_OPEN}olá mundo{Config.TRIGGER_CLOSE}")
    
    # Network Configuration
    print(f"\n🌐 REDE:")
    print(f"   Timeout: {Config.REQUEST_TIMEOUT}s")
    print(f"   Tentativas: {Config.RETRY_ATTEMPTS}")
    
    # Status
    print(f"\n📊 STATUS:")
    discord_available = Config.DISCORD_BOT_URL and _requests_available
    if discord_available:
        print("   ✅ Modo Discord: Enviará áudio para o bot")
    else:
        print("   🔇 Modo Local: Reproduzirá áudio localmente")
        if not Config.DISCORD_BOT_URL:
            print("   💡 Configure Config.DISCORD_BOT_URL para usar Discord")
        if not _requests_available:
            print("   💡 Biblioteca 'requests' não disponível")
    
    print(f"\n🔧 RECURSOS:")
    print(f"   Notificações: {'✅' if Config.SHOW_NOTIFICATIONS else '❌'}")
    print(f"   Logs detalhados: {'✅' if Config.CONSOLE_LOGS else '❌'}")
    print(f"   System Tray: {'✅' if _pystray_available else '❌'}")
    
    print("\n📝 COMO PERSONALIZAR:")
    print("   1. Edite a classe Config no topo do arquivo")
    print("   2. Recompile com: build_configurable.ps1")
    print("   3. Distribua o novo .exe")
    print("=" * 70)

def _speak_and_send(text: str, backspaces: int):
    """Send text to Discord or speak locally."""
    suppress_events.set()
    try:
        discord_bot_url = os.getenv('DISCORD_BOT_URL')
        
        if discord_bot_url and _requests_available:
            print(f"[tts_hotkey] 🚀 Enviando '{text}' para Discord...")
            try:
                payload = {'text': text}
                ch = os.getenv('DISCORD_CHANNEL_ID')
                if ch:
                    payload['channel_id'] = ch
                member = os.getenv('DISCORD_MEMBER_ID')
                if member:
                    payload['member_id'] = member
                
                url = discord_bot_url.rstrip('/') + '/speak'
                resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
                
                if resp.ok:
                    print("[tts_hotkey] ✅ Enviado com sucesso!")
                    for _ in range(backspaces):
                        keyboard.send('backspace')
                    return
                else:
                    print(f"[tts_hotkey] ❌ Erro: {resp.status_code}, usando TTS local")
            except requests.exceptions.Timeout:
                print('[tts_hotkey] ⏰ Timeout, usando TTS local')
            except Exception as e:
                print(f'[tts_hotkey] ❌ Erro: {e}, usando TTS local')
        
        # Local TTS fallback
        print(f"[tts_hotkey] 🔊 Reproduzindo localmente: '{text}'")
        engine = pyttsx3.init()
        engine.setProperty('rate', Config.TTS_RATE)
        engine.say(text)
        engine.runAndWait()
        
        for _ in range(backspaces):
            keyboard.send('backspace')
            
    finally:
        suppress_events.clear()

def on_key(event):
    global recording, buffer
    
    if suppress_events.is_set():
        return
    
    if event.event_type != keyboard.KEY_DOWN:
        return
    
    key = event.name
    
    if key in (Config.TRIGGER_OPEN, 'open_bracket', '[', 'left_bracket', 'braceleft'):
        recording = True
        buffer = []
        return
    
    if recording:
        if key in (Config.TRIGGER_CLOSE, 'close_bracket', ']', 'right_bracket', 'braceright'):
            recording = False
            text = ''.join(buffer).strip()
            if text:
                backspaces = len(buffer) + 2
                t = threading.Thread(target=_speak_and_send, args=(text, backspaces), daemon=True)
                t.start()
            buffer = []
            return
        
        if key in ('backspace', 'back'):
            if buffer:
                buffer.pop()
            return
        
        if key == 'space':
            buffer.append(' ')
        elif len(key) == 1:
            buffer.append(key)

# System tray functions (if available)
if _pystray_available:
    def create_icon_image():
        try:
            icon_path = Path(__file__).resolve().parents[1] / "icon.png"
            if icon_path.exists():
                return Image.open(icon_path)
        except:
            pass
        
        # Fallback icon
        img = Image.new('RGB', (64, 64), color='#2C2F33')
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([22, 15, 42, 35], fill='#7289DA')
        draw.ellipse([22, 30, 42, 45], fill='#7289DA')
        return img
    
    def on_status_click(icon, item):
        discord_url = os.getenv('DISCORD_BOT_URL')
        if discord_url:
            print(f"✅ Conectado ao Discord: {discord_url}")
        else:
            print("⚠️ Discord não configurado (TTS local)")
    
    def on_quit(icon, item):
        print("🛑 Encerrando TTS Hotkey...")
        icon.stop()
        os._exit(0)
    
    def setup_tray_icon():
        menu = Menu(
            MenuItem('TTS Hotkey', on_status_click, default=True),
            MenuItem('Digite {texto} para falar', lambda: None, enabled=False),
            Menu.SEPARATOR,
            MenuItem('Sair', on_quit)
        )
        
        icon_image = create_icon_image()
        return Icon("TTS Hotkey", icon_image, "TTS Hotkey", menu)

def main():
    show_config()
    
    # Setup keyboard hook
    keyboard.hook(on_key)
    
    if _pystray_available:
        # Run with system tray
        icon = setup_tray_icon()
        icon.run()
    else:
        # Run without tray (console mode)
        print("⌨️ Sistema ativo! Pressione Ctrl+C para sair...")
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            print("\n🛑 Encerrando...")

if __name__ == '__main__':
    main()