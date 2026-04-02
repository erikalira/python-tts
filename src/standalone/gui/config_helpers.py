#!/usr/bin/env python3
"""Shared helpers for Desktop App configuration UIs."""

from dataclasses import replace

from ..config.standalone_config import StandaloneConfig


def normalize_optional_text(value: str) -> str | None:
    """Return stripped text or None when blank."""
    stripped = value.strip()
    return stripped or None


def resolve_text_value(value: str, fallback: str) -> str:
    """Return stripped text or fallback when blank."""
    stripped = value.strip()
    return stripped or fallback


def prompt_numeric_input(prompt: str, current_value: str, error_message: str) -> str:
    """Prompt until the user provides a numeric value or keeps the current one."""
    while True:
        value = input(prompt).strip()
        if not value and current_value:
            return current_value
        if value and value.isdigit():
            return value
        print(error_message)


def validate_numeric_field(value: str, *, required: bool, required_message: str, numeric_message: str) -> str | None:
    """Validate a numeric text field and return an error message when invalid."""
    stripped = value.strip()
    if required and not stripped:
        return required_message
    if stripped and not stripped.isdigit():
        return numeric_message
    return None


def build_updated_config(
    current_config: StandaloneConfig,
    *,
    member_id: str | None = None,
    guild_id: str | None = None,
    bot_url: str | None = None,
    engine: str | None = None,
    language: str | None = None,
    voice_id: str | None = None,
    rate: int | None = None,
    trigger_open: str | None = None,
    trigger_close: str | None = None,
    show_notifications: bool | None = None,
    console_logs: bool | None = None,
) -> StandaloneConfig:
    """Create a new config with the provided updated values."""
    return StandaloneConfig(
        discord=replace(
            current_config.discord,
            member_id=current_config.discord.member_id if member_id is None else member_id,
            guild_id=current_config.discord.guild_id if guild_id is None else guild_id,
            bot_url=current_config.discord.bot_url if bot_url is None else bot_url,
        ),
        tts=replace(
            current_config.tts,
            engine=current_config.tts.engine if engine is None else engine,
            language=current_config.tts.language if language is None else language,
            voice_id=current_config.tts.voice_id if voice_id is None else voice_id,
            rate=current_config.tts.rate if rate is None else rate,
        ),
        hotkey=replace(
            current_config.hotkey,
            trigger_open=current_config.hotkey.trigger_open if trigger_open is None else trigger_open,
            trigger_close=current_config.hotkey.trigger_close if trigger_close is None else trigger_close,
        ),
        interface=replace(
            current_config.interface,
            show_notifications=current_config.interface.show_notifications if show_notifications is None else show_notifications,
            console_logs=current_config.interface.console_logs if console_logs is None else console_logs,
        ),
        network=current_config.network,
    )
