"""Voice-channel related application use cases."""

from __future__ import annotations

import logging

from src.application.dto import (
    JOIN_RESULT_MISSING_GUILD_ID,
    JOIN_RESULT_OK,
    JOIN_RESULT_USER_NOT_IN_CHANNEL,
    JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND,
    JOIN_RESULT_VOICE_CONNECTION_FAILED,
    LEAVE_RESULT_MISSING_GUILD_ID,
    LEAVE_RESULT_NOT_CONNECTED,
    LEAVE_RESULT_OK,
    LEAVE_RESULT_VOICE_CONNECTION_FAILED,
    VOICE_CONTEXT_RESULT_MEMBER_REQUIRED,
    VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL,
    VOICE_CONTEXT_RESULT_OK,
    JoinVoiceChannelResult,
    LeaveVoiceChannelResult,
    VoiceContextQueryDTO,
    VoiceContextResult,
)
from src.core.interfaces import IVoiceChannelRepository

logger = logging.getLogger(__name__)


class JoinVoiceChannelUseCase:
    """Use case for connecting the bot to a member's current voice channel."""

    def __init__(self, channel_repository: IVoiceChannelRepository):
        self._channel_repository = channel_repository

    async def execute(self, guild_id: int | None, member_id: int | None) -> JoinVoiceChannelResult:
        if guild_id is None:
            return JoinVoiceChannelResult(success=False, code=JOIN_RESULT_MISSING_GUILD_ID)
        if member_id is None:
            return JoinVoiceChannelResult(success=False, code=JOIN_RESULT_USER_NOT_IN_CHANNEL)

        channel = await self._channel_repository.find_by_member_id(member_id)
        if not channel:
            return JoinVoiceChannelResult(success=False, code=JOIN_RESULT_USER_NOT_IN_CHANNEL)
        if channel.get_guild_id() != guild_id:
            return JoinVoiceChannelResult(success=False, code=JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND)

        try:
            await channel.connect()
        except Exception as exc:
            logger.error("[JOIN_USE_CASE] Failed to connect to voice channel: %s", exc, exc_info=True)
            return JoinVoiceChannelResult(
                success=False,
                code=JOIN_RESULT_VOICE_CONNECTION_FAILED,
                error_detail=str(exc),
            )

        return JoinVoiceChannelResult(success=True, code=JOIN_RESULT_OK)


class LeaveVoiceChannelUseCase:
    """Use case for disconnecting the bot from a guild voice channel."""

    def __init__(self, channel_repository: IVoiceChannelRepository):
        self._channel_repository = channel_repository

    async def execute(self, guild_id: int | None) -> LeaveVoiceChannelResult:
        if guild_id is None:
            return LeaveVoiceChannelResult(success=False, code=LEAVE_RESULT_MISSING_GUILD_ID)

        channel = await self._channel_repository.find_by_guild_id(guild_id)
        if not channel or not channel.is_connected():
            return LeaveVoiceChannelResult(success=False, code=LEAVE_RESULT_NOT_CONNECTED)

        try:
            await channel.disconnect()
        except Exception as exc:
            logger.error("[LEAVE_USE_CASE] Failed to disconnect from voice channel: %s", exc, exc_info=True)
            return LeaveVoiceChannelResult(
                success=False,
                code=LEAVE_RESULT_VOICE_CONNECTION_FAILED,
                error_detail=str(exc),
            )

        return LeaveVoiceChannelResult(success=True, code=LEAVE_RESULT_OK)


class GetCurrentVoiceContextUseCase:
    """Use case for discovering the member's current voice context."""

    def __init__(self, channel_repository: IVoiceChannelRepository):
        self._channel_repository = channel_repository

    async def execute(self, query: VoiceContextQueryDTO) -> VoiceContextResult:
        if query.member_id is None:
            return VoiceContextResult(success=False, code=VOICE_CONTEXT_RESULT_MEMBER_REQUIRED)

        channel = await self._channel_repository.find_by_member_id(query.member_id)
        if not channel:
            return VoiceContextResult(success=False, code=VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL)

        return VoiceContextResult(
            success=True,
            code=VOICE_CONTEXT_RESULT_OK,
            member_id=query.member_id,
            guild_id=channel.get_guild_id(),
            guild_name=channel.get_guild_name(),
            channel_id=channel.get_channel_id(),
            channel_name=channel.get_channel_name(),
        )
