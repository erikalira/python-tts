"""Tests for TTS engines."""

import asyncio
import logging
import sys
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from src.core.entities import AudioFile, TTSConfig
from src.infrastructure.tts.audio_cleanup import FileAudioCleanup
from src.infrastructure.tts.engines import (
    FishAudioError,
    FishAudioSettings,
    RoutedTTSEngine,
    TTSEngineFactory,
)

FISH_VOICE_ID = "0123456789abcdef0123456789abcdef"


class TestTTSEngineFactory:
    """Test TTSEngineFactory."""

    def test_create_gtts_engine(self):
        """Test creating gTTS engine."""
        config = TTSConfig(engine="gtts")
        engine = TTSEngineFactory.create(config)

        assert engine is not None
        from src.infrastructure.tts.engines import GTTSEngine

        assert isinstance(engine, GTTSEngine)

    def test_create_pyttsx3_engine(self):
        """Test creating pyttsx3 engine."""
        config = TTSConfig(engine="pyttsx3")
        engine = TTSEngineFactory.create(config)

        assert engine is not None
        from src.infrastructure.tts.engines import Pyttsx3Engine

        assert isinstance(engine, Pyttsx3Engine)

    def test_create_edge_tts_engine(self):
        """Test creating edge-tts engine."""
        config = TTSConfig(engine="edge-tts")
        engine = TTSEngineFactory.create(config)

        assert engine is not None
        from src.infrastructure.tts.engines import EdgeTTSEngine

        assert isinstance(engine, EdgeTTSEngine)

    def test_create_fish_audio_engine(self):
        """Test creating Fish Audio engine when a credential is supplied."""
        config = TTSConfig(engine="fish-audio")
        engine = TTSEngineFactory.create(config, fish_audio=FishAudioSettings(api_key="test-key"))

        assert engine is not None
        from src.infrastructure.tts.engines import FishAudioEngine

        assert isinstance(engine, FishAudioEngine)

    def test_create_fish_audio_engine_without_credential(self):
        """Selecting fish-audio with no settings fails as a configuration error."""
        config = TTSConfig(engine="fish-audio")

        with pytest.raises(FishAudioError, match="FISH_AUDIO"):
            TTSEngineFactory.create(config)

    def test_create_invalid_engine(self):
        """Test creating invalid engine raises error."""
        config = TTSConfig(engine="invalid")

        with pytest.raises(ValueError, match="Unknown TTS engine"):
            TTSEngineFactory.create(config)


@pytest.mark.asyncio
class TestRoutedTTSEngine:
    async def test_routes_to_engine_requested_by_current_config(self):
        gtts_engine = AsyncMock()
        gtts_engine.generate_audio = AsyncMock(return_value=AudioFile(path="/tmp/gtts.mp3"))
        pyttsx3_engine = AsyncMock()
        pyttsx3_engine.generate_audio = AsyncMock(return_value=AudioFile(path="/tmp/pyttsx3.wav"))
        edge_engine = AsyncMock()
        edge_engine.generate_audio = AsyncMock(return_value=AudioFile(path="/tmp/edge.mp3"))

        create_calls = []

        def fake_create(config: TTSConfig, *, fish_audio=None):
            create_calls.append(config.engine)
            if config.engine == "gtts":
                return gtts_engine
            if config.engine == "pyttsx3":
                return pyttsx3_engine
            if config.engine == "edge-tts":
                return edge_engine
            raise AssertionError(f"unexpected engine {config.engine}")

        router = RoutedTTSEngine()
        with patch("src.infrastructure.tts.engines.TTSEngineFactory.create", side_effect=fake_create):
            first = await router.generate_audio("hello", TTSConfig(engine="gtts", language="pt"))
            second = await router.generate_audio("robot", TTSConfig(engine="pyttsx3", language="en"))
            third = await router.generate_audio(
                "neural", TTSConfig(engine="edge-tts", language="pt-BR", voice_id="pt-BR-FranciscaNeural")
            )

        assert first.path == "/tmp/gtts.mp3"
        assert second.path == "/tmp/pyttsx3.wav"
        assert third.path == "/tmp/edge.mp3"
        assert create_calls == ["gtts", "pyttsx3", "edge-tts"]
        gtts_engine.generate_audio.assert_awaited_once()
        pyttsx3_engine.generate_audio.assert_awaited_once()
        edge_engine.generate_audio.assert_awaited_once()

    async def test_passes_fish_audio_settings_to_the_factory(self):
        fish_engine = AsyncMock()
        fish_engine.generate_audio = AsyncMock(return_value=AudioFile(path="/tmp/fish.mp3"))
        settings = FishAudioSettings(api_key="k", model="s2.1-pro")
        received = []

        def fake_create(config: TTSConfig, *, fish_audio=None):
            received.append(fish_audio)
            return fish_engine

        router = RoutedTTSEngine(fish_audio=settings)
        with patch("src.infrastructure.tts.engines.TTSEngineFactory.create", side_effect=fake_create):
            await router.generate_audio("oi", TTSConfig(engine="fish-audio", voice_id=FISH_VOICE_ID))

        assert received == [settings]

    async def test_caches_one_engine_instance_per_engine_key(self):
        fish_engine = AsyncMock()
        fish_engine.generate_audio = AsyncMock(return_value=AudioFile(path="/tmp/fish.mp3"))
        create_calls = []

        def fake_create(config: TTSConfig, *, fish_audio=None):
            create_calls.append(config.engine)
            return fish_engine

        router = RoutedTTSEngine(fish_audio=FishAudioSettings(api_key="k"))
        config = TTSConfig(engine="fish-audio", voice_id=FISH_VOICE_ID)
        with patch("src.infrastructure.tts.engines.TTSEngineFactory.create", side_effect=fake_create):
            await router.generate_audio("um", config)
            await router.generate_audio("dois", config)

        assert create_calls == ["fish-audio"]


