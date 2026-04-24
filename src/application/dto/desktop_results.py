"""Typed Desktop App result DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DesktopBotConnectionStatusDTO:
    """Structured health-check response from the bot runtime."""

    success: bool
    message: str


@dataclass(frozen=True)
class DesktopBotVoiceContextStatusDTO:
    """Structured voice-context response from the bot runtime."""

    success: bool
    message: str
    guild_name: str | None = None
    guild_id: int | None = None
    channel_name: str | None = None
    channel_id: int | None = None


@dataclass(frozen=True)
class DesktopBotActionResultDTO:
    """Structured result for Desktop App actions against the bot runtime."""

    success: bool
    message: str


@dataclass(frozen=True)
class DesktopBotVoiceContextResultDTO(DesktopBotActionResultDTO):
    """Structured result for Desktop App voice-context detection."""

    guild_name: str | None = None
    channel_name: str | None = None


@dataclass(frozen=True)
class DesktopConfigurationSaveResultDTO:
    """Structured result for Desktop App configuration saves from the main window."""

    success: bool
    message: str
