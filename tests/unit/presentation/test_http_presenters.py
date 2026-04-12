"""Unit tests for HTTP presenters."""

from src.application.dto import (
    SPEAK_RESULT_OK,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_QUEUED,
    VOICE_CONTEXT_RESULT_MEMBER_REQUIRED,
    VOICE_CONTEXT_RESULT_OK,
    SpeakTextResult,
    VoiceContextResult,
)
from src.presentation.http_presenters import HTTPSpeakPresenter, HTTPVoiceContextPresenter


class TestHTTPSpeakPresenter:
    def test_builds_success_message_and_status(self):
        presenter = HTTPSpeakPresenter()
        result = SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)

        assert presenter.build_message(result) == "audio played"
        assert presenter.get_status_code(result) == 200

    def test_builds_queue_message(self):
        presenter = HTTPSpeakPresenter()
        result = SpeakTextResult(success=True, code=SPEAK_RESULT_QUEUED, queued=True, position=0, queue_size=2)

        assert presenter.build_message(result) == "queued at position 1/2"

    def test_maps_failures_to_400(self):
        presenter = HTTPSpeakPresenter()
        result = SpeakTextResult(success=False, code=SPEAK_RESULT_QUEUE_FULL, queued=False)

        assert presenter.get_status_code(result) == 400


class TestHTTPVoiceContextPresenter:
    def test_returns_json_payload_and_success_status(self):
        presenter = HTTPVoiceContextPresenter()
        result = VoiceContextResult(
            success=True,
            code=VOICE_CONTEXT_RESULT_OK,
            member_id=1,
            guild_id=2,
            channel_id=3,
        )

        assert presenter.to_payload(result)["guild_id"] == 2
        assert presenter.get_status_code(result) == 200

    def test_maps_missing_member_to_400(self):
        presenter = HTTPVoiceContextPresenter()
        result = VoiceContextResult(success=False, code=VOICE_CONTEXT_RESULT_MEMBER_REQUIRED)

        assert presenter.get_status_code(result) == 400