@pytest.mark.asyncio
class TestGTTSEngine:
    """Test GTTSEngine (requires network)."""

    @pytest.mark.skip(reason="Requires network connection")
    async def test_generate_audio(self, sample_tts_config):
        """Test generating audio with gTTS."""
        from src.infrastructure.tts.engines import GTTSEngine

        engine = GTTSEngine()
        config = TTSConfig(engine="gtts", language="en")

        audio = await engine.generate_audio("Hello world", config)
        cleanup = FileAudioCleanup()

        assert audio is not None
        assert audio.path.endswith(".mp3")

        # Cleanup
        await cleanup.cleanup(audio)

    async def test_generate_audio_cleans_temp_file_after_cancellation(self):
        from src.infrastructure.tts.engines import GTTSEngine

        engine = GTTSEngine()
        config = TTSConfig(engine="gtts", language="en")
        release = threading.Event()
        generated_paths = []

        def fake_generate_sync(text: str, config: TTSConfig, output_path: str):
            generated_paths.append(output_path)
            release.wait(timeout=1)
            Path(output_path).write_text("audio", encoding="utf-8")

        engine._generate_sync = fake_generate_sync

        task = asyncio.create_task(engine.generate_audio("Hello world", config))
        await asyncio.sleep(0.05)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

        release.set()
        await asyncio.sleep(0.1)

        assert generated_paths
        assert not Path(generated_paths[0]).exists()


@pytest.mark.asyncio
class TestEdgeTTSEngine:
    async def test_generate_audio_uses_selected_edge_voice(self):
        from src.infrastructure.tts.engines import EdgeTTSEngine

        saved_calls = []

        class FakeCommunicate:
            def __init__(self, text: str, voice: str, rate: str):
                saved_calls.append({"text": text, "voice": voice, "rate": rate})

            async def save(self, path: str):
                saved_calls[-1]["path"] = path

        fake_module = SimpleNamespace(Communicate=FakeCommunicate)

        with patch.dict(sys.modules, {"edge_tts": fake_module}):
            engine = EdgeTTSEngine()
            config = TTSConfig(engine="edge-tts", language="pt-BR", voice_id="pt-BR-FranciscaNeural", rate=180)
            audio = await engine.generate_audio("Oi", config)

        try:
            assert audio.path.endswith(".mp3")
            assert saved_calls[0]["voice"] == "pt-BR-FranciscaNeural"
            assert saved_calls[0]["rate"] == "+0%"
        finally:
            # The fake never writes, so the engine hands back a real temp file
            # nobody deletes. Pre-existing leak: one 0-byte file per test run.
            Path(audio.path).unlink(missing_ok=True)

    async def test_generate_audio_cleans_temp_file_when_cancelled(self):
        from src.infrastructure.tts.engines import EdgeTTSEngine

        saved_calls = []

        class FakeCommunicate:
            def __init__(self, text: str, voice: str, rate: str):
                saved_calls.append({"text": text, "voice": voice, "rate": rate})

            async def save(self, path: str):
                saved_calls[-1]["path"] = path
                await asyncio.Future()

        fake_module = SimpleNamespace(Communicate=FakeCommunicate)

        with patch.dict(sys.modules, {"edge_tts": fake_module}):
            engine = EdgeTTSEngine()
            config = TTSConfig(engine="edge-tts", language="pt-BR", voice_id="pt-BR-FranciscaNeural", rate=180)
            task = asyncio.create_task(engine.generate_audio("Oi", config))
            await asyncio.sleep(0.05)
            task.cancel()

            with pytest.raises(asyncio.CancelledError):
                await task

        assert saved_calls
        assert not Path(saved_calls[0]["path"]).exists()


