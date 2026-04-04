"""Focused tests for voice channel resolution rules."""

import pytest

from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.core.entities import TTSRequest
from tests.conftest import MockVoiceChannel, MockVoiceChannelRepository


class ResolutionRepository(MockVoiceChannelRepository):
    """Configurable repository for voice resolution scenarios."""

    def __init__(
        self,
        *,
        member_channel=None,
        connected_channel=None,
        channel_by_id=None,
        return_none=False,
    ):
        super().__init__(channel=member_channel, return_none=return_none)
        self.member_channel = member_channel
        self.connected_channel = connected_channel
        self.channel_by_id = channel_by_id

    async def find_connected_channel(self):
        return self.connected_channel

    async def find_by_member_id(self, member_id: int):
        return None if self.return_none else self.member_channel

    async def find_by_channel_id(self, channel_id: int):
        return self.channel_by_id


@pytest.mark.asyncio
class TestVoiceChannelResolutionService:
    async def test_infer_guild_id_from_member_channel(self):
        member_channel = MockVoiceChannel(channel_id=123456, guild_id=789012)
        service = VoiceChannelResolutionService(
            ResolutionRepository(member_channel=member_channel)
        )

        guild_id = await service.infer_guild_id(TTSRequest(text="test", member_id=345678))

        assert guild_id == 789012

    async def test_reuses_connected_channel_when_member_is_already_there(self):
        channel = MockVoiceChannel(channel_id=123456, guild_id=789012)
        service = VoiceChannelResolutionService(
            ResolutionRepository(member_channel=channel, connected_channel=channel)
        )

        result = await service.resolve_for_request(
            TTSRequest(text="test", guild_id=789012, member_id=345678)
        )

        assert result is not None
        assert result.channel is channel
        assert result.channel_changed is False

    async def test_moves_to_member_channel_when_bot_is_connected_elsewhere(self):
        member_channel = MockVoiceChannel(channel_id=123456, guild_id=789012)
        connected_channel = MockVoiceChannel(channel_id=999999, guild_id=789012)
        service = VoiceChannelResolutionService(
            ResolutionRepository(
                member_channel=member_channel,
                connected_channel=connected_channel,
            )
        )

        result = await service.resolve_for_request(
            TTSRequest(text="test", guild_id=789012, member_id=345678)
        )

        assert result is not None
        assert result.channel is member_channel
        assert result.channel_changed is True

    async def test_rejects_explicit_channel_without_member_context(self):
        service = VoiceChannelResolutionService(ResolutionRepository())

        result = await service.resolve_for_request(
            TTSRequest(text="test", guild_id=789012, channel_id=123456)
        )

        assert result is None

    async def test_rejects_explicit_channel_that_does_not_match_member_location(self):
        member_channel = MockVoiceChannel(channel_id=123456, guild_id=789012)
        other_channel = MockVoiceChannel(channel_id=654321, guild_id=789012)
        service = VoiceChannelResolutionService(
            ResolutionRepository(
                member_channel=member_channel,
                channel_by_id=other_channel,
            )
        )

        result = await service.resolve_for_request(
            TTSRequest(text="test", guild_id=789012, member_id=345678, channel_id=654321)
        )

        assert result is None

    async def test_accepts_explicit_channel_that_matches_member_location(self):
        member_channel = MockVoiceChannel(channel_id=123456, guild_id=789012)
        service = VoiceChannelResolutionService(
            ResolutionRepository(
                member_channel=member_channel,
                channel_by_id=member_channel,
            )
        )

        result = await service.resolve_for_request(
            TTSRequest(text="test", guild_id=789012, member_id=345678, channel_id=123456)
        )

        assert result is not None
        assert result.channel is member_channel
        assert result.channel_changed is False
