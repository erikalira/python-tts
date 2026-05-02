"""Layout helpers for Desktop App main window sections."""

from __future__ import annotations

from collections.abc import Callable


def build_header(ttk, parent, *, help_text: str) -> None:
    """Build the main window title and introductory copy."""
    ttk.Label(parent, text="Desktop App", font=("Arial", 18, "bold")).pack(anchor="w")
    ttk.Label(
        parent,
        text=help_text,
        wraplength=900,
        justify="left",
    ).pack(anchor="w", pady=(6, 12))


def build_action_buttons(ttk, parent, *, on_save: Callable[[], None], on_test_connection: Callable[[], None], on_refresh_voice_context: Callable[[], None], on_send_test: Callable[[], None], on_clear_logs: Callable[[], None], on_minimize: Callable[[], None]) -> None:
    """Build the main action row."""
    action_frame = ttk.Frame(parent)
    action_frame.pack(fill="x", pady=(0, 12))
    ttk.Button(action_frame, text="Save configuration", command=on_save).pack(side="left")
    ttk.Button(action_frame, text="Test connection", command=on_test_connection).pack(side="left", padx=(10, 0))
    ttk.Button(action_frame, text="Refresh detected channel", command=on_refresh_voice_context).pack(side="left", padx=(10, 0))
    ttk.Button(action_frame, text="Send voice test", command=on_send_test).pack(side="left", padx=(10, 0))
    ttk.Button(action_frame, text="Limpar logs", command=on_clear_logs).pack(side="left", padx=(10, 0))
    ttk.Button(action_frame, text="Minimizar para bandeja", command=on_minimize).pack(side="right")


def build_help_section(ttk, parent, *, text: str) -> None:
    """Build the usage help section."""
    help_frame = ttk.LabelFrame(parent, text="Como usar", padding="10")
    help_frame.pack(fill="x", pady=(0, 12))
    ttk.Label(
        help_frame,
        text=text,
        wraplength=900,
        justify="left",
    ).pack(anchor="w")