class _FakeFishResponse:
    """Minimal stand-in for an aiohttp response used as an async context manager."""

    def __init__(
        self,
        status: int,
        chunks=(),
        body: str = "",
        hang: bool = False,
        hang_signal: asyncio.Event | None = None,
        raise_on_post: BaseException | None = None,
        raise_mid_stream: BaseException | None = None,
    ):
        self.status = status
        self._chunks = list(chunks)
        self._body = body
        self._hang = hang
        self._hang_signal = hang_signal
        self.raise_on_post = raise_on_post
        self._raise_mid_stream = raise_mid_stream
        self.content = SimpleNamespace(iter_chunked=self._iter_chunked)

    def _iter_chunked(self, _size: int):
        async def _generator():
            for chunk in self._chunks:
                yield chunk
            if self._raise_mid_stream is not None:
                raise self._raise_mid_stream
            if self._hang:
                if self._hang_signal is not None:
                    self._hang_signal.set()
                await asyncio.Future()

        return _generator()

    async def text(self) -> str:
        return self._body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc):
        return False


class _FakeFishSession:
    """Stand-in for aiohttp.ClientSession that records the single POST it serves."""

    def __init__(self, response: _FakeFishResponse, calls: list):
        self._response = response
        self._calls = calls

    def post(self, url, json=None, headers=None, allow_redirects=True):
        self._calls.append(
            {"url": url, "json": json, "headers": headers, "allow_redirects": allow_redirects}
        )
        if self._response.raise_on_post is not None:
            raise self._response.raise_on_post
        return self._response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc):
        return False


def _patch_fish_session(response: _FakeFishResponse):
    """Patch the engine's aiohttp.ClientSession and return (patcher, calls)."""
    calls: list = []
    patcher = patch(
        "src.infrastructure.tts.engines.aiohttp.ClientSession",
        lambda *a, **kw: _FakeFishSession(response, calls),
    )
    return patcher, calls


