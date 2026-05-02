#!/usr/bin/env python3
"""Validation for Desktop App configuration."""

from src.core.timeouts import (
    MAX_DESKTOP_HTTP_REQUEST_TIMEOUT_SECONDS,
    MIN_DESKTOP_HTTP_REQUEST_TIMEOUT_SECONDS,
)

from .models import DesktopAppConfig


class ConfigurationValidator:
    """Validates configuration values."""

    @staticmethod
    def validate(config: DesktopAppConfig) -> tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, errors)."""
        errors = []

        if config.discord.member_id and not config.discord.member_id.isdigit():
            errors.append("Discord Member ID must contain only numbers")

        if config.tts.rate < 50 or config.tts.rate > 500:
            errors.append("TTS Rate must be between 50 and 500 WPM")

        if (
            config.network.request_timeout < MIN_DESKTOP_HTTP_REQUEST_TIMEOUT_SECONDS
            or config.network.request_timeout > MAX_DESKTOP_HTTP_REQUEST_TIMEOUT_SECONDS
        ):
            errors.append("Request timeout must be between 1 and 60 seconds")

        if config.network.max_text_length < 1 or config.network.max_text_length > 2000:
            errors.append("Maximum text length must be between 1 and 2000 characters")

        return len(errors) == 0, errors

    @staticmethod
    def is_configured(config: DesktopAppConfig) -> bool:
        """Check if minimum configuration is present."""
        return (
            config.discord.member_id is not None
            and len(config.discord.member_id.strip()) > 0
        )
