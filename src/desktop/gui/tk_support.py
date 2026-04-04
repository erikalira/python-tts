"""Shared Tkinter availability and module access for the Desktop App GUI."""

from __future__ import annotations

try:
    import tkinter as tk
    from tkinter import messagebox, ttk

    TKINTER_AVAILABLE = True
except ImportError:
    tk = None
    ttk = None
    messagebox = None
    TKINTER_AVAILABLE = False


__all__ = ["TKINTER_AVAILABLE", "messagebox", "tk", "ttk"]
