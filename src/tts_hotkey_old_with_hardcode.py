# ...existing code...
import os
import tempfile
import keyboard
import pyttsx3
import threading
from dotenv import load_dotenv
from pathlib import Path
from pystray import Icon, Menu, MenuItem
from PIL import Image

# Configuration embedded in the executable (no .env needed!)
def load_config():
    import sys
    import os
    
    print("[tts_hotkey] 🔧 Loading configuration...")
    
    # Default configuration (hardcoded for standalone executable)
    DEFAULT_CONFIG = {
        'DISCORD_BOT_URL': 'https://python-tts-s3z8.onrender.com',
        'DISCORD_CHANNEL_ID': None,  # Optional: set your channel ID here
        'DISCORD_MEMBER_ID': None,   # Optional: set your member ID here
        'TTS_ENGINE': 'gtts',
        'TTS_LANGUAGE': 'pt',
        'TTS_VOICE_ID': 'roa/pt-br'
    }
    
    # Try to load from .env file first (for development)
    env_loaded = False
    if not hasattr(sys, '_MEIPASS'):  # Only in development (not in .exe)
        try:
            from dotenv import load_dotenv
            possible_paths = [
                Path(".") / ".env",
                Path(__file__).resolve().parents[1] / ".env",
                Path(__file__).resolve().parent / ".env",
            ]
            
            for env_path in possible_paths:
                if env_path.exists():
                    load_dotenv(env_path, override=True)
                    print(f"[tts_hotkey] ✅ Development mode: loaded .env from {env_path}")
                    env_loaded = True
                    break
        except ImportError:
            pass  # dotenv not available, use defaults
    
    if not env_loaded:
        print("[tts_hotkey] 📦 Production mode: using embedded configuration")
        # Set default values if not already set by environment
        for key, value in DEFAULT_CONFIG.items():
            if not os.getenv(key) and value is not None:
                os.environ[key] = value
    
    # Show current configuration
    discord_url = os.getenv('DISCORD_BOT_URL')
    channel_id = os.getenv('DISCORD_CHANNEL_ID')
    member_id = os.getenv('DISCORD_MEMBER_ID')
    
    print()
    print("[tts_hotkey] 📋 CONFIGURAÇÃO ATUAL:")
    print(f"[tts_hotkey] DISCORD_BOT_URL = {discord_url!r}")
    print(f"[tts_hotkey] DISCORD_CHANNEL_ID = {channel_id!r}")
    print(f"[tts_hotkey] DISCORD_MEMBER_ID = {member_id!r}")
    print()
    
    if discord_url:
        print("[tts_hotkey] ✅ Discord bot configured - will send requests to bot")
    else:
        print("[tts_hotkey] ⚠️ No Discord bot URL - will use local TTS only")
    
    return discord_url is not None

# Test if requests is available
try:
    import requests
    _requests_available = True
    print("[tts_hotkey] ✅ requests library available")
except ImportError:
    _requests_available = False
    print("[tts_hotkey] ❌ requests library not available - will use local TTS only")

load_config()

# Optional: play audio directly to a specific output device (virtual cable)
try:
    import sounddevice as sd
    import soundfile as sf
    _sd_available = True
except Exception:
    sd = None
    sf = None
    _sd_available = False
else:
    # numpy is used to adapt channels when playing
    try:
        import numpy as np
    except Exception:
        np = None

recording = False
buffer = []
suppress_events = threading.Event()


