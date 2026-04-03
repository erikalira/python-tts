"""Pure hotkey text-capture state used by the Desktop App keyboard monitor."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HotkeyCaptureResult:
    """Structured result produced when a capture session is completed."""

    text: str
    backspace_count: int
    trigger_open: str
    trigger_close: str


class HotkeyTextCaptureSession:
    """Track buffered text between configured trigger keys."""

    def __init__(self, trigger_open: str, trigger_close: str):
        self._trigger_open = trigger_open
        self._trigger_close = trigger_close
        self._recording = False
        self._buffer: list[str] = []

    def reset(self) -> None:
        """Clear current recording state."""
        self._recording = False
        self._buffer = []

    def process_key(self, key: str) -> HotkeyCaptureResult | None:
        """Consume a key press and return a completed capture when available."""
        if self._is_trigger_open(key):
            self._recording = True
            self._buffer = []
            return None

        if not self._recording:
            return None

        if self._is_trigger_close(key):
            self._recording = False
            text = "".join(self._buffer).strip()
            result = None
            if text:
                result = HotkeyCaptureResult(
                    text=text,
                    backspace_count=len(self._buffer) + 2,
                    trigger_open=self._trigger_open,
                    trigger_close=self._trigger_close,
                )
            self._buffer = []
            return result

        if key in ("backspace", "back"):
            if self._buffer:
                self._buffer.pop()
            return None

        if key == "space":
            self._buffer.append(" ")
            return None

        if len(key) == 1:
            self._buffer.append(key)

        return None

    def _is_trigger_open(self, key: str) -> bool:
        return key in (self._trigger_open, "open_bracket", "left_bracket", "braceleft")

    def _is_trigger_close(self, key: str) -> bool:
        return key in (self._trigger_close, "close_bracket", "right_bracket", "braceright")