@pytest.mark.asyncio
class TestFishAudioEngine:
    """Test the Fish Audio HTTP engine."""

    def _engine(self, **kwargs):
        from src.infrastructure.tts.engines import FishAudioEngine

        settings = FishAudioSettings(**{"api_key": "secret-key-value", **kwargs})
        return FishAudioEngine(settings)

    def _config(self, rate: int = 180, voice_id: str = FISH_VOICE_ID) -> TTSConfig:
        return TTSConfig(engine="fish-audio", language="pt", voice_id=voice_id, rate=rate)

    async def test_generate_audio_sends_expected_request_and_returns_mp3(self):
        response = _FakeFishResponse(200, chunks=[b"ID3", b"audio-bytes"])
        patcher, calls = _patch_fish_session(response)

        with patcher:
            audio = await self._engine().generate_audio("Olá mundo", self._config())

        try:
            assert audio.path.endswith(".mp3")
            assert Path(audio.path).read_bytes() == b"ID3audio-bytes"
            assert calls[0]["url"] == "https://api.fish.audio/v1/tts"
            assert calls[0]["headers"]["model"] == "s2.1-pro-free"
            assert calls[0]["headers"]["Authorization"] == "Bearer secret-key-value"
            assert calls[0]["json"]["reference_id"] == FISH_VOICE_ID
            assert calls[0]["json"]["text"] == "Olá mundo"
            assert calls[0]["json"]["format"] == "mp3"
            # Authorization must not follow a cross-origin redirect, independently
            # of the aiohttp version floor.
            assert calls[0]["allow_redirects"] is False
        finally:
            Path(audio.path).unlink(missing_ok=True)

    async def test_authorization_does_not_follow_redirects(self):
        """Security control: the credential must not travel on a 3xx.

        Named separately so a failure reads as a security regression rather
        than as a request-shape mismatch.
        """
        response = _FakeFishResponse(200, chunks=[b"x"])
        patcher, calls = _patch_fish_session(response)

        with patcher:
            audio = await self._engine().generate_audio("Oi", self._config())

        try:
            assert calls[0]["allow_redirects"] is False
        finally:
            Path(audio.path).unlink(missing_ok=True)

    async def test_empty_key_does_not_mangle_the_message(self):
        """str.replace("") would splice the marker between every character."""
        from src.infrastructure.tts.engines import FishAudioEngine

        engine = FishAudioEngine(FishAudioSettings(api_key="   "))

        assert engine._redact_api_key("plain message") == "plain message"

    async def test_short_key_is_still_redacted(self):
        """A short credential is still a credential; readability does not win."""
        from src.infrastructure.tts.engines import FishAudioEngine

        engine = FishAudioEngine(FishAudioSettings(api_key="abc"))

        assert "abc" not in engine._redact_api_key("token abc rejected")

    async def test_generate_audio_omits_language(self):
        """The Fish voice model determines the language, so it is not sent."""
        response = _FakeFishResponse(200, chunks=[b"x"])
        patcher, calls = _patch_fish_session(response)

        with patcher:
            audio = await self._engine().generate_audio("Oi", self._config())

        try:
            assert "language" not in calls[0]["json"]
        finally:
            Path(audio.path).unlink(missing_ok=True)

    async def test_configured_model_is_sent(self):
        response = _FakeFishResponse(200, chunks=[b"x"])
        patcher, calls = _patch_fish_session(response)

        with patcher:
            audio = await self._engine(model="s2.1-pro").generate_audio("Oi", self._config())

        try:
            assert calls[0]["headers"]["model"] == "s2.1-pro"
        finally:
            Path(audio.path).unlink(missing_ok=True)

    @pytest.mark.parametrize(
        ("rate", "expected"),
        [(180, 1.0), (50, 0.5), (90, 0.5), (360, 2.0), (300, 1.667)],
    )
    async def test_rate_maps_to_prosody_speed(self, rate, expected):
        response = _FakeFishResponse(200, chunks=[b"x"])
        patcher, calls = _patch_fish_session(response)

        with patcher:
            audio = await self._engine().generate_audio("Oi", self._config(rate=rate))

        try:
            assert calls[0]["json"]["prosody"]["speed"] == expected
            assert 0.5 <= calls[0]["json"]["prosody"]["speed"] <= 2.0
        finally:
            Path(audio.path).unlink(missing_ok=True)

    async def test_missing_credential_fails_before_any_request(self):
        from src.infrastructure.tts.engines import FishAudioEngine

        engine = FishAudioEngine(FishAudioSettings(api_key=""))
        response = _FakeFishResponse(200, chunks=[b"x"])
        patcher, calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError, match="FISH_AUDIO"):
            await engine.generate_audio("Oi", self._config())

        assert calls == []

    @pytest.mark.parametrize(
        ("status", "body", "expected_fragment"),
        [
            (401, '{"status":401,"message":"Unauthorized"}', "API key"),
            (402, '{"status":402,"message":"Insufficient API credit"}', "requires API credit"),
            (404, '{"status":404,"message":"Model not found"}', "was not found"),
            # Measured 2026-10-07: an unknown reference_id answers 400, not 404.
            (400, '{"status":400,"message":"Reference not found"}', "was not found"),
            (422, '{"status":422,"message":"Validation error"}', "rejected the request"),
            (400, '{"status":400,"message":"Bad chunk_length"}', "rejected the request"),
            (500, '{"status":500,"message":"Internal"}', "failed with status 500"),
        ],
    )
    async def test_error_statuses_produce_distinct_messages(self, status, body, expected_fragment):
        response = _FakeFishResponse(status, body=body)
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError) as excinfo:
            await self._engine().generate_audio("Oi", self._config())

        assert expected_fragment in str(excinfo.value)

    @pytest.mark.parametrize("status", [400, 401, 402, 404, 422, 500])
    async def test_failure_messages_never_leak_the_api_key(self, status):
        response = _FakeFishResponse(status, body=f'{{"status":{status},"message":"nope"}}')
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError) as excinfo:
            await self._engine().generate_audio("Oi", self._config())

        assert "secret-key-value" not in str(excinfo.value)

    async def test_voice_not_found_message_names_the_voice_id(self):
        response = _FakeFishResponse(400, body='{"status":400,"message":"Reference not found"}')
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError) as excinfo:
            await self._engine().generate_audio("Oi", self._config())

        message = str(excinfo.value)
        assert FISH_VOICE_ID in message
        assert "voice_id" in message

    async def test_credit_message_names_the_configured_model(self):
        response = _FakeFishResponse(402, body='{"status":402,"message":"Insufficient API credit"}')
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError) as excinfo:
            await self._engine(model="s2.1-pro-free").generate_audio("Oi", self._config())

        assert "s2.1-pro-free" in str(excinfo.value)

    async def test_generate_audio_cleans_temp_file_on_error(self):
        created: list[str] = []
        real_create = None

        from src.infrastructure.tts import engines as engines_module

        real_create = engines_module._create_temp_audio_path

        def _tracking_create(suffix: str) -> str:
            path = real_create(suffix)
            created.append(path)
            return path

        response = _FakeFishResponse(401, body='{"status":401,"message":"Unauthorized"}')
        patcher, _calls = _patch_fish_session(response)

        with (
            patcher,
            patch.object(engines_module, "_create_temp_audio_path", _tracking_create),
            pytest.raises(FishAudioError),
        ):
            await self._engine().generate_audio("Oi", self._config())

        assert created
        assert not Path(created[0]).exists()

    async def test_generate_audio_cleans_temp_file_when_cancelled(self):
        created: list[str] = []

        from src.infrastructure.tts import engines as engines_module

        real_create = engines_module._create_temp_audio_path

        def _tracking_create(suffix: str) -> str:
            path = real_create(suffix)
            created.append(path)
            return path

        reached_hang = asyncio.Event()
        response = _FakeFishResponse(200, chunks=[b"x"], hang=True, hang_signal=reached_hang)
        patcher, _calls = _patch_fish_session(response)

        with patcher, patch.object(engines_module, "_create_temp_audio_path", _tracking_create):
            task = asyncio.create_task(self._engine().generate_audio("Oi", self._config()))
            # Wait for the engine to actually reach the hang instead of sleeping:
            # cancelling too early would land before the temp file exists.
            await asyncio.wait_for(reached_hang.wait(), timeout=5)
            task.cancel()

            with pytest.raises(asyncio.CancelledError):
                await task

        assert created
        assert not Path(created[0]).exists()

    async def test_empty_success_body_is_an_error_not_silence(self):
        """A 200 with no chunks must not be returned as a playable file."""
        response = _FakeFishResponse(200, chunks=[])
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError, match="empty audio stream"):
            await self._engine().generate_audio("Oi", self._config())

    async def test_empty_success_body_cleans_temp_file(self):
        created: list[str] = []

        from src.infrastructure.tts import engines as engines_module

        real_create = engines_module._create_temp_audio_path

        def _tracking_create(suffix: str) -> str:
            path = real_create(suffix)
            created.append(path)
            return path

        response = _FakeFishResponse(200, chunks=[])
        patcher, _calls = _patch_fish_session(response)

        with (
            patcher,
            patch.object(engines_module, "_create_temp_audio_path", _tracking_create),
            pytest.raises(FishAudioError),
        ):
            await self._engine().generate_audio("Oi", self._config())

        assert created
        assert not Path(created[0]).exists()

    async def test_transport_error_becomes_a_fish_audio_error(self):
        """A raw aiohttp error must not reach the caller as itself."""
        import aiohttp

        response = _FakeFishResponse(200, chunks=[b"x"], raise_on_post=aiohttp.ClientError("boom"))
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError, match="request failed"):
            await self._engine().generate_audio("Oi", self._config())

    async def test_transport_error_cleans_temp_file(self):
        import aiohttp

        created: list[str] = []

        from src.infrastructure.tts import engines as engines_module

        real_create = engines_module._create_temp_audio_path

        def _tracking_create(suffix: str) -> str:
            path = real_create(suffix)
            created.append(path)
            return path

        response = _FakeFishResponse(200, raise_on_post=aiohttp.ClientError("boom"))
        patcher, _calls = _patch_fish_session(response)

        with (
            patcher,
            patch.object(engines_module, "_create_temp_audio_path", _tracking_create),
            pytest.raises(FishAudioError),
        ):
            await self._engine().generate_audio("Oi", self._config())

        assert created
        assert not Path(created[0]).exists()

    async def test_timeout_becomes_a_fish_audio_error(self):
        response = _FakeFishResponse(200, raise_on_post=TimeoutError())
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError, match="timed out"):
            await self._engine().generate_audio("Oi", self._config())

    async def test_partial_stream_failure_cleans_temp_file(self):
        """A connection reset after some bytes landed must not leave the file."""
        import aiohttp

        created: list[str] = []

        from src.infrastructure.tts import engines as engines_module

        real_create = engines_module._create_temp_audio_path

        def _tracking_create(suffix: str) -> str:
            path = real_create(suffix)
            created.append(path)
            return path

        response = _FakeFishResponse(200, chunks=[b"partial"], raise_mid_stream=aiohttp.ClientError("reset"))
        patcher, _calls = _patch_fish_session(response)

        with (
            patcher,
            patch.object(engines_module, "_create_temp_audio_path", _tracking_create),
            pytest.raises(FishAudioError),
        ):
            await self._engine().generate_audio("Oi", self._config())

        assert created
        assert not Path(created[0]).exists()

    @pytest.mark.parametrize(
        ("body", "expected"),
        [
            ("<html><body>502 Bad Gateway</body></html>", "502 Bad Gateway"),
            ("", "no detail reported"),
            ("   ", "no detail reported"),
            # Valid JSON without a "message" field relays the bounded raw body.
            ('{"status":502}', '{"status":502}'),
        ],
    )
    async def test_non_json_and_empty_error_bodies_are_handled(self, body, expected):
        """A gateway HTML page is the most likely real error body."""
        response = _FakeFishResponse(502, body=body)
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError) as excinfo:
            await self._engine().generate_audio("Oi", self._config())

        assert expected in str(excinfo.value)

    async def test_overlong_error_body_is_truncated(self):
        response = _FakeFishResponse(502, body="x" * 5000)
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError) as excinfo:
            await self._engine().generate_audio("Oi", self._config())

        message = str(excinfo.value)
        assert message.endswith("...")
        assert len(message) < 500

    async def test_error_body_echoing_the_key_is_not_relayed_verbatim(self):
        """The leak guard must hold even when the provider echoes the key back."""
        response = _FakeFishResponse(422, body='{"status":422,"message":"bad token secret-key-value"}')
        patcher, _calls = _patch_fish_session(response)

        with patcher, pytest.raises(FishAudioError) as excinfo:
            await self._engine().generate_audio("Oi", self._config())

        assert "secret-key-value" not in str(excinfo.value)

    async def test_no_log_record_contains_the_api_key(self, caplog):
        response = _FakeFishResponse(401, body='{"status":401,"message":"Unauthorized"}')
        patcher, _calls = _patch_fish_session(response)

        with caplog.at_level(logging.DEBUG), patcher, pytest.raises(FishAudioError):
            await self._engine().generate_audio("Oi", self._config())

        assert "secret-key-value" not in caplog.text


