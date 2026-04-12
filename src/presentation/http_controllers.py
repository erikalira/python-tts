"""HTTP controllers for handling web requests."""

import logging

from aiohttp import web

from src.application.dto import SpeakTextInputDTO, VoiceContextQueryDTO
from src.application.use_cases import GetCurrentVoiceContextUseCase, SpeakTextUseCase
from src.core.entities import TTSConfig
from src.core.interfaces import IConfigRepository
from src.presentation.http_presenters import HTTPSpeakPresenter, HTTPVoiceContextPresenter

logger = logging.getLogger(__name__)


class SpeakController:
    """Controller for /speak endpoint."""

    def __init__(
        self,
        speak_use_case: SpeakTextUseCase,
        config_repository: IConfigRepository | None = None,
    ):
        self._speak_use_case = speak_use_case
        self._config_repository = config_repository
        self._presenter = HTTPSpeakPresenter()

    async def handle(self, request: web.Request) -> web.Response:
        try:
            data = await request.json()
        except Exception as exc:
            logger.error("Invalid JSON: %s", exc)
            return web.Response(text="invalid json", status=400)

        guild_id = self._parse_int(data.get("guild_id"))
        tts_request = SpeakTextInputDTO(
            text=data.get("text", ""),
            channel_id=self._parse_int(data.get("channel_id")),
            guild_id=guild_id,
            member_id=self._parse_int(data.get("member_id") or data.get("user_id")),
            config_override=self._parse_config_override(data, guild_id),
        )
        result = await self._speak_use_case.execute(tts_request)
        return web.Response(
            text=self._presenter.build_message(result),
            status=self._presenter.get_status_code(result),
        )

    def _parse_int(self, value) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _parse_config_override(self, data: dict, guild_id: int | None = None) -> TTSConfig | None:
        override = data.get("config_override")
        if not isinstance(override, dict):
            override = data

        engine = override.get("engine")
        language = override.get("language")
        voice_id = override.get("voice_id")
        rate = override.get("rate")

        if engine is None and language is None and voice_id is None and rate is None:
            return None

        base_config = self._get_base_config(guild_id)
        return TTSConfig(
            engine=str(engine or base_config.engine),
            language=str(language or base_config.language),
            voice_id=str(voice_id or base_config.voice_id),
            rate=self._parse_int(rate) or base_config.rate,
            output_device=base_config.output_device,
        )

    def _get_base_config(self, guild_id: int | None) -> TTSConfig:
        if self._config_repository is None:
            return TTSConfig()
        return self._config_repository.get_config(guild_id)


class VoiceContextController:
    """Controller for querying the current voice context for a member."""

    def __init__(self, voice_context_use_case: GetCurrentVoiceContextUseCase):
        self._voice_context_use_case = voice_context_use_case
        self._presenter = HTTPVoiceContextPresenter()

    async def handle(self, request: web.Request) -> web.Response:
        query = VoiceContextQueryDTO(
            member_id=self._parse_int(request.query.get("member_id") or request.query.get("user_id"))
        )
        result = await self._voice_context_use_case.execute(query)
        return web.json_response(
            self._presenter.to_payload(result),
            status=self._presenter.get_status_code(result),
        )

    def _parse_int(self, value) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
