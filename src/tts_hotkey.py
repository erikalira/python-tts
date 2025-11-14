# ...existing code...
import keyboard
import pyttsx3
import threading

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

        if len(key) == 1:
            buffer.append(key)

def main():
    print("TTS Hotkey running. Type {text} anywhere to speak it out loud.")
    print("Press ESC to exit.")
    keyboard.hook(on_key)
    keyboard.wait('esc')

if __name__ == '__main__':
    main()