def _speak_and_send(text: str, backspaces: int):
    """Run speech and then send backspaces in a background thread.

    We initialize a fresh pyttsx3 engine in the thread to avoid main-thread
    or hook-thread blocking issues with the engine's event loop.
    """
    # mark to ignore synthetic events while we speak/send
    suppress_events.set()
    try:
        # If the user set TTS_OUTPUT_DEVICE and sounddevice is available,
        # save TTS to a WAV and play it directly to the named device.
        out_device_name = os.getenv('TTS_OUTPUT_DEVICE')

        # If DISCORD_BOT_URL is set, send the text to the bot instead of local playback
        discord_bot_url = os.getenv('DISCORD_BOT_URL')
        print(f"[tts_hotkey] Checking Discord bot URL: {discord_bot_url!r}")
        if discord_bot_url and _requests_available:
            print("[tts_hotkey] 🚀 Sending request to Discord bot...")
            # send POST to bot (non-blocking behavior is acceptable here since we're in a worker thread)
            try:
                payload = {'text': text}
                # optionally send channel id if configured
                ch = os.getenv('DISCORD_CHANNEL_ID')
                if ch:
                    payload['channel_id'] = ch
                    print(f"[tts_hotkey] Added channel_id: {ch}")
                # optionally send member id (where the user is connected)
                member = os.getenv('DISCORD_MEMBER_ID')
                if member:
                    payload['member_id'] = member
                    print(f"[tts_hotkey] Added member_id: {member}")
                
                url = discord_bot_url.rstrip('/') + '/speak'
                print(f"[tts_hotkey] 📡 POST -> {url}")
                print(f"[tts_hotkey] 📦 Payload: {payload}")
                
                # Use longer timeout for Render cold starts + TTS processing
                print("[tts_hotkey] ⏳ Sending request (timeout: 10s)...")
                resp = requests.post(url, json=payload, timeout=10)
                print(f"[tts_hotkey] 📨 Bot response: {resp.status_code} {resp.text!r}")
                
                if resp.ok:
                    print("[tts_hotkey] ✅ Successfully sent to Discord bot!")
                    # sent to bot; skip local playback
                    for _ in range(backspaces):
                        keyboard.send('backspace')
                    return
                else:
                    print(f"[tts_hotkey] ❌ Bot returned non-OK status: {resp.status_code}")
                    print(f"[tts_hotkey] Falling back to local playback")
            except ImportError:
                print('[tts_hotkey] ❌ requests module not available, falling back to local playback')
            except requests.exceptions.Timeout:
                print('[tts_hotkey] ⏰ Request timed out after 10s (server might be cold starting)')
                print('[tts_hotkey] Falling back to local playback')
            except requests.exceptions.ConnectionError as e:
                print(f'[tts_hotkey] 🌐 Connection error: {e}')
                print('[tts_hotkey] Falling back to local playback')
            except Exception as e:
                # fall back to local playback on error
                import traceback
                print(f'[tts_hotkey] ❌ Unexpected error sending to Discord bot: {e}')
                print('[tts_hotkey] Full traceback:')
                traceback.print_exc()
                print('[tts_hotkey] Falling back to local playback')
        elif discord_bot_url and not _requests_available:
            print("[tts_hotkey] ❌ Discord bot URL configured but requests library not available")
            print("[tts_hotkey] 💡 Recompile with: --hidden-import=requests")
            print("[tts_hotkey] 🔇 Falling back to local TTS")
        else:
            print("[tts_hotkey] 🔇 No Discord bot URL configured, using local TTS")

        if _sd_available and out_device_name:
            # create temporary wav file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                tmpname = f.name

            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.save_to_file(text, tmpname)
            engine.runAndWait()

            try:
                data, samplerate = sf.read(tmpname, dtype='float32')

                # try to find a device that matches the given name (substring, case-insensitive)
                def _find_device(name):
                    try:
                        devices = sd.query_devices()
                    except Exception:
                        return None
                    for idx, dev in enumerate(devices):
                        dev_name = dev.get('name') if isinstance(dev, dict) else str(dev)
                        if name.lower() in dev_name.lower():
                            return idx
                    return None

                device_idx = _find_device(out_device_name)

                # ensure channel count matches device capabilities
                try:
                    dev_info = sd.query_devices(device_idx) if device_idx is not None else None
                except Exception:
                    dev_info = None

                target_ch = None
                if isinstance(dev_info, dict):
                    target_ch = dev_info.get('max_output_channels')

                # If device reports 0 or None channels, fall back to system default playback
                if not target_ch:
                    sd.play(data, samplerate, device=device_idx)
                    sd.wait()
                else:
                    # adapt data channels if numpy is available
                    if np is not None:
                        # normalize shape: (frames, channels)
                        if data.ndim == 1:
                            cur_ch = 1
                            data = data[:, None]
                        else:
                            cur_ch = data.shape[1]

                        if cur_ch != target_ch:
                            if target_ch == 1:
                                # downmix to mono
                                data = data.mean(axis=1)[:, None]
                            else:
                                # upmix by repeating channels
                                data = np.tile(data, (1, target_ch))

                    sd.play(data, samplerate, device=device_idx)
                    sd.wait()
            finally:
                try:
                    os.unlink(tmpname)
                except Exception:
                    pass
        else:
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.say(text)
            engine.runAndWait()

        # send backspaces to erase the typed text + braces
        for _ in range(backspaces):
            keyboard.send('backspace')
    finally:
        suppress_events.clear()

