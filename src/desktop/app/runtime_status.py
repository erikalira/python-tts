"""Status helpers for the Desktop App runtime."""

from __future__ import annotations

from typing import Protocol

from src.application.dto import DesktopAppRuntimeStatusDTO, DesktopTTSServiceStatusDTO

from ..config.desktop_config import DesktopAppConfig


class HotkeyManagerStatusPort(Protocol):
    """Contract needed to determine Desktop App hotkey activity."""

    def is_active(self) -> bool:
        """Return whether hotkey monitoring is active."""
        ...


class DesktopTTSProcessorStatusPort(Protocol):
    """Contract needed to determine Desktop App TTS availability."""

    def get_service_status(self) -> DesktopTTSServiceStatusDTO:
        """Return the typed TTS runtime status."""
        ...


class NotificationServiceStatusPort(Protocol):
    """Contract needed to determine tray availability."""

    def is_available(self) -> bool:
        """Return whether tray support is available."""
        ...


class DesktopAppStatusBuilder:
    """Build compact runtime status views for the Desktop App."""

    def build(
        self,
        *,
        initialized: bool,
        running: bool,
        config: DesktopAppConfig | None,
        hotkey_manager: HotkeyManagerStatusPort | None,
        tts_processor: DesktopTTSProcessorStatusPort | None,
        notification_service: NotificationServiceStatusPort | None,
    ) -> DesktopAppRuntimeStatusDTO:
        """Build the typed current runtime state."""
        tts_status = tts_processor.get_service_status() if tts_processor else None
        return DesktopAppRuntimeStatusDTO(
            initialized=initialized,
            running=running,
            discord_configured=bool(config and config.discord.bot_url and config.discord.member_id),
            hotkey_active=bool(hotkey_manager and hotkey_manager.is_active()),
            tts_available=bool(tts_status and tts_status.tts_available),
            tray_available=bool(notification_service and notification_service.is_available()),
        )
