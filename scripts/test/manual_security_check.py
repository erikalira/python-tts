#!/usr/bin/env python3
"""Manual security check for cross-channel TTS leakage prevention."""

from __future__ import annotations

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.application.use_cases import SpeakTextUseCase
from src.core.entities import TTSRequest
from src.infrastructure.audio_queue import InMemoryAudioQueue
from tests.conftest import (
    MockConfigRepository,
    MockTTSEngine,
    MockVoiceChannel,
    MockVoiceChannelRepository,
)


class SecurityTestChannel(MockVoiceChannel):
    """Test channel with a stable channel id."""

    def __init__(self, channel_id: int):
        super().__init__()
        self._channel_id = channel_id

    def get_channel_id(self) -> int:
        return self._channel_id


class SecurityTestRepository(MockVoiceChannelRepository):
    """Test repository for security scenarios."""

    def __init__(self):
        self.bot_connected_channel = SecurityTestChannel(111)
        self.bot_connected_channel.connected = True

        self.user_current_channel = SecurityTestChannel(222)

        super().__init__(self.bot_connected_channel)

    async def find_connected_channel(self):
        """Return the channel where the bot is connected."""

        print(
            "[REPOSITORY] Bot is connected to channel "
            f"{self.bot_connected_channel.get_channel_id()}"
        )
        return self.bot_connected_channel

    async def find_by_member_id(self, member_id: int):
        """Return the channel where the user is currently connected."""

        print(
            f"[REPOSITORY] User {member_id} is in channel "
            f"{self.user_current_channel.get_channel_id()}"
        )
        return self.user_current_channel


async def test_security_vulnerability() -> None:
    """Test the vulnerable scenario where the user moved channels."""

    print("TTS SECURITY CHECK - Cross-channel information leakage")
    print("=" * 60)

    tts_engine = MockTTSEngine()
    repository = SecurityTestRepository()
    config_repository = MockConfigRepository()
    audio_queue = InMemoryAudioQueue()

    use_case = SpeakTextUseCase(
        tts_engine=tts_engine,
        channel_repository=repository,
        config_repository=config_repository,
        audio_queue=audio_queue,
    )

    print("\nSCENARIO:")
    print("- Bot is connected to Channel A (ID: 111).")
    print("- User left Channel A and is now in Channel B (ID: 222).")
    print("- User requests TTS: 'Confidential information'.")
    print()

    request = TTSRequest(
        text="Confidential information that should not leak",
        member_id=123,
        guild_id=999,
    )

    print("EXECUTING USE CASE...")
    result = await use_case.execute(request)

    print("\nRESULT:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")

    if result["success"]:
        print("\nSECURITY FAILURE: TTS ran after the user moved channels.")
        print("Information leakage confirmed.")
    else:
        print("\nSECURITY FIX WORKING:")
        print("The bot rejected the request for security reasons.")
        print("Information was protected from cross-channel playback.")

    if repository.bot_connected_channel.played_audio:
        print(
            "\nAUDIO PLAYED IN THE WRONG CHANNEL: "
            f"{repository.bot_connected_channel.played_audio}"
        )
    else:
        print("\nNo audio was played, as expected.")

    print("\n" + "=" * 60)


async def test_security_valid_scenario() -> None:
    """Test the valid scenario where the user is in the bot channel."""

    print("TTS SECURITY CHECK - Valid same-channel scenario")
    print("=" * 60)

    tts_engine = MockTTSEngine()
    config_repository = MockConfigRepository()
    audio_queue = InMemoryAudioQueue()

    class ValidRepository(MockVoiceChannelRepository):
        def __init__(self):
            self.shared_channel = SecurityTestChannel(111)
            self.shared_channel.connected = True
            super().__init__(self.shared_channel)

        async def find_connected_channel(self):
            return self.shared_channel

        async def find_by_member_id(self, member_id: int):
            return self.shared_channel

    repository = ValidRepository()

    use_case = SpeakTextUseCase(
        tts_engine=tts_engine,
        channel_repository=repository,
        config_repository=config_repository,
        audio_queue=audio_queue,
    )

    print("\nSCENARIO:")
    print("- Bot is connected to Channel A (ID: 111).")
    print("- User is also in Channel A (ID: 111).")
    print("- User requests TTS: 'Valid information'.")
    print()

    request = TTSRequest(
        text="Valid information for a user in the correct channel",
        member_id=123,
        guild_id=999,
    )

    print("EXECUTING USE CASE...")
    result = await use_case.execute(request)

    print("\nRESULT:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")

    if result["success"]:
        print("\nEXPECTED BEHAVIOR:")
        print("TTS ran safely because the user is in the correct channel.")
    else:
        print("\nPROBLEM: TTS was rejected even though the user is in the correct channel.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("DISCORD TTS BOT SECURITY CHECK")
    print("Checking the information leakage fix.")
    print()

    try:
        asyncio.run(test_security_vulnerability())
        print()
        asyncio.run(test_security_valid_scenario())
        print("\nChecks completed.")
    except Exception as exc:
        print(f"\nERROR DURING CHECK: {exc}")
        import traceback

        traceback.print_exc()
