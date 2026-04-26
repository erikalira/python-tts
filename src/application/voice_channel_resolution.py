"""Application-level voice channel resolution and safety checks."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from src.core.entities import TTSRequest
from src.core.interfaces import IVoiceChannel, IVoiceChannelRepository

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class VoiceChannelResolution:
    """Resolved playback channel and whether a final member revalidation is needed."""

    channel: IVoiceChannel
    channel_changed: bool
    revalidation_recommended: bool


class VoiceChannelResolutionService:
    """Resolve a safe voice channel for a TTS request."""

    def __init__(self, channel_repository: IVoiceChannelRepository):
        self._channel_repository = channel_repository

    async def infer_guild_id(self, request: TTSRequest) -> Optional[int]:
        if request.guild_id is not None or request.member_id is None:
            return request.guild_id

        inferred_channel = await self._channel_repository.find_by_member_id(request.member_id)
        if inferred_channel:
            return inferred_channel.get_guild_id()
        return request.guild_id

    async def resolve_for_request(self, request: TTSRequest) -> Optional[VoiceChannelResolution]:
        user_current_channel = None
        if request.member_id:
            logger.debug("[VOICE_RESOLUTION] Looking up current voice channel for member %s", request.member_id)
            user_current_channel = await self._channel_repository.find_by_member_id(request.member_id)
            if not user_current_channel:
                logger.warning("[VOICE_RESOLUTION] Member %s is not in any voice channel", request.member_id)
                return None

        if request.channel_id:
            if not request.member_id:
                logger.warning("[VOICE_RESOLUTION] Refusing explicit channel without member context")
                return None

            target_channel = await self._channel_repository.find_by_channel_id(request.channel_id)
            if not target_channel or not user_current_channel:
                logger.warning("[VOICE_RESOLUTION] Explicit channel %s could not be resolved safely", request.channel_id)
                return None

            if target_channel.get_channel_id() != user_current_channel.get_channel_id():
                logger.warning(
                    "[VOICE_RESOLUTION] Explicit channel %s does not match member current location",
                    request.channel_id,
                )
                return None

        connected_channel = await self._channel_repository.find_connected_channel()
        if connected_channel:
            if user_current_channel and request.member_id and await self.is_member_in_channel(
                request.member_id, connected_channel
            ):
                logger.debug("[VOICE_RESOLUTION] Reusing current bot channel connection")
                return VoiceChannelResolution(
                    channel=connected_channel,
                    channel_changed=False,
                    revalidation_recommended=False,
                )

            if user_current_channel:
                logger.debug("[VOICE_RESOLUTION] Moving bot to member current voice channel")
                return VoiceChannelResolution(
                    channel=user_current_channel,
                    channel_changed=True,
                    revalidation_recommended=True,
                )

            logger.warning("[VOICE_RESOLUTION] No member channel available while bot is connected")
            return None

        if user_current_channel:
            logger.debug("[VOICE_RESOLUTION] Using member current channel for initial connection")
            return VoiceChannelResolution(
                channel=user_current_channel,
                channel_changed=False,
                revalidation_recommended=True,
            )

        logger.warning("[VOICE_RESOLUTION] No safe voice channel could be resolved")
        return None

    async def is_member_in_channel(self, member_id: int, channel: IVoiceChannel) -> bool:
        try:
            current_user_channel = await self._channel_repository.find_by_member_id(member_id)
            if current_user_channel is None:
                logger.debug("[VOICE_RESOLUTION] Member %s is not in any voice channel", member_id)
                return False

            channel_id = channel.get_channel_id()
            user_channel_id = current_user_channel.get_channel_id()
            is_same = channel_id == user_channel_id
            logger.debug(
                "[VOICE_RESOLUTION] Member %s channel=%s target=%s same=%s",
                member_id,
                user_channel_id,
                channel_id,
                is_same,
            )
            return is_same
        except Exception as exc:
            logger.error("[VOICE_RESOLUTION] Error validating member channel presence: %s", exc)
            return False