def on_key(event):
    global recording, buffer

    # ignore events while we intentionally generate keys (thread-safe)
    if suppress_events.is_set():
        return

    if event.event_type != keyboard.KEY_DOWN:
        return

    key = event.name

    print("event:", event.event_type, "name:", key)

    if key in ('{', 'open_bracket', '[', 'left_bracket', 'braceleft'):
        recording = True
        buffer = []
        return

    if recording:
        if key in ('}', 'close_bracket', ']', 'right_bracket', 'braceright'):
            recording = False
            text = ''.join(buffer).strip()
            if text:
                # run speak+backspace in background so the keyboard hook isn't blocked
                backspaces = len(buffer) + 2
                t = threading.Thread(target=_speak_and_send, args=(text, backspaces), daemon=True)
                t.start()
            buffer = []
            return

        # Handle backspace - remove last character from buffer
        if key in ('backspace', 'back'):
            if buffer:
                buffer.pop()
            return

        # Capture single characters and space
        if key == 'space':
            buffer.append(' ')
        elif len(key) == 1:
            buffer.append(key)

# System tray icon management
tray_icon = None

def create_icon_image():
    """Load icon from file or create a simple default one."""
    icon_path = Path(__file__).resolve().parents[1] / "icon.png"
    
    if icon_path.exists():
        return Image.open(icon_path)
    
    # Fallback: create simple icon
    img = Image.new('RGB', (64, 64), color='#2C2F33')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([22, 15, 42, 35], fill='#7289DA')
    draw.ellipse([22, 30, 42, 45], fill='#7289DA')
    return img

def on_status_click(icon, item):
    """Show status message."""
    discord_url = os.getenv('DISCORD_BOT_URL')
    if discord_url:
        print(f"✅ Connected to Discord bot: {discord_url}")
    else:
        print("⚠️ No Discord bot configured (local TTS only)")

def on_quit(icon, item):
    """Exit the application."""
    print("🛑 TTS Hotkey exiting...")
    icon.stop()
    os._exit(0)

def setup_tray_icon():
    """Setup system tray icon with menu."""
    global tray_icon
    
    menu = Menu(
        MenuItem('TTS Hotkey Running', on_status_click, default=True),
        MenuItem('Type {text} to speak', lambda: None, enabled=False),
        Menu.SEPARATOR,
        MenuItem('Exit', on_quit)
    )
    
    icon_image = create_icon_image()
    tray_icon = Icon("TTS Hotkey", icon_image, "TTS Hotkey - Type {text}", menu)
    
    return tray_icon

def main():
    print("=" * 50)
    print("🎤 TTS Hotkey - Sistema de Voz por Tecla de Atalho")
    print("=" * 50)
    print("📝 Digite {texto} em qualquer lugar para falar")
    print("🖱️ Clique com o botão direito no ícone da bandeja para sair")
    
    # Show configuration status
    discord_url = os.getenv('DISCORD_BOT_URL')
    if discord_url:
        print(f"✅ Discord Bot: {discord_url}")
        channel_id = os.getenv('DISCORD_CHANNEL_ID') 
        member_id = os.getenv('DISCORD_MEMBER_ID')
        if channel_id:
            print(f"📺 Channel ID: {channel_id}")
        if member_id:
            print(f"👤 Member ID: {member_id}")
    else:
        print("🔇 Modo Local: Sem bot do Discord configurado")
    
    print("=" * 50)
    
    # Setup keyboard hook
    keyboard.hook(on_key)
    
    # Setup and run system tray icon (blocks until quit)
    icon = setup_tray_icon()
    icon.run()

if __name__ == '__main__':
    main()