class TestFishAudioIsAbsentFromCatalogAndDesktop:
    """Pin the two invariants that keep Fish Audio bot-only and user-supplied.

    Both currently hold by construction rather than by an explicit guard, so
    these tests exist to make a future regression loud instead of silent.
    """

    def test_runtime_catalog_offers_no_fish_audio_voices(self):
        """Platform-independent: stubs the pyttsx3 enumeration the real catalog does."""
        from src.infrastructure.tts.voice_catalog import RuntimeTTSCatalog

        catalog = RuntimeTTSCatalog()
        with patch.object(catalog, "_get_pyttsx3_options", return_value=[]):
            options = catalog.list_voice_options()

        engines = {option.engine for option in options}
        assert "fish-audio" not in engines
        assert {"gtts", "edge-tts"} <= engines

    def test_desktop_engine_picker_excludes_fish_audio_even_if_catalogued(self):
        """The desktop list is a hardcoded order, not a mirror of the catalog."""
        from src.application.tts_voice_catalog import TTSVoiceOption
        from src.desktop.gui.settings_gui_dialog import GUIConfig

        class _CatalogWithFish:
            def list_voice_options(self):
                return [
                    TTSVoiceOption(
                        key="gtts:pt:roa-pt-br",
                        engine="gtts",
                        label="Google TTS - Portuguese (Brazil)",
                        language="pt",
                        voice_id="roa/pt-br",
                    ),
                    TTSVoiceOption(
                        key="fish-audio:lula",
                        engine="fish-audio",
                        label="Fish Audio - someone added this later",
                        language="pt",
                        voice_id="0123456789abcdef0123456789abcdef",
                    ),
                ]

        dialog = GUIConfig.__new__(GUIConfig)
        # The dialog is built without __init__ to avoid a Tk root; the catalog
        # is the only collaborator _list_engine_values touches.
        object.__setattr__(dialog, "_tts_catalog", _CatalogWithFish())

        assert "fish-audio" not in dialog._list_engine_values()

    def test_desktop_sources_never_reference_fish_audio(self):
        """The Desktop App must not grow a path that needs a Fish credential."""
        desktop_root = Path(__file__).resolve().parents[3] / "src" / "desktop"
        offenders = []
        for path in desktop_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "FISH_AUDIO" in text or "fish-audio" in text or "FishAudio" in text:
                offenders.append(path.name)

        assert offenders == []


