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

# Load .env file
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path, override=True)
print(f"[tts_hotkey] Loaded .env from: {env_path}")
print(f"[tts_hotkey] DISCORD_BOT_URL = {os.getenv('DISCORD_BOT_URL')!r}")

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
        if discord_bot_url:
            # send POST to bot (non-blocking behavior is acceptable here since we're in a worker thread)
            try:
                import requests
                payload = {'text': text}
                # optionally send channel id if configured
                ch = os.getenv('DISCORD_CHANNEL_ID')
                if ch:
                    payload['channel_id'] = ch
                # optionally send member id (where the user is connected)
                member = os.getenv('DISCORD_MEMBER_ID')
                if member:
                    payload['member_id'] = member
                url = discord_bot_url.rstrip('/') + '/speak'
                print(f"[tts_hotkey] POST -> {url} payload={payload}")
                
                # Use longer timeout for Render cold starts + TTS processing
                # First attempt: wake up the server
                resp = requests.post(url, json=payload, timeout=10)
                print(f"[tts_hotkey] bot response: {resp.status_code} {resp.text!r}")
                if resp.ok:
                    # sent to bot; skip local playback
                    for _ in range(backspaces):
                        keyboard.send('backspace')
                    return
                else:
                    print(f"[tts_hotkey] Bot returned non-OK status, falling back to local playback")
            except requests.exceptions.Timeout:
                print('[tts_hotkey] Request timed out after 10s (server might be cold starting)')
                print('[tts_hotkey] Falling back to local playback')
            except Exception:
                # fall back to local playback on error
                import traceback
                print('[tts_hotkey] Error sending to Discord bot:')
                traceback.print_exc()
                print('[tts_hotkey] Falling back to local playback')

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
    print("🎤 TTS Hotkey running in system tray")
    print("📝 Type {text} anywhere to speak it out loud")
    print("🖱️ Right-click the tray icon to exit")
    
    # Setup keyboard hook
    keyboard.hook(on_key)
    
    # Setup and run system tray icon (blocks until quit)
    icon = setup_tray_icon()
    icon.run()

if __name__ == '__main__':
    main()