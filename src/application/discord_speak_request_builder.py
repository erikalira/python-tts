"""Application service for preparing Discord speak-command input."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.application.dto import SpeakTextInputDTO
from src.application.tts_config_use_case import ConfigureTTSUseCase
from src.application.tts_voice_catalog import TTSCatalog
from src.core.entities import TTSConfig

DISCORD_SPEAK_PREP_MISSING_GUILD_ID = "missing_guild_id"
DISCORD_SPEAK_PREP_INVALID_VOICE = "invalid_voice"
DISCORD_SPEAK_PREP_VOICE_CONFIG_UNAVAILABLE = "voice_config_unavailable"

DiscordSpeakPreparationErrorCode = Literal[
    "missing_guild_id",
    "invalid_voice",
    "voice_config_unavailable",
]


@dataclass(frozen=True, slots=True)
class DiscordSpeakPreparationResult:
    """Prepared speak input or a user-facing validation error."""

    request: SpeakTextInputDTO | None = None
    error_code: DiscordSpeakPreparationErrorCode | None = None
    error_message: str | None = None


class DiscordSpeakRequestBuilder:
    """Build speak-command input from Discord interaction primitives."""

    def __init__(self, config_use_case: ConfigureTTSUseCase, tts_catalog: TTSCatalog):
        self._config_use_case = config_use_case
        self._tts_catalog = tts_catalog

    def build(
        self,
        *,
        text: str,
        guild_id: int | None,
        member_id: int | None,
        voice_key: str | None = None,
    ) -> DiscordSpeakPreparationResult:
        if not guild_id:
            return DiscordSpeakPreparationResult(
                error_code=DISCORD_SPEAK_PREP_MISSING_GUILD_ID,
                error_message="missing guild id",
            )

        config_override = None
        if voice_key is not None:
            selected_voice = self._tts_catalog.get_voice_option(voice_key)
            if selected_voice is None:
                return DiscordSpeakPreparationResult(
                    error_code=DISCORD_SPEAK_PREP_INVALID_VOICE,
                    error_message="invalid voice",
                )

            current_config = self._config_use_case.get_config(guild_id, user_id=member_id)
            if not current_config.success or current_config.config is None:
                return DiscordSpeakPreparationResult(
                    error_code=DISCORD_SPEAK_PREP_VOICE_CONFIG_UNAVAILABLE,
                    error_message="voice config unavailable",
                )

            config_override = TTSConfig(
                engine=selected_voice.engine,
                language=selected_voice.language,
                voice_id=selected_voice.voice_id,
                rate=current_config.config.rate,
            )

        return DiscordSpeakPreparationResult(
            request=SpeakTextInputDTO(
                text=text,
                guild_id=guild_id,
                member_id=member_id,
                config_override=config_override,
            )
        )