class TestFishAudioSettingsDoNotDiscloseTheKey:
    """`repr` is the confidentiality gap a frozen dataclass does not close."""

    def test_repr_omits_the_api_key(self):
        settings = FishAudioSettings(api_key="secret-key-value", model="s2.1-pro")

        rendered = repr(settings)

        assert "secret-key-value" not in rendered
        assert "s2.1-pro" in rendered

    def test_repr_of_a_structure_holding_settings_omits_the_key(self):
        settings = FishAudioSettings(api_key="secret-key-value")

        assert "secret-key-value" not in repr({"fish": settings})
        assert "secret-key-value" not in repr([settings])


class TestConfigVoiceFallThrough:
    """`/config voice:<32-hex>` selects Fish Audio without a catalog entry."""

    def _builder(self):
        from src.infrastructure.tts.voice_catalog import RuntimeTTSCatalog
        from src.presentation.discord_command_handlers import _BaseConfigEmbedBuilder

        return _BaseConfigEmbedBuilder(RuntimeTTSCatalog())

    def test_raw_reference_id_resolves_to_fish_audio(self):
        selection = self._builder()._resolve_voice_selection("0123456789abcdef0123456789abcdef")

        assert selection is not None
        assert selection.engine == "fish-audio"
        assert selection.voice_id == "0123456789abcdef0123456789abcdef"

    def test_fish_selection_leaves_language_untouched(self):
        """Fish ignores language; None means the stored value is not updated."""
        selection = self._builder()._resolve_voice_selection("0123456789abcdef0123456789abcdef")

        assert selection is not None
        assert selection.language is None

    def test_whitespace_and_case_are_tolerated(self):
        selection = self._builder()._resolve_voice_selection("  0123456789ABCDEF0123456789ABCDEF \n")

        assert selection is not None
        assert selection.engine == "fish-audio"
        # The canonical value, not the raw input: this is the call site that
        # hands the identifier to the config store.
        assert selection.voice_id == "0123456789ABCDEF0123456789ABCDEF"
        assert selection.voice_id.strip() == selection.voice_id

    def test_catalog_key_takes_precedence(self):
        selection = self._builder()._resolve_voice_selection("edge-tts:pt-br-francisca")

        assert selection is not None
        assert selection.engine == "edge-tts"
        assert selection.language == "pt-BR"

    def test_unresolvable_voice_returns_none(self):
        builder = self._builder()

        assert builder._resolve_voice_selection("not-a-voice") is None
        assert builder._resolve_voice_selection("") is None
        assert builder._resolve_voice_selection("0123456789abcdef0123456789abcde") is None
