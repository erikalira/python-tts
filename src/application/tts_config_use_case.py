"""TTS configuration application use case."""

from __future__ import annotations

import logging
from typing import Optional

from src.application.dto import ConfigureTTSResult, TTSConfigurationData
from src.core.interfaces import IConfigRepository

logger = logging.getLogger(__name__)


class ConfigureTTSUseCase:
    """Use case for configuring TTS settings per guild."""

    def __init__(self, config_repository: IConfigRepository):
        self._config_repository = config_repository

    def get_config(self, guild_id: int, user_id: Optional[int] = None) -> ConfigureTTSResult:
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
        user_id: Optional[int] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
        rate: Optional[int] = None,
    ) -> ConfigureTTSResult:
        if guild_id is None:
            return ConfigureTTSResult(success=False, message="Guild ID is required")

        logger.info("[CONFIG_USE_CASE] Updating config for guild %s", guild_id)
        current_config = self._config_repository.get_config(guild_id, user_id=user_id)

        if engine is not None:
            if engine.lower() not in ["gtts", "pyttsx3", "edge-tts"]:
                return ConfigureTTSResult(
                    success=False,
                    message="Invalid engine. Use 'gtts', 'pyttsx3' or 'edge-tts'",
                )
            current_config.engine = engine.lower()
        if language is not None:
            current_config.language = language.lower()
        if voice_id is not None:
            current_config.voice_id = voice_id
        if rate is not None:
            if not (50 <= rate <= 300):
                return ConfigureTTSResult(
                    success=False,
                    message="Rate must be between 50 and 300",
                )
            current_config.rate = rate

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

    async def reset_config_async(self, guild_id: int, user_id: Optional[int] = None) -> ConfigureTTSResult:
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
