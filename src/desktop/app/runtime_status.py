"""Status helpers for the Desktop App runtime."""

from __future__ import annotations

from typing import Optional

from ..config.desktop_config import DesktopAppConfig


class DesktopAppStatusBuilder:
    """Build compact runtime status views for the Desktop App."""

    def build(
        self,
        *,
        initialized: bool,
        running: bool,
        config: Optional[DesktopAppConfig],
        hotkey_manager: object,
        tts_processor: object,
        notification_service: object,
    ) -> dict:
        """Build a dictionary with the current runtime state."""
        return {
            "initialized": initialized,
            "running": running,
            "discord_configured": bool(config and config.discord.bot_url and config.discord.member_id),
            "hotkey_active": bool(hotkey_manager and hotkey_manager.is_active()),
            "tts_available": bool(
                tts_processor and tts_processor.get_service_status()["tts_available"]
            ),
            "tray_available": bool(
                notification_service and notification_service.is_available()
            ),
        }
