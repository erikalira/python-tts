"""Initial setup dialog flow for the Desktop App."""

from __future__ import annotations

from typing import Any, Optional

from ..config.desktop_config import get_default_discord_bot_url
from .config_dialog_presenter import ConfigDialogsPresenter, InitialSetupResult


class InitialSetupGUI:
    """Initial setup GUI for first-time configuration."""

    def __init__(self):
        self.root: Optional[Any] = None
        self.result: Optional[InitialSetupResult] = None
        self.member_id_var: Optional[Any] = None
        self.bot_url_var: Optional[Any] = None
        self._presenter = ConfigDialogsPresenter()

    def show_initial_setup(self) -> Optional[InitialSetupResult]:
        from . import tk_support as compat

        if not compat.TKINTER_AVAILABLE:
            return self._console_initial_setup()
        try:
            self.root = compat.tk.Tk()
            self.root.title("Desktop App - Initial Setup")
            self.root.geometry("550x500")
            self.root.resizable(False, False)
            self.root.geometry(
                "+%d+%d"
                % (
                    (self.root.winfo_screenwidth() / 2 - 275),
                    (self.root.winfo_screenheight() / 2 - 250),
                )
            )
            self._create_initial_setup_widgets()
            self.root.transient()
            self.root.grab_set()
            self.root.mainloop()
            return self.result
        except Exception as exc:
            print(f"Graphical interface error: {exc}")
            return self._console_initial_setup()

    def _create_initial_setup_widgets(self):
        from . import tk_support as compat

        main_frame = compat.ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=compat.tk.BOTH, expand=True)
        compat.ttk.Label(
            main_frame,
            text="Desktop App - Initial Setup",
            font=("Arial", 16, "bold"),
        ).pack(pady=(0, 20))
        compat.ttk.Label(
            main_frame,
            text=(
                "To use TTS on Discord, configure your Discord User ID.\n"
                "The bot will infer the server and channel from your current voice presence."
            ),
            justify=compat.tk.CENTER,
        ).pack(pady=(0, 20))

        discord_frame = compat.ttk.LabelFrame(main_frame, text="Discord Configuration", padding="10")
        discord_frame.pack(fill=compat.tk.X, pady=(0, 15))
        compat.ttk.Label(discord_frame, text="Your Discord User ID:").pack(anchor=compat.tk.W)
        self.member_id_var = compat.tk.StringVar()
        compat.ttk.Entry(discord_frame, textvariable=self.member_id_var, width=30).pack(fill=compat.tk.X, pady=(5, 10))
        compat.ttk.Label(
            discord_frame,
            text=(
                "How to find it: Discord -> Settings -> Advanced -> Developer Mode (ON)\n"
                "   Right-click your name -> Copy ID"
            ),
            foreground="gray",
            font=("Arial", 8),
        ).pack(anchor=compat.tk.W, pady=(0, 10))

        compat.ttk.Label(discord_frame, text="Bot URL:").pack(anchor=compat.tk.W)
        self.bot_url_var = compat.tk.StringVar(value=get_default_discord_bot_url())
        compat.ttk.Entry(discord_frame, textvariable=self.bot_url_var, width=50).pack(fill=compat.tk.X, pady=(5, 10))

        warning_frame = compat.ttk.Frame(main_frame)
        warning_frame.pack(fill=compat.tk.X, pady=(0, 20))
        compat.ttk.Label(
            warning_frame,
            text="Without the Discord User ID, TTS will only work locally",
            foreground="orange",
            font=("Arial", 9, "italic"),
        ).pack()

        button_frame = compat.ttk.Frame(main_frame)
        button_frame.pack(fill=compat.tk.X)
        compat.ttk.Button(button_frame, text="Continue Without Discord", command=self._skip_discord).pack(
            side=compat.tk.LEFT, padx=(0, 10)
        )
        compat.ttk.Button(button_frame, text="Save and Continue", command=self._save_and_continue).pack(
            side=compat.tk.RIGHT
        )

    def _skip_discord(self):
        self.result = self._presenter.build_skip_discord_result(
            bot_url=get_default_discord_bot_url()
        )
        if self.root is not None:
            self.root.destroy()

    def _save_and_continue(self):
        from . import tk_support as compat

        if self.member_id_var is None or self.bot_url_var is None:
            return

        member_id = self.member_id_var.get().strip()
        bot_url = self.bot_url_var.get().strip()

        validation_error = self._presenter.validate_initial_setup(
            member_id=member_id,
            bot_url=bot_url,
        )
        if validation_error:
            compat.messagebox.showerror(validation_error.title, validation_error.message)
            return

        self.result, feedback = self._presenter.build_initial_setup_result(
            member_id=member_id,
            bot_url=bot_url,
        )
        compat.messagebox.showinfo(feedback.title, feedback.message)
        if self.root is not None:
            self.root.destroy()

    def _console_initial_setup(self) -> Optional[InitialSetupResult]:
        print("\n" + "=" * 60)
        print("Desktop App - Initial Setup")
        print("=" * 60)
        print("To use TTS on Discord, configure your Discord User ID:")
        print("")
        print("1. Discord User ID:")
        print("   How to find it: Discord -> Settings -> Advanced -> Developer Mode")
        print("   Then: right-click your name -> Copy ID")
        member_id = input("   Discord User ID (leave blank to skip): ").strip()
        if member_id and not member_id.isdigit():
            print("ID must contain only numbers!")
            member_id = ""

        print("\n2. Bot URL:")
        default_url = get_default_discord_bot_url()
        bot_url = input(f"   Bot URL [{default_url}]: ").strip()
        if not bot_url:
            bot_url = default_url

        if member_id:
            print("\nConfiguration saved! TTS will work on Discord.")
        else:
            print("\nWithout a Discord User ID, TTS will only work locally.")

        return self._presenter.build_console_initial_setup_result(
            member_id=member_id,
            bot_url=bot_url,
        )
