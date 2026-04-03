#!/usr/bin/env python3
"""Validation for Desktop App configuration."""

from .models import DesktopAppConfig


class ConfigurationValidator:
    """Validates configuration values."""

    @staticmethod
    def validate(config: DesktopAppConfig) -> tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, errors)."""
        errors = []

        if config.discord.member_id and not config.discord.member_id.isdigit():
            errors.append("Discord Member ID deve conter apenas numeros")

        if config.tts.rate < 50 or config.tts.rate > 500:
            errors.append("TTS Rate deve estar entre 50 e 500 WPM")

        if config.network.request_timeout < 1 or config.network.request_timeout > 60:
            errors.append("Request timeout deve estar entre 1 e 60 segundos")

        if config.network.max_text_length < 1 or config.network.max_text_length > 2000:
            errors.append("Comprimento maximo do texto deve estar entre 1 e 2000 caracteres")

        return len(errors) == 0, errors

    @staticmethod
    def is_configured(config: DesktopAppConfig) -> bool:
        """Check if minimum configuration is present."""
        return (
            config.discord.member_id is not None
            and len(config.discord.member_id.strip()) > 0
        )
