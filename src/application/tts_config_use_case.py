"""TTS configuration application use case."""

from __future__ import annotations

import logging
from dataclasses import replace

from src.application.dto import ConfigureTTSResult, TTSConfigurationData
from src.core.entities import SUPPORTED_TTS_ENGINES, normalize_fish_audio_reference_id
from src.core.interfaces import IConfigRepository

logger = logging.getLogger(__name__)



class ConfigureTTSUseCase:
    """Use case for configuring TTS settings per guild."""

    def __init__(self, config_repository: IConfigRepository):
        self._config_repository = config_repository

    def get_config(self, guild_id: int, user_id: int | None = None) -> ConfigureTTSResult:
        if guild_id is None:
            return ConfigureTTSResult(success=False, message="Guild ID is required")

        config = self._config_repository.get_config(guild_id, user_id=user_id)
        return ConfigureTTSResult(
            success=True,
            guild_id=guild_id,
            config=TTSConfigurationData(
                engine=config.engine,
                language=config.language,
                voice_id=config.voice_id,
                rate=config.rate,
            ),
            scope=self._config_repository.get_effective_scope(guild_id, user_id=user_id),
        )

    async def update_config_async(
        self,
        guild_id: int,
        user_id: int | None = None,
        engine: str | None = None,
        language: str | None = None,
        voice_id: str | None = None,
        rate: int | None = None,
    ) -> ConfigureTTSResult:
        if guild_id is None:
            return ConfigureTTSResult(success=False, message="Guild ID is required")

        logger.info("[CONFIG_USE_CASE] Updating config for guild %s", guild_id)
        current_config = self._config_repository.get_config(guild_id, user_id=user_id)
        updates: dict[str, object] = {}

        if engine is not None:
            if engine.lower() not in SUPPORTED_TTS_ENGINES:
                valid = ", ".join(f"'{name}'" for name in SUPPORTED_TTS_ENGINES)
                return ConfigureTTSResult(
                    success=False,
                    message=f"Invalid engine. Use one of: {valid}",
                )
            updates["engine"] = engine.lower()
        if language is not None:
            updates["language"] = language.lower()
        if voice_id is not None:
            updates["voice_id"] = voice_id

        # Validate against the engine this update resolves to, not just the one
        # being set: switching to fish-audio while keeping another engine's
        # voice_id would otherwise persist a configuration that can never speak.
        resolved_engine = str(updates.get("engine", current_config.engine))
        if resolved_engine == "fish-audio":
            resolved_voice_id = str(updates.get("voice_id", current_config.voice_id))
            normalized_voice_id = normalize_fish_audio_reference_id(resolved_voice_id)
            if normalized_voice_id is None:
                return ConfigureTTSResult(
                    success=False,
                    message=(
                        "Invalid voice_id for fish-audio. Expected a 32-character hexadecimal "
                        "reference_id copied from fish.audio, for example "
                        "0123456789abcdef0123456789abcdef"
                    ),
                )
            # Persist what was validated, not the raw input: a pasted identifier
            # often carries whitespace, and storing it would send that to the API.
            updates["voice_id"] = normalized_voice_id
        if rate is not None:
            if not (50 <= rate <= 300):
                return ConfigureTTSResult(
                    success=False,
                    message="Rate must be between 50 and 300",
                )
            updates["rate"] = rate

        # Build a new config instead of mutating the repository's instance: an
        # IConfigRepository that returns a cached object would otherwise leak
        # this guild's edits into every other caller holding the same instance.
        current_config = replace(current_config, **updates)

        saved = await self._config_repository.save_config_async(guild_id, current_config, user_id=user_id)
        if not saved:
            logger.error("[CONFIG_USE_CASE] Failed to persist config for guild %s", guild_id)
            return ConfigureTTSResult(success=False, message="Failed to save configuration")

        return ConfigureTTSResult(
            success=True,
            guild_id=guild_id,
            config=TTSConfigurationData(
                engine=current_config.engine,
                language=current_config.language,
                voice_id=current_config.voice_id,
                rate=current_config.rate,
            ),
            scope="user" if user_id is not None else "guild",
        )

    async def reset_config_async(self, guild_id: int, user_id: int | None = None) -> ConfigureTTSResult:
        if guild_id is None:
            return ConfigureTTSResult(success=False, message="Guild ID is required")

        deleted = await self._config_repository.delete_config_async(guild_id, user_id=user_id)
        if not deleted:
            return ConfigureTTSResult(success=False, message="Failed to reset configuration")

        config = self._config_repository.get_config(guild_id, user_id=user_id)
        return ConfigureTTSResult(
            success=True,
            guild_id=guild_id,
            config=TTSConfigurationData(
                engine=config.engine,
                language=config.language,
                voice_id=config.voice_id,
                rate=config.rate,
            ),
            scope=self._config_repository.get_effective_scope(guild_id, user_id=user_id),
        )
