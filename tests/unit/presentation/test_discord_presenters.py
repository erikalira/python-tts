"""Unit tests for Discord presenters."""

from src.application.dto import (
    JOIN_RESULT_USER_NOT_IN_CHANNEL,
    LEAVE_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_GENERATION_TIMEOUT,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_VOICE_PERMISSION_DENIED,
    JoinVoiceChannelResult,
    LeaveVoiceChannelResult,
    SpeakTextResult,
)
from src.application.rate_limiting import RateLimitResult
from src.presentation.discord_presenters import (
    DiscordJoinPresenter,
    DiscordLeavePresenter,
    DiscordSpeakPresenter,
)


class TestDiscordSpeakPresenter:
    def test_builds_queue_message(self):
        presenter = DiscordSpeakPresenter()

        message = presenter.build_message(
            SpeakTextResult(success=True, code=SPEAK_RESULT_QUEUED, queued=True, position=1, queue_size=3)
        )

        assert "queue" in message
        assert "entered" in message
        assert "2" in message
        assert "3" in message

    def test_builds_permission_denied_message(self):
        presenter = DiscordSpeakPresenter()

        message = presenter.build_message(
            SpeakTextResult(success=False, code=SPEAK_RESULT_VOICE_PERMISSION_DENIED, queued=False)
        )

        assert "permission" in message.lower()

    def test_builds_generation_timeout_message(self):
        presenter = DiscordSpeakPresenter()

        message = presenter.build_message(
            SpeakTextResult(success=False, code=SPEAK_RESULT_GENERATION_TIMEOUT, queued=False)
        )

        assert "generating" in message.lower()

    def test_builds_rate_limit_message(self):
        presenter = DiscordSpeakPresenter()

        message = presenter.build_rate_limit_message(
            RateLimitResult(
                allowed=False,
                scope="discord:speak:guild:1:user:2",
                reason="too_many_requests",
                retry_after_seconds=4.2,
            )
        )

        assert "requests" in message.lower()
        assert "4" in message


class TestDiscordJoinPresenter:
    def test_builds_user_not_in_channel_message(self):
        presenter = DiscordJoinPresenter()

        message = presenter.build_message(
            JoinVoiceChannelResult(success=False, code=JOIN_RESULT_USER_NOT_IN_CHANNEL)
        )

        assert "not connected" in message.lower()

    def test_builds_portuguese_user_not_in_channel_message(self):
        presenter = DiscordJoinPresenter()

        message = presenter.build_message(
            JoinVoiceChannelResult(success=False, code=JOIN_RESULT_USER_NOT_IN_CHANNEL),
            locale="pt-BR",
        )

        assert "não está conectado" in message.lower()


class TestDiscordLeavePresenter:
    def test_includes_error_detail_when_disconnect_fails(self):
        presenter = DiscordLeavePresenter()

        message = presenter.build_message(
            LeaveVoiceChannelResult(
                success=False,
                code=LEAVE_RESULT_VOICE_CONNECTION_FAILED,
                error_detail="boom",
            )
        )

        assert "boom" in message
