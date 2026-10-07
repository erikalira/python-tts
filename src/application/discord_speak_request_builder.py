"""Application service for preparing Discord speak-command input."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from src.application.dto import ConfigureTTSResult, SpeakTextInputDTO
from src.application.tts_voice_catalog import TTSCatalog
from src.core.entities import TTSConfig, normalize_fish_audio_reference_id

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
    used_supplied_provider_voice: bool = False
    """True when the caller supplied a raw third-party voice id.

    The caller is told, in that case, that the text leaves this server. On the
    curated-catalog path the engines are keyless and nothing is retained
    elsewhere, so there is nothing to disclose.
    """


class TTSConfigLookup(Protocol):
    """Minimal config lookup needed to build a speak request."""

    def get_config(self, guild_id: int, user_id: int | None = None) -> ConfigureTTSResult | None:
        """Return the effective TTS config for a guild/user."""
        ...


class DiscordSpeakRequestBuilder:
    """Build speak-command input from Discord interaction primitives."""

    def __init__(self, config_use_case: TTSConfigLookup, tts_catalog: TTSCatalog):
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
        supplied_reference_id: str | None = None
        if voice_key is not None:
            selected_voice = self._tts_catalog.get_voice_option(voice_key)
            if selected_voice is None:
                supplied_reference_id = normalize_fish_audio_reference_id(voice_key)
            if selected_voice is None and supplied_reference_id is None:
                return DiscordSpeakPreparationResult(
                    error_code=DISCORD_SPEAK_PREP_INVALID_VOICE,
                    error_message="invalid voice",
                )

            current_config = self._config_use_case.get_config(guild_id, user_id=member_id)
            if current_config is None or not current_config.success or current_config.config is None:
                return DiscordSpeakPreparationResult(
                    error_code=DISCORD_SPEAK_PREP_VOICE_CONFIG_UNAVAILABLE,
                    error_message="voice config unavailable",
                )

            if selected_voice is not None:
                config_override = TTSConfig(
                    engine=selected_voice.engine,
                    language=selected_voice.language,
                    voice_id=selected_voice.voice_id,
                    rate=current_config.config.rate,
                )
            elif supplied_reference_id is not None:
                # A raw Fish Audio reference_id: no catalog entry exists for it,
                # and the voice model determines the language, so the stored
                # language is preserved rather than guessed at.
                config_override = TTSConfig(
                    engine="fish-audio",
                    language=current_config.config.language,
                    voice_id=supplied_reference_id,
                    rate=current_config.config.rate,
                )

        return DiscordSpeakPreparationResult(
            used_supplied_provider_voice=supplied_reference_id is not None,
            request=SpeakTextInputDTO(
                text=text,
                guild_id=guild_id,
                member_id=member_id,
                config_override=config_override,
            )
        )
