"""Use cases for Discord interface language preferences."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(slots=True)
class InterfaceLanguagePreferenceResult:
    """Result for interface language preference updates."""

    success: bool
    locale: Optional[str] = None
    message: Optional[str] = None


class InterfaceLanguagePreferenceRepository(Protocol):
    """Persistence contract for interface language preferences."""

    def get_user_language(self, guild_id: int, user_id: int) -> Optional[str]:
        """Return a user's explicit interface language for a guild, if any."""

    def get_guild_language(self, guild_id: int) -> Optional[str]:
        """Return a guild's explicit default interface language, if any."""

    async def set_user_language(self, guild_id: int, user_id: int, locale: str) -> bool:
        """Persist a user's explicit interface language for a guild."""

    async def set_guild_language(self, guild_id: int, locale: str) -> bool:
        """Persist a guild's explicit default interface language."""

    async def delete_user_language(self, guild_id: int, user_id: int) -> bool:
        """Delete a user's explicit interface language preference."""

    async def delete_guild_language(self, guild_id: int) -> bool:
        """Delete a guild's explicit default interface language."""


class ConfigureInterfaceLanguageUseCase:
    """Configure interface language preferences without changing TTS voice settings."""

    def __init__(self, preference_repository: InterfaceLanguagePreferenceRepository):
        self._preference_repository = preference_repository

    def get_user_language(self, guild_id: int | None, user_id: int | None) -> str | None:
        if guild_id is None or user_id is None:
            return None
        return self._preference_repository.get_user_language(guild_id, user_id)

    def get_guild_language(self, guild_id: int | None) -> str | None:
        if guild_id is None:
            return None
        return self._preference_repository.get_guild_language(guild_id)

    async def set_user_language(
        self,
        guild_id: int | None,
        user_id: int | None,
        locale: str,
    ) -> InterfaceLanguagePreferenceResult:
        if guild_id is None:
            return InterfaceLanguagePreferenceResult(False, message="Guild ID is required")
        if user_id is None:
            return InterfaceLanguagePreferenceResult(False, message="User ID is required")

        saved = await self._preference_repository.set_user_language(guild_id, user_id, locale)
        if not saved:
            return InterfaceLanguagePreferenceResult(False, message="Failed to save interface language")
        return InterfaceLanguagePreferenceResult(True, locale=locale)

    async def set_guild_language(
        self,
        guild_id: int | None,
        locale: str,
    ) -> InterfaceLanguagePreferenceResult:
        if guild_id is None:
            return InterfaceLanguagePreferenceResult(False, message="Guild ID is required")

        saved = await self._preference_repository.set_guild_language(guild_id, locale)
        if not saved:
            return InterfaceLanguagePreferenceResult(False, message="Failed to save interface language")
        return InterfaceLanguagePreferenceResult(True, locale=locale)

    async def reset_user_language(
        self,
        guild_id: int | None,
        user_id: int | None,
    ) -> InterfaceLanguagePreferenceResult:
        if guild_id is None:
            return InterfaceLanguagePreferenceResult(False, message="Guild ID is required")
        if user_id is None:
            return InterfaceLanguagePreferenceResult(False, message="User ID is required")

        deleted = await self._preference_repository.delete_user_language(guild_id, user_id)
        if not deleted:
            return InterfaceLanguagePreferenceResult(False, message="Failed to reset interface language")
        return InterfaceLanguagePreferenceResult(True)

    async def reset_guild_language(self, guild_id: int | None) -> InterfaceLanguagePreferenceResult:
        if guild_id is None:
            return InterfaceLanguagePreferenceResult(False, message="Guild ID is required")

        deleted = await self._preference_repository.delete_guild_language(guild_id)
        if not deleted:
            return InterfaceLanguagePreferenceResult(False, message="Failed to reset interface language")
        return InterfaceLanguagePreferenceResult(True)
